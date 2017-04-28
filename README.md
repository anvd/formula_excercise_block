# Formula Exercise XBlock
## Introduction
Formula Exercise XBlock (FEX) allows to create formula exercises. 
Formula exercise is a kind of exercise that asks user to calculate the value of some (mathematical) expressions depending on the value of (input) variables. 
The exercise content, i.e., variable values, are dynamically generated and changed between users as well as between login sessions of a user. In addition, FEX is capable of evaluating the user's answer.

## Exercise definition
We create an exercise in the studio by defining the following information: a question template, variables and expressions.
  1. Question template: A question template represents the content of a question. It contains placeholders for variables whose values are generated at runtime. A variable placeholder takes the form of <variable_name> in which "variable_name" is the name of a variable defined in the "Variables" session.
  2. Variables: A question can contain a set of variables. A variable is defined by name, value range (i.e., min, max), type. The variable value is generated at runtime within the value range. 
  3. Expressions: An expression is a mathematical formula which can be composed of a set of (pre-defined) variables, operators (e.g., +, -, sin, cos, ...) and well-known constants (e.g., pi). An expression is defined by name, formula, type and decimal places.
  
## Exercise generation
Based on the question template, variables and expressions, FEX generates a question to be displayed in the student view. FEX takes the question template then generates the variable values to replace the variable placeholders. In addition, it also generates a textfields for expressions.

## Answer evaluation
The user answers a question by filling in the expression textfields. When he/she submits the answer, FEX will perform the evaluation by computing the expression values based on the formula and compare the computed values with the submitted ones. FEX uses cexprtk [1] as the expression parser and evaluator. Hence, theoretically, we can use all the cexprtk's supported operators and functions.

## Exercise definition example
The following three images show the graphical user interface (GUI) for creating an exercise. The GUI consists of two tabs: General Information and Template. The user inputs common XBlock information in the General Information tab and question related information in the Template tab.

![General Information tab](https://github.com/anvd/formula_excercise_block/blob/master/doc/FEX_GI.png "General Information tab")

![Template tab (1)](https://github.com/anvd/formula_excercise_block/blob/master/doc/FEX_T1.png "Template tab (1)")

![Template tab (2)](https://github.com/anvd/formula_excercise_block/blob/master/doc/FEX_T2.png "Template tab (2)")


## References
  1. cexprtk: https://pypi.python.org/pypi/cexprtk/0.2.0
