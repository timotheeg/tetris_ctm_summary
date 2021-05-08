import os


def promptForVideo() -> str:
    """
    Scans ./videos directory for all *.mp4 files.  Prompts user for selection.
    """
    while True:
        files: list = os.listdir("./input")
        filenames: list = [
            f"{i}) {filename}"
            for i, filename in enumerate(files)
            if filename[-4:] == ".mp4"
        ]
        filenames: str = "\n".join(filenames)

        prompt: str = f"""Please select a file:
{filenames}

$> """
        choice: int = int(input(prompt))
        return files[choice]
