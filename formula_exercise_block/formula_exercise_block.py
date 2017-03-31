"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment

from submissions import api as sub_api
from sub_api_util import SubmittingXBlockMixin

from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblockutils.resources import ResourceLoader

import mysql.connector
from mysql.connector import errorcode
import settings as s

import question_generator

loader = ResourceLoader(__name__)

class FormulaExerciseXBlock(XBlock, SubmittingXBlockMixin, StudioEditableXBlockMixin):
    """
    TO-DO: XBlock life-cycle to initialize, open and close connection to MySQL server appropriately
    """

    display_name = String(
        display_name="Title (Display name)", 
        help="Title to display", 
        default="Formula Exercise 2", 
        scope=Scope.settings)

    max_attempts = Integer(
        display_name="Maximum Attempts",
        help="Defines the number of times a student can try to answer this problem. If the value is not set, infinite attempts are allowed.",
        values={"min": 0}, scope=Scope.settings)
    
    max_points = Integer(
        display_name="Possible points",
        help="Defines the maximum points that the learner can earn.",
        default=1,
        scope=Scope.settings)

 
    apples = Integer(
        display_name="Apples",
        help="Number of apples",
        default=0,
        values={"min": 0}, 
        scope=Scope.user_state)
    
    meters = Integer(
        display_name="Meters",
        help="Height (in meters)",
        default=0,
        values={"min": 0}, 
        scope=Scope.user_state)
    
    question = String(
      display_name="Generated question", 
        help="Generated question", 
        default="",
        scope=Scope.user_state)
    
    energy = Integer(
        display_name="Calculated energy",
        help="Result input by learner",
        values={"min": 0}, 
        scope=Scope.user_state)
    
    
    xblock_id = None
    newly_created_block = False
    
    question_template = "What is the energy to raise <n> apples to <m> meters?"
    variables = {}
    expressions = {}
    

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.
    editable_fields = ('display_name', 'max_attempts', 'max_points')

    has_score = True

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the FormulaExerciseXBlock, shown to students
        when viewing courses.
        """
        
        
        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))
        
        if (self.question == ""):
            generated_data = question_generator.generate_question(self.question_template)
            self.apples = generated_data[0]
            self.meters = generated_data[1]
            self.question = generated_data[2]
            
        context = {
            'point_string': self.point_string,
            'question': self.question,
            'energy': self.energy
        }
        
        frag = Fragment()
        frag.content = loader.render_template('static/html/formula_exercise_block.html', context)
        frag.add_css(self.resource_string("static/css/formula_exercise_block.css"))
        frag.add_javascript(self.resource_string("static/js/src/formula_exercise_block.js"))
        frag.initialize_js('FormulaExerciseXBlock')
        return frag
    
    
    def studio_view(self, context):
        """
        Render a form for editing this XBlock (override the StudioEditableXBlockMixin's method)
        """

        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))
        
        fragment = Fragment()
        context = {'fields': []}
        # Build a list of all the fields that can be edited:
        for field_name in self.editable_fields:
            field = self.fields[field_name]
            assert field.scope in (Scope.content, Scope.settings), (
                "Only Scope.content or Scope.settings fields can be used with "
                "StudioEditableXBlockMixin. Other scopes are for user-specific data and are "
                "not generally created/configured by content authors in Studio."
            )
            field_info = self._make_field_info(field_name, field)
            if field_info is not None:
                context["fields"].append(field_info)
                
        
        self.fetch_question_template_data()
        context["question_template"] = self.question_template
        context["xblock_id"] = self.xblock_id
        context["variables"] = self.variables
        context["expressions"] = self.expressions
        
        
        fragment.content = loader.render_template('static/html/formula_exercise_studio_edit.html', context)
        fragment.add_css(self.resource_string("static/css/formula_exercise_block_studio_edit.css"))
        fragment.add_javascript(loader.load_unicode('static/js/src/formula_exercise_studio_edit.js'))
        fragment.initialize_js('StudioEditableXBlockMixin')
        return fragment
    
    
    def fetch_question_template_data(self):
        """
        Fetches question template data from the database:
            question_template
            variables
            expressions
        """
        connection = mysql.connector.connect(**s.database)
        
        # query question_template
        question_template_query = "SELECT template FROM edxapp.question_template where xblock_id = '" + self.xblock_id + "'"
        question_template_cursor = connection.cursor()
        question_template_cursor.execute(question_template_query)
        row = question_template_cursor.fetchone()
        
        if row is not None:
            self.question_template = row[0]
        question_template_cursor.close()
        
        
        # query variables
        variable_query = "SELECT name, type, min_value, max_value, type, accuracy FROM edxapp.variable WHERE xblock_id = '" + self.xblock_id + "'"
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
            
            self.variables[variable['name']] = variable
            row = variable_query_cursor.fetchone()
            
        variable_query_cursor.close()
        
        
        # query expressions
        expression_query = "SELECT name, formula, accuracy FROM edxapp.expression WHERE xblock_id = '" + self.xblock_id + "'"
        expression_query_cursor = connection.cursor()
        expression_query_cursor.execute(expression_query)
        row = expression_query_cursor.fetchone()
        
        
        # fetch expressions from the result set
        while row is not None:
            expression = {}
            expression['name'] = row[0]
            expression['formula'] = row[1]
            expression['accuracy'] = row[2]
            
            self.expressions[expression['name']] = expression
            row = expression_query_cursor.fetchone()
            
        expression_query_cursor.close()
        
        
        connection.close()
    
    
    def generate_question_template_data(self):
        """
        Generates data for a newly created question template
        """
        
        pass


    @XBlock.json_handler
    def student_submit(self, data, suffix=''):
        """
        AJAX handler for Submit button
        """
        submission = sub_api.create_submission(self.student_item_key, data)
        
        submitted_energy = data["energy"]
        self.energy = int(submitted_energy) # ??? correct way to set value?
        if question_generator.is_answer_correct(int(self.apples), int(self.meters), int(self.energy)):
            sub_api.set_score(submission['uuid'], self.max_points, self.max_points)
        else:
            sub_api.set_score(submission['uuid'], 0, self.max_points)
            
        
        new_score = sub_api.get_score(self.student_item_key)
        
        submit_result = {
            'points_earned': new_score['points_earned'],
            'points_possible': new_score['points_possible']
        }
        return submit_result

    
    @XBlock.json_handler
    def submit_studio_edits(self, data, suffix=''):
        # TODO how to initialize default data when creating a Formula Exercise XBlock
        
        # validate and save question template
        # call StudioEditableXBlockMixin.submit_studio_edits to save XBlock configuration
        
        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))
        
        connection = mysql.connector.connect(**s.database)
        
        self.clean_up_variables_and_expressions(connection)
        
        # question_template
        question_template = data['question_template']
        self.update_or_insert_question_template(connection, question_template)
        
        # variables dict
        updated_variables = data['variables']
        self.create_variables(connection, updated_variables)
        
        # expressions dict
        updated_expressions = data['expressions']
        self.create_expressions(connection, updated_expressions)
        
        connection.commit()
        connection.close()
    
    
    def clean_up_variables_and_expressions(self, connection):
        """
        Removes variables and expressions of the question template
        """
        
        cursor = connection.cursor()
        
        # remove variables
        VARIABLES_REMOVE_QUERY = ("DELETE FROM edxapp.variable WHERE xblock_id = '" + self.xblock_id + "'")
        cursor.execute(VARIABLES_REMOVE_QUERY)
        
        # remove expressions
        EXPRESSIONS_REMOVE_QUERY = ("DELETE FROM edxapp.expression WHERE xblock_id = '" + self.xblock_id + "'")
        cursor.execute(EXPRESSIONS_REMOVE_QUERY)
        
        cursor.close()
    
    
    def update_or_insert_question_template(self, connection, question_template):
        """
        Updates or inserts question template
        """
        
        # 1. if exist the record then update it
        # 2 else update it
        cursor = connection.cursor()
        query = ""
        if self.is_block_newly_created(connection):
            query = "INSERT INTO edxapp.question_template (xblock_id, template) VALUES ('" + self.xblock_id + "', '" + question_template + "')"
        else:
            query = "UPDATE edxapp.question_template SET template = '" + question_template + "' WHERE xblock_id = '" + self.xblock_id + "'"
        
        cursor.execute(query)
        cursor.close()
    
    
    def create_variables(self, connection, updated_variables):
        """
        Creates variables for a question template
        """
        
        cursor = connection.cursor()
        query = "INSERT INTO edxapp.variable (xblock_id, name, type, min_value, max_value, accuracy) VALUES (%s, %s, %s, %s, %s, %s)"
        for variable_name, variable in updated_variables.iteritems():
            updated_variable_data = (self.xblock_id, variable_name, variable['type'], variable['min_value'], variable['max_value'], variable['accuracy'])
            cursor.execute(query, updated_variable_data)
        
        cursor.close()
    
    
    def create_expressions(self, connection, updated_expressions):
        """
        Create expressions for a question template
        """
        
        cursor = connection.cursor()
        query = "INSERT INTO edxapp.expression (xblock_id, name, formula, accuracy) VALUES (%s, %s, %s, %s)"
        for expression_name, expression in updated_expressions.iteritems():
            updated_expression_data = (self.xblock_id, expression_name, expression['formula'], expression['accuracy'])
            cursor.execute(query, updated_expression_data)
        
        cursor.close()
        pass
    
    
    def is_block_newly_created(self, connection):
        if self.newly_created_block is False:
            query = "SELECT id FROM edxapp.question_template WHERE xblock_id = '" + self.xblock_id + "'"
            cursor = connection.cursor()
            cursor.execute(query)
        
            self.newly_created_block = cursor.rowcount == 0
            cursor.close()
            
        return self.newly_created_block


    @property
    def point_string(self):
        score = sub_api.get_score(self.student_item_key)
        
        if score != None:
            return str(score['points_earned']) + ' / ' + str(score['points_possible']) + ' point(s)'
        else:
            return str(self.max_points) + ' point(s) possible'

    
    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("FormulaExerciseXBlock",
             """<formula_exercise_block/>
             """),
            ("Multiple FormulaExerciseXBlock",
             """<vertical_demo>
                <formula_exercise_block/>
                <formula_exercise_block/>
                <formula_exercise_block/>
                </vertical_demo>
             """),
        ]
