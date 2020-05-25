const margin = {
	top: 20,
	right: 120,
	bottom: 20,
	left: 120
},
	width = 500 - margin.left - margin.right,
	height = 500 - margin.top - margin.bottom,
	fontSize = '12px',
	radius = 4.5;
	
let diagonal = d3.linkHorizontal()
	.x(function(d) { return d.y })
	.y(function(d) { return d.x });

let duration = 750
let root = d3.stratify()
	.id(d => { return d.icd })
	.parentId(d => { return d.parent })
	(dataArray);

let treemap = d3.tree().nodeSize([20, null]);

let searchResult = []

let svg = d3.select('body').append('svg')
	.attr("width", width + margin.right + margin.left)
	.attr("height", height + margin.top + margin.bottom)
	.append("g")
	.attr("transform", "translate(" +
		margin.left + "," + margin.top + ")");

initTree()

function collapse(d) {
	if (d.children) {
		d._children = d.children
		d.children.forEach(collapse)
		d.children = null
	}
}

function initTree(){
	const color_list = [
		'Pink', 'Salmon', 'DarkRed', 'Red', 'Orange', 
		'Yellow', 'Lime', 'Green', 'SpringGreen', 'Aquamarine',
		'Teal', 'Cyan', 'SkyBlue', 'Blue', 'Navy',
		'Indigo', 'Purple', 'DarkViolet', 'SlateBlue', 'Violet', 'Lavender'
	]
	let color_index = 0, color_to_add;

	function addColorForChapter(d) {
		color_to_add = color_list[color_index++]
		d.color = color_to_add
		d.children.forEach(addColor)
	}

	function addColor(d) {
		d.color = color_to_add
		if (d.children) {
			d.children.forEach(addColor)
		}
	}
	root.x0 = height / 2;
	root.y0 = 0;
	root.color = 'black';
	root.children.forEach(addColorForChapter);
	root.children.forEach(collapse);
	update(root)
}

