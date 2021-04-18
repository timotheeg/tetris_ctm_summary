import sys
import numpy
import cv2
import time
import json

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from player import Player

import argparse

start_time = time.time()


parser = argparse.ArgumentParser(description="Compute commpetition Tetris stats")
parser.add_argument("--verify", action="store_true")
parser.add_argument("--snap", type=int)
parser.add_argument("--start_level", type=int, default=18)
parser.add_argument("source_video")

args = parser.parse_args()

source_file = args.source_video

# config must be present and valid, will throw if not
with open("config.json") as f:
    conf = json.load(f)

    # TODO: Make a Proper config class to handle the config file properly
    # i.e. handle default, missing entries, unexpected values, etc.
    if "show_trt" not in conf:
        conf["show_trt"] = False

    if "p1_trt_stats_xy" not in conf:
        conf["p1_trt_stats_xy"] = [406, 0]

    if "p2_trt_stats_xy" not in conf:
        conf["p2_trt_stats_xy"] = [1392, 0]

cap = cv2.VideoCapture(args.source_video)

# More stuff we *could* put in config?
h_spacing = 10  # horizontal spacing
v_spacing = 20  # vertical spacing
font_file = "./prstartk_nes_tetris_8.ttf"

font = ImageFont.truetype(font_file, 36)
font_big = ImageFont.truetype(font_file, 64)
font_small = ImageFont.truetype(font_file, 16)
font_trt = ImageFont.truetype(font_file, 32)

player1 = Player(
    conf["p1_lines_xywh"],
    conf["p1_score_xywh"],
    conf["p1_score_stats_xy"],
    conf["p1_pace_stats_xy"],
    conf["p1_trt_stats_xy"],
    args.start_level,
)
player2 = Player(
    conf["p2_lines_xywh"],
    conf["p2_score_xywh"],
    conf["p2_score_stats_xy"],
    conf["p2_pace_stats_xy"],
    args.start_level,
)

players = [player1, player2]

if args.verify:
    output_file = "%s.verify.mp4" % source_file
else:
    output_file = "%s.out.mp4" % source_file

print(
    "Generating Stats from file\n%s\ninto output file\n%s" % (source_file, output_file)
)

total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
base_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
base_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

if not args.snap:
    out = cv2.VideoWriter(
        output_file,
        cv2.VideoWriter_fourcc(*"mp4v"),
        cap.get(cv2.CAP_PROP_FPS),
        (base_width, base_height),
    )

composite_color = (255, 0, 255, 0)

# TRT Box Variables
trt_box_header_xy = (19, 24)
trt_box_value_xy = (21, 58)
trt_box_template = "./trt_box.png"
trt_box_img = Image.open(trt_box_template)

draw = ImageDraw.Draw(trt_box_img)
draw.text(trt_box_header_xy, "TRT", (255, 255, 255), font=font_trt)


def drawTextWithBorder(draw, text, loc, color, font):
    x, y = loc

    border_col = (0, 0, 0, 255)
    border_width = 4

    if conf["text_has_border"]:
        draw.text((x - border_width, y - border_width), text, border_col, font=font)
        draw.text((x + border_width, y - border_width), text, border_col, font=font)
        draw.text((x - border_width, y + border_width), text, border_col, font=font)
        draw.text((x + border_width, y + border_width), text, border_col, font=font)

    # now draw the text over it
    draw.text((x, y), text, color, font=font)


