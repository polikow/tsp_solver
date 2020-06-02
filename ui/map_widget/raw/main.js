let map;
let python;
let directionsService;
let distanceMatrixService;
let markers = [];
let polylines = [];
let routeRenderers = [];
let distanceMatrix;
let status = 'loading';

loadGoogleMapsScript()
    .then(initialize)
    .catch(console.warn)

function loadGoogleMapsScript() {
    return loadScript({
        url: `https://maps.googleapis.com/maps/api/js`,
        params: {
            key: 'ADD_YOUR_KEY',
            language: 'ru',
        }
    });
}

function initialize() {
    map = new google.maps.Map(document.getElementById('map'), mapOptions);
    directionsService = new google.maps.DirectionsService;
    distanceMatrixService = new google.maps.DistanceMatrixService();

    new QWebChannel(qt.webChannelTransport, function (channel) {
        python = channel.objects.handler;
    });

    map.addListener('click', event => addMarker(toLatLng(event.latLng)))

    status = 'ready';
}
