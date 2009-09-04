/* UNICEF RapidSMS UI
 * vim:set noet:
 * --
 * training/global.js
 * --
 * Since error messages are trapped while the training app is running, callers
 * receive no feedback until someone has dealt with them. this script polls the
 * server every 30 seconds to notify WebUI users that they need to pay attention */

$(function() {
	var tab = $("#tabs li.app-training");
	var link = $("a", tab);
	
	
	/* if there's no TRAINING tab (how
	 * did that happen?), do nothing */
	if(!tab.length)
		return;
	
	
	/* a global function (WTF). to  update
	 * the tab, since app.js needs it also. */
	window["update_training_tab"] = function(num) {
		
		/* add the number of outstanding messages to
		 * the tab tooltip, and add a fancy little icon */
		if(num > 0) {
			link.attr("title", num + " messages pending");
			tab.addClass("unread");

		} else {
			/* no pending messages, so reset the tooltip and
			 * class of the tab (in case there _were_ messages,
			 * but they were cleared by someone else) */
			tab.removeClass("unread");
			link.attr("title", "");
		}
	};
	
	
	/* if we're currently viewing the training
	 * page, app.js will take care of this live */
	if(tab.hasClass("active"))
		return;
	
	
	var check = function() {
		$.getJSON("/ajax/training/pending_count", function(data) {
			window["update_training_tab"](data);
		});

		/* check again in 30 seconds */
		timeout = setTimeout(check, 30000);
	};
	
	
	/* start polling */
	check();
});
