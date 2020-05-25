const d3 = require('d3');
const fs = require('fs');
const csvPath = '../raw_data/final_count_new.csv'

let csvdata = fs.readFileSync(csvPath, 'utf-8')
let dataArray = d3.csvParse(csvdata)
console.log(dataArray);
let stratify = d3.stratify()
	.id(d => {return d.icd})
	.parentId(d => {return d.parent})
	(dataArray);
fs.writeFileSync('../app/icd_tree.json', JSON.stringify(dataArray));
