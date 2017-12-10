$(document).ready(function() {
    var icon = L.divIcon({
        iconSize: [25, 25],
        iconAnchor: [12, 12],
        popupAnchor: [0, -6],
        shadowSize: [0, 0],
        className: 'marker-icon'
    })

    var map = L.map('live-map').setView([52.53, 13.403], 13);
    map.zoomControl.setPosition('bottomright');

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}{r}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery &copy; <a href="http://mapbox.com">Mapbox</a>',
        maxZoom: 18,
        id: 'mapbox.streets-basic',
        accessToken: mapbox_key
    }).addTo(map);

    // Display the "city boundaries"
    var circle = L.circle([52.53, 13.403], {
        color: '#0078A8',
        opacity: 0.7,
        fillOpacity: 0.07,
        radius: 3500,
        interactive: false
    }).addTo(map);

    var markers = {};
    var clustermarkers = L.markerClusterGroup({
        disableClusteringAtZoom: 14,
        spiderfyOnMaxZoom: false
    });

    map.addLayer(clustermarkers);

    namespace = '/vehicles';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function() {
        socket.emit('connected');
    });

    socket.on('update_location', function(data) {
        if (data.vehicle_id in markers) {
            var oldLatlgn = markers[data.vehicle_id].getLatLng()
            var newLatLng = new L.LatLng(data.lat, data.lng);
            var bearing = L.GeometryUtil.bearing(oldLatlgn, newLatLng)

            markers[data.vehicle_id].setLatLng(newLatLng);
            markers[data.vehicle_id].options.rotationAngle = bearing + 135;
        } else {
            markers[data.vehicle_id] = L.marker([data.lat, data.lng], {
                icon: icon,
                rotationAngle: -45
            }).bindPopup(data.vehicle_id);
            clustermarkers.addLayer(markers[data.vehicle_id]);
        }
    });

    // Remove vehicle markers when they leave the city boundaries
    socket.on('delete_vehicle', function(data) {
        if (data.vehicle_id in markers) {
            clustermarkers.removeLayer(markers[data.vehicle_id]);
        }
    });
});
