import argparse

parser = argparse.ArgumentParser()
parser.add_argument('sourcefile',nargs='*', help='File to parse')
parser.add_argument('-p', '--print_steps', action='store_true', help="Print all the resolver steps")
args = parser.parse_args()
def GetFilepaths():
    return args.sourcefile
def GetOptions():
	if args.print_steps:
		return True
	return False
