import numpy
import cv2
import os

import time
from PIL import Image
from player import Player
import main.config as config
import main.cli as cli
import utils


def initializePlayers(c: config.Config) -> list:
    player1 = Player(
        c.p1_lines_xywh,
        c.p1_score_xywh,
        c.p1_level_xywh,
        c.p1_score_stats_xy,
        c.p1_pace_stats_xy,
        c.p1_trt_stats_xy,
    )
    player2 = Player(
        c.p2_lines_xywh,
        c.p2_score_xywh,
        c.p2_level_xywh,
        c.p2_score_stats_xy,
        c.p2_pace_stats_xy,
        c.p2_trt_stats_xy,
    )
    return [player1, player2]


def log(message: str, console: bool):
    if console:
        print(message)


def extractStats() -> None:

    filename: str = cli.promptForVideo()
    inputVideo: str = f"./input/{filename}"
    outputSubtitle: str = f"./output/{filename[:-4]}.srt"

    c: config.Config = config.setup()
    # print(">> Debug Config:", c)

    cap = cv2.VideoCapture(inputVideo)
    total_frames: int = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    [player1, player2] = initializePlayers(c)

    frame_idx: int = -1
    start_time = time.time()

    extractedStats: list = []
    try:
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

            if changed:
                p1_stat = player1.getStatsData()
                p2_stat = player2.getStatsData()

                cur_ts: str = utils.conv_ms_to_timestamp(cap.get(cv2.CAP_PROP_POS_MSEC))
                if p1_changed:
                    p1_stat = str(p1_stat) + f" <- {cur_ts}"
                if p2_changed:
                    p2_stat = str(p2_stat) + f" <- {cur_ts}"

                log(
                    "Change detected:                                  ",  # To clear buffer issues.
                    console=True,
                )
                log(f"{cur_ts}\n{p1_stat}\n{p2_stat}", console=True)
                extractedStats.append((cur_ts, p1_stat, p2_stat))

            frame = cv2.cvtColor(numpy.array(frame), cv2.COLOR_RGB2BGR)
            status: str = "Processed frame %d of %d (at %5.1f fps)" % (
                frame_idx + 1,
                total_frames,
                (frame_idx + 1) / (time.time() - start_time),
            )
            print(status, end="\r")

            if changed:
                log(f"{status}\n", console=True)

        log(
            "\nDone - processed %d frames in %d seconds"
            % (total_frames, int(time.time() - start_time)),
            console=True,
        )
    except KeyboardInterrupt:
        print("\n\n❌❌❌ Loop exited before reading entire video! ❌❌❌\n")
    except TypeError as err:  # Squelch and bypass the weird cv2 'TypeError: src data type = 17 is not supported' error on early exit.
        print(">> Type error occurred:", err)

    print(
        "Now dumping all extracted Tetris metadata stored in memory to .srt file:\n\t",
        outputSubtitle,
    )

    # Calculate total duration of video.
    # https://stackoverflow.com/questions/49048111/how-to-get-the-duration-of-video-using-cv2
    fps: int = cap.get(cv2.CAP_PROP_FPS)
    durationInSeconds: float = float(total_frames) / float(fps)
    endTimestamp: str = utils.conv_ms_to_timestamp(int(durationInSeconds * 1000))

    # Add final timestamp to final tuple to extractedStats to handle LAST subtitle.
    extractedStats.append((endTimestamp, None, None))

    # Create output directories if neccessary.
    os.makedirs(os.path.dirname(outputSubtitle), exist_ok=True)

    with open(outputSubtitle, "w") as outFile:
        for i in range(len(extractedStats) - 1):
            outFile.write(f"{i + 1}\n")  # This is the subtitle id-- starts from 1
            outFile.write(f"{extractedStats[i][0]} --> {extractedStats[i+1][0]}\n")
            outFile.write(f"{extractedStats[i][1]}\n")
            outFile.write(f"{extractedStats[i][2]}\n\n")


if __name__ == "__main__":
    print("\n### Running StatsExtractor in standlone mode!! ####\n")
    extractStats()
