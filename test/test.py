#!/usr/bin/env python

import urllib2
from threading import Thread

URL = 'http://localhost:8001'

class SiteRequest:
    def __init__(self, x=10, suffixName='', tables=[]):
        self.__x = x
        self.__tables = tables
        self.__suffixName = suffixName

    def hit(self, hitCount):
        for i in range(hitCount):
            for table in self.__tables:
                pt = urllib2.urlopen(URL + '/' + self.__suffixName + '/' + table)
                print(pt.read())

theBearArgs = (1, 'thebear', ['songHandler', 'entryHandler', 'playTimeHandler'])
gcsArgs = (1, 'gcs', ['imageHandler', 'markerHandler'])

argList = [theBearArgs, gcsArgs]

def main():
    for i in argList:
        th = Thread(target=lambda *args : SiteRequest(*args).hit(40000), args=i)
        th.start()

if __name__ == '__main__':
    main()
