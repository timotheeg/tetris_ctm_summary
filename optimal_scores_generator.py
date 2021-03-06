# Script by fractal161
# https://discord.com/channels/374368504465457153/788646151716339744/810970077015965757

lineClears = [40, 100, 300, 1200]

def clearScore(clear, lines):
    if clear + lines < 130:
        return 19 * lineClears[clear - 1]
    else:
        return int((clear + lines + 70) / 10) * lineClears[clear - 1]

bestClears = ["" for i in range(234)]
maxScore = [0 for i in range(230)]

scoring_potential = {}

for i in range(229, -1, -1):
    # Figure out best score
    bestScore = 0
    bestClear = 1
    for j in range(1, 5):
        newScore = clearScore(j, i)
        if i + j < 230:
            newScore += maxScore[i + j]
        if newScore > bestScore:
            bestScore = newScore;
            bestClear = j
    maxScore[i] = bestScore
    bestClears[i] = str(bestClear) + bestClears[i + bestClear]

    scoring_potential[i] = {
        'score': maxScore[i],
        'clears': bestClears[i],
    }
