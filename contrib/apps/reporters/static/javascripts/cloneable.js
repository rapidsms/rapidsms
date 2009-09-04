jQuery.fn.cloneable = function(noun, clear_form_elements) {
	
	/* */
	if (noun == undefined)
		noun = "item";
	
	/* as default, clear form elements when cloning,
	 * since it's rare that'd you'd want to keep them */
	if (clear_form_elements == undefined)
		clear_form_elements = true;
	
	this.each(function() {
		
		/* create an "add" button, which duplicate the clonable (we're assuming
		 * that it is the direct parent, for now...), clear the form elements
		 * within it, and append it as a sibling */
		var ah = '<input type="button" class="js-add" value="Add" title="Add another ' + noun + '" />';
		var add = jQuery(ah).click(function() {
		
			/* duplicate the parent node, which
			 * is (or should be) the clonable */
			var p = jQuery(this).parent();
			var c = p.clone(true);
			
			/* maybe clear the form */
			if(clear_form_elements)
				c.clearFormElements();
			
			/* our brand new clonable is
			 * ready to insert into the dom */
			p.after(c);
		});
	
	
		/* also create a "delete" button, which is a
		 * lot simpler. it just destroys it's parent */
		var dh = '<input type="button" class="js-del" value="Remove" title="Remove this ' + noun + '" />';
		var del = jQuery(dh).click(function() {
			$(this).parent().remove();
		});
	
		/* inject the ADD and REMOVE
		 * buttons into this clonable */
		jQuery(this).append(add, " ", del);
	});
	
	 /* all plugins must return
	  * jQuery, to allow chaining */
	 return jQuery;
};
