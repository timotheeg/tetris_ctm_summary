from utils import xywh_to_ltrb
from digitocr import scoreImage

FRAMES_READ_DELAY = 1

def tetris_value(level):
	return 1200 * (level + 1)

class Player:
	def __init__(self, lines_loc_xywh, score_loc_xywh, level_loc_xywh, stats_xy):
		self.lines_loc = xywh_to_ltrb(lines_loc_xywh)
		self.score_loc = xywh_to_ltrb(score_loc_xywh)
		self.level_loc = xywh_to_ltrb(level_loc_xywh)

		self.stats_xy = stats_xy

		self.remaining_delay_frames = 0 # controls one frame delay to read line count

		self.score = 0
		self.lines = 0
		self.level = 0
		self.pace_score = 0

		self.in_game = False
		self.pending_lines = True
		self.pending_score = True

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
		tetrises += diff / tetris_value(level)

		return tetrises

	def setFrame(self, frame):
		lines_img = frame.crop(self.lines_loc)
		lines = scoreImage(lines_img, "TDD")[1]

		score_img = frame.crop(self.score_loc)
		score = scoreImage(score_img, "ADDDDD")[1]

		level_img = frame.crop(self.level_loc)
		level = scoreImage(level_img, "TD")[1]

		return self.setFrameData((lines, score, level))

	def setFrameData(self, values): # lines, score, level
		# we always set values after 1 frame delay
		# That is to allow them to settle and fix incorrect reads
		lines, score, level = values

		if lines is None or score is None or level is None:
			self.in_game = False
			return False

		elif not self.in_game:
			self.in_game = True
			self.pending_lines = False
			self.pending_score = False
			self.lines = lines
			self.score = score
			self.level = level
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
			self.level = level;

		elif lines != self.lines:
			self.pending_lines = True

		if self.pending_score:
			changed = True
			self.pending_score = False;
			self.score = score;
			self.pace_score = self.getPaceMaxScore()
		elif score != self.score:
			self.pending_score = True

		return changed

	def getPaceMaxScore(self):
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
