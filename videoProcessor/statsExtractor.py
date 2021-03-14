from io import TextIOWrapper
import numpy
import cv2

import time
from PIL import Image
from player import Player
import main.config as config


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


def log(message: str, fileOutput: TextIOWrapper, file: bool, console: bool):
    if console:
        print(message)
    if file:
        fileOutput.write(f"{message}\n\n")


# https://stackoverflow.com/questions/5531249/how-to-convert-time-format-into-milliseconds-and-back-in-python
def conv_ms_to_timestamp(ms: int) -> str:
    hours, milliseconds = divmod(ms, 3600000)
    minutes, milliseconds = divmod(ms, 60000)
    seconds = float(milliseconds) / 1000
    return "%02i:%02i:%06.3f" % (hours, minutes, seconds)


def extractStats() -> None:
    print("Time to extract some stats!")
    c: config.Config = config.setup()
    # print(">> FINAL Config:", c)

    cap = cv2.VideoCapture(r"./videos/fullkoryanscotto1080p.mp4")
    total_frames: int = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    [player1, player2] = initializePlayers(c)

    frame_idx: int = -1
    start_time = time.time()

    with open("./videos/statsOutput.txt", "w") as outFile:
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

                cur_ts: str = conv_ms_to_timestamp(cap.get(cv2.CAP_PROP_POS_MSEC))
                if p1_changed:
                    p1_stat = str(p1_stat) + f" <- {cur_ts}"
                if p2_changed:
                    p2_stat = str(p2_stat) + f" <- {cur_ts}"

                log(
                    "Change detected:                                  ",  # To clear buffer issues.
                    outFile,
                    file=False,
                    console=True,
                )
                log(f"{cur_ts}\n{p1_stat}\n{p2_stat}", outFile, file=True, console=True)
                # print(f"Current timestamp in video: {cur_ts}")

            frame = cv2.cvtColor(numpy.array(frame), cv2.COLOR_RGB2BGR)
            status: str = "Processed frame %d of %d (at %5.1f fps)" % (
                frame_idx + 1,
                total_frames,
                (frame_idx + 1) / (time.time() - start_time),
            )
            print(status, end="\r")
            # print(status)
            # print("\033[A\033[A")

            if changed:
                # status: str = "Processed frame %d of %d (at %5.1f fps)" % (
                #     frame_idx + 1,
                #     total_frames,
                #     (frame_idx + 1) / (time.time() - start_time),
                # )
                log(f"{status}\n", outFile, file=False, console=True)

        log(
            "\nDone - processed %d frames in %d seconds"
            % (total_frames, int(time.time() - start_time)),
            outFile,
            file=True,
            console=True,
        )


if __name__ == "__main__":
    print("\n### Config StatsExtractor in standlone mode!! ####\n")
    extractStats()
