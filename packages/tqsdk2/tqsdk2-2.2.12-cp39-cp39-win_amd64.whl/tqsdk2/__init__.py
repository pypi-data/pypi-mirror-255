#!/usr/bin/env python
#  -*- coding: utf-8 -*-
name = "tqsdk2"

import os

this_dir = os.path.abspath(os.path.dirname(__file__))

os.environ['PATH'] += ';' + this_dir
os.environ['TQSDK2_RUN_PATH'] = this_dir
os.environ['TQSDK2_WEB_PATH'] = os.path.join(this_dir, 'web')

from tqsdk2.tqsdk2 import TqApi
from tqsdk2.tqsdk2 import TqAuth
from tqsdk2.tqsdk2 import TqAccount, TqCtp, TqSim, TqKq, TqRohon, TqJees, TqYida, TqCtpMini, TqKqStock
from tqsdk2.tqsdk2 import TargetPosTask, TqBacktest, BacktestFinished
from tqsdk2.tqsdk2 import TqMarketMaker

from tqsdk2.tqsdk2 import TradingStatus, Account, Order, Position, Quote, Trade

from tqsdk2.tqsdk2 import __version__