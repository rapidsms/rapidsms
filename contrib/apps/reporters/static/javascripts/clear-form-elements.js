jQuery.fn.clearFormElements = function() {
	this.each(function() {
		
		/* iterate over all elements within the context, and
		 * clear the value of any form element. note that this
		 * does not act with the FORM, just the CONTEXT, making
		 * it possible to clear a part of a form, or multiple
		 * forms at once, by calling it on a parent element */
		jQuery("*", this).each(function() {
			switch (this.type) {
				case "password":
				case "textarea":
				case "text":
					this.value = "";
					break;
			
				case "select-multiple":
				case "select-one":
					this.selectedIndex = -1;
					break;
				
				case "radio":
				case "checkbox":
					this.checked = false;
					break;
			}
		});
	});
	
	 /* all plugins must return
	  * jQuery, to allow chaining */
	 return jQuery;
};
