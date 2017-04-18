/* Javascript for FormulaExerciseXBlock. */
function FormulaExerciseXBlock(runtime, xblockElement) {
	"use strict";

	var student_view_expressions_table_element = $(xblockElement).find('table[name=student_view_expressions_table]');

  		
	var hidden_question_template_element = $(xblockElement).find('input[name=question_template]');
	var hidden_variables_element = $(xblockElement).find('input[name=variables]');
	var hidden_expressions_element = $(xblockElement).find('input[name=expressions]');
	var hidden_generated_variables_element = $(xblockElement).find('input[name=generated_variables]');
	var hidden_generated_question_element = $(xblockElement).find('input[name=generated_question]');
    var xblock_id = $(xblockElement).find('input[name=xblock_id]').val();
    
    var answer_div_element = $(xblockElement).find('div[name=answer]');
    var show_answer_button = $(xblockElement).find('input[name=show_answer-button]');


	function handleSubmissionResult(results) {
		console.log('handleSubmissionResult INVOKED');
    	$(xblockElement).find('div[name=attempt-number]').text(results['attempt_number']);
    	$(xblockElement).find('div[name=problem-progress]').text(results['point_string']);
    	if (results['submit_disabled'] == 'disabled') {
    		$(xblockElement).find('input[name=submit-button]').attr('disabled','disabled');
    	}
  	}
  	

  	function handleShowAnswerResult(result) {
  		console.log('handleShowAnswerResult INVOKED');
  	
  		// add "pre" element
  		var pre_element = $('<pre></pre>');
  		pre_element.text('Answer:');
  		answer_div_element.append(pre_element);
  		
  		// add "table" element
  		var table_element = $('<table></table>');
  		table_element.attr("name", "answer_table");
  		table_element.attr("class", "fe_student_expressions_table");
  		answer_div_element.append(table_element);
  		
  		// build table rows
  		var expression_values = result['expression_values'];
  		for (var expr_name in expression_values) {
  			var row_element = $('<tr></tr>');
  			table_element.append(row_element);
  			
  			
  			// first column (empty)
  			var first_col = $('<td></td>');
  			first_col.attr('width', '10%');
  			row_element.append(first_col);
  			
  			
  			// second column (expression name)
  			var second_col = $('<td></td>');
  			second_col.attr('width', '15%');
  			second_col.attr('class', 'table_cell_alignment');
  			row_element.append(second_col);
  			
  			var expr_name_label = $('<label></label>');
  			expr_name_label.attr('class', 'label setting-label expression_name_alignment');
  			expr_name_label.text(expr_name);
  			second_col.append(expr_name_label);
  			
  			
  			// third column (empty)
  			var third_col = $('<td></td>');
  			third_col.attr('width', '5%');
  			row_element.append(third_col);
  			
  			
  			// fourth column (expression value)
  			var fourth_col = $('<td></td>');
  			fourth_col.attr('width', '40%');
  			fourth_col.attr('class', 'table_cell_alignment');
  			row_element.append(fourth_col);
  			
  			// expression value label
  			var expr_value_label = $('<label></label>');
  			expr_value_label.attr('class', 'label setting-label expression_value_alignment');  			
  			expr_value_label.text(expression_values[expr_name]);
  			fourth_col.append(expr_value_label);
  			
  			
  			// fifth column (empty)
  			var fifth_col = $('<td></td>');
  			fifth_col.attr('width', '30%');
  			row_element.append(fifth_col);
  		}
  		
  		show_answer_button.attr('disabled', 'disabled');
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
    	console.log("formula_exercise_block initialized");
    	if (show_answer_button != null) {
    		show_answer_button.bind('click', function() {
    			console.log("show_answer_button CLICKED");
    			
    			// prepare data
    			var data = {
      				'saved_question_template': hidden_question_template_element.val(),
		      		'serialized_variables': hidden_variables_element.val(),
		      		'serialized_expressions': hidden_expressions_element.val(),
		      		'serialized_generated_variables': hidden_generated_variables_element.val()
    			}
    			
    			var handlerUrl = runtime.handlerUrl(xblockElement, 'show_answer_handler');
    			$.post(handlerUrl, JSON.stringify(data)).success(handleShowAnswerResult);
    		});
    	}
    });
  	
}
