from utils import xywh_to_ltrb
from digitocr import scoreImage
from score_fixer import ScoreFixer

from score_utils import (
    getPotentialScore,
    getTetrisValue,
    getTransitionLines,
    getLevel,
)

FRAMES_READ_DELAY = 1

DEATH_NULLS = 5


class Player:
    def __init__(
        self,
        lines_loc_xywh,
        score_loc_xywh,
        score_stats_xy,
        pace_stats_xy,
        trt_stats_xy,
        start_level=18,
    ):
        self.lines_loc = xywh_to_ltrb(lines_loc_xywh)
        self.score_loc = xywh_to_ltrb(score_loc_xywh)

        self.score_stats_xy = score_stats_xy
        self.pace_stats_xy = pace_stats_xy
        self.trt_stats_xy = trt_stats_xy

        self.start_level = start_level

        self.remaining_delay_frames = 0  # controls one frame delay to read line count

        self.score = 0
        self.lines = 0
        self.level = 0
        self.pace_score = 0

        self.not_in_game_count = 1
        self.pending_score = True

        self.score_fixer = ScoreFixer()

        self.tetris_line_count = 0
        self.total_line_count = None

    # coded for 18 start

    @staticmethod
    def getTetrisDiff(p1, p2, use_pace_score=False) -> float:
        p1_score = p1.pace_score if use_pace_score else p1.score
        p2_score = p2.pace_score if use_pace_score else p2.score

        if p1_score > p2_score:
            level = p2.level
            lines = p2.lines
            transition_lines = getTransitionLines(p2.start_level)
        elif p2_score > p1_score:
            level = p1.level
            lines = p1.lines
            transition_lines = getTransitionLines(p1.start_level)
        else:
            return 0

        tetrises: float = 0
        diff = abs(p1_score - p2_score)

        if lines is None:
            return 0

        while diff > 0:
            if (
                lines >= transition_lines - 4
            ):  # below transition lines, level doesn't change every 10 lines
                if (
                    lines % 10 >= 6
                ):  # the tetris is counted at end level, not start level
                    level += 1

            lines += 4
            tetrises += 1

            diff -= getTetrisValue(level)

        # correct the overshot
        # note: diff is negative, to this statement *reduces* the tetrises value
        tetrises += diff / getTetrisValue(level)

        return tetrises

    def setFrame(self, frame):
        score_img = frame.crop(self.score_loc)
        score_label, score = scoreImage(score_img, "ADDDDD")

        # assign raw data not suitable for computation, but useful to debug
        # matches the order of the verify data
        self.raw_data = (score_label, score, self.lines)

        # we always set values after 1 frame delay
        # That is to allow them to settle and fix incorrect reads

        if score is None:
            self.not_in_game_count += 1

            if self.not_in_game_count == DEATH_NULLS:
                # player considered dead, score potential IS score
                self.pace_score = self.score
                return True

            return False

        elif self.not_in_game_count:
            lines_img = frame.crop(self.lines_loc)
            lines = scoreImage(lines_img, "TDD")[1]
            self.raw_data = (score_label, score, lines)

            self.not_in_game_count = 0
            self.pending_score = False
            self.lines = lines or 0
            self.level = getLevel(self.start_level, self.lines)
            self.score = score
            self.pace_score = self.getPaceMaxScore()

            self.score_fixer.reset()
            self.score_fixer.fix(score_label, score)

            return True

        # When digits change in an interlaced setup, the transition frame can be blurry and yield an incorrect read
        # We introduce a 1-frame delay system for the value to stabilize before checking the value

        # This means stats derived from the value will appear with one frame delay, which we consider acceptable for human viewing

        changed = False

        if self.pending_score:
            self.pending_score = False
            new_score = self.score_fixer.fix(score_label, score)[1]
            if new_score != self.score:
                changed = True
                self.score = new_score

                lines_img = frame.crop(self.lines_loc)
                lines = scoreImage(lines_img, "TDD")[1]
                self.raw_data = (score_label, score, lines)

                # since score changed, assume lines is readable
                if lines is None or lines == 0:
                    self.tetris_line_count = 0
                else:
                    cleared = lines - (self.lines or 0)
                    if cleared == 4:
                        self.tetris_line_count += 4

                self.lines = lines or 0
                self.level = getLevel(self.start_level, self.lines)

                self.pace_score = self.getPaceMaxScore()

        elif score != self.score:
            self.pending_score = True

        return changed

    def getPaceMaxScore(self):
        try:
            return self.score + getPotentialScore(self.start_level, self.lines)
        except Exception:
            return self.score  # assume key error, lines > 230, extra potential is 0

        # Code below is a naive algorithm, that just scores tetrises all the way into
        # the kill screen.
        # The function getPotentialScore implements a better strategy to squeeze single/double/triples
        # to truly maximise the score

        # calculate maximum possible score from this point in the game
        # assume lvl18 starts
        """
        level = self.level
        score = self.score
        lines = self.lines
        # Naive iterative computation... Maybe there's a formula to get it quick?
        # Oh well...
        # Basically, we assume scoring all tetrises till into kill screen
        while lines < 230:
            if lines >= 126:  # below 126 lines, level doesn't change every 10 lines
                if (
                    lines % 10 >= 6
                ):  # the tetris is counted at end level, not start level
                    level += 1
            lines += 4
            score += getTetrisValue(level)
        return score
        """

    def getData(self, frame_idx):
        return self.lines, self.score, self.level

    def getStatsData(self) -> str:
        return (
            f"{self.score}, {self.lines}, {self.level}, {self.pace_score}, "
            + f"{self.tetris_line_count}"
        )

    def getTRTLabel(self):
        if self.lines is None:
            label = ""
        elif self.lines == 0:
            label = "---"
        else:
            trt = self.tetris_line_count / self.lines

            if trt >= 1:
                label = "100"
            else:
                # should this be floor insted of round?
                label = "%02d%%" % round(trt * 100)

        return label
