import re
from random import randint


APPLES_VARIABLE_PATTERN = re.compile("<n>");
compiled_apples_variable_pattern = re.compile(APPLES_VARIABLE_PATTERN)

METERS_VARIABLES_PATTERN = re.compile("<m>")
compiled_meters_variable_pattern = re.compile(METERS_VARIABLES_PATTERN)


def is_answer_correct(apples, meters, energy):
    return (energy == (apples * meters))

def is_answer_correct_BDD(template, apples, meters, energy):
    pass


def generate_question_with_apples_and_meters(template, apples, meters):
    question_with_apples = compiled_apples_variable_pattern.sub(str(apples), template)
    return compiled_meters_variable_pattern.sub(str(meters), question_with_apples)

def generate_question(template):
    apples = randint(1, 10)
    meters = randint(2, 20)
    return [ apples, meters, generate_question_with_apples_and_meters(template, apples, meters) ]


if __name__ == "__main__":
    test_template = "What is the energy to raise <n> apples to <m> meters?"
    print('test_template: ' + test_template)
    print(generate_question_with_apples_and_meters(test_template, 10, 15))
    pass