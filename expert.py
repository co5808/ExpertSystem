#!/usr/bin/python

# from __future__ import print_function

import sys
import argparse
from printFunctions import printUsage, exitWithError
from readFile import GetFilepaths
from node import *

class ExpertSys:

	def __init__(self, filepath, options):
		self.path = filepath
		self.nodes = {};
		self.facts = None
		self.goals = None
		self.options = options

		try:
			with open(filepath) as f:
				tmp = f.readlines()
				for line in tmp:
					line = line.strip();
					if '#' in line:
						line = line.split('#')[0].strip();
					if line != '\n' and line != '':
						# TODO: check errors
						if line[0] == '=':
							self.facts = line.split("=")[1].split(" ")[0]
						elif line[0] == '?':
							self.goals = line.split("?")[1].split(" ")[0]
						else:
							# need to check errors.
							if "=>" in line:
								rule = line.split("=>")[0].strip()
								name = line.split("=>")[1].strip()
								if name in self.nodes:
									self.nodes[name].AddRule(rule);
								else:
									self.nodes[name] = Node(name, rule);

				for cle,node in self.nodes.items():
					node.PrintRules();
				print self.facts;
		except (OSError, IOError) as e:
			exitWithError('Trying to open file with path "' + filepath + '", got error: ' + e.strerror)
		return


	def BackwordChaining(self, query):
		if query in self.facts:
			# print query + " is known fact",
			return True
		elif query in self.nodes:
			isTrue = False;
			for rule in self.nodes[query].rules:
				print rule,

				rule = rule.replace(" ", "")

				leftSide = rule[0]
				rightSide = rule[2]
				vals = []
				ops = []
				operator = rule[1]
				ops.append(operator)
				otherSide = rule[3:]

				left = self.BackwordChaining(leftSide)
				vals.append(left)
				if left:
					self.facts = self.facts + leftSide

				while True:

					right = self.BackwordChaining(rightSide)
					vals.append(right)
					if right:
						self.facts = self.facts + rightSide

					if operator == "+":
						leftSide = left and right
					if operator == "|":
						leftSide = left or right
					if operator == "^":
						leftSide = (not left and right) or (not right and left);

					if otherSide != "":
						rightSide = otherSide[1]
						operator = otherSide[0]
						ops.append(operator)
						otherSide = otherSide[2:]
					else:
						break

				i = 1
				j = 0
				ret = vals[0]
				print "(",vals[0],
				while i < len(vals):
					print ops[j],vals[i],

					if ops[j] == "+":
						ret = ret and vals[i]
					if ops[j] == "|":
						ret = ret or vals[i]
					if ops[j] == "^":
						ret = (not ret and vals[i]) or (not vals[i] and ret);
					i += 1
					j += 1
				print ")",

				return ret
		else:
			# print query + " is impossible to get",
			return False

		return isTrue

	def Eval(self):
		for i, query in enumerate(self.goals):
			if i != 0:
				print ""

			print query + " =>",
			if self.BackwordChaining(query):
				print "\n" + query + ": True"
			else:
				print "\n" + query + ": False"
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
	for path in GetFilepaths():
		newExpert = ExpertSys(path, options)

		experts.append(newExpert)
	if len(experts) == 0:
		exitWithError("No filepath given", True)
	else:
		for i, expert in enumerate(experts):
			if i != 0:
				print ""

			print "- " + expert.path
			expert.Eval()

main(sys.argv)
