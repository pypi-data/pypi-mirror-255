# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : demo
# @Time         : 2023/12/21 17:22
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from urllib.parse import quote, unquote


_ = quote("sk-PB2D9FR6tBNml59tAc72E49982Aa476a9d792b01152a96D7777||1")

print(_)

print(unquote(_))
