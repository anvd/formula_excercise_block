/* Javascript for StudioEditableXBlockMixin. */
function StudioEditableXBlockMixin(runtime, xblockElement) {
    "use strict";
    
    var fields = [];
    var tinyMceAvailable = (typeof $.fn.tinymce !== 'undefined'); // Studio includes a copy of tinyMCE and its jQuery plugin
    var datepickerAvailable = (typeof $.fn.datepicker !== 'undefined'); // Studio includes datepicker jQuery plugin

    var csxColor = ["#009FE6", "black"];
    var studio_buttons = {
        "general_information-tab": "General information",
        "question_template-tab": "Template",
    };
    
    var question_template_textarea_element = $(xblockElement).find('textarea[name=question_template]');
    var variables_table_element = $(xblockElement).find('table[name=variables_table]');
    var expressions_table_element = $(xblockElement).find('table[name=expressions_table]');
    
    var error_message_element = $(xblockElement).find('div[name=error-message]');
    

   function fillErrorMessage(errorMessage) {
		error_message_element.empty();

		if (errorMessage != null) {
			var errorLabelNode = "<label class='validation_error'>" + errorMessage + "</label>";
			error_message_element.append(errorLabelNode);
		}
    }

    $(xblockElement).find('.field-data-control').each(function() {
        var $field = $(this);
        var $wrapper = $field.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');
        var type = $wrapper.data('cast');
        fields.push({
            name: $wrapper.data('field-name'),
            isSet: function() { return $wrapper.hasClass('is-set'); },
            hasEditor: function() { return tinyMceAvailable && $field.tinymce(); },
            val: function() {
                var val = $field.val();
                // Cast values to the appropriate type so that we send nice clean JSON over the wire:
                if (type == 'boolean')
                    return (val == 'true' || val == '1');
                if (type == "integer")
                    return parseInt(val, 10);
                if (type == "float")
                    return parseFloat(val);
                if (type == "generic" || type == "list" || type == "set") {
                    val = val.trim();
                    if (val === "")
                        val = null;
                    else
                        val = JSON.parse(val); // TODO: handle parse errors
                }
                return val;
            },
            removeEditor: function() {
                $field.tinymce().remove();
            }
        });
        var fieldChanged = function() {
            // Field value has been modified:
            $wrapper.addClass('is-set');
            $resetButton.removeClass('inactive').addClass('active');
        };
        
        $field.bind("change input paste", fieldChanged);
        $resetButton.click(function() {
            $field.val($wrapper.attr('data-default')); // Use attr instead of data to force treating the default value as a string
            $wrapper.removeClass('is-set');
            $resetButton.removeClass('active').addClass('inactive');
        });

        if (type == 'datepicker' && datepickerAvailable) { // TODO remove?
            $field.datepicker('destroy');
            $field.datepicker({dateFormat: "m/d/yy"});
        }
    });


    $(xblockElement).find('.wrapper-list-settings .list-set').each(function() {
        var $optionList = $(this);
        var $checkboxes = $(this).find('input');
        var $wrapper = $optionList.closest('li');
        var $resetButton = $wrapper.find('button.setting-clear');

        fields.push({
            name: $wrapper.data('field-name'),
            isSet: function() { return $wrapper.hasClass('is-set'); },
            hasEditor: function() { return false; },
            val: function() {
                var val = [];
                $checkboxes.each(function() {
                    if ($(this).is(':checked')) {
                        val.push(JSON.parse($(this).val()));
                    }
                });
                return val;
            }
        });
        var fieldChanged = function() {
            // Field value has been modified:
            $wrapper.addClass('is-set');
            $resetButton.removeClass('inactive').addClass('active');
        };
        $checkboxes.bind("change input", fieldChanged);

        $resetButton.click(function() {
            var defaults = JSON.parse($wrapper.attr('data-default'));
            $checkboxes.each(function() {
                var val = JSON.parse($(this).val());
                $(this).prop('checked', defaults.indexOf(val) > -1);
            });
            $wrapper.removeClass('is-set');
            $resetButton.removeClass('active').addClass('inactive');
        });
    });

    var studioSubmit = function(data) {
        var handlerUrl = runtime.handlerUrl(xblockElement, 'fe_submit_studio_edits');
        runtime.notify('save', {state: 'start', message: gettext("Saving")});
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(data),
            dataType: "json",
            global: false,  // Disable Studio's error handling that conflicts with studio's notify('save') and notify('cancel') :-/
            success: function(response) { runtime.notify('save', {state: 'end'}); }
        }).fail(function(jqXHR) {
            var message = gettext("This may be happening because of an error with our server or your internet connection. Try refreshing the page or making sure you are online.");
            if (jqXHR.responseText) { // Is there a more specific error message we can show?
                try {
                    message = JSON.parse(jqXHR.responseText).error;
                    if (typeof message === "object" && message.messages) {
                        // e.g. {"error": {"messages": [{"text": "Unknown user 'bob'!", "type": "error"}, ...]}} etc.
                        message = $.map(message.messages, function(msg) { return msg.text; }).join(", ");
                    }
                } catch (error) { message = jqXHR.responseText.substr(0, 300); }
            }
            runtime.notify('error', {title: gettext("Unable to update settings"), message: message});
        });
    };
    
    
    $(xblockElement).find('a[name=save_button]').bind('click', function(e) {
    	console.log("Save button clicked");
    	
    	error_message_element.empty();
    	
    	// "General information" tab
        e.preventDefault();
        var fieldValues = {};
        var fieldValuesNotSet = []; // List of field names that should be set to default values
        for (var i in fields) {
            var field = fields[i];
            if (field.isSet()) {
                fieldValues[field.name] = field.val();
            } else {
                fieldValuesNotSet.push(field.name);
            }
            // Remove TinyMCE instances to make sure jQuery does not try to access stale instances
            // when loading editor for another block:
            if (field.hasEditor()) {
                field.removeEditor();
            }
        }
        
        
        // "Template" tab
        /*
			1. question_template
			2. variables (name, min_valua, max_value, type, decimal_places)
			3. expressions
        */
        // 1. question_template_textarea_element
        var question_template = question_template_textarea_element.val();
        console.log('question_template: ' + question_template);
        
        // 2. variables_table_element
        var variables = {};
    	variables_table_element.find('tr').each(function(row_index) {
    		if (row_index > 0) { // first row is the header
    			var variable = {}
    			
    			var columns = $(this).find('td');
    			
    			// 2nd column: "variable name"
    			var variable_name = columns.eq(1).children().eq(0).val();

    			if (variable_name.length == 0) { // empty variable name
    				fillErrorMessage('Variable name can not be empty');
    				return false;
    			}
    			
    			if (variables.hasOwnProperty(variable_name)) { // duplicate verification
    				fillErrorMessage('Variable names can not be duplicated');
    				return false;
    			}
    			
    			variable['name'] = variable_name;

    			
    			// 3rd column: "min_value"
    			var min_value = columns.eq(2).children().eq(0).val();
    			
    			if (min_value.length == 0) { // empty min_value
    				fillErrorMessage('min_value can not be empty');
    				return false;
    			}
    			
    			variable['min_value'] = min_value;

    			
    			// 4th column: "max_value"
    			var max_value = columns.eq(3).children().eq(0).val();

    			if (max_value.length == 0) { // empty max_value
    				fillErrorMessage('max_value can not be empty');
    				return false;
    			}
    			
    			var min_value_numer = Number(min_value);
    			var max_value_number = Number(max_value);
    			if (min_value_numer > max_value_number) {
    				fillErrorMessage('min_value can not be bigger than max_value');
    				return false;
    			}
    			
    			variable['max_value'] = max_value;
    			

    			// 5th column: "type"
    			var type = columns.eq(4).children().eq(0).val();
    			variable['type'] = type;

    			
    			// 6th column: "decimal_places"
    			var decimal_places = columns.eq(5).children().eq(0).val();
    			variable['decimal_places'] = decimal_places;
    			
    			variables[variable_name] = variable;
    			console.log('Row ' + row_index + ': variable_name: ' + variable_name + ', min: ' + min_value + ', max: ' + max_value + ', type: ' + type + ', decimal_places: ' + decimal_places);
    		}
    	});
        
        // 3. expressions_table_element
        var expressions = {};
    	expressions_table_element.find('tr').each(function(row_index) {
    		if (row_index > 0) { // first row is the header
    			var expression = {};
    			
    			var columns = $(this).find('td');
    			
    			// 2nd column: "expression name"
    			var expression_name = columns.eq(1).children().eq(0).val();

    			if (expression_name.length == 0) { // empty expression name
    				fillErrorMessage('Expression name can not be empty');
    				return false;
    			}
    			
    			if (expressions.hasOwnProperty(expression_name)) { // duplicate verification
    				fillErrorMessage('Expression names can not be duplicated');
    				return false;
    			}

    			expression['name'] = expression_name;

    			
    			// 3rd column: "type"
    			var expression_type = columns.eq(2).children().eq(0).val();
    			expression['type'] = expression_type;
    			

    			// 4rd column: "formula"
    			var expression_formula = columns.eq(3).children().eq(0).val();
    			if (expression_formula.length == 0) { // empty expression name
    				fillErrorMessage('Expression formula can not be empty');
    				return false;
    			}
    			// TODO (server side) cexprtk parsable formula/expression
    			expression['formula'] = expression_formula;
    			

    			// 5th column: "decimal_places"
    			var expression_decimal_places = columns.eq(4).children().eq(0).val();
    			expression['decimal_places'] = expression_decimal_places;
    			
    			
    			expressions[expression_name] = expression;
    			
    			console.log('Row ' + row_index + ': expression_name: ' + expression_name + ', type: ' + expression_type + ', formula: '+ expression_formula + ', decimal_places: ' + expression_decimal_places);
    		}
    	});
        
        // client-side validation error
        if (error_message_element.children().length > 0) { 
        	return;
        }
        
        // server side validation
        debugger;
        var server_side_validation_url = runtime.handlerUrl(xblockElement, 'validate_expressions');
        $.post(server_side_validation_url, JSON.stringify(expressions)).success(function(validationResult) {
	    	debugger;
	    	if (Object.keys(validationResult).length > 0) { // error
	    		var errMsg = 'The following expressions can not be parsed: '
	    		for (var expression_name in validationResult) { errMsg += "[ " + (expression_name + ": " + validationResult[expression_name] + " ], "); }
	    		fillErrorMessage(errMsg);
	    	} else { // no error
	    		studioSubmit({values: fieldValues, defaults: fieldValuesNotSet, question_template: question_template, variables: variables, expressions: expressions});
	    	}
        });
    });


    $(xblockElement).find('.cancel-button').bind('click', function(e) {
        // Remove TinyMCE instances to make sure jQuery does not try to access stale instances
        // when loading editor for another block:
        for (var i in fields) {
            var field = fields[i];
            if (field.hasEditor()) {
                field.removeEditor();
            }
        }
        e.preventDefault();
        runtime.notify('cancel', {});
    });
    
    
    $(xblockElement).find('a[name=add_variable_button]').bind('click', function(e) {
    	// console.log("Add VARIABLE button clicked");
    	
    	
    	var new_row = $('<tr></tr>');
    	new_row.attr("class", "formula_edit_table_row");
    	
    	 // first column (empty space)
    	var first_column = $('<td></td>');
    	new_row.append(first_column);
    	
    	
    	// second column: variable name
    	var second_column = $('<td></td>');
    	second_column.attr("class", "table_cell_alignment");
    	
    	var variable_name_element = $('<input />');
    	variable_name_element.attr("type", "text");
    	variable_name_element.attr("class", "formula_input_text");
    	variable_name_element.attr("value", "");
    	second_column.append(variable_name_element);
    	new_row.append(second_column);
    	

    	// third column: min value
    	var third_column  = $('<td></td>');
    	third_column.attr("class", "table_cell_alignment number_input_cell");
    	
    	var variable_min_value_element = $('<input />');
    	variable_min_value_element.attr("type", "number");
    	variable_min_value_element.attr("class", "formula_input_text");
    	variable_min_value_element.attr("value", "1");
    	third_column.append(variable_min_value_element);
    	new_row.append(third_column);

    	
    	// fourth column: max value
    	var fourth_column  = $('<td></td>');
    	fourth_column.attr("class", "table_cell_alignment number_input_cell");
    	
    	var variable_max_value_element = $('<input />');
    	variable_max_value_element.attr("type", "number");
    	variable_max_value_element.attr("class", "formula_input_text");
    	variable_max_value_element.attr("value", "10");
    	fourth_column.append(variable_max_value_element);
    	new_row.append(fourth_column);

    	
    	// fifth column: type
    	var fifth_column  = $('<td></td>');
    	fifth_column.attr("class", "table_cell_alignment");
    	
    	var variable_type_element = $('<select></select>');
    	variable_type_element.attr("class", "formula_input_text");
    	
    	var int_option_element = $("<option></option>");
    	int_option_element.attr("value", "int");
    	int_option_element.text("int");
    	int_option_element.attr("selected", "selected");
    	variable_type_element.append(int_option_element);
    	
    	var float_option_element = $("<option></option>");
    	float_option_element.attr("value", "float");
    	float_option_element.text("float");
    	variable_type_element.append(float_option_element);
    	
    	fifth_column.append(variable_type_element);
    	new_row.append(fifth_column);

    	
    	// sixth column: decimal_places
    	var sixth_column  = $('<td></td>');
    	sixth_column.attr("class", "table_cell_alignment number_input_cell");
    	
    	var variable_decimal_places_element = $('<input>');
    	variable_decimal_places_element.attr("type", "number");
    	variable_decimal_places_element.attr("min", "0");
    	variable_decimal_places_element.attr("max", "7");
    	variable_decimal_places_element.attr("class", "formula_input_text");
    	variable_decimal_places_element.attr("value", "0");
    	sixth_column.append(variable_decimal_places_element);
    	new_row.append(sixth_column);


    	// seventh column: Remove button
    	var seventh_column  = $('<td></td>');
    	seventh_column.attr("class", "table_cell_alignment");

    	var remove_variable_button = $('<input>');
    	remove_variable_button.attr("type", "button");
    	remove_variable_button.attr("class", "remove_button");
    	remove_variable_button.attr("value", "Remove");
    	seventh_column.append(remove_variable_button);
    	new_row.append(seventh_column);
    	
    	// add event handler
    	remove_variable_button.click(function() {
    		new_row.remove();
    		// console.log("REMOVE BUTTON CLICKED");
    	});

    	
    	// eighth column: empty column
    	var eighth_column  = $('<td></td>');
    	new_row.append(eighth_column);
    	
    	
    	// append the new row to variables table
    	variables_table_element.append(new_row);
    });


    
    $(xblockElement).find('a[name=add_expression_button]').bind('click', function(e) {
    
    	// console.log("Add EXPRESSIOn button clicked");
    	
    	var new_row = $('<tr></tr>');
    	new_row.attr("class", "formula_edit_table_row");
    	
    	 // first column
    	var first_column = $('<td></td>');
    	new_row.append(first_column);
    	
    	
    	// second column: name
    	var second_column = $('<td></td>');
    	second_column.attr("class", "table_cell_alignment");
    	
    	var expression_name_element = $('<input />');
    	expression_name_element.attr("type", "text");
    	expression_name_element.attr("class", "formula_input_text");
    	expression_name_element.attr("value", "");
    	second_column.append(expression_name_element);
    	new_row.append(second_column);
    	

    	// third column: expression
    	var third_column  = $('<td></td>');
    	third_column.attr("class", "table_cell_alignment");
    	
    	var expression_type_element = $('<select></select>');
    	expression_type_element.attr("class", "formula_input_text");
    	
    	var int_option_element = $("<option></option>");
    	int_option_element.attr("value", "int");
    	int_option_element.text("int");
    	int_option_element.attr("selected", "selected");
    	expression_type_element.append(int_option_element);
    	
    	var float_option_element = $("<option></option>");
    	float_option_element.attr("value", "float");
    	float_option_element.text("float");
    	expression_type_element.append(float_option_element);
    	
    	third_column.append(expression_type_element);
    	new_row.append(third_column);
    	
    	
    	// fourth column: formula
    	var fourth_column  = $('<td></td>');
    	fourth_column.attr("class", "table_cell_alignment");
    	
    	var expression_formula_element = $('<input />');
    	expression_formula_element.attr("type", "text");
    	expression_formula_element.attr("class", "formula_input_text");
    	expression_formula_element.attr("value", "");
    	fourth_column.append(expression_formula_element);
    	new_row.append(fourth_column);
    	
    	
    	// fifth column: decimal_places
    	var fifth_column  = $('<td></td>');
    	fifth_column.attr("class", "table_cell_alignment number_input_cell");
    	
    	var expression_decimal_places_element = $('<input />');
    	expression_decimal_places_element.attr("type", "number");
    	expression_decimal_places_element.attr("min", "0");
    	expression_decimal_places_element.attr("max", "7");
    	expression_decimal_places_element.attr("class", "formula_input_text");
    	expression_decimal_places_element.attr("value", "0");
    	fifth_column.append(expression_decimal_places_element);
    	new_row.append(fifth_column);


    	// sixth column: Remove button 
    	var sixth_column  = $('<td></td>');
    	sixth_column.attr("class", "table_cell_alignment");

    	var remove_expression_button = $('<input />');
    	remove_expression_button.attr("type", "button");
    	remove_expression_button.attr("class", "remove_button");
    	remove_expression_button.attr("value", "Remove");
    	sixth_column.append(remove_expression_button);
    	new_row.append(sixth_column);
    	
    	// add event handler
    	remove_expression_button.click(function() {
    		new_row.remove();
    		// console.log("REMOVE BUTTON CLICKED");
    	});

    	
    	// seventh column
    	var seventh_column  = $('<td></td>');
    	new_row.append(seventh_column);
    	
    	
    	// append the new row to variables table
    	expressions_table_element.append(new_row);
    });


    function tab_highlight(toHighlight) {
        for (var b in studio_buttons) {
            if (b != toHighlight) $("a[id=" + b + "]").css({"color": csxColor[0]});
        }
        $("a[id=" + toHighlight + "]").css({"color": csxColor[1]});
    }
    
    
    function update_buttons(toShow) {
    	if (toShow == 'general_information-tab') {
    		// hide "Add variable" and "Add expression" buttons
    		$("li[name=add_variable]").hide()
    		$("li[name=add_expression]").hide()
    	} else {
    		// show "Add variable" and "Add expression" buttons
    		$("li[name=add_variable]").show()
    		$("li[name=add_expression]").show()
    	}
    }


    // Hide all panes except toShow
    function tab_switch(toShow) {
        tab_highlight(toShow);
        for (var b in studio_buttons) $("div[name=" + b + "]").hide();
        $("div[name=" + toShow + "]").show();
        
        update_buttons(toShow);
    }


    $(function($) {
        for (var b in studio_buttons) {
            $('.editor-modes')
                .append(
                    $('<li>', {class: "action-item"}).append(
                        $('<a />', {class: "action-primary", id: b, text: studio_buttons[b]})
                    )
                );
        }

        // Set main pane to "General information"
        tab_switch("general_information-tab");
    
        $('#general_information-tab').click(function() {
            tab_switch("general_information-tab");
        });

        $('#question_template-tab').click(function() {
            tab_switch("question_template-tab");
        });
        
        
        // listeners for "Remove" buttons of "Variables"
        variables_table_element.find('input[type=button][class=remove_button]').bind('click', function(e) {
        	var removeButton = $(this);
        	var parentRow = removeButton.closest('tr');
        	parentRow.remove();
        });
        
        
        // listeners for "Remove" buttons of Expressions"
        expressions_table_element.find('input[type=button][class=remove_button]').bind('click', function(e) {
        	var removeButton = $(this);
        	var parentRow = removeButton.closest('tr');
        	parentRow.remove();
        });
    });
}
