import sys
import numpy
import cv2
import time
import json

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from player import Player

start_time = time.time()

source_file = sys.argv[1]

cap = cv2.VideoCapture(source_file)

font = ImageFont.truetype(r'./prstartk_nes_tetris_8.ttf', 32)
font_big = ImageFont.truetype(r'./prstartk_nes_tetris_8.ttf', 64)

font_size = 32

p1_line_count_xywh = (818, 58, 101, 31)
p1_score_xywh = (572, 59, 206, 32)
p1_level_xywh = (577, 168, 57, 28)
p1_stats_xy = (507, 110) # player 1 data will be right aligned on the x

p2_line_count_xywh = (1260, 58, 100, 32)
p2_score_xywh = (1016, 61, 205, 32)
p2_level_xywh = (1022, 171, 56, 27)
p2_stats_xy = (1430, 110)

player1 = Player(p1_line_count_xywh, p1_score_xywh, p1_level_xywh, p1_stats_xy)
player2 = Player(p2_line_count_xywh, p2_score_xywh, p2_level_xywh, p2_stats_xy)

players = [player1, player2]

output_file = "%s.out.mp4" % source_file

print("Generating Stats from file\n%s\ninto output file\n%s" % (
	source_file,
	output_file
))

total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
base_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
base_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter(
	output_file,
	cv2.VideoWriter_fourcc(*'mp4v'),
	23.976,
	(
		base_width,
		base_height
	)
)

composite_color = (255, 0, 255, 0)


def drawTextWithBorder(draw, text, loc, color, font):
	x, y = loc

	border_col  = (0, 0, 0, 255)

	# thin border
	draw.text((x-3,   y), text, border_col, font=font)
	draw.text((x+3,   y), text, border_col, font=font)
	draw.text((x,   y-3), text, border_col, font=font)
	draw.text((x,   y+3), text, border_col, font=font)

	# thicker border
	draw.text((x-3, y-3), text, border_col, font=font)
	draw.text((x+3, y-3), text, border_col, font=font)
	draw.text((x-3, y+3), text, border_col, font=font)
	draw.text((x+3, y+3), text, border_col, font=font)

	# now draw the text over it
	draw.text((x, y), text, color, font=font)


spacing = 10

