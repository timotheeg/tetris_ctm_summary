import videoProcessor.statsExtractor as se


def invoke_exit() -> None:
    print("Bye! Have a great day! 😀")
    exit()


# fmt: off
options = {
    0: invoke_exit,
    4: se.extractStats
}
# fmt: on

# Present an options menu to solicit the user's input
while True:
    prompt: str = """
_____________________________________________

 --- Welcome to Yobi's CTM Summary Tool! ---
_____________________________________________

1) Generate 'stats-injected' video
2) Generate '*.verify.mp4' video
3) Generate 'verify-snap' frame
4) Extract stats metadata from video (-> *.txt)

0) Exit

$> """

    choice: int = input(prompt)
    print()
    options[int(choice)]()

    prompt: str = """
Do you wish to continue?
"""
    choice = input(prompt)
