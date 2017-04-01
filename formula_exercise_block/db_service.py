import mysql.connector
from mysql.connector import errorcode
import settings as s


def create_question_template(xblock_id, question_template, variables, expressions):
    connection = mysql.connector.connect(**s.database)
    
    # clean_up_variables_and_expressions(fe_xblock, connection)
    
    insert_question_template(xblock_id, connection, question_template)
    
    create_variables(xblock_id, connection, variables)
    
    create_expressions(xblock_id, connection, expressions)
    
    connection.commit()
    connection.close()


def update_question_template(xblock_id, question_template, updated_variables, updated_expressions):
        
    connection = mysql.connector.connect(**s.database)
    
    clean_up_variables_and_expressions(xblock_id, connection)
    
    update_question_template_content(xblock_id, connection, question_template)
    
    create_variables(xblock_id, connection, updated_variables)
    
    create_expressions(xblock_id, connection, updated_expressions)
    
    connection.commit()
    connection.close()


def fetch_question_template_data(xblock_id):
    """
    Fetches question template data from the database:
        question_template
        variables
        expressions
    """
    connection = mysql.connector.connect(**s.database)
    
    question_template = ""
    variables = {}
    expressions = {}
    
    # query question_template
    question_template_query = "SELECT template FROM edxapp.question_template where xblock_id = '" + xblock_id + "'"
    question_template_cursor = connection.cursor()
    question_template_cursor.execute(question_template_query)
    row = question_template_cursor.fetchone()
    
    if row is not None:
        question_template = row[0]
    question_template_cursor.close()
    
    
    # query variables
    variable_query = "SELECT name, type, min_value, max_value, type, accuracy FROM edxapp.variable WHERE xblock_id = '" + xblock_id + "'"
    variable_query_cursor = connection.cursor()
    variable_query_cursor.execute(variable_query)
    row = variable_query_cursor.fetchone()
    
    
    # fetch variables from the result set
    while row is not None:
        variable = {}
        variable['name'] = row[0]
        variable['type'] = row[1]
        variable['min_value'] = row[2]
        variable['max_value'] = row[3]
        variable['type'] = row[4]
        variable['accuracy'] = row[5]
        
        variables[variable['name']] = variable
        row = variable_query_cursor.fetchone()
        
    variable_query_cursor.close()
    
    
    # query expressions
    expression_query = "SELECT name, formula, accuracy FROM edxapp.expression WHERE xblock_id = '" + xblock_id + "'"
    expression_query_cursor = connection.cursor()
    expression_query_cursor.execute(expression_query)
    row = expression_query_cursor.fetchone()
    
    
    # fetch expressions from the result set
    while row is not None:
        expression = {}
        expression['name'] = row[0]
        expression['formula'] = row[1]
        expression['accuracy'] = row[2]
        
        expressions[expression['name']] = expression
        row = expression_query_cursor.fetchone()
        
    expression_query_cursor.close()
    
    
    connection.close()
    return question_template, variables, expressions


def clean_up_variables_and_expressions(xblock_id, connection):
    """
    Removes variables and expressions of the question template
    """
    
    cursor = connection.cursor()
    
    # remove variables
    VARIABLES_REMOVE_QUERY = ("DELETE FROM edxapp.variable WHERE xblock_id = '" + xblock_id + "'")
    cursor.execute(VARIABLES_REMOVE_QUERY)
    
    # remove expressions
    EXPRESSIONS_REMOVE_QUERY = ("DELETE FROM edxapp.expression WHERE xblock_id = '" + xblock_id + "'")
    cursor.execute(EXPRESSIONS_REMOVE_QUERY)
    
    cursor.close()


def insert_question_template(xblock_id, connection, question_template):
    cursor = connection.cursor()
    query = "INSERT INTO edxapp.question_template (xblock_id, template) VALUES ('" + xblock_id + "', '" + question_template + "')"
    cursor.execute(query)
    cursor.close()


def update_question_template_content(xblock_id, connection, question_template):
    """
    Updates question template
    """
    
    cursor = connection.cursor()
    query = "UPDATE edxapp.question_template SET template = '" + question_template + "' WHERE xblock_id = '" + xblock_id + "'"
    
    cursor.execute(query)
    cursor.close()


def create_variables(xblock_id, connection, updated_variables):
    """
    Creates variables for a question template
    """
    
    cursor = connection.cursor()
    query = "INSERT INTO edxapp.variable (xblock_id, name, type, min_value, max_value, accuracy) VALUES (%s, %s, %s, %s, %s, %s)"
    for variable_name, variable in updated_variables.iteritems():
        updated_variable_data = (xblock_id, variable_name, variable['type'], variable['min_value'], variable['max_value'], variable['accuracy'])
        cursor.execute(query, updated_variable_data)
    
    cursor.close()


def create_expressions(xblock_id, connection, updated_expressions):
    """
    Create expressions for a question template
    """
    
    cursor = connection.cursor()
    query = "INSERT INTO edxapp.expression (xblock_id, name, formula, accuracy) VALUES (%s, %s, %s, %s)"
    for expression_name, expression in updated_expressions.iteritems():
        updated_expression_data = (xblock_id, expression_name, expression['formula'], expression['accuracy'])
        cursor.execute(query, updated_expression_data)
    
    cursor.close()
    pass


def is_block_in_db(xblock_id):
    
    connection = mysql.connector.connect(**s.database)
    
    query = "SELECT id FROM edxapp.question_template WHERE xblock_id = '" + xblock_id + "'"
    cursor = connection.cursor()
    cursor.execute(query)
    
    rowcount = cursor.rowcount
    cursor.close()
    connection.close()

    return (rowcount > 0)
