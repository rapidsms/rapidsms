$(document).ready(function(){
	$("#lgas").treeview({
		collapsed: true,
		url: "/reports/json/"
	});
	$("#lgas").ajaxComplete(function (req, settings) {
/**
 * TODO: Fix the javascript so every row is zebra stripped properly
 *
		$("#lga li").removeClass("odd");
		$("#lga li").removeClass("even");
		$("#lgas li:even").addClass("even");
		$("#lgas li:odd").addClass("odd");
 */
	});
});