def drawStats(frame):
	red = (0xef, 0x05, 0x05)
	green = (0x2e, 0xff, 0x10)
	white = (0xff, 0xff, 0xff)

	draw = ImageDraw.Draw(frame)

	try:
		score_diff = abs(player1.score - player2.score)
		tetris_diff = Player.getTetrisDiff(player1, player2)

		pace_diff = abs(player1.pace_score - player2.pace_score)
		pace_tetris_diff = Player.getTetrisDiff(player1, player2, use_pace_score=True)
	except Exception as err:
		print('exception', player1.score, player2.score)
		print(err)
		print("")
		return

	p1 = {}
	p2 = {}

	if player1.score < player2.score:
		p1["score"] = {
			"score": "-%d" % (score_diff, ),
			"tetrises": "-%.2f" % (tetris_diff, ),
			"color": red
		}
		p2["score"] = {
			"score": "+%d" % (score_diff, ),
			"tetrises": "+%.2f" % (tetris_diff, ),
			"color": green
		}
	elif player1.score < player2.score:
		p1["score"] = {
			"score": "-%d" % (score_diff, ),
			"tetrises": "-%.2f" % (tetris_diff, ),
			"color": red
		}
		p2["score"] = {
			"score": "+%d" % (score_diff, ),
			"tetrises": "+%.2f" % (tetris_diff, ),
			"color": green
		}
	else:
		p1["score"] = p2["score"] = {
			"score": "+0",
			"tetrises": "+0",
			"color": green
		}

	if player1.pace_score < player2.pace_score:
		p1["pace"] = {
			"score": "-%d" % (pace_diff, ),
			"tetrises": "-%.2f" % (pace_tetris_diff, ),
			"color": red
		}
		p2["pace"] = {
			"score": "+%d" % (pace_diff, ),
			"tetrises": "+%.2f" % (pace_tetris_diff, ),
			"color": green
		}
	elif player1.pace_score > player2.pace_score:
		p1["pace"] = {
			"score": "-%d" % (pace_diff, ),
			"tetrises": "-%.2f" % (pace_tetris_diff, ),
			"color": red
		}
		p2["pace"] = {
			"score": "+%d" % (pace_diff, ),
			"tetrises": "+%.2f" % (pace_tetris_diff, ),
			"color": green
		}
	else:
		p1["pace"] = p2["pace"] = {
			"score": "+0",
			"tetrises": "+0",
			"color": green
		}


	# Draw Player 2 first (easier because left aligned)
	x, y = player2.stats_xy

	drawTextWithBorder(draw
		, p2["score"]["score"]
		, (x, y)
		, p2["score"]["color"]
		, font_big
	)

	w, h = draw.textsize(p2["score"]["score"], font_big)
	cur_y = y + h + spacing

	drawTextWithBorder(draw
		, p2["score"]["tetrises"]
		, (x, cur_y)
		, p2["score"]["color"]
		, font
	)

	w, h = draw.textsize(p2["score"]["tetrises"], font)

	drawTextWithBorder(draw
		, "Tetrises"
		, (x + w + spacing, cur_y)
		, white
		, font
	)

	cur_y += h + spacing

	drawTextWithBorder(draw
		, p2["pace"]["score"]
		, (x, cur_y)
		, p2["pace"]["color"]
		, font
	)

	w, h = draw.textsize(p2["pace"]["score"], font)

	drawTextWithBorder(draw
		, "Pace"
		, (x + w + spacing, cur_y)
		, white
		, font
	)

	cur_y += h + spacing

	drawTextWithBorder(draw
		, p2["pace"]["tetrises"]
		, (x, cur_y)
		, p2["pace"]["color"]
		, font
	)

	w, h = draw.textsize(p2["pace"]["tetrises"], font)

	drawTextWithBorder(draw
		, "Tetrises"
		, (x + w + spacing, cur_y)
		, white
		, font
	)


	## and then player 1... right aligned T_T

	x, y = player1.stats_xy
	w, h = draw.textsize(p1["score"]["score"], font_big)
	cur_y = y
	cur_x = x - w

	drawTextWithBorder(draw
		, p1["score"]["score"]
		, (cur_x, cur_y)
		, p1["score"]["color"]
		, font_big
	)

	cur_y += h + spacing

	w, h = draw.textsize("Tetrises", font)
	cur_x = x - w

	drawTextWithBorder(draw
		, "Tetrises"
		, (cur_x, cur_y)
		, white
		, font
	)

	w, h = draw.textsize(p1["score"]["tetrises"], font)
	cur_x -= (w + spacing)

	drawTextWithBorder(draw
		, p1["score"]["tetrises"]
		, (cur_x, cur_y)
		, p1["score"]["color"]
		, font
	)

	cur_y += h + spacing

	w, h = draw.textsize("Pace", font)
	cur_x = x - w

	drawTextWithBorder(draw
		, "Pace"
		, (cur_x, cur_y)
		, white
		, font
	)

	w, h = draw.textsize(p1["pace"]["score"], font)
	cur_x -= (w + spacing)

	drawTextWithBorder(draw
		, p1["pace"]["score"]
		, (cur_x, cur_y)
		, p1["pace"]["color"]
		, font
	)

	cur_y += h + spacing

	w, h = draw.textsize("Tetrises", font)
	cur_x = x - w

	drawTextWithBorder(draw
		, "Tetrises"
		, (cur_x, cur_y)
		, white
		, font
	)

	w, h = draw.textsize(p1["pace"]["tetrises"], font)
	cur_x -= (w + spacing)

	drawTextWithBorder(draw
		, p1["pace"]["tetrises"]
		, (cur_x, cur_y)
		, p1["pace"]["color"]
		, font
	)


frame_idx = -1
last_stats_frame = None

while True:
	cv2_retval, cv2_image = cap.read()

	if not cv2_retval:
		break

	frame_idx += 1

	cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
	frame = Image.fromarray(cv2_image)

	p1_changed = player1.setFrame(frame)
	p2_changed = player2.setFrame(frame)

	changed = p1_changed or p2_changed

	if (last_stats_frame is None) or changed:
		last_stats_frame = Image.new('RGBA', (base_width, base_height), composite_color)
		drawStats(last_stats_frame)

	frame.paste(last_stats_frame, (0, 0), last_stats_frame)

	frame = cv2.cvtColor(numpy.array(frame), cv2.COLOR_RGB2BGR)
	out.write(frame);

	print("Processed frame %d of %d (at %5.1f fps)" %
		(
			frame_idx + 1,
			total_frames,
			(frame_idx + 1) / (time.time() - start_time)
		),
		end="\r"
	)


out.release()

print("\nDone - processed %d frames in %d seconds" % (total_frames, int(time.time() - start_time)))
