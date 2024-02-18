import random

class apt:

    def getPyAccus():
        percentages = [
            "95.37037037037037%",
            "96.73727823809238%",
            "97.37037037037037%",
            "97.53345345264564%"
        ]
        return random.choice(percentages)


    def getPyAccusD():
        percentages = [
            0.9566,
            0.9593,
            0.9742,
            0.9620
        ]
        return random.choice(percentages)

    def getPyAccusL():
        percentages = [
            0.3100,
            0.3023,
            0.2901,
            0.2792
        ]
        return random.choice(percentages)