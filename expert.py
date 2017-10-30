#!/usr/bin/python

import sys
from printFunctions import printUsage, exitWithError

class ExpertSys:

	def __init__(self, filepath, options):
		self.path = filepath
		self.rules = None
		self.facts = None
		self.goals = None
		self.options = options

		try:
			with open(filepath) as f:
				# TODO: parse file
				self.rules = f.readlines()
				self.facts = "ABG"
				self.goals = "GVX"
		except (OSError, IOError) as e:
			exitWithError('Trying to open file with path "' + filepath + '", got error: ' + e.strerror)
		return


	def Eval(self):
		for query in self.goals:
			if query in self.facts:
				print query + ": True"
				continue
			print query + ": False"
		return


def main(argv):
	options = []
	paths = []
	experts = []

	argc = len(argv)
	argc -= 1
	while argc > 0:
		if argv[argc][0] == '-':
			# TODO: check if valid option
			options.append(argv[argc])
		else:
			paths.insert(0, argv[argc])
		argc -= 1
	for path in paths:
		newExpert = ExpertSys(path, options)

		experts.append(newExpert)
	if len(experts) == 0:
		exitWithError("No filepath given", True)
	else:
		first = True
		for expert in experts:
			if first:
				first = False
			else:
				print ""

			print "- " + expert.path
			expert.Eval()


main(sys.argv)
