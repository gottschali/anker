#!/usr/bin/env python3

import csv
import sys

def Fetcher():
    return csv.reader(sys.stdin, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
