from gen import sayHello, Test

aaa: int = Test.sayTest()


def invoke_exit() -> None:
    print("Bye! Have a great day! 😀" + str(aaa))
    exit()


options = {0: invoke_exit, 1: sayHello}

# Present an options menu to solicit the user's input
while True:
    prompt: str = """
_____________________________________________

 --- Welcome to Yobi's CTM Summary Tool! ---
_____________________________________________

1) Generate 'stats-injected' video
2) Generate '*.verify.mp4' video
3) Generate 'verify-snap' frame
4) Generate all stats meta data as '*.txt' file

0) Exit

$> """

    choice: int = input(prompt)
    print()
    options[int(choice)]()

    prompt: str = """
Do you wish to continue?
"""
    choice = input(prompt)
