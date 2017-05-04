$(document).ready(function () {

	var data = [[], [], [], []];
	d3.csv("PatientA-risk.csv", function (data0) {
		d3.csv("PatientC-risk.csv", function (data1) {
			d3.csv("PatientD-risk.csv", function (data2) {
				d3.csv("PatientE-risk.csv", function (data3) {
					data[0] = data0;
					data[1] = data1;
					data[2] = data2;
					data[3] = data3;
					for (var i = 1; i <= 4; i++) {

						var chartArr = [];
						var chartDivArr = [];

						// create the real time chart
						chartArr[i] = icuChart()
							.title("ICU " + data[i - 1][0].icustay_id + " :: Chance of Developing Sepsis in Next 8 Hours")
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

						// start the data generator
						dataGenerator(data, chartArr[i], i, 0, {
							temp: 0,
							press: 0,
							resp: 0,
							o2sat: 0
						});
					}
				});
			});
		});
	});

	// configure the data generator

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
	function dataGenerator(data, chart, chartIndex, dataIndex, prevData) {
		setTimeout(function () {
			var now = new Date(new Date().getTime());

			// create new data item
			var obj;
			var prob = parseFloat(data[chartIndex - 1][dataIndex].risk_score);
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

			if (isNaN(prevData.temp) || prevData.temp == 0)
				prevData.temp = parseInt(data[chartIndex - 1][dataIndex]["223761"]).toFixed(0);
			if (isNaN(prevData.press) || prevData.press == 0)
				prevData.press = parseInt(data[chartIndex - 1][dataIndex]["220052"]).toFixed(0);
			if (isNaN(prevData.resp) || prevData.resp == 0)
				prevData.resp = parseInt(data[chartIndex - 1][dataIndex]["224690"]).toFixed(0);
			if (isNaN(prevData.o2sat) || prevData.o2sat == 0)
				prevData.temp = parseInt(data[chartIndex - 1][dataIndex]["220277"]).toFixed(0);

			var change = "";
			if (prevData.temp != parseInt(data[chartIndex - 1][dataIndex]["223761"]).toFixed(0)) {
				change = change + "Temperature ";
				if (prevData.temp > parseInt(data[chartIndex - 1][dataIndex]["223761"]).toFixed(0)) {
					change = change + '<i class="fa fa-chevron-down" aria-hidden="true"></i> ';
				} else {
					change = change + '<i class="fa fa-chevron-up" aria-hidden="true"></i> ';
				}
			}
			if (prevData.press != parseInt(data[chartIndex - 1][dataIndex]["220052"]).toFixed(0)) {
				change = change + "Blood Pressure ";
				if (prevData.press > parseInt(data[chartIndex - 1][dataIndex]["220052"]).toFixed(0)) {
					change = change + '<i class="fa fa-chevron-down" aria-hidden="true"></i> ';
				} else {
					change = change + '<i class="fa fa-chevron-up" aria-hidden="true"></i> ';
				}
			}
			if (prevData.resp != parseInt(data[chartIndex - 1][dataIndex]["224690"]).toFixed(0)) {
				change = change + "Respiratory Rate ";
				if (prevData.resp > parseInt(data[chartIndex - 1][dataIndex]["224690"]).toFixed(0)) {
					change = change + '<i class="fa fa-chevron-down" aria-hidden="true"></i> ';
				} else {
					change = change + '<i class="fa fa-chevron-up" aria-hidden="true"></i> ';
				}
			}
			if (prevData.o2sat != parseInt(data[chartIndex - 1][dataIndex]["220277"]).toFixed(0)) {
				change = change + "02 Sat ";
				if (prevData.o2sat > parseInt(data[chartIndex - 1][dataIndex]["220277"]).toFixed(0)) {
					change = change + '<i class="fa fa-chevron-down" aria-hidden="true"></i> ';
				} else {
					change = change + '<i class="fa fa-chevron-up" aria-hidden="true"></i> ';
				}
			}

			obj = {
				time: now,
				color: color,
				opacity: 1,
				category: prob,
				type: "circle",
				size: 6,
				temp: parseInt(data[chartIndex - 1][dataIndex]["223761"]).toFixed(0),
				press: parseInt(data[chartIndex - 1][dataIndex]["220052"]).toFixed(0),
				resp: parseInt(data[chartIndex - 1][dataIndex]["224690"]).toFixed(0),
				o2sat: parseInt(data[chartIndex - 1][dataIndex]["220277"]).toFixed(0),
				prevData: prevData,
				change: change
			};

			// send the datum to the chart
			chart.datum(obj);

			// drive data into the chart at average interval of five seconds
			// here, set the timeout to roughly five seconds
			timeout = Math.round(timeScale(normal()));

			// do forever
			dataGenerator(data, chart, chartIndex, dataIndex + 1, prevData);
		}, timeout);
	}
});