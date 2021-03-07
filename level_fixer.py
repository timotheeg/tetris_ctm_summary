class LevelFixer(object):
	def __init__(self):
		self.lastGoodLabel = None

	def reset(self):
		self.lastGoodLabel = None

	def fix(self, label, value):
		if (label is None) or (self.lastGoodLabel is None):
			self.lastGoodLabel = label
			return label, value

		# level maps for 30 to 35
		# 00:30 - 0A:31 - 14:32 - 1E:33 - 28:34 - 32:35
		# what's the logic? 🤔

		# Fix the levels with no ambiguity
		if label == '1E':
			label = '33'
			value = 33

		elif label == '32':
			label = '35'
			value = 35

		# fix the funny ones
		else:
			if self.lastGoodLabel == "29" or self.lastGoodLabel == "30":
				if label == '00':
					label = '30'
					value = 30

			elif self.lastGoodLabel == "30" or self.lastGoodLabel == "31":
				if label == '0A' or label == '04':
					label = '31'
					value = 31

			elif self.lastGoodLabel == "31" or self.lastGoodLabel == "32":
				if label == '14' or label == '1A':
					label = '32'
					value = 32

			elif self.lastGoodLabel == "33" or self.lastGoodLabel == "34":
				if label == '28' or label == '2B':
					label = '34'
					value = 34

			# Fix any other A and B in second place, since they're impossible
			elif label[1] == 'A':
				label = label[0] + '4'
				value += (4-10)

			elif label[1] == 'B':
				label = label[0] + '8'
				value += (8-11)


		self.lastGoodLabel = label

		return label, value