/* vim:set et ts=4 sw=4 */

jQuery(function() {
    jQuery("div.map").each(function() {

        // coordinates for center of ground image (custom map image)
        var centerpoint = new google.maps.LatLng(40.490325, 17.789084);

        // bottom left and top right boundaries of image
        var brinlandbounds = new google.maps.LatLngBounds(
            new google.maps.LatLng(40.232605, 17.313499),
            new google.maps.LatLng(40.745111, 18.265061)
        );

        // blank layer of custom background images so googlemap's 
        // road, terrain, etc layers are not shown behind our image
        var blankOverlayOptions = {
            getTileUrl: function(coord, zoom){
                return "/static/rapidsms/images/body-bg.png";
            },
            tileSize: new google.maps.Size(128, 128),
            isPng: true,
            center: centerpoint,
        };

        var blankMapType = new google.maps.ImageMapType(blankOverlayOptions);
        // zoom constrains, since our users won't need to zoom out
        // beyond our image
        blankMapType.minZoom = 10; 
        blankMapType.maxZoom = 15;

        var map;
        // create map and 
        // turn off layer type selectors (terrain, satellite, road, etc)
        map = new google.maps.Map($("div.container", this).get(0),{
            "mapTypeControl": false,
            "center": centerpoint 
        });

        // set blank layer as the base layer
        map.mapTypes.set('blankbase', blankMapType);
        map.setMapTypeId('blankbase'); 
        map.overlayMapTypes.insertAt(0, blankMapType);

        // set image as ground overlay in the lat/lng bounds
        // declared above
        var brinland = new google.maps.GroundOverlay(
            "/static/locations/images/brinland.jpg", 
            brinlandbounds);
        brinland.setMap(map);

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
