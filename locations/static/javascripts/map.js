/* vim:set et ts=4 sw=4 */

jQuery(function() {
    jQuery("div.map").each(function() {
        var map = new google.maps.Map(
            $("div.container", this).get(0), {
                "mapTypeId": google.maps.MapTypeId.TERRAIN,
                "mapTypeControl": false
            }
        );

        var bounds = new google.maps.LatLngBounds();

        $("ul.labels > li", this).each(function() {
            var loc = $(this);
            var lat = loc.attr("lat");
            var lng = loc.attr("lng");

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

        if(bounds.isEmpty()) {
            bounds.extend(
                new google.maps.LatLng(
                    $(this).attr("lat"),
                    $(this).attr("lng")
                )
            );
        }

        map.fitBounds(bounds);
    });
});
