document.addEventListener('DOMContentLoaded', function() {
    // Listen for button, then create chip reader
    document.querySelector('#createChip').addEventListener('click', event => {
        create_chip_reader(event.target.attributes.sim_id.value)
    });
    // Go back to a fresh ModelForm to add more readers
    document.querySelector('#anotherReader').addEventListener('click', event => {
        window.map.remove()
        document.getElementById("readerForm").reset();
        document.getElementById("readerSection").style.display = "block";
        document.getElementById("simContainer").style.display = "none";
    });
    // Listen for button, then run the simulation
    document.querySelector('#runSimButton').addEventListener('click', event => {
        document.getElementById("runForm").style.display = "none";
        var sim_id = event.target.attributes.sim_id.value
        // Wait for promise, then generate the table
        add_routes_to_map(sim_id).then(response => {
            fetch(`/simulations/${response}/run`)
            .then(response => response.json())
            .then(data => {
                table = document.getElementById("resultsTable")
                create_table(table, data.results)
            })
        })
    })
    // View a simulation that has already been run
    if (document.querySelector("#simRun").innerHTML == "True") {
        document.getElementById("readerSection").style.display = "none";
        document.getElementById("simContainer").style.display = "block";
        document.getElementById("runForm").style.display = "none";
        // Add layers to the map
        window.map = L.map('map').setView([42.37, -71.10], 14);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);
        let sim_id = document.querySelector("#simRun").getAttribute("sim_id");
        var routes = new L.GeoJSON.AJAX(`../routes/${sim_id}`).addTo(map);
        var buffers = new L.GeoJSON.AJAX(`../rfidbuffers/${sim_id}`).addTo(map);
        // Make the table
        fetch(`/simulations/${sim_id}/run`)
        .then(response => response.json())
        .then(data => {
            table = document.getElementById("resultsTable")
            create_table(table, data.results)
        })
    }
});


function generate_point() {
    // Get x coordinate
    bounds = {'north': 42.39, 'south': 42.36, 'east': -71.08, 'west': -71.12,}
    var xmax = Math.max(bounds.south, bounds.north);
    var xmin = Math.min(bounds.south, bounds.north);
    var x = Math.random() * (xmax - xmin) + xmin;
    // Get y coordinate
    var ymax = Math.max(bounds.west, bounds.east);
    var ymin = Math.min(bounds.west, bounds.east);
    var y = Math.random() * (ymax - ymin) + ymin;
    return `${y},${x}`
}


function generate_route(sim_id) {
    // Get a route from OSRM, save it to the database, and return the feature as JSON
    var start_pt = generate_point();
    var end_pt = generate_point();
    return fetch(`http://172.23.144.1:5000/route/v1/driving/${start_pt};${end_pt}?geometries=geojson&overview=full`)
    .then(response => response.json())
    .then(data => {
        if (data.code != 'Ok') {
            console.log(data.code)
        } else {
            // Construct GeoJSON
            var geojson = data.routes[0].geometry
            var geojsonFeature = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {},
                        "geometry": {
                            "coordinates": [],
                            "type": "LineString"
                        }
                    }
                ]
            };
            geojsonFeature.features[0].geometry = geojson
            // Save to database via API
            fetch('/routes/new', {
                method: "POST",
                body: JSON.stringify({
                    sim_id: sim_id,
                    geom: geojson
                })
            })
            // Get response data
            .then(response => {
                if (!response.ok) {
                    throw new Error(response.json())
                }
            })
            .catch(error => {
                // Catch any errors
                console.log("Route could not be saved.")
            })
            return geojsonFeature;
        }
    })
    .catch(error => {
        // Catch any errors
        console.log("Route could not be created.")
    })
}


function create_chip_reader(simulation_id) {
    // Save chip reader to the database
    var form = new FormData(document.getElementById('readerForm'))
    fetch(`/rfidreaders/new/${simulation_id}`, {
        method: "POST",
        body: form
    })
    // Get response data
    .then(response => {
        if (!response.ok) {
            throw new Error(response.json())
        }
        return response.json()
    })
    // Update map with point and buffer
    .then(() => {
        document.getElementById("readerSection").style.display = "none";
        document.getElementById("simContainer").style.display = "block";
        window.map = L.map('map').setView([42.37, -71.10], 14);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);
        // Make buffer layer and add to the map
        var buffers = new L.GeoJSON.AJAX(`../rfidbuffers/${simulation_id}`).addTo(map);
    })
    .catch(error => {
        // Catch any errors
        console.log(error)
        window.alert("Valid map marker is required.")
    })
}


function create_table(table, data) {
    // Generate an html table from JSON array of dicts
    for (let element of data) {
        let row = table.insertRow();
        for (key in element) {
            let cell = row.insertCell();
            let text = document.createTextNode(element[key]);
            cell.appendChild(text);
        }
    }
    let thead = table.createTHead();
    let row = thead.insertRow();
    for (let key of Object.keys(data[0])) {
        let key_lookup = {
            "id": "ID",
            "chip_class": "Chip Reader Class",
            "chip_range": "Chip Reader Range",
            "route_count": "Route Count"
        }
        let th = document.createElement("th");
        let text = document.createTextNode(key_lookup[key]);
        th.appendChild(text);
        row.appendChild(th);
    }
    
}


async function add_routes_to_map(sim_id) {
    // Anync call to generate 100 routes, and add them to the empty route layer
    var routes = new L.geoJSON().addTo(window.map);
    for (var i=0; i<100; i++) {
        await generate_route(sim_id)
        .then(data => {
            routes.addData(data)
        })
        if (i == 99) {
            return sim_id
        }
    }
}
