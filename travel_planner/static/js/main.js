/* ============================================================
   AI 旅行规划师 - Main JavaScript
   ============================================================ */

/**
 * Initialize Leaflet map with itinerary spots.
 * @param {Array} days - Array of day objects, each containing spots with lat/lng
 */
function initMap(days) {
    var mapElement = document.getElementById('map');
    if (!mapElement) return;

    // Collect all spots from all days
    var allSpots = [];
    if (days && days.length > 0) {
        days.forEach(function(day) {
            if (day.spots && day.spots.length > 0) {
                day.spots.forEach(function(spot) {
                    allSpots.push({
                        name: spot.name,
                        lat: spot.lat,
                        lng: spot.lng,
                        description: spot.description,
                        cost: spot.cost,
                        day: day.day_number
                    });
                });
            }
        });
    }

    if (allSpots.length === 0) return;

    // Calculate map bounds
    var bounds = L.latLngBounds();
    allSpots.forEach(function(spot) {
        bounds.extend([spot.lat, spot.lng]);
    });

    // Initialize map with Gaode (AMap) tile layer
    var map = L.map('map', {
        zoomControl: true,
        attributionControl: false
    }).fitBounds(bounds, { padding: [40, 40] });

    // Use OpenStreetMap tile layer (better compatibility)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    // Color palette for different days
    var dayColors = ['#2563eb', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6'];

    // Add markers for each spot, grouped by day
    var markers = [];
    var routePoints = [];

    allSpots.forEach(function(spot, index) {
        var color = dayColors[(spot.day - 1) % dayColors.length];

        var marker = L.circleMarker([spot.lat, spot.lng], {
            radius: 8,
            fillColor: color,
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });

        marker.bindPopup(
            '<strong>' + spot.name + '</strong>' +
            (spot.description ? '<br>' + spot.description : '') +
            '<br>第' + spot.day + '天 | ¥' + spot.cost
        );

        marker._spotData = spot;
        marker.addTo(map);
        markers.push(marker);
        routePoints.push([spot.lat, spot.lng]);
    });

    // Draw route line
    if (routePoints.length > 1) {
        L.polyline(routePoints, {
            color: '#2563eb',
            weight: 2,
            opacity: 0.5,
            dashArray: '8, 8'
        }).addTo(map);
    }

    // Click spot items to focus on map
    var spotItems = document.querySelectorAll('.spot-item');
    spotItems.forEach(function(item) {
        item.addEventListener('click', function() {
            var lat = parseFloat(this.dataset.lat);
            var lng = parseFloat(this.dataset.lng);
            var name = this.dataset.name;

            // Find matching marker
            markers.forEach(function(marker) {
                var data = marker._spotData;
                if (data && data.lat === lat && data.lng === lng) {
                    map.setView([lat, lng], 15);
                    marker.openPopup();
                }
            });

            // Highlight current spot
            spotItems.forEach(function(s) { s.classList.remove('highlighted'); });
            this.classList.add('highlighted');
        });
    });
}
