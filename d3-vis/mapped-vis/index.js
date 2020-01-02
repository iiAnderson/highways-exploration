var width = 960,
    height = 500,
    active = d3.select(null);

var projection = d3.geo.albersUsa()
    .scale(1000)
    .translate([width / 2, height / 2]);

var path = d3.geo.path()
    .projection(projection);

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

svg.append("rect")
    .attr("class", "background")
    .attr("width", width)
    .attr("height", height)
    .on("click", reset);

var g = svg.append("g")
    .style("stroke-width", "1.5px");

d3.json("m5-cardiff.geojson", function (error, us) {
    if (error) throw error;

    g.selectAll("path")
        .data(topojson.feature(us, us.objects.states).features)
        .enter().append("path")
        .attr("d", path)
        .attr("class", "feature")
        .on("click", clicked);

    g.append("path")
        .datum(topojson.mesh(us, us.objects.states, function (a, b) { return a !== b; }))
        .attr("class", "mesh")
        .attr("d", path);
});
















// var svg = d3.select("body")
//     .append("svg")
//     .attr("width", width)  // apply width,height to svg
//     .attr("height", height);

// var projection = d3.geoMercator();
// var path = d3.geoPath().projection(projection);

// d3.json("m5-cardiff.geojson").then(function (data, err) {
//     console.log(data);
//     var points = data.features;
//     var geojson = []
//     for (var i = 0; i < points.length; i++) {
//         var x = points[i].geometry.coordinates[0];
//         var y = points[i].geometry.coordinates[1];
//         geojson.push([x, y]);
//     }

//     var lineString = { "type": "LineString", "coordinates": geojson }

//     var linepath = svg.append("path")
//         .data([lineString]) //works with path but not line
//         .attr("d", path)
//         //  .data([geojson])// works with line but not path
//         // .attr("d", line)
//         .attr('class', 'journey');
// });