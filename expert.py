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
									exitWithError("Not valid char in facts:" + c)
							factsSet = True
							self.facts = "1" + self.facts
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
							# need to check errors.
							if "=>" in line:
								rule = line.split("=>")[0].strip()
								rule = "(" + rule + ")"
								rightSide = line.split("=>")[1].strip()

								# error check
								isRule = False
								if not self.HasGoodSyntax(rightSide, isRule):
									exitWithError('Error with right side of expression: "' + line + '"')
								isRule = True
								if not self.HasGoodSyntax(rule, isRule):
									exitWithError('Error with left side of expression: "' + line + '"')

								# add nodes
								namesPos, namesNeg = self.GetNames(rightSide)
								for name in namesPos:
									if name in self.nodes:
										self.nodes[name].AddRule(rule);
									else:
										self.nodes[name] = Node(name, rule);
								rule = "!" + rule
								for name in namesNeg:
									if name in self.nodes:
										self.nodes[name].AddRule(rule);
									else:
										self.nodes[name] = Node(name, rule);
							else:
								exitWithError('Implication symbol is not found: "' + line + '"')

				for cle,node in self.nodes.items():
					node.PrintRules();
				print "Facts:",self.facts;
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
				if parenthesisCount <= 0:
					return False
				if not self.IsQueryChar(prevC) and not prevC == ')':
					return False
				parenthesisCount -= 1
			elif c == "!":
				if self.IsQueryChar(prevC):
					return False
			elif c == "+":
				if not self.IsQueryChar(prevC) and not prevC == ")":
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
		rightSide = rightSide.replace(" ", "")
		namesPos = []
		namesNeg = []
		negParenthesis = []
		parenthesisCount = 0
		previous = None;
		for c in rightSide:
			if c == "(":
				parenthesisCount += 1
				if previous == "!":
					negParenthesis.append(parenthesisCount)
			elif c == ")":
				if parenthesisCount in negParenthesis:
					negParenthesis.remove(parenthesisCount)
				parenthesisCount -= 1
			elif c.isalpha():
				negCount = len(negParenthesis)
				if previous == '!':
					negCount += 1
				if negCount % 2 == 0:
					namesPos.append(c)
				else:
					namesNeg.append(c)
			previous = c;


		return namesPos, namesNeg


	def BackwordChaining(self, query, stringIndent):

		print stringIndent + "Quering " + query
		stringIndent += '\t';
		if query in self.facts:
			print stringIndent + query + " is known fact"
			return True
		elif query in self.nodes:
			for rule in self.nodes[query].rules:
				print stringIndent + "Rule for " + query + ": " + rule
				rule = rule.replace(" ", "")
				while "(" in rule:
					print stringIndent + "\tBecomes: " + rule
					closePar = rule.find(")")
					openPar = rule.rfind("(", 0, closePar)
					# print openPar, closePar;
					extract = rule[openPar + 1 : closePar]
					# print "Extract:",extract

					resultEval = self.EvalExtract(extract, stringIndent + "\t\t")

					# combine left + result + right
					tmpRule = rule[0:openPar]
					if resultEval:
						tmpRule = tmpRule + "1"
					else:
						tmpRule = tmpRule + "0"
					rule = tmpRule + rule[closePar + 1:]
				print stringIndent + "Rule for " + query + " evaluated to: " + rule
				if rule == "1":
					if query not in self.facts:
						self.facts += query
					return True
			return False
		else:
			print stringIndent + query + " is impossible to get"
			return False

	def EvalExtract(self, extract, stringIndent):
		# TODO: extract can also be just a single value
		# TODO: extract can contain exclamation mark
		leftSide = extract[0]
		vals = []
		ops = []
		otherSide = extract[1:]

		left = self.BackwordChaining(leftSide, stringIndent)
		vals.append(left)

		while True:
			if otherSide != "":
				operator = otherSide[0]
				ops.append(operator)
				rightSide = otherSide[1]
				otherSide = otherSide[2:]
			else:
				break
			right = self.BackwordChaining(rightSide, stringIndent)
			vals.append(right)

			if operator == "+":
				leftSide = left and right
			if operator == "|":
				leftSide = left or right
			if operator == "^":
				leftSide = (not left and right) or (not right and left);


		i = 1
		j = 0
		ret = vals[0]
		print stringIndent + "(",vals[0],
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
		print ")"

		return ret

	def Eval(self):
		for i, query in enumerate(self.goals):
			if i != 0:
				print ""

			if self.BackwordChaining(query, ''):
				print "\n" + query + ": True"
			else:
				print "\n" + query + ": False"
			# print self.facts;
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
