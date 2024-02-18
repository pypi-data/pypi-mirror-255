import os
from . import Member, ExitType
import pandas as pd


class Fitness:
    _low_def_tf = '',
    _high_def_tf = '',
    _order_price = 0
    _order_type = ''
    _total_pips = 0
    _total_trades = 0
    _tp:float = 0
    _sl:float = 0
    _initial_balance = 0
    _balance:float = 100
    _file_pointer = None
    _success = 0
    _t_positive = 0
    _member = None
    _log_line = ""
    _log_file_path = ''

    def __init__(self,
                 low_def_timeframe:str='D',
                 high_def_timeframe:str='H1',
                 initial_balance:int=100,
                 pip:float=0.0001,
                 log_to_file:bool=False,
                 log_file_path='trade_log.txt'):
        self._low_def_tf = low_def_timeframe
        self._high_def_tf = high_def_timeframe
        self._initial_balance = initial_balance
        self._pip = pip
        self._log_to_file = log_to_file
        self._log_file_path = log_file_path

        if self._log_to_file:
            if os.path.isfile(self._log_file_path):
                os.remove(self._log_file_path)

    def get_fitness(self, member:Member, dataset:pd.DataFrame):
        self._order_price = 0
        self._order_type = ''
        self._total_pips = 0
        self._total_trades = 0
        self._tp = 0
        self._sl = 0
        self._file_pointer = None
        self._t_positive = 0
        self._balance = self._initial_balance
        self._member = member

        dataset.apply(self._callback, axis=1)
        self._success = 0

        if self._total_trades > 0:
            self._success = self._t_positive / self._total_trades

        return self._balance

    def _log(self, message:str):
        #print(message)
        if not self._log_to_file:
            return

        with open(self._log_file_path, 'a') as f:
            f.write(message + '\n')

    def pips_earned(self, diff_open_close:float):
        """
        Convert the profit/loss PIPs to an integer using the pip value for this instrument

        :param diff_open_close:
        :return:
        """
        return diff_open_close / self._pip

    def profit_loss(self, pips_total:float, close_price:float, units:int)->float:
        """
        Calculate the total profit or loss in base currency. Based on the number of pips earned

        :param pips_total:
        :param close_price:
        :param units:
        :return:
        """
        return (pips_total / close_price) * units

    def _callback(self, r):
        """
        Updates to the fitness method on 24/04/23

        An order can not end during the immediately closed candle and a new created immediately afterward
        Removed filters on ATR

        :param r:
        :return:
        """
        if self._balance <= 0:
            return self._total_pips

        if self._order_type == 'LONG':
            if self._member.exit_type == ExitType.TP_SL:
                """
                1. Testing for TP and SL
                """
                if r['TF'] == self._high_def_tf:
                    # test for TP and SL
                    if r['high_bid'] > self._tp or r['low_bid'] > self._tp:
                        pl = self._tp - self._order_price
                        pips_pl = self.pips_earned(pl)
                        self._total_pips += pips_pl
                        self._order_type = ''
                        self._t_positive += 1
                        self._balance += self.profit_loss(pl, self._tp, int(self._balance * self._member.leverage))
                        self._log_line += f"close {r['TS']} Price {self._tp} TP {pips_pl} Balance {self._balance}"
                        self._log(self._log_line)

            if self._member.exit_type == ExitType.IN_PROFIT:
                """
                2. Testing for In profit exit type
                """
                if r['TF'] == self._high_def_tf:
                    if r['close_bid'] - self._order_price > 0.0:
                        pl = r['close_bid'] - self._order_price
                        pips_pl = self.pips_earned(pl)
                        self._total_pips += pips_pl
                        self._order_type = ''
                        self._t_positive += 1
                        self._balance += self.profit_loss(pl, r['close_bid'], int(self._balance * self._member.leverage))
                        self._log_line += f"close {r['TS']} Price {r['close_bid']} TP {pips_pl} Balance {self._balance}"
                        self._log(self._log_line)

            if self._member.exit_type == ExitType.SIGNAL:
                """
                3. Testing for opposing signal type
                """
                if r['TF'] == self._low_def_tf:
                    signal = self._member.tree.resolve(r)
                    if signal == 'SELL':
                        pl = r['close_bid'] - self._order_price
                        pips_pl = self.pips_earned(pl)
                        self._total_pips += pips_pl
                        self._order_type = ''
                        self._t_positive += 1
                        self._balance += self.profit_loss(pl, r['close_bid'], int(self._balance * self._member.leverage))
                        self._log_line += f"close {r['TS']} Price {r['close_bid']} Close {pips_pl} Balance {self._balance}"
                        self._log(self._log_line)

            if r['TF'] == self._high_def_tf:
                """
                4. Always test for SL
                """
                if r['high_bid'] < self._sl or r['low_bid'] < self._sl:
                    pl = self._sl - self._order_price
                    pips_pl = self.pips_earned(pl)
                    self._total_pips += pips_pl
                    self._order_type = ''
                    self._balance += self.profit_loss(pl, self._sl, int(self._balance * self._member.leverage))
                    self._log_line += f"close {r['TS']} Price {self._sl} SL {pips_pl} Balance {self._balance}"
                    self._log(self._log_line)

            return self._total_pips

        if self._order_type == 'SHRT':
            if self._member.exit_type == ExitType.TP_SL:
                """
                1. Testing for TP and SL
                """
                if r['TF'] == self._high_def_tf:
                    if r['high'] < self._tp or r['low'] < self._tp:
                        pl = self._order_price - self._tp
                        pips_pl = self.pips_earned(pl)
                        self._total_pips += pips_pl
                        self._order_type = ''
                        self._t_positive += 1
                        self._balance += self.profit_loss(pl, self._tp, int(self._balance * self._member.leverage))
                        self._log_line += f"close {r['TS']} Price {self._tp} TP {pips_pl} Balance {self._balance}"
                        self._log(self._log_line)

            elif self._member.exit_type == ExitType.IN_PROFIT:
                """
                2. Testing for In profit exit type
                """
                if r['TF'] == self._high_def_tf:
                    if self._order_price - r['close_ask'] > 0.0:
                        pl = self._order_price - r['close_ask']
                        pips_pl = self.pips_earned(pl)
                        self._total_pips += pips_pl
                        self._order_type = ''
                        self._t_positive += 1
                        self._balance += self.profit_loss(pl, r['close_ask'], int(self._balance * self._member.leverage))
                        self._log_line += f"close {r['TS']} Price {r['close_ask']} TP {pips_pl} Balance {self._balance}"
                        self._log(self._log_line)

            elif self._member.exit_type == ExitType.SIGNAL:
                """
                3. Testing for opposing signal type
                """
                if r['TF'] == self._low_def_tf:
                    signal = self._member.tree.resolve(r)
                    if signal == 'SELL':
                        pl = self._order_price - r['close_ask']
                        pips_pl = self.pips_earned(pl)
                        self._total_pips += pips_pl
                        self._order_type = ''
                        self._t_positive += 1
                        self._balance += self.profit_loss(pl, r['close_ask'], int(self._balance * self._member.leverage))
                        self._log_line += f"close {r['TS']} Price {r['close_ask']} Close {pips_pl} Balance {self._balance}"
                        self._log(self._log_line)

            if r['TF'] == self._high_def_tf:
                """
                4. Always test for SL
                """
                if r['high'] > self._sl or r['low'] > self._sl:
                    pl = self._order_price - self._sl
                    pips_pl = self.pips_earned(pl)
                    self._total_pips += pips_pl
                    self._order_type = ''
                    self._balance += self.profit_loss(pl, self._sl, int(self._balance * self._member.leverage))
                    self._log_line += f"close {r['TS']} Price {self._sl} SL {pips_pl} Balance {self._balance}"
                    self._log(self._log_line)
            return self._total_pips

        if self._order_type != '' or r['TF'] != self._low_def_tf:
            return self._total_pips

        signal = self._member.tree.resolve(r)
        # if r['TS'] > datetime(2024, 1, 17):
        #      print(f"{r['TS']} {signal}")

        if signal == 'BUY':
            self._order_price = r['close_ask']
            self._order_type = 'LONG'
            if self._member.exit_type == ExitType.TP_SL:
                self._tp = self._order_price + self._member.tp
            self._sl = self._order_price - self._member.sl
            self._log_line = f"Long {r['TS']} {self._order_price} TP {self._tp} SL {self._sl} "
            self._total_trades += 1
        elif signal == 'SELL':
            self._order_price = r['close_bid'] # ask price
            self._order_type = 'SHRT'
            if self._member.exit_type == ExitType.TP_SL:
                self._tp = self._order_price - self._member.tp
            self._sl = self._order_price + self._member.sl
            self._log_line = f"Short {r['TS']} {self._order_price} TP {self._tp} SL {self._sl} "
            self._total_trades += 1

        return self._total_pips
