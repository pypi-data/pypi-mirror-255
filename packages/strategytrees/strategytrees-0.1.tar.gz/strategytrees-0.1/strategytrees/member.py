from . import Node
from . import ExitType
import random

available_leverages = [30]
#available_leverages = [10, 20, 30, 50]

# JPY
available_tp = [0.05, 0.1, 0.2, 0.5, 1, 2, 3]
available_sl = [0.05, 0.1, 0.2, 0.5, 1, 2, 2.5]
# available_tp = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01]
# available_sl = [0.001, 0.005, 0.01, 0.02, 0.025]

class Member:
    tree:Node = None
    fitness:int = 0
    cumulated_fitness = 0
    success:int = 0
    trades:int = 0
    pips:int = 0

    exit_type:ExitType = ExitType.TP_SL
    tp = 0
    sl = 0
    leverage = 1

    def __init__(self, t:Node):
        self.fitness = 0
        self.cumulated_fitness = 0
        self.tree = t
        self.success = 0
        self.trades = 0
        self.pips = 0
        self.exit_type = random.choice(list(ExitType))
        #self.exit_type = random.choice([ExitType.TP_SL, ExitType.IN_PROFIT])
        self.tp = random.choice(available_tp)
        self.sl = random.choice(available_sl)
        self.leverage = random.choice(available_leverages)