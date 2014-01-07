#!/usr/bin/python
#
# Author: Emmanuel Odeke <odeke@ualberta.ca>
# Functions to handle validation of data
# Copyright (c) 2014

import re

intRegCompile = re.compile("^(\d+)$", re.UNICODE)
floatRegCompile = re.compile("^(\d+)?.(\d+)$", re.UNICODE)

isInt = lambda s: \
  isinstance(isInt, int) or (intRegCompile.match(str(s)) != None)
