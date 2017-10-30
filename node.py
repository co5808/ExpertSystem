#!/usr/bin/python

class Node:
    def AddRule(self, rule):
        if rule not in self.rules:
            self.rules.append(rule)

    def __init__(self, name, rule):
        self.name = name;
        self.rules = [];
        self.found = -2;
        self.AddRule(rule);

    def PrintRules(self):
        print self.name
        print self.rules;
        print ""
