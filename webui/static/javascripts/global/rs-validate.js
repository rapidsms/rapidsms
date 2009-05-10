(function() {
	var defaults = {
		"showErrors": function(errors_map, errors_list) {
			this.defaultShowErrors();
	
			/* after showing the error labels, wrap the message
			 * with a span, which we can use as a CSS hook */
			jQuery(this.currentForm)
				.find("label.error:not(:has(span))")
				.wrapInner('<span></span>');
		},

		/* place the error labels before, (the
		 * default is AFTER), the invalid field */
		"errorPlacement": function(error, invalid_field) {
			invalid_field.after(error);
			var pos = invalid_field.position();
	
			/* HACK: absolutely position the error label, to
			 * line up with the right-hand side of the field */
			error.css({
				"position": "absolute",
				"line-height": invalid_field.outerHeight() + "px",
				"left": pos["left"] + invalid_field.outerWidth(),
				"top": pos["top"]
			});
		},

		/* in addition to creating the error label
		 * (which is done by jQ validation), add a
		 * class to the invalid element's label */
		"highlight": function(invalid_field) {
			var sel = "label[for=" + invalid_field.id + "]";
			jQuery(invalid_field.form).find(sel).addClass("invalid");
			jQuery(invalid_field).parent().addClass("invalid");
		},

		/* remove the INVALID class from
		 * the newly-valid element's label */
		"unhighlight": function(valid_field) {
			var sel = "label[for=" + valid_field.id + "]";
			jQuery(valid_field.form).find(sel).removeClass("invalid");
			jQuery(valid_field).parent().removeClass("invalid");
		},

		/* in addition to the validator's usual behavior, create a notification
		 * box just above the submit buttons, to inform the user that there was
		 * a problem -- if the error labels are offscreen, or far away from the
		 * click, it's easy to miss them, which is confusing as hell */
		"invalidHandler": function(ev, validator) {
			var form = jQuery(ev.target);
			var submit = form.find(".submit");
			var errors = submit.find(".errors");
			var n = validator.numberOfInvalids();
	
			/* if this is the first time we've displayed
			 * errors for this form, there will be nowhere
			 * to put the summary - so create one! */
			if(errors.length == 0) {
				submit.prepend('<div class="errors"></div>');
				errors = submit.find(".errors");
			}
	
			/* if there are any errors to display (this function
			 * is called even when there are none), add a summary
			 * to the errors container, and slide it into view */
			if(n > 0) {
				var txt = (n > 1) ?
					"There were " + n + " problem(s) with your submission.<br>Please fix them and try again." :
					"There was 1 problem with your submission.<br>Please fix it and try again.";
				errors.html("<p>" + txt + "</p>").show();
		
			/* no errors, so hide the errors
			 * container while submitting */
			} else { errors.hide(); }
		},

		/* when the field is no longer invalid, remove the error label,
		* to avoid leaving an empty element (not sure why the jQ plugin
		* already doesn't do this - it just clears the text) */
		"success": function(error_label) {
			error_label.remove();
		}
	};
	
	jQuery.fn.rs_validate = function(options) {
		if(options == undefined) options = {}
		this.validate(jQuery.merge(defaults, options));
	};
})();
