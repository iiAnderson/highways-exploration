
d3.select(window).on("load", function () {
    Network.init();
    Network.graph("eastbound-out.csv", "m4");
    Network.clear();
});
