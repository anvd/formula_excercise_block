/* Javascript for FormulaExerciseXBlock. */
function FormulaExerciseXBlock(runtime, xblockElement) {

	function handleSubmissionResult(results) {
	
		// debugger;
		// var errorMessage = results['error'];
		// var errorSectionElement = $(xblockElement).find('div[name=errorSection]');
		
		// errorSectionElement.empty();
		// if (errorMessage != null) {
			
			// var errorLabelNode = "<label class='submit-error'>" + errorMessage + "</label>";
			// errorSectionElement.append(errorLabelNode);
		//}
	
    	$(xblockElement).find('.problem-progress').html(results['points_earned'] + ' / ' + results['points_possible'] + ' points');
  	}


  	$(xblockElement).find('input[name=submit-button]').bind('click', function() {
    	var data = {
      		"energy": $(xblockElement).find('input[id=energy]').val()
    	};
    
    	var handlerUrl = runtime.handlerUrl(xblockElement, 'student_submit');
    	$.post(handlerUrl, JSON.stringify(data)).success(handleSubmissionResult);
  	});
  	
  	
}
