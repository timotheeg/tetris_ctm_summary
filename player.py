from utils import xywh_to_ltrb
from digitocr import scoreImage
from score_fixer import ScoreFixer
from level_fixer import LevelFixer

from optimal_scores_generator import scoring_potential

FRAMES_READ_DELAY = 1

DEATH_NULLS = 5

def tetris_value(level):
	return 1200 * (level + 1)

class Player:
	def __init__(self, lines_loc_xywh, score_loc_xywh, level_loc_xywh, score_stats_xy, pace_stats_xy):
		self.lines_loc = xywh_to_ltrb(lines_loc_xywh)
		self.score_loc = xywh_to_ltrb(score_loc_xywh)
		self.level_loc = xywh_to_ltrb(level_loc_xywh)

		self.score_stats_xy = score_stats_xy
		self.pace_stats_xy = pace_stats_xy

		self.remaining_delay_frames = 0 # controls one frame delay to read line count

		self.score = 0
		self.lines = 0
		self.level = 0
		self.pace_score = 0

		self.not_in_game_count = 1
		self.pending_lines = True
		self.pending_score = True

		self.score_fixer = ScoreFixer()
		self.level_fixer = LevelFixer()

		self.tetris_line_count = 0
		self.total_line_count = None

	# coded for 18 start
	@staticmethod
	def getTetrisDiff(p1, p2, use_pace_score=False):
		p1_score = p1.pace_score if use_pace_score else p1.score
		p2_score = p2.pace_score if use_pace_score else p2.score

		if p1_score > p2_score:
			level = p2.level
			lines = p2.lines
		elif p2_score > p1_score:
			level = p1.level
			lines = p1.lines
		else:
			return 0

		tetrises = 0
		diff = abs(p1_score - p2_score)

		while diff > 0:
			if lines >= 126: # below 126 lines, level doesn't change every 10 lines
				if lines % 10 >= 6: # the tetris is counted at end level, not start level
					level += 1

			lines += 4
			tetrises += 1

			diff -= tetris_value(level)

		# correct the overshot
		# note: diff is negative, to this statement *reduces* the tetrises value
		tetrises += diff / tetris_value(level)

		return tetrises

	def setFrame(self, frame):
		lines_img = frame.crop(self.lines_loc)
		lines = scoreImage(lines_img, "TDD")[1]

		score_img = frame.crop(self.score_loc)
		score_label, score  = scoreImage(score_img, "ADDDDD")

		level_img = frame.crop(self.level_loc)
		level_label, level = scoreImage(level_img, "TA")

		return self.setFrameData(lines, score, level, score_label, level_label)

	def setFrameData(self, lines, score, level, score_label, level_label): # lines, score, level
		# assign raw data not suitable for computation, but useful to debug
		self.raw_data = (score, lines, level, score_label, level_label) # matches the order of the verify data

		# we always set values after 1 frame delay
		# That is to allow them to settle and fix incorrect reads

		if lines is None or score is None or level is None:
			self.not_in_game_count += 1

			if self.not_in_game_count == DEATH_NULLS:
				# player considered dead, score potential IS score
				self.pace_score = self.score
				return True

			return False

		elif self.not_in_game_count:
			self.not_in_game_count = 0
			self.pending_lines = False
			self.pending_score = False
			self.lines = lines
			self.score = score
			self.level = level
			self.pace_score = self.getPaceMaxScore()

			self.score_fixer.reset()
			self.score_fixer.fix(score_label, score)

			self.level_fixer.reset()
			self.level_fixer.fix(level_label, level)

			return True

		changed = False

		if self.pending_lines:
			changed = True
			self.pending_lines = False;

			if lines == None or lines == 0:
				self.tetris_line_count = 0
			else:
				cleared = lines - (self.lines or 0)
				if cleared == 4:
					self.tetris_line_count =+ 4

			self.lines = lines;
			self.level = self.level_fixer.fix(level_label, level)[1]
			self.pace_score = self.getPaceMaxScore()

		elif lines != self.lines:
			self.pending_lines = True

		if self.pending_score:
			new_score = self.score_fixer.fix(score_label, score)[1]
			if new_score != self.score:
				changed = True
				self.pending_score = False;
				self.score = new_score
				self.pace_score = self.getPaceMaxScore()
		elif score != self.score:
			self.pending_score = True

		return changed

	def getPaceMaxScore(self):
		try:
			return self.score + scoring_potential[self.lines]['score']
		except:
			return self.score # assume key error, lines > 230, extra potential is 0

		# code below is a naive algorithm, that just scores tetrises all the way into the kill screen
		# the table scoring_potential contains better strategies to squeeze single/double/triples
		# to truly maximise the score

		"""
		# calculate maximum possible score from this point in the game
		# assume lvl18 starts

		level = self.level
		score = self.score
		lines = self.lines

		# Naive iterative computation... Maybe there's a formula to get it quick?
		# Oh well...

		# Basically, we assume scoring all tetrises till into kill screen
		while lines < 230:
			if lines >= 126: # below 126 lines, level doesn't change every 10 lines
				if lines % 10 >= 6: # the tetris is counted at end level, not start level
					level += 1

			lines += 4
			score += tetris_value(level)

		return score;
		"""


	def getData(self, frame_idx):
		return self.lines, self.score, self.level;

	def getTRTLabel(self):
		if self.lines == None:
			label = ""
		elif self.lines == 0:
			label = "---"
		else:
			trt = self.tetris_line_count / self.lines

			if trt >= 1:
				label = "100"
			else:
				label = "%02d%%" % round(trt * 100) # should this be floor insted of round?

		return label
