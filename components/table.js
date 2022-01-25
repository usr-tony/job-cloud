import * as d3 from 'd3'

var database = require('./data.json');
const padding = 20;
const height = window.screen.height * 0.6 ;
const width = window.screen.width * 0.5;
const btm_pad = height * 0.4
const backgroundColor = 'black'
const cols_per_page = 10
var database = require('./data.json')

function RenderTable (index) {
	const data = database[index].data.slice(0,30)
	//set y scale
	var yscale = d3.scaleLinear()
		.domain([0, parseFloat(data[0][1])])
		.range([height - btm_pad, padding]);
	// set x scale
	var xscale = d3.scaleLinear()
		.domain([0, 10])
		.range([0, width])
	// lets graph zoom and pan as required
	var transform = {x:0}
	var zoom = d3.zoom() 
		.on("zoom", (e) => {
			var dx = e.transform.x - transform.x; // gets change in coordinates thanks to mouse drag
			if (Math.abs(dx) > 3) g.interrupt(); // interrupts transition defined near bottom of function if the user zooms
			transform = e.transform;
			var currX = g.attr('transform').match(/-{0,1}[0-9]+\.?\d*/g); // gets the current x coordinates
			var nx = parseFloat(currX[0]) + dx 
			if (nx > 0) nx = 0; // sets min translate
			let max_translate = -width * 0.1 * (data.length - cols_per_page + 1) - 200
			if (nx < max_translate) nx = max_translate
			g.attr('transform', 'translate(' + nx + ',0)')
		})
	d3.select('#table').selectAll('*').remove() // clears the element before appending to it
	var svg = d3.select('#table').append('svg')
		.attr('height', height)
		.attr('width', width)
		.style('background-color', backgroundColor)
		.style('fill','white')
		.style('color', 'white')
		.attr('cursor', 'move')
		.style('font-family', 'monospace')
		.style('border-style', 'dashed')
		.style('border-color', 'white')
		.style('border-width', '1px')
		.call(zoom)
		.on('wheel.zoom', null) // disables scroll wheel zoom 
		.on('dblclick.zoom', () => {
			g.transition()
			.duration(200)
			.ease(d3.easeLinear)
			.attr('transform', 'translate(0, 0)')
		})
	
	
	var g = svg.append('g') // contains everything else
		.attr('transform', 'translate(0, 0)')
	//draws a bunch of rects	
	var rect_width = 15
	let rect_transition_dur = 500
	let min_height = 30 // min height of columns
	let miny = height - btm_pad - min_height
	var rects = g.selectAll('rect')
		.data(data)
		.enter()
		.append('rect') 
		.attr('x', (d, i) => xscale(i + 1))
		.attr('y', height - btm_pad - 40 )
		.attr('width', rect_width)
		.attr('height', 40)
		.transition()
		.duration(rect_transition_dur)
		.attr('height', d => {
			let h = yscale(data[0][1] - d[1]) - padding
			if (h < min_height) h = min_height;
			return h
		})
		.attr('y', (d) => {
			let y = yscale(parseFloat(d[1]))
			if (y > miny) y = miny;
			return y
		})

	// adds column numbers
	let xoffset = 2
	let yoffset = 2
	let degrees = 90;
	var col_nums = g.selectAll('.col-num')
		.data(data)
		.enter()
		.append('text')
		.style('fill', 'black')
		.text(d => d[1])
		.attr('class', 'col-num')
		.attr('transform', (d,i) => {
			let y = height - btm_pad + yoffset - 40
			let x = xscale(i + 1) + xoffset
			return 'translate(' + x + ', ' + y + ') rotate(' + degrees + ')'
		})
		.transition()
		.duration(rect_transition_dur)
		.attr('transform', (d,i) => {
			let y = yscale(d[1]) + yoffset;
			if (y > miny) y = miny + yoffset;
			let x = xscale(i + 1) + xoffset;
			return 'translate(' + x + ', ' + y + ') rotate(' + degrees + ')'
		})
		

	// appends text to bottom columns
	var btm_axis = g.selectAll('.btm-axis')
		.data(data)
		.enter()
		.append('text')
		.text(d => d[0])
		.attr('class', 'btm-axis')
		.attr('transform', (d, i) => {
			let degrees = 45
			let y = height - btm_pad + 20
			let x = xscale(i + 1)
			return 'translate(' + x + ', ' + y + ') rotate(' + degrees + ')'
		})
	
	var btm_ticks = g.selectAll('line')
		.data(data)
		.enter()
		.append('line')
		.attr('x1', (d, i) => xscale(i + 1) + rect_width / 2)
		.attr('y1', height - btm_pad)
		.attr('x2', (d, i) => xscale(i + 1) + rect_width / 2)
		.attr('y2', height - btm_pad + 10)
		.style('stroke', 'white')
	var g0 = svg.append('g') // contains the y axis
		.attr('opacity', 1)
		
		.attr('transform', 'translate(40, 0)')
	var btm_line = g0.append('line')
		.attr('x1', 0)
		.attr('y1', height - btm_pad)
		.attr('x2', 99999)
		.attr('y2', height - btm_pad)
		.style('stroke', 'white')
	
	// adds a black box at the y axis to stop bar chart from overlapping
	var left_box = g0.append('rect')
		.attr('width', 40)
		.attr('height', height - btm_pad + 10)
		.attr('transform', 'translate(-40, 0)')
		.style('fill', backgroundColor)

	g0.call(d3.axisLeft(yscale).ticks(3))
	
	// adds auto movement to the main graph, this movement is interrupted when panning is initiated by the user
	g.transition( 
		d3.transition()
		.duration(15000)
		.delay(5000)
		.ease(d3.easeLinear)
	)
		.attr('transform', 'translate(-1500, 0)')
}
	
export { RenderTable, database };
	
