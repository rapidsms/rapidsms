// vim: noet

jQuery(function() {
	jQuery(document.body).click(function(e) {
		
		/* ignore this click if it wasn't a link */
		var link = $(e.target);
		if(link.get(0).tagName.toLowerCase() != "a")
			return true;

		/* find the paginator that this link lives within. if there
		 * is none (ie, a link that isn't within a paginator was clicked),
		 * we're not interested in this event */
		var paginator = link.parents("div.paginator");
		if(!paginator.length)
			return true;

		/* as above, for the table that we will reload with the new
		 * page of data. a paginator shouldn't exist outside of a
		 * table, but let's not blow up if it does */
		var table = paginator.parents("table");
		if(!table.length)
			return true;


		/* this click was within a paginator link.
		 * we'll take it from here, so kill the event */
		e.preventDefault();

		/* wat */
		jQuery.ajax({
			dataType: "html",
			url: link.attr("href"),
			complete: function(res, status) {

				/* if the request was successful... */
				if(status == "success" || status == "notmodified") {

					/* create a dummy div, and inject the results into it. since the
					 * page we just requested is the SAME PAGE that we're currently
					 * viewing, only with a different page of objects, we can find
					 * the new table the old paginator's DOM id.
					 * --
					 * NOTE: this is mostly ripped off from the jQuery.load
					 *       function, which removes SCRIPT tags to avoid a
					 *       permission error in internet exploder */
					var new_table =
						jQuery("<div />")
							.append(res.responseText.replace(
								/<script(.|\s)*?\/script>/g, ""))
							.find("#" + paginator.attr("id")) // <-- new paginator
							.closest("table");

					/* replace the current table with the replacement
					 * from the new page. this will destroy any events
					 * currently attached, but will leave the rest of
					 * the page alone */
					table.replaceWith(new_table);
				}
			}
		});
	});
});
