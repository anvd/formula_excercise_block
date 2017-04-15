import unittest

import formula_service
from django.template.defaultfilters import length

class FormulaServiceTest(unittest.TestCase):
    
    def test_evaluate_int_expressions_correct(self):
        
        # prepare variables
        variable_values = { 'a' : 10, 'b' : 5 }
        
        a_variable = {
            'name': 'a',
            'type': 'int',
            'min_value': 0,
            'max_value': 10,
            'decimal_places': 3
        }
        
        b_variable = {
            'name': 'b',
            'type': 'int',
            'min_value': 0,
            'max_value': 10,
            'decimal_places': 3
        }
        
        variables = {
            a_variable['name']: [ a_variable, variable_values['a'] ],
            b_variable['name']: [ b_variable, variable_values['b'] ]
        }
        
        
        sum_expression = {
            'name': 'Sum',
            'type': 'float',
            'formula': 'a+b',
            'decimal_places': 3
        }
        
        difference_expression = {
            'name': 'Difference',
            'type': 'float',
            'formula': 'a-b',
            'decimal_places': 3
        }
        
        multiplication_expression = {
            'name': 'Multiplication',
            'type': 'float',
            'formula': 'a*b',
            'decimal_places': 3
        }
        
        quotient_expression = {
            'name': 'Quotient',
            'type': 'float',
            'formula': 'a/b',
            'decimal_places': 3
        }
        
        
        # prepare expressions
        student_sum_expr_value = 15
        student_difference_expr_value = 5
        student_multiplication_expr_value = 50
        student_quotient_expr_value = 2
        
        expression_values_1 = {
            sum_expression['name']: [ sum_expression, student_sum_expr_value ],
            difference_expression['name']: [ difference_expression, student_difference_expr_value ],
            multiplication_expression['name']: [ multiplication_expression, student_multiplication_expr_value ],
            quotient_expression['name']: [ quotient_expression, student_quotient_expr_value ]
        }
        
        
        # perform the test
        result = formula_service.evaluate_expressions(variables, expression_values_1)
        
        
        self.assertTrue(len(result) == 4)
        for expression_name, evaluation_result in result.iteritems():
            self.assertTrue(evaluation_result)
  
    
    def test_evaluate_expressions_all_incorrect(self):
        # prepare variables
        variable_values = { 'a' : 10, 'b' : 5 }
        
        a_variable = {
            'name': 'a',
            'type': 'int',
            'min_value': 0,
            'max_value': 10,
            'decimal_places': 3
        }
        
        b_variable = {
            'name': 'b',
            'type': 'int',
            'min_value': 0,
            'max_value': 10,
            'decimal_places': 3
        }
        
        variables = {
            a_variable['name']: [ a_variable, variable_values['a'] ],
            b_variable['name']: [ b_variable, variable_values['b'] ]
        }
        
        
        sum_expression = {
            'name': 'Sum',
            'type': 'float',
            'formula': 'a+b',
            'decimal_places': 3
        }
        
        difference_expression = {
            'name': 'Difference',
            'type': 'float',
            'formula': 'a-b',
            'decimal_places': 3
        }
        
        multiplication_expression = {
            'name': 'Multiplication',
            'type': 'float',
            'formula': 'a*b',
            'decimal_places': 3
        }
        
        quotient_expression = {
            'name': 'Quotient',
            'type': 'float',
            'formula': 'a/b',
            'decimal_places': 3
        }
        
        
        # prepare expressions
        student_sum_expr_value = 14
        student_difference_expr_value = 4
        student_multiplication_expr_value = 51
        student_quotient_expr_value = 3
        
        expression_values_1 = {
            sum_expression['name']: [ sum_expression, student_sum_expr_value ],
            difference_expression['name']: [ difference_expression, student_difference_expr_value ],
            multiplication_expression['name']: [ multiplication_expression, student_multiplication_expr_value ],
            quotient_expression['name']: [ quotient_expression, student_quotient_expr_value ]
        }
        
        
        # perform the test
        result = formula_service.evaluate_expressions(variables, expression_values_1)
        
        
        self.assertTrue(len(result) == 4)
        for expression_name, evaluation_result in result.iteritems():
            self.assertFalse(evaluation_result)
  

    def test_evaluate_expressions_50percent_correct(self):
        # prepare variables
        variable_values = { 'a' : 10, 'b' : 5 }
        
        a_variable = {
            'name': 'a',
            'type': 'int',
            'min_value': 0,
            'max_value': 10,
            'decimal_places': 3
        }
        
        b_variable = {
            'name': 'b',
            'type': 'int',
            'min_value': 0,
            'max_value': 10,
            'decimal_places': 3
        }
        
        variables = {
            a_variable['name']: [ a_variable, variable_values['a'] ],
            b_variable['name']: [ b_variable, variable_values['b'] ]
        }
        
        
        sum_expression = {
            'name': 'Sum',
            'type': 'float',
            'formula': 'a+b',
            'decimal_places': 3
        }
        
        difference_expression = {
            'name': 'Difference',
            'type': 'float',
            'formula': 'a-b',
            'decimal_places': 3
        }
        
        multiplication_expression = {
            'name': 'Multiplication',
            'type': 'float',
            'formula': 'a*b',
            'decimal_places': 3
        }
        
        quotient_expression = {
            'name': 'Quotient',
            'type': 'float',
            'formula': 'a/b',
            'decimal_places': 3
        }
        
        
        # prepare expressions
        student_sum_expr_value = 15
        student_difference_expr_value = 4
        student_multiplication_expr_value = 51
        student_quotient_expr_value = 2
        
        expression_values_1 = {
            sum_expression['name']: [ sum_expression, student_sum_expr_value ],
            difference_expression['name']: [ difference_expression, student_difference_expr_value ],
            multiplication_expression['name']: [ multiplication_expression, student_multiplication_expr_value ],
            quotient_expression['name']: [ quotient_expression, student_quotient_expr_value ]
        }
        
        
        # perform the test
        result = formula_service.evaluate_expressions(variables, expression_values_1)
        
        
        self.assertTrue(len(result) == 4)
        self.assertTrue(result['Sum'])
        self.assertFalse(result['Difference'])
        self.assertFalse(result['Multiplication'])
        self.assertTrue(result['Quotient'])
        
        
        
    def test_evaluate_expressions_float_correct(self):
        # prepare variables
        variable_values = { 'a' : 7.5, 'b' : 2.5 }
        
        a_variable = {
            'name': 'a',
            'type': 'float',
            'min_value': 0,
            'max_value': 10,
            'decimal_places': 3
        }
        
        b_variable = {
            'name': 'b',
            'type': 'float',
            'min_value': 0,
            'max_value': 10,
            'decimal_places': 3
        }
        
        variables = {
            a_variable['name']: [ a_variable, variable_values['a'] ],
            b_variable['name']: [ b_variable, variable_values['b'] ]
        }
        
        
        sum_expression = {
            'name': 'Sum',
            'type': 'float',
            'formula': 'a+b',
            'decimal_places': 3
        }
        
        difference_expression = {
            'name': 'Difference',
            'type': 'float',
            'formula': 'a-b',
            'decimal_places': 3
        }
        
        multiplication_expression = {
            'name': 'Multiplication',
            'type': 'float',
            'formula': 'a*b',
            'decimal_places': 3
        }
        
        quotient_expression = {
            'name': 'Quotient',
            'type': 'float',
            'formula': 'a/b',
            'decimal_places': 3
        }
        
        
        # prepare expressions
        student_sum_expr_value = 10
        student_difference_expr_value = 5
        student_multiplication_expr_value = 18.75
        student_quotient_expr_value = 3
        
        expression_values_1 = {
            sum_expression['name']: [ sum_expression, student_sum_expr_value ],
            difference_expression['name']: [ difference_expression, student_difference_expr_value ],
            multiplication_expression['name']: [ multiplication_expression, student_multiplication_expr_value ],
            quotient_expression['name']: [ quotient_expression, student_quotient_expr_value ]
        }
        
        
        # perform the test
        result = formula_service.evaluate_expressions(variables, expression_values_1)
        self.assertTrue(result[sum_expression['name']] == 1)
        self.assertTrue(result[difference_expression['name']] == 1)
        self.assertTrue(result[multiplication_expression['name']] == 1)
        self.assertTrue(result[quotient_expression['name']] == 1)


    def testAreAlmostEqual(self):
        a = 1.1
        b = 1.11
        self.assertTrue(formula_service.areAlmostEqual(a, b, 1))
        self.assertFalse(formula_service.areAlmostEqual(a, b, 2))
        
        c = 1.2
        d = 1.234
        self.assertFalse(formula_service.areAlmostEqual(c, d))
        self.assertTrue(formula_service.areAlmostEqual(a, b, 1))
        self.assertFalse(formula_service.areAlmostEqual(a, b, 2))
        self.assertFalse(formula_service.areAlmostEqual(a, b, 3))
        
        e = 1.05
        f = 1
        self.assertFalse(formula_service.areAlmostEqual(e, f))
        self.assertTrue(formula_service.areAlmostEqual(e, f, 0))
        self.assertFalse(formula_service.areAlmostEqual(e, f, 1))
        self.assertFalse(formula_service.areAlmostEqual(e, f, 2))
        
        g = 1.155
        h = 1.1556
        self.assertFalse(formula_service.areAlmostEqual(g, h))
        self.assertTrue(formula_service.areAlmostEqual(g, h, 0))
        self.assertTrue(formula_service.areAlmostEqual(g, h, 1))
        self.assertTrue(formula_service.areAlmostEqual(g, h, 2))
        self.assertFalse(formula_service.areAlmostEqual(g, h, 3))
        self.assertFalse(formula_service.areAlmostEqual(g, h, 4))
        
        i = 1.21
        j = 1
        self.assertFalse(formula_service.areAlmostEqual(i, j, 2))
        self.assertFalse(formula_service.areAlmostEqual(i, j, 1))
        self.assertTrue(formula_service.areAlmostEqual(i, j, 0))
        
        pass
        

    def test_check_expressions(self):
        
        expression1 = {
            'name': 'Sum',
            'type': 'float',
            'formula': 'a+b',
            'decimal_places': 3
        }
        
        expression2 = {
            'name': 'expr2',
            'type': 'float',
            'formula': 'foo(a)',
            'decimal_places': 3
        }
        
        expression3 = {
            'name': 'expr3',
            'type': 'float',
            'formula': 'a',
            'decimal_places': 3
        }

        expression4 = {
            'name': 'expr4',
            'type': 'float',
            'formula': 'log(a + 1)',
            'decimal_places': 3
        }
        
        expressions = {}
        expressions[expression1['name']] = expression1
        expressions[expression2['name']] = expression2
        expressions[expression3['name']] = expression3
        expressions[expression4['name']] = expression4
        
        
        check_result = formula_service.check_expressions(expressions)
        self.assertTrue(length(check_result) == 1)
        self.assertTrue('expr2' in check_result)


if __name__ == '__main__':
    unittest.main()
