/* vim:set et ts=4 sw=4 */

window.adammck = window.adammck || {};
adammck.maps = adammck.maps || {};

(function(namespace) {
    var mask_paths = [[
        new google.maps.LatLng( 90, -180),
        new google.maps.LatLng( 90, 0),
        new google.maps.LatLng(-90, 0),
        new google.maps.LatLng(-90, -180)
    ], [
        new google.maps.LatLng( 90, -180),
        new google.maps.LatLng( 90, 0.000001),
        new google.maps.LatLng(-90, 0.000001),
        new google.maps.LatLng(-90, -180)
    ]];

    namespace.Mask = function(options) {
        this.mask_ = new google.maps.Polygon();
        this.polygon_ = new google.maps.Polygon();

        this.fillColor = "#FFFFFF";
        this.fillOpacity = 0.6;
        this.map = null;
        this.paths = [];
        this.strokeColor = "#FFFFFF";
        this.strokeOpacity = 1;
        this.strokeWeight = 2;
        this.zIndex = -100;
        this.setOptions(options);
    };

    namespace.Mask.prototype =
        new google.maps.MVCObject();

    namespace.Mask.prototype.setMap = function(map) {
        this.mask_.setMap(map);
        this.polygon_.setMap(map);
        this.map = map;
    };

    namespace.Mask.prototype.setPaths = function(paths) {
        this.mask_.setPaths(mask_paths.concat(paths));
        this.polygon_.setPaths(paths);
        this.paths = paths;
    };

    namespace.Mask.prototype.setOptions = function(options) {
        this.setValues(options);

        this.mask_.setOptions({
            fillColor: this.fillColor,
            fillOpacity: this.fillOpacity,
            strokeWeight: 0,
            strokeOpacity: 0,
            zIndex: this.zIndex,
            map: this.map
        });

        this.polygon_.setOptions({
            fillOpacity: 0,
            strokeColor: this.strokeColor,
            strokeOpacity: this.strokeOpacity,
            strokeWeight: this.strokeWeight,
            zIndex: this.zIndex,
            map: this.map,
        });
    };
})(adammck.maps);
