import re
from random import randint, uniform


APPLES_VARIABLE_PATTERN = re.compile("<n>");
compiled_apples_variable_pattern = re.compile(APPLES_VARIABLE_PATTERN)

METERS_VARIABLES_PATTERN = re.compile("<m>")
compiled_meters_variable_pattern = re.compile(METERS_VARIABLES_PATTERN)


def is_answer_correct(apples, meters, energy):
    return (energy == (apples * meters))

def is_answer_correct_BDD(template, apples, meters, energy):
    pass


def generate_question_template():
    """
    Generates data for a newly created question template
    """
    sample_template = "Given a = <a> and b = <b>. Calculate the sum, difference, multiplication and quotient."
    
    a_variable = {
        'name': 'a',
        'min_value': 0,
        'max_value': 10,
        'type': 'int',
        'accuracy': 2
    }
    
    b_variable = {
        'name': 'a',
        'min_value': 10,
        'max_value': 20,
        'type': 'int',
        'accuracy': 2
    }
    
    variables = {
        'a': a_variable,
        'b': b_variable,
    }
    
    
    sum_expression = {
        'name': 'Sum',
        'formula': 'a+b',
        'accuracy': 2
    }
    
    difference_expression = {
        'name': 'Difference',
        'formula': 'a-b',
        'accuracy': 2
    }
    
    multiplication_expression = {
        'name': 'Multiplication',
        'formula': 'a*b',
        'accuracy': 2
    }
    
    quotient_expression = {
        'name': 'Quotient',
        'formula': 'a+b',
        'accuracy': 2
    }
    
    expressions = {
        'Sum': sum_expression,
        'Difference': difference_expression,
        'Multiplication': multiplication_expression,
        'Quotient': quotient_expression
    }
    
    return sample_template, variables, expressions


def generate_question(template, variables):
    
    compiled_variable_patterns = {}
    generated_variables = {}
    
    
    # generate variables' value
    for var_name, variable in variables.iteritems():
        compiled_variable_patterns[var_name] = re.compile('<' + var_name + '>')
        var_type = variable['type']
        
        var_value = ""
        if var_type == 'int':
            var_value = str(randint(int(variable['min_value']), int(variable['max_value'])))
        else: # float
            var_value = str(uniform(float(variable['min_value']), float(variable['max_value'])))

        generated_variables[var_name] = var_value
        
    # generate the question
    generated_question = template
    for var_name, var_value in generated_variables.iteritems():
        generated_question = compiled_variable_patterns[var_name].sub(str(generated_variables[var_name]), generated_question)
    
    return generated_question, generated_variables


def generate_question_with_apples_and_meters(template, apples, meters):
    question_with_apples = compiled_apples_variable_pattern.sub(str(apples), template)
    return compiled_meters_variable_pattern.sub(str(meters), question_with_apples)

def internal_generate_question(template):
    apples = randint(1, 10)
    meters = randint(2, 20)
    return [ apples, meters, generate_question_with_apples_and_meters(template, apples, meters) ]


if __name__ == "__main__":
#    test_template = "What is the energy to raise <n> apples to <m> meters?"
#    print('test_template: ' + test_template)
#    print(generate_question_with_apples_and_meters(test_template, 10, 15))
    
    
    test_template1 = "What is the energy to raise <n> apples to <m> meters?"
    n_variable = {
        'name': 'n',
        'type': 'int',
        'min_value': 1,
        'max_value': 10,
        'accuracy': 2
    }
    
    m_variable = {
        'name': 'm',
        'type': 'int',
        'min_value': 5,
        'max_value': 20,
        'accuracy': 2
    }
    
    variables = {
        'n': n_variable,
        'm': m_variable
    }
    
    generated_question, generated_variables = generate_question(test_template1, variables)
    
    print('test_template1: ' + test_template1)
    print('generated test_template1: ' +  generated_question)
    print 'Generated n: ' + generated_variables['n']
    print 'Generated m: ' + generated_variables['m']
    
