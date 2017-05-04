$(document).ready(function () {
	
	var icuIdArr = ['1','2','3','4'];
	
	// mean and deviation for generation of time intervals
	var tX = 5; // time constant, multiple of one second
	var meanMs = 1000 * tX, // milliseconds
	dev = 200 * tX; // std dev

	// define time scale
	var timeScale = d3.scale.linear()
		.domain([300 * tX, 1700 * tX])
		.range([300 * tX, 1700 * tX])
		.clamp(true);

	// define function that returns normally distributed random numbers
	var normal = d3.random.normal(meanMs, dev);
	
	var timeout = 0;

	// define data generator
	function dataGenerator(chart, index, prevData) {
		setTimeout(function () {
			

			$.get("http://127.0.0.1:8080/drive/rest/enrichment_manager/entity_profile/get/Patient/" + index, function( data ) {
				// Example API
				//{
				//  "name": "sepsisPrediction", 
				//  "singleValue": {
				//		"boolList": [], 
				//		"double": 0.202914407, 
				//		"doubleList": [], 
				//		"integerList": [], 
				//		"longList": [], 
				//		"stringList": []
				//  }
				//}
				
				var now = new Date(new Date().getTime());
				
				// create new data item
				var obj;
				var prob = parseFloat(data.singleValue["double"]);
				var color = d3.rgb("white");
				if (prob >= 0.9) {
					color = d3.rgb("#a50026");
				} else if (prob >= 0.8) {
					color = d3.rgb("#d73027");
				} else if (prob >= 0.7) {
					color = d3.rgb("#f46d43");
				} else if (prob >= 0.6) {
					color = d3.rgb("#fdae61");
				} else if (prob >= 0.5) {
					color = d3.rgb("#fee08b");
				} else if (prob >= 0.4) {
					color = d3.rgb("#d9ef8b");
				} else if (prob >= 0.3) {
					color = d3.rgb("#a6d96a");
				} else if (prob >= 0.2) {
					color = d3.rgb("#66bd63");
				} else if (prob >= 0.2) {
					color = d3.rgb("#1a9850");
				} else if (prob >= 0.0) {
					color = d3.rgb("#006837");
				}

				obj = {
					time: now, // This is just for simulation, else use time from API
					color: color,
					opacity: 1,
					category: prob,
					type: "circle",
					size: 6,
					temp: 0,
					press: 0,
					resp: 0,
					o2sat:0,
					prevData: prevData,
					change: "-"
				};

				// send the datum to the chart
				chart.datum(obj);

				// drive data into the chart at average interval of five seconds
				// here, set the timeout to roughly five seconds
				timeout = Math.round(timeScale(normal()));

				// do forever
				dataGenerator(chart, index, {
							temp: 0,
							press: 0,
							resp: 0,
							o2sat: 0
						});
			});
		}, timeout);
	}
	
	// create all the charts in the page
	var chartArr = [];
	var chartDivArr = [];
	for (var i = 1; i <= 4; i++) {
		// create the real time chart
		chartArr[i] = icuChart()
			.title("ICU " + icuIdArr[i - 1][0].icustay_id + " :: Chance of Developing Sepsis in Next 8 Hours")
			.yTitle("Probability of onset of Sepsis")
			.xTitle("Time")
			.yDomain([0.25, 0.5, 0.75, 1]) // initial y domain (note array)
			.border(true)
			.width($("#viewDiv" + i).width() - 20)
			.height($("#viewDiv" + i).height() - 20);

		// invoke the chart
		chartDivArr[i] = d3.select("#viewDiv" + i).append("div")
			.attr("id", "chartDiv" + i)
			.call(chartArr[i]);
			
		dataGenerator(chartArr[i], i, {
							temp: 0,
							press: 0,
							resp: 0,
							o2sat: 0
						});
	}
});