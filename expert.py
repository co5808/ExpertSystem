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
			factsSet = False
			goalsSet = False
			with open(filepath) as f:
				tmp = f.readlines()
				for line in tmp:
					line = line.strip();
					if '#' in line:
						line = line.split('#')[0].strip();
					if line != '\n' and line != '':
						if line[0] == '=':
							if factsSet:
								exitWithError("You already defined facts one..!")
							self.facts = line.split("=")[1].replace(" ", "").strip()
							for c in self.facts:
								if not self.IsQueryChar(c):
									exitWithError("Not valid char in facts (" + c +")")
							factsSet = True
						elif line[0] == '?':
							if not factsSet:
								exitWithError("You must defines facts before goals..!")
							if goalsSet:
								exitWithError("You already defined goals one..!")
							self.goals = line.split("?")[1].replace(" ", "").strip()
							for c in self.goals:
								if not self.IsQueryChar(c):
									exitWithError("Not valid char in goals (" + c +")")
							goalsSet = True
						else:
							# TODO: need to check errors.
							if "=>" in line:
								rule = line.split("=>")[0].strip()
								rule = "(" + rule + ")"
								rightSide = line.split("=>")[1].strip()

								isRule = False
								if not self.HasGoodSyntax(rightSide, isRule):
									exitWithError('Error with right side of expression: "' + line + '"')
								isRule = True
								if not self.HasGoodSyntax(rule, isRule):
									exitWithError('Error with left side of expression: "' + line + '"')

								names = self.GetNames(rightSide)
								for name in names:
									tmpRule = rule
									if name[0] == "!":
										tmpRule = "!" + tmpRule
										name = name[1:]

									if name in self.nodes:
										self.nodes[name].AddRule(tmpRule);
									else:
										self.nodes[name] = Node(name, tmpRule);
							else:
								exitWithError('Wrong format for line: "' + line + '"')
				# finished parsing file
				if not factsSet or not goalsSet:
					exitWithError("You must give facts and goals")
				for cle,node in self.nodes.items():
					node.PrintRules();
				print self.facts;
		except (OSError, IOError) as e:
			exitWithError('Trying to open file with path "' + filepath + '", got error: ' + e.strerror)
		return

	def IsQueryChar(self, c):
		if c and c.isalpha() and c.isupper():
			return True
		return False

	def HasGoodSyntax(self, line, isRule):
		line = line.replace(" ", "")
		if line == '\n' and line == '':
			return False

		parenthesisCount = 0
		prevC = None
		for c in line:
			if c == "(":
				if self.IsQueryChar(prevC):
					return False
				parenthesisCount += 1
			elif c == ")":
				if parenthesisCount <= 0 or not self.IsQueryChar(prevC):
					return False
				parenthesisCount -= 1
			elif c == "!":
				if self.IsQueryChar(prevC):
					return False
			elif c == "+":
				if not self.IsQueryChar(prevC):
					return False
			elif isRule and c == "|":
				if not self.IsQueryChar(prevC):
					return False
			elif isRule and c == "^":
				if not self.IsQueryChar(prevC):
					return False
			elif self.IsQueryChar(c):
				if self.IsQueryChar(prevC):
					return False
			else:
				return False
			prevC = c

		if parenthesisCount > 0 or prevC == "!":
			return False
		return True

	def GetNames(self, rightSide):
		names = []
		names.append(rightSide)
		return names

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
			# if self.BackwordChaining(query):
			# 	print "\n" + query + ": True"
			# else:
				# print "\n" + query + ": False"
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
