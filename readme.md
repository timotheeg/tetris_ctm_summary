This Repo contains a script to help [aGameScout](https://www.twitch.tv/agamescout) prepare the CTM video with extra stats for his commentary

# Installation

(OSX instruction)

This was only tested in python 3.7.9, so on OSX use it with `brew`:

```bash
brew update
brew install python@3.7
brew link --overwrite python@3.7
pip3 install -r requirements.txt
```

# Usage

Preferrably have the video segments you want to annotate with stats ready. Do not mix multiple games by multiple players in the same video file, because it is likely the location of their game stats changes a bit.

Instead, cut your video into segment by game to comment on, and then identify the location of the data areas for player 1 and 2 in `(x, y, width, height)` tuples, and populate them the script.

Then run the script with
```
python3 generate.py FILEPATH_TO_VIDEO_FILE
```

# Sample output

![sample frame](./sample_frame.jpg)

## Aknowledgment

Reading the line count from the TreyVision footage is done using the file `digitocr.py` from the excellent [NESTrisOCR](https://github.com/alex-ong/NESTrisOCR) project by [Alex Ong](https://github.com/alex-ong).


## Related Project

This project is pretty much a clone of tetris_rate_adder that I made for a similar purpose for Chris Higgins's project [Best of Five](https://www.kickstarter.com/projects/chrishiggins/best-of-five-the-classic-tetris-champions).

Take a look at [NESTrisStatsUI](https://github.com/timotheeg/NESTrisStatsUI) for a project computing Tetris stats from a live tetris games.