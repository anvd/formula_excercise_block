import mysql.connector
from mysql.connector import errorcode
import settings as s


def create_dummy_data(xblock_id):
    """
        INSERT INTO edxapp.question_template (xblock_id, question_template) VALUES (?, ?)

        INSERT INTO edxapp.variable (xblock_id, name, type, min_value, max_value, accuracy) VALUES (?, a, int, 0, 10)
        INSERT INTO edxapp.variable (xblock_id, name, type, min_value, max_value, accuracy) VALUES (?, b, int, 10, 100)

        INSERT INTO edxapp.expression (xblock_id, name, formula, accuracy) VALUES (?, Tong, a+b)
        INSERT INTO edxapp.expression (xblock_id, name, formula, accuracy) VALUES (?, Hieu, a-b)
    """
    
    connection = mysql.connector.connect(**s.database)
    cursor = connection.cursor()
    
    # create question template
    question_template_query = "INSERT INTO edxapp.question_template (xblock_id, template) VALUES ('" + xblock_id + "', " + "'Given a and b'" + ")"
    question_template_cursor = connection.cursor()
    question_template_cursor.execute(question_template_query)
    question_template_cursor.close()

    
    # create variables
    variable_template_query = "INSERT INTO edxapp.variable (xblock_id, name, type, min_value, max_value, accuracy) VALUES (%s, %s, %s, %s, %s, %s)"
    
    # "a" variable
    a_variable_data = (xblock_id, 'a', 'int', 0, 10, 2)
    cursor.execute(variable_template_query, a_variable_data)
    
    # "b" variable
    b_variable_data = (xblock_id, 'b', 'int', 0, 10, 3)
    cursor.execute(variable_template_query, b_variable_data)
    
    
    # create expressions
    expression_template_query = "INSERT INTO edxapp.expression (xblock_id, name, formula, accuracy) VALUES (%s, %s, %s, %s)"
    
    # 'Tong' expression
    tong_expression_data = (xblock_id, 'Tong', 'a+b', 2)
    cursor.execute(expression_template_query, tong_expression_data)
    
    # 'Hieu' expression
    hieu_expression_data = (xblock_id, 'Hieu', 'a-b', 3)
    cursor.execute(expression_template_query, hieu_expression_data)
    
    connection.commit()
    cursor.close()


if __name__ == "__main__":
    xblock_id_1 = "block-v1:Home+CS107+2017_T1+type@formula_exercise_block+block@3d06adc38f334114a475eab3518862dd"
    create_dummy_data(xblock_id_1)
    
    xblock_id_2 = "block-v1:Home+CS107+2017_T1+type@formula_exercise_block+block@ebff890deebe4a39a3844ecf17e6e187"
    create_dummy_data(xblock_id_2)
