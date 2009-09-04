/* UNICEF RapidSMS UI
 * vim:set noet:
 * --
 * training/app.js
 * --
 * This file polls the server for incoming messages which
 * caused errors (via the AJAX app), and displays them in
 * the WebUI until responded to. Responses are POSTed back
 * to the server, to be dispatched by RapidSMS. */


$(function() {
		
	/* everything that we're touching happens
	 * inside the container. maybe we can make
	 * this whole thing a template tag later! */
	var container = $("div.training tbody");
	if(!container) return False;
	
	/* grab this app's tab, so we can keep it
	 * updated with the number of messages */
	var tab = $("#tabs li.app-training");
	var link = $("a", tab);
	
	/* store the current document title, so we can
	 * add the number of pending messages later */
	var doc_title = document.title;
	
	/* keep all update-related timeouts here,
	 * to be sure that we update in serial */
	var timeout = null;
	
	/* extract the primary key back out of the
	 * row class by dropping all non-numerics */
	var get_pk = function(row) {
		return Number(row.className.replace(/\D/g, ""));
	};
	
	
	/* EVENT HANDLERS */
	var accept_click = function(ev) {
		var row = $(ev.target).parents("tr");
		var pk = get_pk(row[0]);
		
		/* build an array of the values entered
		 * in each <input> within the row, which
		 * will be sent back to the Reporter */
		var responses = $.map(
			$("input[type=text]", row),
			function(input) {
				return input.value;
			}
		);
		
		/* POST the responses back to the method:
		 * apps.training.app.App.ajax_POST_accept */ 
		$.ajax({
			"type": "POST",
			"url":  "/ajax/training/accept",
			"data": {
				"msg_pk": pk,
				"responses": responses
			},
			"success": function() {
				
				/* cancel any pending updates (so we don't accidentally
				 * start two polling updates in parallel!), and update now,
				 * which _should_ cause the updated message to be removed */
				clearTimeout(timeout);
				update();
			}
		});
	};
	
	var add_click = function(ev) {
		$(ev.target).parent().prev().append(
			$('<input type="text" class="added response" value="" maxlength="140">')
		);
	};
	
	container.keyup(function(ev) {
		if($(ev.target).is("input.response")) {
		
			/* we're only interested in ctrl+[1-9] */
			if(ev.ctrlKey) {
				var w = ev.which;
				if((w >= 49) && (w <= 57)) {
				
					/* insert the current value of the
					 * numbered response template field */
					var val = $("#tmpl-" + String.fromCharCode(w))[0].value;
					if(val != "") ev.target.value = val;
					return true;
				}
			}
			
			if($(ev.target).hasClass("added") && ev.target.value == "")
				$(ev.target).remove();
		}
	});
	
	var update = function() {
		$.getJSON("/ajax/training/pending", function(data) {
			$.each(data, function() {
				
				/* if this message has not already been seen, and a row
				 * has not been created (by trying to find it with a jQ
				 * selector), we will create one now... */
				var klass = ("m-" + this["pk"]);
				if($('tr.' + klass, container).length == 0) {
					
					/* create a text field for each response to
					 * this message, o be embedded in the row */
					var responses = $("<td></td>");
					$.each(this["responses"], function() {
						responses.append(
								$('<input type="text" class="response" value="' + this["text"] + '" maxlength="140">')
						);
					});
					
					var sender = $("<td></td>");
					if(this["reporter"]) {
						sender.append(
							$('<a href="/reporters/' + this["reporter"]["pk"] + '"></a>')
								.text(this["reporter"]["str"])
						)
					} else {
						sender.text(this["connection"]["str"]);
					}
					
					/* create an ACCEPT button with the appropriate click handler,
					 * to post the modified responses back to the training App */
					var acc = $('<input type="button" class="js-accept" value="Accept" title="Accept these responses">').click(accept_click);
					var add = $('<input type="button" class="js-add" value="Add" title="Add a response">').click(add_click);
					
					/* build the row for this message, including
					 * the dynamic stuff we just build, and inject
					 * it into the dom */
					container.append(
						$('<tr class="msg ' + klass + '"></tr>').append(
							sender,
							$("<td></td>").append(
								$("<div></div>").append(
									this["text"])),
							responses,
							$('<td class="actions"></td>').append(add, acc)
						)
					);
				} // if
			}); // each
			
			/* iterate all of the visible fields, and remove
			 * any that are no longer pending (they may have
			 * been removed by THIS user, or some other) */
			var data_ids = $.map(data, function(d) { return d["pk"] });
			$("tr.msg", container).each(function() {
				
				/* if this row is no longer pending, remove it! */
				if($.inArray(get_pk(this), data_ids) == -1)
					$(this).remove();
			});
			
			/* update the visibility of the "there are no
			 * items!", because the items may have changed */
			var waiting = $("tr.msg", container).length;
			$("tr.no-data", container).css(
				"display", ((waiting==0) ? "table-row" : "none"));
	
			/* update the title of the page with the number of
			 * waiting messages, in case i'm reading reddit */
			document.title = "[" + waiting + "] " + doc_title;
			
			/* update the tab with the number of messages */
			window["update_training_tab"](waiting);
		});
		
		/* update again in five seconds */
		timeout = setTimeout(update, 5000);
	};
	
	/* start polling */
	update();
});
