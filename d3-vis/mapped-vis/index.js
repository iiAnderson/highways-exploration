
d3.select(window).on("load", function () {
    Network.init();
    Network.map("eastbound-out.csv", "M4");
    Network.clear();
});
