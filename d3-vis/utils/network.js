
var Network = {

    width: 1200,
    height: 1200,
    radius: 6,
    force: null,
    centered: false,
    svg: null,

    div: d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0),

    init: function () {
        Network.force = d3.layout.force()
            // .distance(100)
            .size([Network.width, Network.height]);

        Network.svg = d3.select("body").append("svg")
            .attr("width", Network.width)
            .attr("height", Network.height);
    },

    clear: function () {
        console.log("Clearing SVG");
        d3.selectAll("svg > *").remove();
    },

    graph: function (dataFile, motorway) {

        NetworkData.generateData(dataFile, motorway, function (links) {
            console.log("Building Node Graph for " + motorway);

            var colours = interpolateColors("rgb(124,252,0)", "rgb(255,0,0)", 10);

            var node = Network.svg.selectAll("circle")
                .data(links.nodes)
                .enter().append("circle")
                .attr("r", Network.radius - .75)
                .style("stroke", function (d) {
                    return colours[parseInt((round(d.value) + "").charAt(0))];
                })
                .style("fill", function (d) {
                    return colours[parseInt((round(d.value) + "").charAt(0))];
                })
                .on("mouseover", function (d) {
                    Network.div.transition()
                        .duration(200)
                        .style("opacity", .9);
                    Network.div.html(d.name + " : " + d.value)
                        .style("left", (d3.event.pageX) + "px")
                        .style("top", (d3.event.pageY - 28) + "px");
                })
                .on("mouseout", function (d) {
                    Network.div.transition()
                        .duration(500)
                        .style("opacity", 0);
                })
                .call(Network.force.drag);

            var link = Network.svg.selectAll("line")
                .data(links.links)
                .enter().append("line");

            Network.force
                .nodes(links.nodes)
                .links(links.links)
                .on("tick", tick)
                .start();

            function tick() {
                node.attr("cx", function (d) { return d.x = Math.max(Network.radius, Math.min(Network.width - Network.radius, d.x)); })
                    .attr("cy", function (d) { return d.y = Math.max(Network.radius, Math.min(Network.height - Network.radius, d.y)); });

                link.attr("x1", function (d) { return d.source.x; })
                    .attr("y1", function (d) { return d.source.y; })
                    .attr("x2", function (d) { return d.target.x; })
                    .attr("y2", function (d) { return d.target.y; });
            }


        });
    },

    map: function (dataFile, motorway) {

        var projection = d3.geo.albers()
            .center([0, 55.4])
            .rotate([4.4, 0])
            .parallels([50, 60])
            .scale(1200 * 5)
            .translate([Network.width / 2, Network.height / 2]);

        Network.path = d3.geo.path()
            .projection(projection)
            .pointRadius(2);

        var colours = interpolateColors("rgb(124,252,0)", "rgb(255,0,0)", 10);

        d3.json("/d3-vis/data/uk.json", function (error, uk) {

            var subunits = topojson.object(uk, uk.objects.subunits),
                places = topojson.object(uk, uk.objects.places);

            Network.svg.selectAll(".subunit")
                .data(subunits.geometries)
                .enter().append("path")
                .attr("class", function (d) { return "subunit " + d.id; })
                .attr("d", Network.path);

            Network.svg.append("path")
                .datum(topojson.mesh(uk, uk.objects.subunits, function (a, b) { return a !== b && a.id !== "IRL"; }))
                .attr("d", Network.path)
                .attr("class", "subunit-boundary");

            Network.svg.append("path")
                .datum(topojson.mesh(uk, uk.objects.subunits, function (a, b) { return a === b && a.id === "IRL"; }))
                .attr("d", Network.path)
                .attr("class", "subunit-boundary IRL");

            Network.svg.selectAll(".subunit-label")
                .data(subunits.geometries)
                .enter().append("text")
                .attr("class", function (d) { return "subunit-label " + d.id; })
                .attr("transform", function (d) { return "translate(" + Network.path.centroid(d) + ")"; })
                .attr("dy", ".35em")
                .text(function (d) { return d.properties.name; });

            Network.svg.append("path")
                .datum(places)
                .attr("d", Network.path)
                .attr("class", "place");

            Network.svg.selectAll(".place-label")
                .data(places.geometries)
                .enter().append("text")
                .attr("class", "place-label")
                .attr("transform", function (d) { return "translate(" + projection(d.coordinates) + ")"; })
                .attr("x", function (d) { return d.coordinates[0] > -1 ? 6 : -6; })
                .attr("dy", ".35em")
                .style("text-anchor", function (d) { return d.coordinates[0] > -1 ? "start" : "end"; })
                .text(function (d) { return d.properties.name; });

            d3.json("/d3-vis/data/all.geojson", function (js) {

                d3.csv("/d3-vis/data/" + dataFile, function (csvData) {
                    console.log(csvData);
                    for (var l in js.features) {
                        var line = js.features[l];
                        if (line.properties.junctionNumber.split(" ")[0] === motorway) {
                            var juncNumber = line.properties.junctionNumber.split(" ")[line.properties.junctionNumber.split(" ").length - 1].match(/\d+(\D*)/)[0];
                            var val = csvData[0][juncNumber];
                            if (val === undefined) continue;

                            line.properties['value'] = colours[parseInt((round(val) + "").charAt(0))];
                        }
                    }

                    Network.svg.selectAll("path")
                        .data(js.features)
                        .enter()
                        .append("path")
                        .attr("d", Network.path)
                        .attr("fill", function (d) {
                            if (d.properties.value === undefined) {
                                return "#666666";
                            }
                            return d.properties.value;
                        })
                        .on("click", Network.clicked);

                });
                //Bind data and create one path per GeoJSON feature

            });
        });

    },

    clicked: function (d) {
        console.log(d)
        var x, y, k;

        if (d && Network.centered !== d) {
            var centroid = Network.path.centroid(d);
            console.log(centroid);

            x = centroid[0] - (Network.width / 2.3);
            y = centroid[1] - (Network.height / 2.5);
            k = 4;
            Network.centered = d;
        } else {
            x = Network.width / 2;
            y = Network.height / 2;
            k = 1;
            centered = null;
        }

        Network.svg.selectAll("path")
            .classed("active", Network.centered && function (d) { return d === Network.centered; });

        Network.svg.transition()
            .duration(750)
            .attr("transform", "translate(" + Network.width / 2 + "," + Network.height / 2 + ")scale(" + k + ")translate(" + -x + "," + -y + ")")
            .style("stroke-width", 1.5 / k + "px");
    }
}