def drawStats(frame):
    red = (0xEF, 0x10, 0x10)
    green = (0x30, 0xFF, 0x10)
    white = (0xFF, 0xFF, 0xFF)

    draw = ImageDraw.Draw(frame)

    pace_tetris_diff: int = -1  # Add this to appease VSCode Linter. Weird bug? 3/12/21
    try:
        score_diff = abs(player1.score - player2.score)
        tetris_diff = Player.getTetrisDiff(player1, player2)

        pace_diff = abs(player1.pace_score - player2.pace_score)
        pace_tetris_diff = Player.getTetrisDiff(player1, player2, use_pace_score=True)
    except Exception as err:
        print("exception", player1.score, player2.score, pace_diff, pace_tetris_diff)
        print(err)
        print("")
        return

    p1 = {}
    p2 = {}

    if player1.score < player2.score:
        p1["score"] = {
            "score": "-%d" % (score_diff,),
            "tetrises": "-%.2f" % (tetris_diff,),
            "color": red,
        }
        p2["score"] = {
            "score": "+%d" % (score_diff,),
            "tetrises": "+%.2f" % (tetris_diff,),
            "color": green,
        }
    elif player1.score > player2.score:
        p1["score"] = {
            "score": "+%d" % (score_diff,),
            "tetrises": "+%.2f" % (tetris_diff,),
            "color": green,
        }
        p2["score"] = {
            "score": "-%d" % (score_diff,),
            "tetrises": "-%.2f" % (tetris_diff,),
            "color": red,
        }
    else:
        p1["score"] = p2["score"] = {"score": "+0", "tetrises": "+0", "color": green}

    if player1.pace_score < player2.pace_score:
        p1["pace"] = {
            "score": "-%d" % (pace_diff,),
            "tetrises": "-%.2f" % (pace_tetris_diff,),
            "color": red,
        }
        p2["pace"] = {
            "score": "+%d" % (pace_diff,),
            "tetrises": "+%.2f" % (pace_tetris_diff,),
            "color": green,
        }
    elif player1.pace_score > player2.pace_score:
        p1["pace"] = {
            "score": "+%d" % (pace_diff,),
            "tetrises": "+%.2f" % (pace_tetris_diff,),
            "color": green,
        }
        p2["pace"] = {
            "score": "-%d" % (pace_diff,),
            "tetrises": "-%.2f" % (pace_tetris_diff,),
            "color": red,
        }
    else:
        p1["pace"] = p2["pace"] = {"score": "+0", "tetrises": "+0", "color": green}

    # =========================
    # 0. Draw verification data if needed

    if args.verify:
        spacer = 5
        w, h = draw.textsize("0", font_small)

        p1_data = "%d %d %d %d" % (
            player1.score,
            player1.lines,
            player1.level,
            player1.pace_score,
        )
        p2_data = "%d %d %d %d" % (
            player2.score,
            player2.lines,
            player2.level,
            player2.pace_score,
        )

        p1_raw: str = " ".join([str(v).upper() for v in player1.raw_data])
        drawTextWithBorder(draw, p1_raw, (spacer, spacer), white, font_small)

        # Draw P1 pace data
        drawTextWithBorder(draw, p1_data, (spacer, h + spacer * 2), white, font_small)

        p2_raw: str = " ".join([str(v).upper() for v in player2.raw_data])
        w, h = draw.textsize(p2_raw, font_small)
        drawTextWithBorder(
            draw, p2_raw, (base_width - w - spacer, spacer), white, font_small
        )

        # Draw P2 pace data
        w, h = draw.textsize(p2_data, font_small)
        drawTextWithBorder(
            draw, p2_data, (base_width - w - spacer, h + spacer * 2), white, font_small
        )

    # =========================
    # 1. render score stats

    # Draw Player 2 first (easier because left aligned)
    x, cur_y = player2.score_stats_xy

    if conf["print_score_difference"]:
        drawTextWithBorder(
            draw, p2["score"]["score"], (x, cur_y), p2["score"]["color"], font_big
        )

        w, h = draw.textsize(p2["score"]["score"], font_big)
        cur_y += h + v_spacing

    drawTextWithBorder(
        draw, p2["score"]["tetrises"], (x, cur_y), p2["score"]["color"], font
    )

    w, h = draw.textsize(p2["score"]["tetrises"], font)

    drawTextWithBorder(draw, "Tetrises", (x + w + h_spacing, cur_y), white, font)

    # then player 1 score

    x, cur_y = player1.score_stats_xy
    cur_x = x

    if conf["print_score_difference"]:
        w, h = draw.textsize(p1["score"]["score"], font_big)
        cur_x -= w
        drawTextWithBorder(
            draw, p1["score"]["score"], (cur_x, cur_y), p1["score"]["color"], font_big
        )
        cur_y += h + v_spacing

    w, h = draw.textsize("Tetrises", font)
    cur_x = x - w

    drawTextWithBorder(draw, "Tetrises", (cur_x, cur_y), white, font)

    w, h = draw.textsize(p1["score"]["tetrises"], font)
    cur_x -= w + h_spacing

    drawTextWithBorder(
        draw, p1["score"]["tetrises"], (cur_x, cur_y), p1["score"]["color"], font
    )

    # =========================
    # 2. render pace stats

    # Player 2 first again

    x, cur_y = player2.pace_stats_xy
    cur_x = x

    if conf["print_score_potential"]:
        drawTextWithBorder(
            draw,
            "Pace Potential: %d" % (player2.pace_score,),
            (cur_x, cur_y),
            white,
            font_small,
        )
        w, h = draw.textsize("0", font_small)
        cur_y += h + v_spacing

    drawTextWithBorder(
        draw, p2["pace"]["score"], (cur_x, cur_y), p2["pace"]["color"], font
    )

    w, h = draw.textsize(p2["pace"]["score"], font)

    drawTextWithBorder(draw, "Pace", (x + w + h_spacing, cur_y), white, font)

    cur_y += h + v_spacing

    drawTextWithBorder(
        draw, p2["pace"]["tetrises"], (x, cur_y), p2["pace"]["color"], font
    )

    w, h = draw.textsize(p2["pace"]["tetrises"], font)

    drawTextWithBorder(draw, "Tetrises", (x + w + h_spacing, cur_y), white, font)

    # and finally player 1 pace

    x, cur_y = player1.pace_stats_xy

    if conf["print_score_potential"]:
        potential_txt = "Pace Potential: %d" % (player1.pace_score,)
        w, h = draw.textsize(potential_txt, font_small)
        cur_x = x - w
        drawTextWithBorder(draw, potential_txt, (cur_x, cur_y), white, font_small)
        cur_y += h + v_spacing

    w, h = draw.textsize("Pace", font)
    cur_x = x - w

    drawTextWithBorder(draw, "Pace", (cur_x, cur_y), white, font)

    w, h = draw.textsize(p1["pace"]["score"], font)
    cur_x -= w + h_spacing

    drawTextWithBorder(
        draw, p1["pace"]["score"], (cur_x, cur_y), p1["pace"]["color"], font
    )

    cur_y += h + v_spacing

    w, h = draw.textsize("Tetrises", font)
    cur_x = x - w

    drawTextWithBorder(draw, "Tetrises", (cur_x, cur_y), white, font)

    w, h = draw.textsize(p1["pace"]["tetrises"], font)
    cur_x -= w + h_spacing

    drawTextWithBorder(
        draw, p1["pace"]["tetrises"], (cur_x, cur_y), p1["pace"]["color"], font
    )

    # =========================
    # 3. Render the trt box

    if conf["show_trt"]:
        # Player 1 TRT Box
        trt_box = trt_box_img.copy()
        draw = ImageDraw.Draw(trt_box)
        draw.text(
            trt_box_value_xy, player1.getTRTLabel(), (255, 255, 255), font=font_trt
        )
        frame.paste(trt_box, player1.trt_stats_xy, trt_box)

        # Player 2 TRT Box
        trt_box = trt_box_img.copy()
        draw = ImageDraw.Draw(trt_box)
        draw.text(
            trt_box_value_xy, player2.getTRTLabel(), (255, 255, 255), font=font_trt
        )
        frame.paste(trt_box, player2.trt_stats_xy, trt_box)


