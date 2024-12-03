// Set margin, height and width of map and line chart
let margin = { top: 50, bottom: 50, left: 70, right: 50 };
let height = 500
let width = 1075

// Create svg for choropleth map
let svg = d3.select("#map")
    .append("svg")
    .attr("id", "choropleth")
    //.attr("preserveAspectRatio", "xMinYMin meet")
    .attr("viewBox", [0, 0, width, height])
    .attr("width", width + margin.right + margin.left)
    .attr("height", height + margin.bottom + margin.top);

// Crease svg1 for line chart that shows the median house price data over time
let svg1 = d3
    .select("#line-chart")
    .append("svg")
    .attr("id", "line_chart")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("id", "container")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// State and County json data to map boundaries
let state_data = d3.json("static/us-states.json")
let county_data = d3.json("static/us-counties.json")
let monthly_price_data = d3.json("static/month_sales_price_redfin.json")

// Create projection
let projection = d3.geoAlbersUsa()
let path = d3.geoPath().projection(projection);

// Promise Data
let promises = [
    state_data,
    county_data,
    monthly_price_data
];


Promise.all(promises
    // enter code to read files
).then(
    // enter code to call ready() with required arguments
    function (d) {
        stateData = d[0];
        countyData = d[1];
        monthPriceData = d[2]
        //console.log("Monthly Price Data", monthPriceData)
        //console.log("State Data", stateData);
        //console.log("County Data", countyData);

        // Ready function to run with map
        ready(stateData, countyData, test_data, monthPriceData);
    }
);

