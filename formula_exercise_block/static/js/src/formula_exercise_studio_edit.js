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
    
    var question_template_list_element = $(xblockElement).find('ul[name=question_template_list]');
    var variables_table_element = $(xblockElement).find('table[name=variables_table]');
    var expressions_table_element = $(xblockElement).find('table[name=expressions_table]');
    var question_template_textarea_element = $(xblockElement).find('textarea[name=question_template]');
    var variables_table_element = $(xblockElement).find('table[name=variables_table]');
    var expressions_table_element = $(xblockElement).find('table[name=expressions_table]');

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
        var handlerUrl = runtime.handlerUrl(xblockElement, 'submit_studio_edits');
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
    	
    	
    	// "General information" tab
        e.preventDefault();
        var values = {};
        var notSet = []; // List of field names that should be set to default values
        for (var i in fields) {
            var field = fields[i];
            if (field.isSet()) {
                values[field.name] = field.val();
            } else {
                notSet.push(field.name);
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
			2. variables (name, min_valua, max_value, type, accuracy)
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
    			
    			// 1st column: "variable name"
    			var variable_name = columns.eq(1).children().eq(0).val();
    			variable['name'] = variable_name;
    			
    			// 3rd column: "min_value"
    			var min_value = columns.eq(3).children().eq(0).val();
    			variable['min_value'] = min_value;
    			
    			// 4st column: "max_value"
    			var max_value = columns.eq(4).children().eq(0).val();
    			variable['max_value'] = max_value;
    			
    			// 5st column: "type"
    			var type = columns.eq(5).children().eq(0).val();
    			variable['type'] = type;
    			
    			// 6st column: "accuracy"
    			var accuracy = columns.eq(6).children().eq(0).val();
    			variable['accuracy'] = accuracy;
    			
    			variables[variable_name] = variable;
    			console.log('Row ' + row_index + ': variable_name: ' + variable_name + ', min: ' + min_value + ', max: ' + max_value + ', type: ' + type + ', accuracy: ' + accuracy);
    		}
    	});
        
        // 3. expressions_table_element
        var expressions = {};
    	expressions_table_element.find('tr').each(function(row_index) {
    		if (row_index > 0) { // first row is the header
    			var expression = {};
    			
    			var columns = $(this).find('td');
    			
    			// 1st column: "variable name"
    			var expression_name = columns.eq(1).children().eq(0).val();
    			expression['name'] = expression_name;
    			
    			// 3rd column: "formula"
    			var expression_formula = columns.eq(3).children().eq(0).val();
    			expression['formula'] = expression_formula;
    			
    			// 4th column: "accuracy"
    			var expression_accuracy = columns.eq(4).children().eq(0).val();
    			expression['accuracy'] = expression_accuracy;
    			
    			
    			expressions[expression_name] = expression;
    			
    			console.log('Row ' + row_index + ': expression_name: ' + expression_name + ', formula: '+ expression_formula + ', accuracy: ' + expression_accuracy);
    		}
    	});
        
        
        studioSubmit({values: values, defaults: notSet, question_template: question_template, variables: variables, expressions: expressions});
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
    	
    	 // first column
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
    	

    	// third column
    	var third_column  = $('<td></td>');
    	new_row.append(third_column);
    	
    	
    	// fourth column: min value
    	var fourth_column  = $('<td></td>');
    	fourth_column.attr("class", "table_cell_alignment");
    	
    	var variable_min_value_element = $('<input />');
    	variable_min_value_element.attr("type", "text");
    	variable_min_value_element.attr("class", "formula_input_text");
    	variable_min_value_element.attr("value", "");
    	fourth_column.append(variable_min_value_element);
    	new_row.append(fourth_column);

    	
    	// fifth column: max value
    	var fifth_column  = $('<td></td>');
    	fifth_column.attr("class", "table_cell_alignment");
    	
    	var variable_max_value_element = $('<input />');
    	variable_max_value_element.attr("type", "text");
    	variable_max_value_element.attr("class", "formula_input_text");
    	variable_max_value_element.attr("value", "");
    	fifth_column.append(variable_max_value_element);
    	new_row.append(fifth_column);

    	
    	// sixth column: type
    	var sixth_column  = $('<td></td>');
    	sixth_column.attr("class", "table_cell_alignment");
    	
    	var variable_type_element = $('<input />');
    	variable_type_element.attr("type", "text");
    	variable_type_element.attr("class", "formula_input_text");
    	variable_type_element.attr("value", "");
    	sixth_column.append(variable_type_element);
    	new_row.append(sixth_column);

    	
    	// seventh column: accuracy
    	var seventh_column  = $('<td></td>');
    	seventh_column.attr("class", "table_cell_alignment");
    	
    	var variable_accuracy_element = $('<input />');
    	variable_accuracy_element.attr("type", "text");
    	variable_accuracy_element.attr("class", "formula_input_text");
    	variable_accuracy_element.attr("value", "");
    	seventh_column.append(variable_accuracy_element);
    	new_row.append(seventh_column);


    	// eigth column: Remove button
    	var eigth_column  = $('<td></td>');
    	eigth_column.attr("class", "table_cell_alignment");

    	var remove_variable_button = $('<input />');
    	remove_variable_button.attr("type", "button");
    	remove_variable_button.attr("class", "formula_edit_button");
    	remove_variable_button.attr("value", "Remove");
    	eigth_column.append(remove_variable_button);
    	new_row.append(eigth_column);
    	
    	// add event handler
    	remove_variable_button.click(function() {
    		new_row.remove();
    		// console.log("REMOVE BUTTON CLICKED");
    	});

    	
    	// nineth column
    	var nineth_column  = $('<td></td>');
    	new_row.append(nineth_column);
    	
    	
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
    	

    	// third column
    	var third_column  = $('<td></td>');
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
    	
    	
    	// fifth column: accuracy
    	var fifth_column  = $('<td></td>');
    	fifth_column.attr("class", "table_cell_alignment");
    	
    	var expression_accuracy_element = $('<input />');
    	expression_accuracy_element.attr("type", "text");
    	expression_accuracy_element.attr("class", "formula_input_text");
    	expression_accuracy_element.attr("value", "");
    	fifth_column.append(expression_accuracy_element);
    	new_row.append(fifth_column);


    	// sixth column: Remove button 
    	var sixth_column  = $('<td></td>');
    	sixth_column.attr("class", "table_cell_alignment");

    	var remove_expression_button = $('<input />');
    	remove_expression_button.attr("type", "button");
    	remove_expression_button.attr("class", "formula_edit_button");
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
    });
    
}
