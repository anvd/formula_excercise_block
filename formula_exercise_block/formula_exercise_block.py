"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, JSONField, Integer, String, Boolean
from xblock.fragment import Fragment

from xblock.exceptions import JsonHandlerError, NoSuchViewError
from xblock.validation import Validation

from submissions import api as sub_api
from sub_api_util import SubmittingXBlockMixin

from xblockutils.studio_editable import StudioEditableXBlockMixin, FutureFields
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
    Formula Exercise XBlock
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
        default=1,
        values={"min": 1}, scope=Scope.settings)
    
    max_points = Integer(
        display_name="Possible points",
        help="Defines the maximum points that the learner can earn.",
        default=1,
        scope=Scope.settings)
    
    show_points_earned = Boolean(
        display_name="Shows points earned",
        help="Shows points earned",
        default=True,
        scope=Scope.settings)
    
    
    xblock_id = None
    newly_created_block = True
    
    
    question_template = ""
    variables = {}
    expressions = {}
    
    
    generated_question = ""
    generated_variables = {}
    submitted_expressions = {}
    

    editable_fields = ('display_name', 'max_attempts', 'max_points', 'show_points_earned')

    has_score = True

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")


    def student_view(self, context=None):
        """
        The primary view of the FormulaExerciseXBlock, shown to students when viewing courses.
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
        
        
        # load submission data to display the previously submitted result
        submissions = sub_api.get_submissions(self.student_item_key, 1)
        if submissions:
            latest_submission = submissions[0]

            # parse the answer
            answer = latest_submission['answer']
            self.generated_question = answer['generated_question']
            saved_submitted_expressions = json.loads(answer['expression_values'])
            for submitted_expr_name, submitted_expr_val in saved_submitted_expressions.iteritems():
                self.submitted_expressions[submitted_expr_name] = submitted_expr_val
                
            attempt_number = latest_submission['attempt_number']
            if (attempt_number >= self.max_attempts):
                context['disabled'] = 'disabled'
            else:
                context['disabled'] = ''

        
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
        
        # if the XBlock has been submitted already then disable the studio_edit screen
        location = self.location.replace(branch=None, version=None)  # Standardize the key in case it isn't already
        item_id=unicode(location)
        if db_service.is_xblock_submitted(item_id):
            disabled_edit_fragment = Fragment()
            disabled_edit_fragment.content = loader.render_template('static/html/formula_exercise_disabled_studio_edit.html', {})
            disabled_edit_fragment.add_javascript(loader.load_unicode('static/js/src/formula_exercise_disabled_studio_edit.js'))
            disabled_edit_fragment.initialize_js('StudioDisabledEditXBlock')
            return disabled_edit_fragment

        
        # Student not yet submit then we can edit the XBlock
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
        Save data to context to re-use later to avoid re-accessing the DBMS
        """
        context['saved_question_template'] = self.question_template
        context['serialized_variables'] = json.dumps(self.variables)
        context['serialized_expressions'] = json.dumps(self.expressions)
        context['serialized_generated_variables'] = json.dumps(self.generated_variables)
    
    
    def deserialize_data_from_context(self, context):
        """
        De-serialize data previously saved to context
        """
        self.question_template = context['saved_question_template']
        self.variables = json.loads(context['serialized_variables'])
        self.expressions = json.loads(context['serialized_expressions'])
        self.generated_variables = json.loads(context['serialized_generated_variables'])
    
    
    def load_data_from_dbms(self):
        """
        Load question template data from MySQL
        """

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
        points_earned = self.max_points;
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
        
        submit_result = {}
        submit_result['point_string'] = self.point_string

        # disable the "Submit" button once the submission attempts reach max_attemps value
        attempt_number = submission['attempt_number']
        if (attempt_number >= self.max_attempts):
            submit_result['submit_disabled'] = 'disabled'
        else:
            submit_result['submit_disabled'] = ''

        return submit_result

    
    @XBlock.json_handler
    def validate_expressions(self, expressions, suffix=''):
        return formula_service.check_expressions(expressions)
    
    
    @XBlock.json_handler
    def fe_submit_studio_edits(self, data, suffix=''):
        """
        AJAX handler for studio edit submission
        """
        
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
        
        # call parent method
        # StudioEditableXBlockMixin.submit_studio_edits(self, data, suffix)
        # self.submit_studio_edits(data, suffix)
        # super(FormulaExerciseXBlock, self).submit_studio_edits(data, suffix)
        
        # copy from StudioEditableXBlockMixin (can not call parent method)
        values = {}  # dict of new field values we are updating
        to_reset = []  # list of field names to delete from this XBlock
        for field_name in self.editable_fields:
            field = self.fields[field_name]
            if field_name in data['values']:
                if isinstance(field, JSONField):
                    values[field_name] = field.from_json(data['values'][field_name])
                else:
                    raise JsonHandlerError(400, "Unsupported field type: {}".format(field_name))
            elif field_name in data['defaults'] and field.is_set_on(self):
                to_reset.append(field_name)
        self.clean_studio_edits(values)
        validation = Validation(self.scope_ids.usage_id)
        # We cannot set the fields on self yet, because even if validation fails, studio is going to save any changes we
        # make. So we create a "fake" object that has all the field values we are about to set.
        preview_data = FutureFields(
            new_fields_dict=values,
            newly_removed_fields=to_reset,
            fallback_obj=self
        )
        self.validate_field_data(validation, preview_data)
        if validation:
            for field_name, value in values.iteritems():
                setattr(self, field_name, value)
            for field_name in to_reset:
                self.fields[field_name].delete_from(self)
            return {'result': 'success'}
        else:
            raise JsonHandlerError(400, validation.to_json())
        
    
    
    @property
    def point_string(self):
        if self.show_points_earned:
            score = sub_api.get_score(self.student_item_key)
            if score != None:
                return str(score['points_earned']) + ' / ' + str(score['points_possible']) + ' point(s)'
            
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
