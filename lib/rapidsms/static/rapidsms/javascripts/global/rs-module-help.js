// vim: noet

jQuery(function() {

	/* hide the help text for each module that contains
	 * it, and add a "show help" button to the toolbar */
	jQuery(".module div.help").each(function() {
		var help_box = jQuery(this);
		help_box.hide();

		var module = help_box.parent(".module");
		var toolbar = jQuery("div.toolbar", module);

		/* create a toolbar, if this module
		 * does not already have one */
		if(!toolbar.length) {
			toolbar = jQuery('<div class="toolbar"></div>')
			module.append(toolbar);
		}

		/* add a tool button to show
		 * the div that we just hid */
		toolbar.append(
			jQuery('<span class="help">Show Help</span>').click(function(ev) {
				help_box.slideToggle();
			})
		);
	})
});
