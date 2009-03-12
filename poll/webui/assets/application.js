(function () {
	window.addEvent("domready", function () {
		$(document.body.parentNode)
			.addClass(Browser.Platform.name)
			.addClass(Browser.Engine.name);
	});
})();
