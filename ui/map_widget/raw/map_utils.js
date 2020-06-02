let requestRoute = (function () {
    let cache = {};

    return function (origin, destination) {
        return new Promise(function (resolve, reject) {
            if (cache[[origin, destination].toString()]) {
                resolve(cache[[origin, destination].toString()]);
                console.log(`${[origin, destination].toString()} был кэширован`)
                return
            }

            directionsService.route({
                origin,
                destination,
                ...directionsOptions
            }, function (response, status) {
                if (status === 'OK') {
                    cache[[origin, destination].toString()] = response;
                    resolve(response)
                } else {
                    reject(new Error(status))
                }
            })
        })
    }
})();

function drawRoute(route) {
    const renderer = new google.maps.DirectionsRenderer({
        map,
        polylineOptions: primePolyOptions,
        ...directionsRendererOptions
    });

    renderer.setDirections(route);
    routeRenderers.push(renderer)
}

function requestDistanceMatrix() {
    let places = markers.map(marker => marker.position);

    return new Promise(function (resolve, reject) {
        distanceMatrixService.getDistanceMatrix(
            {
                origins: places,
                destinations: places,
                ...distanceMatrixServiceOptions
            }, (response, status) => {
                if (status === 'OK') {
                    let matrix = [];

                    try {
                        for (let row of response.rows) {
                            matrix.push(row.elements.map(elem => elem.distance.value))
                        }
                        resolve(matrix);
                    } catch (e) {
                        reject(e)
                    }

                } else {
                    reject(new Error(`${status}`));
                }
            });
    })
}


function removeMarker(markerToRemove) {
    markerToRemove.setMap(null);
    markers = markers.filter(marker => marker !== markerToRemove);

    if (python) python._marker_removed();

    removeAllPaths();
}

function removeAllMarkers() {
    markers.forEach(marker => removeMarker(marker));
}

function addMarker(position, update = true) {
    if (!(position.hasOwnProperty('lat') && position.hasOwnProperty('lng'))) {
        return false;
    }

    if (update) removeAllPaths();

    if (python && update) {
        let {lat, lng} = position;
        python._marker_added(lat, lng);
    }

    const marker = new google.maps.Marker({
        map,
        position,
        ...markerOptions
    });
    marker.addListener('click', () => removeMarker(marker));

    markers.push(marker)
    return true;
}

function toLatLng(obj) {
    return {lat: obj.lat(), lng: obj.lng()};
}

function markersToPoints() {
    return markers.map(marker => toLatLng(marker.position));
}

function addMarkers(positions) {
    for (let position of positions) {
        if (!addMarker(position)) {
            return false;
        }
    }
    return true;
}

function loadMatrix() {
    if (markers.length <= 3) {
        if (python) python._error_loading_matrix('not enough markers!');
        return;
    }

    requestDistanceMatrix()
        .then((matrix) => {
            distanceMatrix = matrix;

            if (python) python._matrix_loaded(distanceMatrix);
        })
        .catch((error) => {
            if (python) python._error_loading_matrix(error.message || toString(error));
        })
}

function removeSimplePath() {
    polylines.forEach(poly => poly.setMap(null));
    polylines = [];
}

function removePrecisePath() {
    routeRenderers.forEach(renderer => renderer.setMap(null));
    routeRenderers = [];
}

function removeAllPaths() {
    removeSimplePath();
    removePrecisePath();
}

function requestPreciseRoutes(positions) {
    let paths = [];
    let requests = [];

    for (let i = 0; i < positions.length; i++) {
        let origin = positions[i];
        let destination = positions[(i < positions.length - 1) ? i + 1 : 0];

        let request = requestRoute(origin, destination);
        paths.push([origin, destination])

        requests.push(request)
    }

    return new Promise(function (resolve, reject) {
        Promise.allSettled(requests)
            .then(results => {
                let rejected = [];
                let resolved = [];

                results.forEach((result, index) => {
                    if (result.status === 'rejected') {
                        rejected.push(paths[map]);
                    } else {
                        resolved.push(result.value);
                    }
                })

                if (rejected.length > 0) {
                    console.warn(rejected);
                }

                resolve({resolved, rejected});
            })
            .catch((error) => reject(error));
    })
}

function drawPrecisePath(positions, drawSecondary) {
    drawSimplePath(positions, drawSecondary);

    requestPreciseRoutes(positions)
        .then(function ({resolved, rejected}) {
            removeAllPaths();
            resolved.forEach(route => drawRoute(route));
            rejected.forEach(route => drawPoly(...route, primePolyOptions));
            if (drawSecondary) drawSecondaryPaths(positions);
        })
        .catch(reason => {
            console.warn(reason);
            drawSimplePath(positions, drawSecondary);
        });
}

function drawPoly(origin, destination, polyOptions) {
    let poly = new google.maps.Polyline({
        path: [origin, destination],
        map,
        ...polyOptions
    });

    polylines.push(poly);
}

function drawSimplePath(positions, drawSecondary) {
    removeAllPaths();

    for (let i = 0; i < positions.length; i++) {
        let origin = positions[i];
        let destination = positions[(i < positions.length - 1) ? i + 1 : 0];

        drawPoly(origin, destination, primePolyOptions);
    }

    if (drawSecondary) drawSecondaryPaths(positions);
}

function drawSecondaryPaths(positions) {
    for (let i = 0; i < positions.length; i++) {
        let origin = positions[i];
        let k = (i < positions.length - 1) ? i + 1 : 0;

        for (let j = i + 1; j < positions.length; j++) {
            if (i !== j && k !== j && !(i === 0 && j === positions.length - 1)) {
                let otherDestination = positions[j];
                drawPoly(origin, otherDestination, secondaryPolyOptions);
            }
        }
    }
}

function drawPath(solution, drawSecondary = false, drawPrecise = false) {
    if (
        solution.length !== markers.length ||
        !onlyUniqueValues(solution) ||
        !(Math.max(...solution) in range(0, markers.length)) ||
        !(Math.min(...solution) in range(0, markers.length))
    ) throw new Error('Неправильное решение!');

    // упорядоченные точки
    let positions = solution.map(i => markers[i].position);

    if (drawPrecise) {
        drawPrecisePath(positions, drawSecondary);
    } else {
        drawSimplePath(positions, drawSecondary);
    }
}

function loadSaved(points) {
    removeAllMarkers();

    points.forEach(point => addMarker(point, false));

    let bounds = new google.maps.LatLngBounds();
    points.forEach(point => bounds.extend(point))
    map.fitBounds(bounds);
}
    