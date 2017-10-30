import argparse

parser = argparse.ArgumentParser()
parser.add_argument('sourcefile',nargs='*', help='File to parse')
args = parser.parse_args()

def GetFilepaths():
    return args.sourcefile
