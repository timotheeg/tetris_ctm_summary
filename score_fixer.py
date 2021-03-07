class ScoreFixer(object):
	def __init__(self):
		self.lastGoodLabel = None

	def charToDigit(self, item):
		return int(item, 16)

	def digitToChar(self, item):
		return hex(item).upper()[2:]

	def reset(self):
		self.lastGoodLabel = None

	def fix(self, label, value):
		if (label is None) or (self.lastGoodLabel is None):
			self.lastGoodLabel = label
			return label, value

		if self.lastGoodLabel[0] == label[0]:
			self.lastGoodLabel = label
			return label, value

		goodFirstDigit = self.charToDigit(self.lastGoodLabel[0])
		newFirstDigit = self.charToDigit(label[0])

		# we should only be able to up by one digit at a time...
		if newFirstDigit == goodFirstDigit + 1:
			self.lastGoodLabel = label
			return label, value

		# K, if this point is reached, something is not right, and we need to apply correction

		# switch first digit between 8 and B dependant on last state.
		if self.lastGoodLabel[0] == "A" or self.lastGoodLabel[0] == "B":
			if label[0] == "8":
				label = "B" + label[1:]
				value += (11-8)*10**6

		elif self.lastGoodLabel[0] == "7" or self.lastGoodLabel[0] == "8":
			if label[0] == "B":
				label = "8" + label[1:]
				value += (8-11)*10**6

		# switch first digit between 4 and A dependant on last state.
		elif self.lastGoodLabel[0] == "9" or self.lastGoodLabel[0] == "A":
			if label[0] == "4":
				label = "A" + label[1:]
				value += (10-4)*10**6

		elif self.lastGoodLabel[0] == "3" or self.lastGoodLabel[0] == "4":
			if label[0] == "A":
				label = "4" + label[1:]
				value += (4-10)*10**6

		self.lastGoodLabel = label

		return label, value

