
#!/usr/bin/python

import sys


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def printUsage():
	print bcolors.HEADER + 'USAGE:' + bcolors.ENDC + '\n $> python expert.py [options] "filepath" ["another_filepath"]\n'
	print bcolors.HEADER + "OPTIONS:" + bcolors.ENDC + " (you need to include the '-')"
	print ' -h\tdisplay help and exit'
	print ' -p\tprints steps of the resolver'


def exitWithError(message, usage = None):
	print bcolors.FAIL + 'ERROR' + bcolors.ENDC + ' - ' + bcolors.WARNING  + message + bcolors.ENDC

	if usage:
		printUsage()

	sys.exit(2)
