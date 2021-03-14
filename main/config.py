import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """
    Default values - Set these to be automatically used if
    no 'config.json' is detected? 🤔🤔🤔

    These settings will automatically work out of the box against
    the `Koryan vs Scotto CTM Feb 2021` 1min:53sec 1080p test video sample:
    https://drive.google.com/file/d/1MlSVk3E9k-WU97qd49e8xfcjKoiqACqY
    """

    print_score_difference: bool = True
    print_score_potential: bool = True
    text_has_border: bool = True
    show_trt: bool = True

    p1_lines_xywh: tuple = (818, 58, 101, 31)
    p1_score_xywh: tuple = (572, 59, 206, 32)
    p1_level_xywh: tuple = (577, 168, 57, 28)

    p2_lines_xywh: tuple = (1260, 58, 100, 32)
    p2_score_xywh: tuple = (1016, 61, 205, 32)
    p2_level_xywh: tuple = (1022, 171, 56, 27)

    p1_score_stats_xy: tuple = (525, 120)
    p1_pace_stats_xy: tuple = (525, 350)
    p1_trt_stats_xy: tuple = (406, 0)

    p2_score_stats_xy: tuple = (1405, 120)
    p2_pace_stats_xy: tuple = (1405, 350)
    p2_trt_stats_xy: tuple = (1392, 0)


def setup() -> Config:
    try:
        print(">> Trying reading from 'config.json'...\n")
        # config must be present and valid, will throw if not
        with open("config.json") as f:
            configDict: dict = json.load(f)
            config_from_file: Config = Config(**configDict)
            print(">> SUCCESSFULLY read config_from_file!\n")
            # print(config_from_file)
            return config_from_file

            # # TODO: Make a Proper config class to handle the config file properly
            # # i.e. handle default, missing entries, unexpected values, etc.
            # if "show_trt" not in conf:
            #     conf["show_trt"] = False

    except FileNotFoundError as err:
        print("ERROR 01!! No config found! Defaulting to hardcoded config values.", err)
        return Config()

    except TypeError as err:
        print("ERROR 02!! Your config is malformed:", err)
        print("We will default to hardcoded config values.")
        return Config()


if __name__ == "__main__":
    print("### Config Running in standlone mode!! ####")
    c: Config = setup()

    print("\n\n>> FINAL Config:", c)
