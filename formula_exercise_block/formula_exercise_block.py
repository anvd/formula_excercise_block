"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment

from submissions import api as sub_api
from sub_api_util import SubmittingXBlockMixin

from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblockutils.resources import ResourceLoader

import question_service
import db_service
import formula_service
import json

import xblock_deletion_handler

loader = ResourceLoader(__name__)


@XBlock.needs("i18n")
class FormulaExerciseXBlock(XBlock, SubmittingXBlockMixin, StudioEditableXBlockMixin):
    """
    TO-DO: XBlock life-cycle to initialize, open and close connection to MySQL server appropriately
    """

    display_name = String(
        display_name="Formula Exercise XBlock",
        help="This name appears in the horizontal navigation at the top of the page",
        scope=Scope.settings,
        default="Formula Exercise XBlock"
    )

    max_attempts = Integer(
        display_name="Maximum Attempts",
        help="Defines the number of times a student can try to answer this problem. If the value is not set, infinite attempts are allowed.",
        values={"min": 0}, scope=Scope.settings)
    
    max_points = Integer(
        display_name="Possible points",
        help="Defines the maximum points that the learner can earn.",
        default=1,
        scope=Scope.settings)
    
    
    xblock_id = None
    newly_created_block = True
    
    standard_question_template = String(
        display_name="Question template",
        help="Question template",
        scope=Scope.settings,
        default="???"
    )
    
    standard_variables_str = String(
        display_name="Standard",
        help="Question template",
        scope=Scope.settings,
        default="???"
    )
    
    
    
    question_template = ""
    variables = {}
    expressions = {}
    
    
    generated_question = ""
    generated_variables = {}
    submitted_expressions = {}
    
    
    

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.
    editable_fields = ('display_name', 'max_attempts', 'max_points')

    has_score = True

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")


    def student_view(self, context=None):
        """
        The primary view of the FormulaExerciseXBlock, shown to students
        when viewing courses.
        """
        
        context = {}
        self.submitted_expressions = {}
        
        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))
        
        
        if self.newly_created_block:
            self.newly_created_block =  (db_service.is_block_in_db(self.xblock_id) is False)
        
        
        if (self.newly_created_block is True): # generate question template for newly created XBlock
            self.question_template, self.variables, self.expressions = question_service.generate_question_template()
            db_service.create_question_template(self.xblock_id, self.question_template, self.variables, self.expressions)
            self.newly_created_block = False
        else: # existing question template in dbms
            self.load_data_from_dbms()
        
        # generate question from template if necessary
        if (self.generated_question == ""):
            self.generated_question, self.generated_variables = question_service.generate_question(self.question_template, self.variables)
        
        
        for expression_name, expression_value in self.expressions.iteritems():
            self.submitted_expressions[expression_name] = ''
        
        
        # load submission data
        submissions = sub_api.get_submissions(self.student_item_key, 1)
        if submissions:
            latest_submission = submissions[0]

            # parse the answer
            answer = latest_submission['answer']
            self.generated_question = answer['generated_question']
            saved_submitted_expressions = json.loads(answer['expression_values'])
            for submitted_expr_name, submitted_expr_val in saved_submitted_expressions.iteritems():
                self.submitted_expressions[submitted_expr_name] = submitted_expr_val

        
        self.serialize_data_to_context(context)    
        
        context['point_string'] = self.point_string
        context['question'] = self.generated_question
        context['xblock_id'] = self.xblock_id
        context['submitted_expressions'] = self.submitted_expressions

        
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
        
        # TODO check that if the XBlock has been submitted already to view the "disable_edit.html" page
