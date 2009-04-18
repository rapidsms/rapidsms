jQuery(function() {
	
	/* */
	if (window.frameElement) {
		jQuery(window.frameElement).css({
			"height": jQuery(document.body).outerHeight(),
			"overflow-y": "scroll"
		});
	
	/* we're not running in an iframe; let's assume that
	 * we're running the main webui */
	} else {
		
		/* if there are split panels, we're going to attach
		 * some fancy behavior to links within them... */
		$("#inner div.split").each(function() {
			
			/* if this split panel
			 * has an iframe... */
			var frame = $(this).find("iframe");
			if(frame) {
				
				/* iterate all links in the panel, and redirect each
				 * one to open in the frame with the BARE layout */
				$(this).find("a").each(function() {
					this.href += ((this.href.indexOf("?") != -1) ? "&" : "?") + "bare=1"
					this.target = frame[0].name;
				});
			}
		});
	}
});
