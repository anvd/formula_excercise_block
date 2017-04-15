import cexprtk


def is_int(value):
  try:
    int(value)
    return True
  except:
    return False


def evaluate_expressions(variables, expressions):
    """
    Evaluates whether the expression values are correct with respect to variable values
    
    Parameters:
        + variables: a dict in which each element is { variable name: [ variable instance, variable value ]}
        + expressions: a dict in which each element is { expression name: [ expression instance, expression value of student ] }
    
    Returns:
        + a dict in which each element is (expression_name: 0 / 1) indicating whether each expression value is correct (1) or not (0) with respect to the expression formula
    """
    
    cexprtk_variables = {} # variable_name : variable_value
    result = {} # result (expression name : 0 / 1)
    
    for var_name, var_data in variables.iteritems():
        variable = var_data[0]
        var_value = 0
        var_type = variable['type']
        
        if var_type == 'int':  # integer
            if (is_int(var_data[1])):
                var_value = int(var_data[1])
            else:
                var_value = int(float(var_data[1]))
        else: # float
            var_value = float(var_data[1])
        
        cexprtk_variables[var_name] = var_value
    
    
    #    create SymbolTable
    symbol_table = cexprtk.Symbol_Table(cexprtk_variables, add_constants= True)
    
    
    for expr_name, expr_data in expressions.iteritems():
        expression = expr_data[0]
        student_expression_value = expr_data[1]
        expr_formula = expression['formula'] # BUG why this is unicode????
        expr_type = expression['type']
        expr_val_decimal_places = int(expression['decimal_places'])
        coerced_student_expression_value = 0
        
        if expr_type == 'int': # integer
            if is_int(student_expression_value):
                coerced_student_expression_value = int(student_expression_value)
            else:
                coerced_student_expression_value = int(float(student_expression_value))
        else: # float TODO use Decimal
            coerced_student_expression_value = float(student_expression_value)
        
        # ask cexprtk to evaluate the expression
        # print('expr_formula: ' + expr_formula)
        cexprtk_expression = cexprtk.Expression(expr_formula.encode('utf-8'), symbol_table) # remove unicode: http://stackoverflow.com/questions/4855645/how-to-turn-unicode-strings-into-regular-strings
        # cexprtk_expression = cexprtk.Expression(expr_formula, symbol_table)
        cexprtk_expression_value = cexprtk_expression.value()
        
        # compare the student's result
        if (expr_type == 'int'):
            expr_val_decimal_places = 0
        if (areAlmostEqual(coerced_student_expression_value, cexprtk_expression_value, expr_val_decimal_places)):
            result[expr_name] = 1
        else:
            result[expr_name] = 0
    
    return result


def check_expressions(expressions):
    """
    Checks whether the expressions are parse-able
    """
    not_parseable_expressions = {}
    
    for expr_name, expression in expressions.iteritems():
        expr_formula = expression['formula'] # BUG why this is unicode????
        
        try:
            cexprtk.check_expression(expr_formula)
        except cexprtk.ParseException:
            not_parseable_expressions[expr_name] = expr_formula
        
    # TODO check that the expressions can be evaluated also
    return not_parseable_expressions


def areAlmostEqual(first, second, places=None, msg=None, delta=None):
    """
        Note: Inspired by unittest.TestCase's 'assertAlmostEquals' method
        
        Fail if the two objects are unequal as determined by their
       difference rounded to the given number of decimal places
       (default 7) and comparing to zero, or by comparing that the
       between the two objects is more than the given delta.
    
       Note that decimal places (from zero) are usually not the same
       as significant digits (measured from the most significant digit).
    
       If the two objects compare equal then they will automatically
       compare almost equal.
    """
    if first == second:
        # shortcut
        return True
    
    if delta is not None and places is not None:
        raise TypeError("specify delta or places not both")
    
    if delta is not None:
        if abs(first - second) <= delta:
            return True
    
    else:
        if places is None:
            places = 7
    
        if round(abs(second-first), places) == 0:
            return True
    
    return False
    
    
    