#        location = self.location.replace(branch=None, version=None)  # Standardize the key in case it isn't already
#        course_id=unicode(location.course_key),
#        item_id=unicode(location),
#        item_type=self.scope_ids.block_type,
#        submissions = sub_api.get_all_submissions(course_id, item_id, item_type) # Not a good query
#        if submissions:
#            disabled_context = {}
#            disabled_context['xblock_id'] = unicode(self.location.replace(branch=None, version=None))
#            disabled_context['submissions'] = str(len(submissions))
            
            
#            disabled_edit_fragment = Fragment()
#            disabled_edit_fragment.content = loader.render_template('static/html/formula_exercise_disabled_studio_edit.html', disabled_context)
#            disabled_edit_fragment.add_javascript(loader.load_unicode('static/js/src/formula_exercise_disabled_studio_edit.js'))
#            disabled_edit_fragment.initialize_js('StudioDisabledEditXBlock')
#            return disabled_edit_fragment


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
                
        
        # (re-)fetch data from the database
        self.load_data_from_dbms()
        # self.serialize_data_to_context(context) ??? REMOVE not necessary, remove 
        context['question_template'] = self.question_template
        context["variables"] = self.variables
        context["expressions"] = self.expressions
        
        
        fragment.content = loader.render_template('static/html/formula_exercise_studio_edit.html', context)
        fragment.add_css(self.resource_string("static/css/formula_exercise_block_studio_edit.css"))
        fragment.add_javascript(loader.load_unicode('static/js/src/formula_exercise_studio_edit.js'))
        fragment.initialize_js('StudioEditableXBlockMixin')
        return fragment
    
    
    def serialize_data_to_context(self, context):
        """
        """
        context['saved_question_template'] = self.question_template
        context['serialized_variables'] = json.dumps(self.variables)
        context['serialized_expressions'] = json.dumps(self.expressions)
        context['serialized_generated_variables'] = json.dumps(self.generated_variables)
    
    
    def deserialize_data_from_context(self, context):
        """
        """
        self.question_template = context['saved_question_template']
        self.variables = json.loads(context['serialized_variables'])
        self.expressions = json.loads(context['serialized_expressions'])
        self.generated_variables = json.loads(context['serialized_generated_variables'])
    
    
    def load_data_from_dbms(self):

        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))
        
        self.question_template, self.variables, self.expressions = db_service.fetch_question_template_data(self.xblock_id)


    @XBlock.json_handler
    def student_submit(self, data, suffix=''):
        """
        AJAX handler for Submit button
        """
        
        submitted_expression_values = json.loads(data['submitted_expression_values'])
        self.deserialize_data_from_context(data)
        
        
        # prepare "expressions" data for formula_service.evaluate_expressions(variables, expressions)
        formula_service_expressions = {}
        for expression_name, expression in self.expressions.iteritems(): # expressions is unicode???
            formula_service_expressions[expression_name] = [ expression, submitted_expression_values[expression_name] ]
        
        
        # prepare "variables" data for formula_service.evaluate_expressions(variables, expressions)
        formula_service_variables = {} # TODO cache the following loop
        for var_name, var_value in self.generated_variables.iteritems():
            formula_service_variables[var_name] = [ self.variables[var_name], var_value ]
        
        
        # ask cexprtk to verify submit result
        evaluation_result = formula_service.evaluate_expressions(formula_service_variables, formula_service_expressions)
        points_earned = 1;
        for expr_name, point in evaluation_result.iteritems():
            if (point == 0):
                points_earned = 0
                break
        
        
        # save the submission
        submission_data = {
            'generated_question': data['saved_generated_question'],
            'expression_values': data['submitted_expression_values']
        }
        submission = sub_api.create_submission(self.student_item_key, submission_data)
        sub_api.set_score(submission['uuid'], points_earned, self.max_points)

        submit_result = {
            'points_earned': points_earned,
            'points_possible': 1
        }
        return submit_result

    
    @XBlock.json_handler
    def submit_studio_edits(self, data, suffix=''):
        # TODO how to initialize default data when creating a Formula Exercise XBlock
        
        # validate and save question template
        # call StudioEditableXBlockMixin.submit_studio_edits to save XBlock configuration
        
        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))
        
        question_template = data['question_template']
        updated_variables = data['variables']
        updated_expressions = data['expressions']
        db_service.update_question_template(self.xblock_id, question_template, updated_variables, updated_expressions)
        
    
        # "refresh" XBlock's values
        self.question_template = question_template
        self.variables = updated_variables
        self.expressions = updated_expressions
    
    
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
