import sys
def loadProject():
    # appending root project dir to the module search list of the python 
    sys.path.append(__file__.split("\\tests")[0])
