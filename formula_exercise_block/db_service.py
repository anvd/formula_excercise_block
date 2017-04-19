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
    variable_query = "SELECT name, type, min_value, max_value, type, decimal_places FROM edxapp.variable WHERE xblock_id = '" + xblock_id + "'"
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
        variable['decimal_places'] = row[5]
        
        variables[variable['name']] = variable
        row = variable_query_cursor.fetchone()
        
    variable_query_cursor.close()
    
    
    # query expressions
    expression_query = "SELECT name, type, formula, decimal_places FROM edxapp.expression WHERE xblock_id = '" + xblock_id + "'"
    expression_query_cursor = connection.cursor()
    expression_query_cursor.execute(expression_query)
    row = expression_query_cursor.fetchone()
    
    
    # fetch expressions from the result set
    while row is not None:
        expression = {}
        expression['name'] = row[0]
        expression['type'] = row[1]
        expression['formula'] = row[2]
        expression['decimal_places'] = row[3]
        
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
    query = "INSERT INTO edxapp.variable (xblock_id, name, type, min_value, max_value, decimal_places) VALUES (%s, %s, %s, %s, %s, %s)"
    for variable_name, variable in updated_variables.iteritems():
        updated_variable_data = (xblock_id, variable_name, variable['type'], variable['min_value'], variable['max_value'], variable['decimal_places'])
        cursor.execute(query, updated_variable_data)
    
    cursor.close()


def create_expressions(xblock_id, connection, updated_expressions):
    """
    Create expressions for a question template
    """
    
    cursor = connection.cursor()
    query = "INSERT INTO edxapp.expression (xblock_id, name, type, formula, decimal_places) VALUES (%s, %s, %s, %s, %s)"
    for expression_name, expression in updated_expressions.iteritems():
        updated_expression_data = (xblock_id, expression_name, expression['type'], expression['formula'], expression['decimal_places'])
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


def delete_xblock(xblock_id):
    
    connection = mysql.connector.connect(**s.database)
    
    delete_query_str = "DELETE FROM edxapp.question_template WHERE xblock_id like '%" + xblock_id + "%'"
    cursor = connection.cursor()
    cursor.execute(delete_query_str)
    
    cursor.close()
    connection.commit()
    connection.close()
    
    
def is_xblock_submitted(item_id):
    
    # 1. TABLE submissions_studentitem(id)
    # 2. TABLE submissions_submission(student_item_id)
    """
    SELECT count(*) FROM edxapp.submissions_submission WHERE student_item_id IN (SELECT id FROM edxapp.submissions_studentitem WHERE item_id = item_id )
    """
    
    is_submitted = False
    
    query = "SELECT count(*) FROM edxapp.submissions_submission WHERE student_item_id IN (SELECT id FROM edxapp.submissions_studentitem WHERE item_id = '" + item_id + "')"
    connection = mysql.connector.connect(**s.database)
    cursor = connection.cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    if row is not None:
        is_submitted = row[0] > 0
        
    cursor.close()
    connection.close()

    return is_submitted    
