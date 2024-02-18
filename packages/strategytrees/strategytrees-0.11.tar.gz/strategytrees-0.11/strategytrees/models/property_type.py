from enum import Enum

class PropertyType(Enum):
    TrainingFitness = 1
    TrainingSuccess = 2
    TrainingTrades = 3
    TrainingPips = 4
    TestingFitness = 5
    TestingSuccess = 6
    TestingTrades = 7
    TestingPips = 8 
    BestExitType = 9
    BestTP = 10 
    BestSL = 11
    Size = 12