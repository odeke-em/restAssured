#!/usr/bin/python
#
# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Functions to handle validation of data
# Copyright (c) 2014

import re

intRegCompile = re.compile("^(-?\d+)$", re.UNICODE)
UIntRegCompile = re.compile("^(\d+)$", re.UNICODE)
floatRegCompile = re.compile("^(\d+)?.(\d+)$", re.UNICODE)

isInt = lambda i: isinstance(i, int) or (intRegCompile.match(str(i)) != None)

isUInt = lambda u: (isinstance(u, int) and u >= 0)  or (UIntRegCompile.match(str(u)) != None)

isUIntLike = isUInt