function update(source) {
	treeData = treemap(root)
	let roof = 0
	let translateY = Number(svg.attr('transform').split(/[,\s]/)[1].split(')')[0]);
	let nodes = treeData.descendants(),
		links = treeData.links();
	nodes.forEach(d => {
		if (d.x < roof) {
			roof = d.x
		}
	})
	roof = Math.abs(roof)
	svg.transition()
			.duration(duration)
			.attr('transform', 'translate(' + margin.left + ',' + (roof + margin.top) + ')');
	//Indicate the left side depth for specific level (circal point as center)
	var leftDepth = { 0: 0 };
	//Indicate the right side depth for specific level (circal point as center)
	var rightDepth = { 0: 0 };

	//Calculate maximum length of selected nodes in different levels
	nodes.forEach(function (d) {
		var _nameLength = d.data.description.length * 6 + 30;
		if (d.depth !== 0) {
			if (!leftDepth.hasOwnProperty(d.depth)) {
				leftDepth[d.depth] = 0;
				rightDepth[d.depth] = 0;
			}
			//Only calculate the point without child and without showed child
			if (!d.children && !d._children && rightDepth[d.depth] < _nameLength) {
				rightDepth[d.depth] = _nameLength;
			}
			//Only calculate the point with child(ren) or with showed child(ren)
			if ((d.children || d._children) && leftDepth[d.depth] < _nameLength) {
				leftDepth[d.depth] = _nameLength;
			}
		}
	});

	//Calculate the transform information for each node.
	nodes.forEach(function (d) {
		if (d.depth === 0) {
			d.y = 0;
		} else {
			var _y = 0,
				_length = d.depth;

			for (var i = 1; i <= _length; i++) {
				if (leftDepth[i] === 0) {
					//Give constant depth if no point has child or has showed child
					if (rightDepth[i - 1]) {
						_y += rightDepth[i - 1];
					} else {
						_y += 50;
					}
				} else {
					if (i > 1) {
						_y += leftDepth[i] + rightDepth[i - 1];
						if (leftDepth[i] > 0 && rightDepth[i - 1] > 0) {
							_y -= 50;
						} else {
							_y -= 0;
						}
					} else {
						_y += leftDepth[i];
					}
				}
			}
			d.y = _y;
		}
	});

	// ****************** Nodes section ***************************
	var node = svg.selectAll("g.node")
			.data(nodes, function (d) {
				return d.id || (d.id = ++i);
			});

	// Enter any new nodes at the parent's previous position.
	var nodeEnter = node.enter().append("svg:g")
		.attr("class", "node")
		.attr("transform", function (d) {
			return "translate(" + source.y0 + "," + source.x0 + ")";
		})
		.on("click", function (d) {
			toggle(d);
		});

	nodeEnter.append("svg:circle")
		.attr("r", 1e-6)
		.style("stroke", function (d) {
			return d.color;
		})
		.style("fill", function (d) {
			return (d._children ? d.color : "#fff");
		});

	var nodeContent = '';
	var nodeText = nodeEnter.append("svg:text")
		.attr("x", function (d) {
			return d.children || d._children ? -10 : 10;
		})
		.attr("dy", ".35em")
		.attr('font-size', fontSize)
		.attr("text-anchor", function (d) {
			return d.children || d._children ? "end" : "start";
		})
		.text(function (d) {
			let combined = d.data.icd != 'root' ? d.data.icd + " " + d.data.description + " :" + d.data.pc : d.data.description + " :" + d.data.pc 
			return combined
		})
		.style("fill-opacity", 1e-6);

	// Transition nodes to their new position.
	let nodeUpdate = nodeEnter.merge(node);
	nodeUpdate.transition()
		.duration(duration)
		.attr("transform", function (d) {
			return "translate(" + d.y + "," + d.x + ")";
		});

	nodeUpdate.select("circle")
		.attr("r", radius)
		.style("fill", function (d) {
			return d._children ? d.color : "#fff";
		});

	nodeUpdate.select("text")
		.style("fill-opacity", 1)
		.style("font-size", fontSize);

	// Transition exiting nodes to the parent's new position.
	var nodeExit = node.exit().transition()
		.duration(duration)
		.attr("transform", function (d) {
			return "translate(" + source.y + "," + source.x + ")";
		})
		.remove();

	nodeExit.select("circle")
		.attr("r", 1e-6);

	nodeExit.select("text")
		.style("fill-opacity", 1e-6);

	// ****************** Links section ***************************
	let link = svg.selectAll("path.link")
		.data(links,function (d) {
			return d.target.id;
		});

	// Enter any new links at the parent's previous position.
	let linkEnter = link.enter().insert("svg:path", "g")
		.attr("class", "link")
		.attr("d", function (d) {
			var o = {x: source.x0, y: source.y0};
			return diagonal({source: o, target: o});
		})

	// Transition links to their new position.
	let linkUpdate = linkEnter.merge(link);
	linkUpdate.transition()
		.duration(duration)
		.attr("d", diagonal);

	// Transition exiting nodes to the parent's new position.
	link.exit().transition()
		.duration(duration)
		.attr("d", function (d) {
			var o = {x: source.x, y: source.y};
			return diagonal({source: o, target: o});
		})
		.remove();

	// Stash the old positions for transition.
	nodes.forEach(function (d) {
		d.x0 = d.x;
		d.y0 = d.y;
	});
	resizeSVG(rightDepth);
}

function toggle(d) {
	if (d.children) {
		d._children = d.children;
		d.children = null;
	} else {
		d.children = d._children;
		d._children = null;
	}
	update(d)
}

function resizeSVG(rightDepth) {
	let nodes = root.descendants(),
		maxHeight = 0,
		maxWidth = 0,
		lastDepth = 0;

	nodes.forEach(function (d) {
		if (d.x > maxHeight) {
			maxHeight = d.x;
		}

		if (d.y > maxWidth) {
			maxWidth = d.y;
		}
	});
	maxHeight += 10
	maxHeight *= 2;
	

	lastDepth = rightDepth[Math.max.apply(Math, (Object.keys(rightDepth)).map(function (item) {
		return Number(item);
	}))];
	maxWidth = maxWidth + 200 + lastDepth;

	if (500 < maxWidth) {
		d3.select("svg").attr("width", maxWidth);
	} else {
		d3.select("svg").attr("width", 500);
	}

	if (500 < maxHeight) {
		d3.select("svg").attr("height", maxHeight);
	} else {
		d3.select("svg").attr("height", 500);
	}
}

function condenseChildren(d){
	if(d.children){
		d.children.forEach(condenseChildren)
		toggle(d)
	}
}

function collapseAll(){
	root.children.forEach(condenseChildren)
	update(root)
}

function searchByNodeName(searchKey) {
	searchResult = []
	collapseAll()
}