function ready(state, county, data, monthPrice) {

    function createObject(keys, values) {
        const obj = Object.fromEntries(
            keys.map((key, index) => [key, values[index]]),
        );
        return obj;
    }


    // Data from render_template
    const test_data_fips = data.map(x => x.fips);
    const test_county_name = data.map(x => x.county_name);
    const test_state_name = data.map(x => x.state_name);

    // well_being key is the one containing the cluster number
    const test_data_wellbeing = data.map(x => x.well_being)

    const test_data_median_price = data.map(x => x.avg_med_sale_price)
    const test_data_inventory = data.map(x => x.avg_inventory)

    // test_score_obj has the fips number as a key and the cluster number as the value paired
    let test_score_obj = createObject(test_data_fips, test_data_wellbeing)

    let test_med_price_obj = createObject(test_data_fips, test_data_median_price)
    let test_inventory_obj = createObject(test_data_fips, test_data_inventory)
    let test_county_obj = createObject(test_data_fips, test_county_name)
    let test_state_obj = createObject(test_data_fips, test_state_name)

    // Color schemes based on how many clusters, in this instance this is for 10 total clusters
    let color_2 = {
        0: "#a6cee3", 1: "#1f78b4", 2: "#b2df8a", 3: "#33a02c",
        4: "#fb9a99", 5: "#e31a1c", 6: "#fdbf6f", 7: "#ff7f00",
        8: "#cab2d6", 9: "#65010c"
    }



    let clickEvent = function (d, i) {
        // Function to display the line chart with monthly housing price data upon clicking on county

        svg1.selectAll("*").remove();

        var selectCounty = d3.select(this).node().__data__.id


        let newArray = monthPrice.filter(function (i) {
            return i.fips === selectCounty;
        });

        if (newArray.length > 0 && test_score_obj[selectCounty] >= 0) {

            var month = newArray.map(x => x.month_number)
            var month_date = month.map(d => new Date("2023", (d - 1), "1"))
            var price = newArray.map(x => +x.median_sale_price_per_month)
            var fips_price_trend = month_date.map((item, index) => { return [item, price[index]] })

            var xAxis = d3.scaleTime()
                .domain(d3.extent(month_date))
                .range([0, width])

            svg1.append("g")
                .attr("transform", "translate(0," + height + ")")
                .call(d3.axisBottom(xAxis));

            var yAxis = d3.scaleLinear()
                .domain([0, d3.max(price)])
                .range([height, 0]);

            svg1.append("g")
                .call(d3.axisLeft(yAxis));

            // Tooltip for chart
            var toolTip = d3.tip()
                .attr("id", "price_tooltip")
                .attr("class", "d3-tip")
                .html(function (d) {
                    return String("Month: " + String((new Date(d[0])).toLocaleString('default', { month: "long" })) +
                        "<br>Price: $" + String(d[1])
                    )
                });

            const months = ["January", "February", "March", "April", "May", "June", "July",
                "August", "September", "October", "November", "December",];

            svg1.call(toolTip);

            // Scatter dots
            svg1
                .append("g")
                .selectAll("dot")
                .data(fips_price_trend)
                .enter()
                .append("circle")
                .attr("cx", function (d) { return xAxis(d[0]); })
                .attr("cy", function (d) { return yAxis(d[1]); })
                .attr("r", 7)
                .attr("fill", "#0066b2")
                .on('mouseover', function (d) {
                    var x = d3.event.x,
                        y = d3.event.y;
                    toolTip.show(d);
                    toolTip.style('top', y);
                    toolTip.style('left', x);
                })
                .on('mouseout', toolTip.hide);

            svg1.append("path")
                .datum(fips_price_trend)
                .attr("fill", "none")
                .attr("stroke", "#0066b2")
                .attr("stroke-width", 2.5)
                .attr("d", d3.line().x(function (d) { return xAxis(d[0]); }).y(function (d) { return yAxis(d[1]); }));

            svg1.append("text")
                .attr("class", "x-label")
                .attr("text-anchor", "end")
                .attr("x", width / 2)
                .attr("y", height + 35)
                .text("Month");

            svg1.append("text")
                .attr("class", "y-label")
                .attr("text-anchor", "end")
                .attr("x", -(height / 4.2))
                .attr("y", -60)
                .attr("transform", "rotate(-90)")
                .text("Median Home Price (USD)");

            svg1.append("text")
                .attr("x", (width / 2))
                .attr("y", -30)
                .attr("id", "line_chart_title")
                .attr("class", "title")
                .style("font-size", "16px")
                .style("text-anchor", "middle")
                .text("State: " + test_state_obj[selectCounty] + "; County: " + test_county_obj[selectCounty]);
        }
    }

    // Tooltip for hovering over map area
    var toolTip = d3.tip()
        .attr("id", "map_tooltip")
        .attr("class", "d3-tip")
        .html(function (d) {
            if (test_score_obj[d.id] === undefined) {

                return String("State: N/A" +
                    "<br>County: N/A" +
                    "<br>Median Home Value: N/A " +
                    "<br>Home Inventory: N/A")
            }

            else {
                return String("State: " + String(test_state_obj[d.id]) +
                    "<br>County: " + String(test_county_obj[d.id]) +
                    "<br>Median Home Value: $" + String(test_med_price_obj[d.id]) +
                    "<br>Home Inventory: " + String(test_inventory_obj[d.id]) +
                    "<br>Cluster Identity: " + String((test_score_obj[d.id]).valueOf() + 1))
            }
        });

    svg.call(toolTip);

    d3.select('#choropleth').append("g")
        .attr('id', 'plot')

    d3.select('#plot').append("g")
        .attr("id", "states")
        .selectAll("path")
        .data(state.features)
        .enter()
        .append("path")
        .attr("stroke", "#000")
        .attr("stroke-width", 0.5)
        .attr("d", path)
        .attr("fill", "none")


    var plotheight = document.getElementById("plot").getBBox().height;
    var plotwidth = document.getElementById("plot").getBBox().width;
    var plotx = document.getElementById("plot").getBBox().x;
    var ploty = document.getElementById("plot").getBBox().y;


    var svgheight = document.getElementById("choropleth").getBBox();

    var delta_x = plotx - 31.93626594543457
    var delta_y = plotx - 10.830191612243652

    var scalewidth = 834.6173095703125 / plotwidth
    var scaleheight = 485.30126953125 / plotheight

    var newscale = Math.min(scalewidth, scaleheight)

    // var svgheight = svg.attr("height")
    // var svgwidth = svg.attr("width")
    // var svgx = svg.attr("x")
    // var svgy = svg.attr("y")
    // console.log("svgheight", svgheight)
    // console.log("svgwidth", svgwidth)
    // console.log("svgx", svgx)
    // console.log("svgy", svgy)



    //path.attr("transform", "translate(0," + -100 + ")")


    // var widthratio = svgwidth / mywidth;
    // var heightratio = svgheight / myheight;
    // console.log(widthratio, heightratio)

    //projection.attr("transform", "translate(," + - 100 + ")")
    var plot = d3.select('#plot')



    const zoom = d3.zoom()
        .scaleExtent([1, 8])
        .extent([[0, 0], [width, height]])
        .on("zoom", () => plot.attr("transform", d3.event.transform));

    svg.call(zoom);


    d3.select('#plot').append("g")
        .attr("id", "counties")
        .selectAll("path")
        .data(county.features)
        .enter()
        .append("path")
        .attr("stroke", "#000")
        .attr("stroke-width", 0.5)
        .attr("d", path)
        .attr("fill", function (d) {
            if (test_data_fips.includes(d.id)) {

                return color_2[test_score_obj[d.id]]
            }
            else { return "#8c8c8c" }
        })
        .on('mouseover', function (d) {
            var x = d3.event.x,
                y = d3.event.y;
            toolTip.show(d);
            toolTip.style('top', y);
            toolTip.style('left', x);
        })
        .on('mouseout',
            toolTip.hide
        )
        .on('click', clickEvent);



    //function (d){
    //var clusterSelection = d3.select(this).node().__data__.id
    //console.log(clusterSelection)
    //console.log(test_score_obj[clusterSelection])
    //if (test_score_obj[clusterSelection] >= 0){
    //  return clickEvent();
    //  }
    // }


    //function () {
    //if (d3.select(this).node().__data__.id === undefined){
    //console.log("test success");
    //}
    //}




    //clickEvent);

    //plot.attr("transform", 'translate(-400, -400)')
    plot.attr("transform", `scale(${newscale}) translate(-${plotx},-${ploty})`)
    //translate(-${delta_x},-${delta_y})
    //plot.attr("transform", 'translate(-200, -200)')
    //plot.attr("transform", "scale(2)")
    // d3.select('#counties').attr("transform", 'translate(-400, -400)')
    // d3.select('#states').attr("transform", 'translate(-400, -400)')

    // function getscale(myscale){
    //     return `scale${myscale}!`
    // }



    function onlyUnique(value, index, array) {
        return array.indexOf(value) === index;
    }

    var uniqueClusters = test_data_wellbeing.filter(onlyUnique)
    uniqueClusters.sort();

    console.log(uniqueClusters);

    var x_leg = 900
    var y_leg = 50
    var interval = 17

    d3.select('#plot').append("g").attr("id", "legend")

    uniqueClusters.forEach(function (item, index) {
        d3.select('#legend').append('rect')
            .attr("x", x_leg)
            .attr("y", y_leg + (index * interval))
            .attr("width", 12)
            .attr("height", 12)
            .attr('fill', color_2[item]);

        d3.select('#legend')
            .append("text")
            .attr("id", "legend-text")
            .attr("x", x_leg + 14)
            .attr("y", y_leg + 10 + (index * interval))
            .text(String("Cluster " + String((item + 1))))

    }

    );




    // for (let i = 0; i < 10; i++){
    //     d3.select('#legend').append('rect')
    //         .attr("x", x_leg)
    //         .attr("y", y_leg + (i * interval))
    //         .attr("width", 12)
    //         .attr("height", 12)
    //         .attr('fill', color_2[i]);
    //
    //     d3.select('#legend')
    //         .append("text")
    //         .attr("id", "legend-text")
    //         .attr("x", x_leg + 14)
    //         .attr("y", y_leg + 10 + (i * interval))
    //         .text(String("Cluster " + String(i)))


}

