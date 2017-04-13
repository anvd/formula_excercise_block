import unittest
from question_service import generate_question
from decimal import *

class QuestionServiceTest(unittest.TestCase):
    
    def test_generate_question_float_numbers(self):
        
        test_template1 = "What is the energy to raise <n> apples to <m> meters?"
        n_variable = {
            'name': 'n',
            'type': 'float',
            'min_value': 1,
            'max_value': 9,
            'decimal_places': 5
        }
        
        m_variable = {
            'name': 'm',
            'type': 'float',
            'min_value': 10,
            'max_value': 20,
            'decimal_places': 2
        }
        
        variables = {
            'n': n_variable,
            'm': m_variable
        }
        
        generated_question, generated_variables = generate_question(test_template1, variables)
        
        generate_n_value =  generated_variables['n']
        self.assertTrue(len(generate_n_value.split('.')[0]) == 1)
        self.assertTrue(len(generate_n_value.split('.')[1]) == 5)
        
        generated_m_value = generated_variables['m']
        self.assertTrue(len(generated_m_value.split('.')[0]) == 2)
        self.assertTrue(len(generated_m_value.split('.')[1]) == 2)


if __name__ == '__main__':
    unittest.main()
