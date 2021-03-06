
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

def exitWithError(message):
	raise RuntimeError(bcolors.FAIL + 'ERROR' + bcolors.ENDC + ' - ' + bcolors.WARNING  + message + bcolors.ENDC)

def printFilename(filepath):
	print bcolors.HEADER + "### " + filepath + " ###############################" + bcolors.ENDC

def printResult(query, res):
	if res == True:
		print bcolors.OKGREEN + query + ": True" + bcolors.ENDC
	else:
		print bcolors.FAIL + query + ": False" + bcolors.ENDC

def printQuery(query):
	print bcolors.OKBLUE + query + bcolors.ENDC
