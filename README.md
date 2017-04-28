# Formula Exercise XBlock
## Introduction
The Formula Exercise XBlock allows to create formula exercises. 
Formula exercise is a kind of exercise that asks user to calculate the value of some (mathematical) expressions depending on the value of (input) variables. 
The exercise content, i.e., variable values, are dynamically generated and changed between users as well as between login sessions of a user. In addition, the XBlock is capable of evaluating the user's answer.

## Exercise definition
We create an exercise in the studio by defining the following information: a question template, variables and expressions.
  1. Question template: A question template represents the content of a question. It contains placeholders for variables whose values are generated at runtime. A variable placeholder takes the form of <variable_name> in which "variable_name" is the name of a variable defined in the "Variables" session.
  2. Variables: A question can contain a set of variables. A variable is defined by name, value range (i.e., min, max), type. The variable value is generated at runtime within the value range. 
  3. Expressions: An expression is a mathematical formula which can be composed of a set of (pre-defined) variables, operators (e.g., +, -, sin, cos, ...) and well-known constants (e.g., pi). An expression is defined by name, formula, type and decimal places.
  
## Exercise generation
Based on the question template, variables and expressions, the XBlock generates a question to be displayed in the student view. The XBlock takes the question template then generates the variable values to replace the variable placeholders. In addition, it also generates a textfields for expressions.

## Answer evaluation
The user answers a question by filling in the expression textfields. When he/she submits the answer, the XBlock will perform the evaluation by computing the expression values based on the formula and compare the computed values with the submitted ones. The XBlock uses cexprtk [1] as the expression parser and evaluator. Hence, theoretically, we can use all the cexprtk's supported operators.

## References
  1. cexprtk: https://pypi.python.org/pypi/cexprtk/0.2.0