def drawAreas(frame):
    draw = ImageDraw.Draw(frame, "RGBA")
    orange = (0xFF, 0x6C, 0x00, 100)
    for id in [
        "p1_lines_xywh",
        "p1_score_xywh",
        "p2_lines_xywh",
        "p2_score_xywh",
    ]:
        x, y, w, h = conf[id]
        draw.rectangle(
            [(x, y), (x + w, y + h)],
            fill=orange,
        )


frame_idx = -1
last_stats_frame = None

while True:
    cv2_retval, cv2_image = cap.read()

    if not cv2_retval:
        break

    frame_idx += 1

    if args.snap and frame_idx < args.snap:
        continue

    cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    frame = Image.fromarray(cv2_image)

    p1_changed = player1.setFrame(frame)
    p2_changed = player2.setFrame(frame)

    changed = p1_changed or p2_changed or args.snap

    if (last_stats_frame is None) or changed:
        print("\n")
        print("Change detected:")
        p1_stat: str = player1.getStatsData()
        p2_stat: str = player2.getStatsData()
        print(p1_stat)
        print(p2_stat)

        last_stats_frame = Image.new("RGBA", (base_width, base_height), composite_color)
        drawStats(last_stats_frame)

    frame.paste(last_stats_frame, (0, 0), last_stats_frame)

    if args.snap:
        drawAreas(frame)
        frame.show()
        sys.exit(0)

    frame = cv2.cvtColor(numpy.array(frame), cv2.COLOR_RGB2BGR)
    out.write(frame)

    print(
        "Processed frame %d of %d (at %5.1f fps)"
        % (frame_idx + 1, total_frames, (frame_idx + 1) / (time.time() - start_time)),
        end="\r",
    )


out.release()

print(
    "\nDone - processed %d frames in %d seconds"
    % (total_frames, int(time.time() - start_time))
)
