#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from ClGui import ClGui
from ClStock import ClStock
import warnings
#warnings.filterwarnings('ignore')


if __name__ == '__main__':
    uGui = ClGui("603111")
    uGui.MainLoop()
