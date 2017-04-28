# formula_excercise_block
The Formula Exercise XBlock allows to generate formula exercises. 
Formula exercise is an exercise that asks user to compute the value of some (mathematical) expressions depending on the value of (input) variables.
Variable values are generated and are changed between users and login sessions. The XBlock is capable of evaluating the answer of user.

To create a formula exercise, we create an XBlock instance in the studio and define the following information: a question template,
variables and expressions.
  1. Question template: A question template represents the content of a question. It contains placeholders for variables whose values are generated at runtime.
  2. Variables: A set of variables of the question. A variable is defined by name, value range (i.e., min, max), type. The variable value is generated at runtime within the value range.
  3. Expressions: An expression is a mathematical formula which can be composed of a set (pre-defined) variables, operators (e.g., +, -, sin, cos, ...) and well-known constants (e.g., pi).
  
To answer a question, the user computes the expressions' values and submits result.

