# Script inspired and modified from script by fractal161
# https://discord.com/channels/374368504465457153/788646151716339744/810970077015965757

SCORE_BASES = [0, 40, 100, 300, 1200]

TRANSITIONS = {
    "0": 10,
    "1": 20,
    "2": 30,
    "3": 40,
    "4": 50,
    "5": 60,
    "6": 70,
    "7": 80,
    "8": 90,
    "9": 100,
    "10": 100,
    "11": 100,
    "12": 100,
    "13": 100,
    "14": 100,
    "15": 100,
    "16": 110,
    "17": 120,
    "18": 130,
    "19": 130,
}


def getPotentialScore(start_level, lines):
    return SCORING_POTENTIAL.get(start_level, {}).get(lines, 0)


def getClearValue(level, clear):
    return SCORE_BASES[clear] * (level + 1)


def getTetrisValue(level):
    return getClearValue(level, 4)


def getTransitionLines(start_level):
    return TRANSITIONS[str(start_level)]


def getLevel(start_level, lines):
    transition_lines = getTransitionLines(start_level)

    if lines < transition_lines:
        level = start_level
    else:
        level = start_level + 1 + int((lines - transition_lines) / 10)

    return level


def getPacePotentialForLevel(start_level, transition_lines, kill_screen_lines):
    def clearScore(current_lines, clear):
        target_lines = current_lines + clear

        level = getLevel(start_level, target_lines)

        return getClearValue(level, clear)

    potential = {}
    potential[kill_screen_lines + 0] = 0
    potential[kill_screen_lines + 1] = 0
    potential[kill_screen_lines + 2] = 0
    potential[kill_screen_lines + 3] = 0

    lines = kill_screen_lines

    while lines:
        lines -= 1

        best_score = 0

        for clear in (1, 2, 3, 4):
            new_score = clearScore(lines, clear) + potential[clear + lines]

            if new_score > best_score:
                best_score = new_score

        potential[lines] = best_score

    return potential


SCORING_POTENTIAL = {}


for start_level, transition_lines in TRANSITIONS.items():
    start_level = int(start_level)

    kill_screen_lines = 290 - (((start_level + 1) * 10) - transition_lines)

    SCORING_POTENTIAL[start_level] = getPacePotentialForLevel(
        start_level, transition_lines, kill_screen_lines
    )
