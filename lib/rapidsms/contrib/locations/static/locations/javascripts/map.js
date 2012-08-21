/* vim:set et ts=4 sw=4 */

jQuery(function() {
    var maps = [];

    jQuery("div.map").each(function() {
        var map = new google.maps.Map(
            jQuery("div.container", this).get(0), {
                "mapTypeId": google.maps.MapTypeId.TERRAIN,
                "mapTypeControl": false
            }
        );

        var bounds = new google.maps.LatLngBounds();

        /* add a label for each location. TODO: simple markers and
         * clustering could be lovely (if a bit awkard) here. */
        jQuery("ul.labels > li", this).each(function() {
            var loc = jQuery(this);
            var lat = loc.attr("lat");
            var lng = loc.attr("lng");

            /* locations without a lat and/or long are ignored. */
            if(lat && lng) {
                var label = new adammck.maps.Label({
                    "map": map,
                    "content": loc.html(),
                    "position": new google.maps.LatLng(lat, lng),
                    "direction": loc.attr("direction"),
                    "className": loc.attr("class")
                });

                bounds.extend(label.position);
            }
        });

        /* if there are no locations on this map, there's nothing to
         * center on, so use the default (from settings.py) instead. */
        if(bounds.isEmpty()) {
            bounds.extend(
                new google.maps.LatLng(
                    jQuery(this).attr("lat"),
                    jQuery(this).attr("lng")
                )
            );
        }

        map.fitBounds(bounds);
        maps.push(map);
    });

    /* maximize the map, by hiding the two outer columns. */
    jQuery("div.toolbar .maximize").click(function() {
        jQuery(this).parents("div.three-columns").toggleClass("max-map");

        /* fire the resize event on every map (although there's probably
         * only one) to spawn new tiles to fill the extra space. */
        jQuery.each(maps, function(n, map) {
            google.maps.event.trigger(map, "resize");
        });
    });

    var pp_events = [];

    /* start watching the map(s) for clicks, to fill the lat+lng fields
     * preceding `trigger`. after click, stop_pinpoint is called. */
    var start_pinpoint = function(trigger) {
        jQuery(document.body).addClass("pinpointing");
        trigger.parent().addClass("pp-target");

        jQuery.each(maps, function(n, map) {
            map.setOptions({
                "draggable": false
            });

            pp_events.push(
                google.maps.event.addListener(map, "click", function(event) {
                    trigger.prev().prev().attr("value", event.latLng.lat());
                    trigger.prev().attr("value", event.latLng.lng());
                    stop_pinpoint(trigger);
                })
            );
        });
    };

    /* stop watching map(s) for clicks, and undo ui changes. */
    var stop_pinpoint = function(trigger) {
        jQuery.each(pp_events, function(n, event) {
            google.maps.event.removeListener(event);
        });

        jQuery.each(maps, function(n, map) {
            map.setOptions({
                "draggable": true
            });
        });

        jQuery(".pp-target").removeClass("pp-target");
        jQuery(document.body).removeClass("pinpointing");
    };

    /* add a trigger to each co-ord field (before the help text), to
     * make it easy to fill the widgets by clicking on the map. */
    jQuery("div.field.point p.help").each(function() {
        var trigger = jQuery('<input class="js-button pinpoint">');

        trigger.click(function() {
            if(jQuery(document.body).hasClass("pinpointing")) {
                stop_pinpoint(trigger);
            } else {
                start_pinpoint(trigger);
            }
        });

        jQuery(this).before(trigger);
    });
});
