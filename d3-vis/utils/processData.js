
var NetworkData = {

    generateData: function (dataFile, whitelist, callback) {
        console.log("Generating Node/Link dictionary for " + whitelist);

        d3.csv("/d3-vis/data/" + dataFile, function (error, graph) {
            if (error) throw error;

            var links = {
                links: [],
                nodes: []
            };

            var nodeLink = {
                // Junc Name: index
            }
            for (var key in Object.keys(graph[0])) {
                if (key === '""' || key === "") {
                    continue;
                }

                var feature = graph[0][key]
                var junc = key;
                var motorwayName = whitelist
                var junctionName = junc;
                var splitName = motorwayName + "-" + junctionName;

                if (feature === undefined) continue;

                links.nodes.push({ name: splitName, group: junc.match(/\d+(\D*)/)[0], value: feature });

                if (motorwayName in nodeLink) {
                    nodeLink[motorwayName][junctionName] = links.nodes.length - 1;
                } else {
                    nodeLink[motorwayName] = {}
                    nodeLink[motorwayName][junctionName] = links.nodes.length - 1;
                }

            }

            for (var key in nodeLink) {
                if (nodeLink.hasOwnProperty(key)) {
                    const ordered = Object.keys(nodeLink[key]).sort(function (a, b) {
                        return parseInt(a.match(/\d+/)) - parseInt(b.match(/\d+/));
                    });

                    for (var j = 0; j < ordered.length; j++) {

                        var indexSourceVal = nodeLink[key][ordered[j]];
                        var indexTargetVal = nodeLink[key][ordered[j + 1]];

                        if (indexSourceVal == undefined || indexTargetVal == undefined) {
                            continue;
                        }

                        links.links.push({ source: indexSourceVal, target: indexTargetVal, value: 1 })
                    }
                }
            }

            callback(links);

        });
    }
}