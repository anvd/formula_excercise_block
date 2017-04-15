/* Javascript for FormulaExerciseXBlock. */
function FormulaExerciseXBlock(runtime, xblockElement) {

	var student_view_expressions_table_element = $(xblockElement).find('table[name=student_view_expressions_table]');

  		
	var hidden_question_template_element = $(xblockElement).find('input[name=question_template]');
	var hidden_variables_element = $(xblockElement).find('input[name=variables]');
	var hidden_expressions_element = $(xblockElement).find('input[name=expressions]');
	var hidden_generated_variables_element = $(xblockElement).find('input[name=generated_variables]');
	var hidden_generated_question_element = $(xblockElement).find('input[name=generated_question]');
    var xblock_id = $(xblockElement).find('input[name=xblock_id]').val();


	function handleSubmissionResult(results) {
    	$(xblockElement).find('.problem-progress').html(results['point_string']);
    	if (results['submit_disabled'] == 'disabled') {
    		$(xblockElement).find('input[name=submit-button]').attr('disabled','disabled')
    	}
  	}


  	$(xblockElement).find('input[name=submit-button]').bind('click', function() {
		// accumulate expression values for submission  		
        var submitted_expression_values = {};
    	student_view_expressions_table_element.find('tr').each(function(row_index) {
			var columns = $(this).find('td');
			
			var name = columns.eq(1).children().eq(0).text(); // 1st column: "expression name"
			var value = columns.eq(3).children().eq(0).val(); // 3rd column: "expression value"
			submitted_expression_values[name] = value;
			
			console.log('Row ' + row_index + ': expression_name: ' + name + ', value: ' + value);
    	});
    	
    	var data = {
      		'submitted_expression_values': JSON.stringify(submitted_expression_values),
      		'saved_question_template': hidden_question_template_element.val(),
      		'serialized_variables': hidden_variables_element.val(),
      		'serialized_expressions': hidden_expressions_element.val(),
      		'serialized_generated_variables': hidden_generated_variables_element.val(),
      		'saved_generated_question': hidden_generated_question_element.val()
    	};
    	
    	
    	console.log('submitted_expression_values: ' + data['submitted_expression_values'])
    	console.log('saved_question_template: ' + data['saved_question_template'])
    	console.log('serialized_variables: ' + data['saved_variables'])
    	console.log('serialized_expressions: ' + data['saved_expressions'])
    	console.log('serialized_generated_variables: ' + data['saved_generated_variables'])
    	console.log('saved_generated_question: ' + data['saved_generated_question'])
    	
    
    	var handlerUrl = runtime.handlerUrl(xblockElement, 'student_submit');
    	$.post(handlerUrl, JSON.stringify(data)).success(handleSubmissionResult);
  	});
  	
  	
    $(function($) {
		$.event.special.destroyed = {
			remove: function(o) {
				if (o.handler) { o.handler(); }
			}
		}
    });
  	
}
