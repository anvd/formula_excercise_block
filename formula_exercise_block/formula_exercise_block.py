"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment

from submissions import api as sub_api
from sub_api_util import SubmittingXBlockMixin

from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblockutils.resources import ResourceLoader

import question_generator

loader = ResourceLoader(__name__)

class FormulaExerciseXBlock(XBlock, SubmittingXBlockMixin, StudioEditableXBlockMixin):
    """
    TO-DO: document what your XBlock does.
    """

    display_name = String(
        display_name="Title (Display name)", 
        help="Title to display", 
        default="Formula Exercise 2", 
        scope=Scope.settings)

    question_template = String(
        display_name="Enter question template", 
        help="Enter the question", 
        default="What is the energy to raise <n> apples to <m> meters?", 
        multiline_editor=True, 
        scope=Scope.content)
    
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

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # For question_template to create the "edit" form
    editable_fields = ('display_name', 'question_template', 'max_attempts', 'max_points')

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
        fragment.content = loader.render_template('static/html/formula_exercise_studio_edit.html', context)
        fragment.add_css(self.resource_string("static/css/formula_exercise_block_studio_edit.css"))
        fragment.add_javascript(loader.load_unicode('static/js/src/formula_exercise_studio_edit.js'))
        fragment.initialize_js('StudioEditableXBlockMixin')
        return fragment
    


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
