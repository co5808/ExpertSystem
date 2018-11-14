#!/usr/bin/python

# from __future__ import print_function

import sys
import argparse
from printFunctions import exitWithError, printFilename, printResult, printQuery
from readFile import GetFilepaths, GetOptions
from node import *

class ExpertSys:

	def __init__(self, filepath, options):
		self.path = filepath
		self.nodes = {};
		self.facts = None
		self.negativeFacts = ""
		self.goals = None
		self.openQuery = [];
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
								rule = self.AddPriorities(rule)

								# add nodes
								namesPos, namesNeg = self.GetNames(rightSide)
								for name in namesPos:
									if name in self.nodes:
										self.nodes[name].AddRule(rule);
									else:
										self.nodes[name] = Node(name, rule);
								rule = "(!" + rule + ")"
								for name in namesNeg:
									if name in self.nodes:
										self.nodes[name].AddRule(rule);
									else:
										self.nodes[name] = Node(name, rule);
							else:
								exitWithError('Implication symbol is not found: "' + line + '"')

			#for cle,node in self.nodes.items():
			#	node.PrintRules();
			print self.nodes
			print "Facts:",self.facts;
		except (OSError, IOError) as e:
			exitWithError('Trying to open file with path "' + filepath + '", got error: ' + e.strerror)
		return

	def InsertInString(self, index, s, c):
		return s[:index] + c + s[index:]

	def InglobeOperator(self, rule, operator):
		i = 0
		while i < len(rule):
			if rule[i] == operator:
				left = i
				right = i
				i += 1
				counter = 0
				while left > 0:
					if rule[left] == ")":
						counter += 1
					elif rule[left] == "(":
						counter -= 1
						if counter == 0:
							break
					elif rule[left].isalpha() and counter == 0:
						break
					left -= 1
				while right < len(rule):
					if rule[right] == "(":
						counter += 1
					elif rule[right] == ")":
						counter -= 1
						if counter == 0:
							break
					elif rule[right].isalpha() and counter == 0:
						break
					right += 1
				rule = self.InsertInString(right + 1, rule, ")")
				rule = self.InsertInString(left - 1, rule, "(")
			i += 1
		return rule



	def AddPriorities(self, rule):
		i = 0
		# print "Rule:",rule
		while i < len(rule):
			if rule[i] == "!":
				i += 1
				j = i
				if not rule[i].isalpha():
					counter = 0
					while j < len(rule):
						if rule[j] == "(":
							counter += 1
						elif rule[j] == ")":
							counter -= 1
							if counter == 0:
								break
						j += 1
				rule = self.InsertInString(j + 1, rule, ")")
				rule = self.InsertInString(i - 1, rule, "(")
			i += 1
		# print "After !: ",rule
		rule = self.InglobeOperator(rule, "+")
		# print "After +: ",rule
		rule = self.InglobeOperator(rule, "|")
		# print "After |: ",rule
		rule = self.InglobeOperator(rule, "^")
		# print "After ^: ",rule + "\n"



		return rule

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


	def BackwordChaining(self, query, stringIndent, needPrint):
		if query in self.openQuery:
			exitWithError("Infinite loop detected. (Query: '" + query + "')")
		else:
			self.openQuery.append(query)
		if needPrint:
			printQuery(stringIndent + "Quering " + query)
		stringIndent += '\t';
		if query in self.facts:
			if needPrint:
				print stringIndent + query + " is known fact"
			self.openQuery.remove(query)
			return True
		elif query in self.negativeFacts:
			if needPrint:
				print stringIndent + query + " has already been evaluated false once"
			if query not in self.negativeFacts:
				self.negativeFacts += query
			self.openQuery.remove(query)
			return False
		elif query in self.nodes:
			for rule in self.nodes[query].rules:
				if needPrint:
					print stringIndent + "Rule for " + query + ": " + rule
				rule = rule.replace(" ", "")
				while "(" in rule:
					if needPrint:
						print stringIndent + "\tBecomes: " + rule
					closePar = rule.find(")")
					openPar = rule.rfind("(", 0, closePar)
					extract = rule[openPar + 1 : closePar]

					resultEval = self.EvalExtract(extract, stringIndent + "\t\t", needPrint)

					# combine left + result + right
					tmpRule = rule[0:openPar]
					if resultEval:
						tmpRule = tmpRule + "1"
					else:
						tmpRule = tmpRule + "0"
					rule = tmpRule + rule[closePar + 1:]
				if needPrint:
					print stringIndent + "Rule for " + query + " evaluated to: " + rule
				if rule == "1":
					if query not in self.facts:
						self.facts += query
					self.openQuery.remove(query)
					return True
			if query not in self.negativeFacts:
				self.negativeFacts += query
			self.openQuery.remove(query)
			return False
		else:
			if needPrint:
				print stringIndent + query + " is impossible to get"
			if query not in self.negativeFacts:
				self.negativeFacts += query
			self.openQuery.remove(query)
			return False

	def EvalExtract(self, extract, stringIndent, needPrint):
		leftSide = extract[0]
		isNeg = False;
		vals = []
		valsSigns = []
		ops = []
		otherSide = extract[1:]

		if leftSide == '!':
			isNeg = True
			leftSide = extract[1]
			otherSide = extract[2:]
		left = self.BackwordChaining(leftSide, stringIndent, needPrint)
		vals.append(left)
		if (isNeg):
			left = not left
		valsSigns.append(isNeg);

		while True:
			isNeg = False;
			if otherSide != "":
				operator = otherSide[0]
				ops.append(operator)
				rightSide = otherSide[1]
				otherSide = otherSide[2:]
			else:
				break
			if rightSide == '!':
				isNeg = True;
				rightSide = otherSide[0]
				otherSide = otherSide[1:]
			right = self.BackwordChaining(rightSide, stringIndent, needPrint)
			# print rightSide;
			vals.append(right)
			if isNeg:
				right = not right
			valsSigns.append(isNeg);

			if operator == "+":
				left = left and right
			if operator == "|":
				left = left or right
			if operator == "^":
				left = (not left and right) or (not right and left);


		if needPrint:
			i = 1
			j = 0
			print stringIndent + "(",
			if valsSigns[0]:
				print "!" +  str(vals[0]),
				vals[0] = not vals[0]
			else:
				print vals[0],
			while i < len(vals):
				print ops[j],
				if valsSigns[i]:
					print "!" +  str(vals[i]),
					vals[i] = not vals[i]
				else:
					print vals[i],
				i += 1
				j += 1
			print ")"

		return left

	def Eval(self):
		needPrint = False
		if "p" in self.options:
			needPrint = True
		for i, query in enumerate(self.goals):
			if i != 0 and needPrint:
				print ""

			res = self.BackwordChaining(query, '', needPrint)
			printResult(query, res)
		return

def main(argv):
	options = ""
	experts = []

	if GetOptions():
		options += "p"

	if len(GetFilepaths()) == 0:
		exitWithError("No filepath given", True)
	else:
		for i,path in enumerate(GetFilepaths()):
			try:
				if i != 0:
					print ""
				printFilename(path)
				newExpert = ExpertSys(path, options)

				newExpert.Eval()
			except (RuntimeError) as e:
				print e.args[0]

main(sys.argv)
