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
                    "direction": adammck.maps.Label.Direction.CENTER
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
});
