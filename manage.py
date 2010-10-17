#!/usr/bin/python
import getopt, sys

try:
    opts, args = getopt.getopt(sys.argv[1:], None, ['settings='])
except getopt.GetoptError, err:
    raise

a_ = ""
s = ""
for a in args:
    if a_ == "--settings":
        s = a
    a_ = a

from django.core.management import execute_manager
try:
    obj = __import__(s, None, None) 
except:
    raise

if __name__ == "__main__":
    execute_manager(obj)
