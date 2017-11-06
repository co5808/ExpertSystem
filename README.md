# ExpertSystem
42 project: ExpertSystem
By Claudio Mutti and Hamza Louar

### Objective:
The goal of this project is to make a propositional calculus expert system by implementing a backward-chaining inference engine.

### Project's constraints
Rules and facts will be given as a text file and the following logical operators must be supported: NOT ('!'), AND ('+'), XOR ('^'), OR ('|') and parenthesis. However, OR and XOR must not be in the right side of a rule. 

A fact can be any uppercase alphabetical character and, by default, all facts are false and can only be made true by the initial facts statement,
or by application of a rule.

If there is an error in the input, the program will inform the user of the problem.

### Usage
$> expert.py [-h] [-p] sourcefile [sourcefile_2 ...]

#### Options:
  - -h -> show help message and exit
  - -p -> print all the resolver steps
