/* UNICEF RapidSMS UI
 * vim:set noet:
 * --
 * export/global.js
 * --
 * This script looks for things marked as exportable, and adds all
 * of the necessary elements and events to make it so. This only
 * works in conjunction with the views.py */

jQuery.fn.dump = function() {
	var content = $("thead, tbody", this);
		
	/* iterate (functionally) the rows */
	return $.map($("tr", content), function(row) {
		return $.map($("td, th", row), function(cell) {
			return $(cell).text() + ((cell.colSpan > 1) ? (":" + cell.colSpan) : "");
		}).join("|");
	}).join("\n");
};

$(function() {
	$("table.export").each(function() {
		var table = $(this);
		
		/* make sure that the table has
		 * a footer - create it if not */
		var tfoot = $("tfoot", table);
		if(!tfoot.length) {
			
			/* count the number of columns in the first
			 * row, to make the footer span them all */
			var cols = 0;
			for(var td in this.rows[0].cells)
				cols += td.colSpan || 1;
			
			/* create a footer with a single full-width cell */
			tfoot = $('<tfoot><tr><td colspan="' + cols + '"></td></tr></tfoot>');
			table.append(tfoot);
		}
		
		var link = $('<a href="">Export</a>').click(function(ev) {
			ev.stopPropagation();
			ev.preventDefault();

			/* POST the responses back to the method:
			 * apps.training.app.App.ajax_POST_accept */ 
			$('<form action="/export/str" method="post"></form>').append(
				$('<input type="hidden" name="data" value="' + table.dump() + '" />')
			).appendTo("body").submit();
		});
		
		
		var target = $("td", tfoot);
		target.append(link);
	});
});
