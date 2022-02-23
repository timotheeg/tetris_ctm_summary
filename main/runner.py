import videoProcessor.statsExtractor as se


def invoke_exit() -> None:
    print("Bye! Have a great day! 😀")
    exit()


def unimplemented() -> None:
    print("Sorry, not yet implemented! 😅 Check back soon! 👋")


def runMainLoop() -> None:
    """
    Present an options menu to solicit the user's input
    """
    # fmt: off
    options = {
        0: invoke_exit,
        1: unimplemented,
        2: unimplemented,
        3: unimplemented,
        4: se.extractStats
    }
    # fmt: on
    while True:
        prompt: str = """
_____________________________________________

  🚀 Welcome to Yobi's CTM Summary Tool! 🚀
_____________________________________________

1) Generate 'stats-injected' video
2) Generate '*.verify.mp4' video
3) Generate 'verify-snap' frame
4) Extract stats metadata from video (-> *.srt)

0) Exit

$> """
        choice: int = input(prompt)
        print()
        options[int(choice)]()


if __name__ == "__main__":
    runMainLoop()
