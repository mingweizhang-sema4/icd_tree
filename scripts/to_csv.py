import pandas as pd
import xml.etree.ElementTree as ET

XML_PATH = '../raw_data/icd10cm_tabular_2020.xml'
CSV_PATH = '../raw_data/icd10_with_parent.csv'
chapter_icd_list = [
	'A00-B99', 'C00-D49', 'D50-D89', 'E00-E89', 'F01-F99', 'G00-G99', 'H00-H59', 
	'H60-H95', 'I00-I99', 'J00-J99', 'K00-K95', 'L00-L99', 'M00-M99', 'N00-N99', 
	'O00-O9A', 'P00-P96', 'Q00-Q99', 'R00-R99', 'S00-T88', 'V00-Y99', 'Z00-Z99'
	]

def importdata(path):
	xmltree = ET.parse(path)
	root = xmltree.getroot()
	return root

def trim_tree(element):
	interested = element.findall('chapter')
	allsub = list(element)
	for child in allsub:
		if child not in interested:
			element.remove(child)

def get_list(source):
	result_list = [['','root','root node']]
	for chapter in source:
		chapter_desc = _get_description(chapter)
		chapter_name = chapter[0].text
		chapter_icd = chapter_icd_list[int(chapter_name)-1]
		result_list.append(['root', chapter_icd, chapter_desc])
		section_list = _get_section_info(chapter)
		for section_tuple in section_list:
			section_icd = section_tuple[0]
			section_obj = section_tuple[1]
			section_desc = _get_description(section_obj)
			result_list.append([chapter_icd, section_icd, section_desc])
			diagnosis = section_obj.findall('diag')
			for diagnose in diagnosis:
				_get_diag_detail(diagnose, section_icd, result_list)
	
	return result_list
			
def _get_description(element):
	return element.find('desc').text

def _get_section_info(chapter_node):
	sections = chapter_node.findall('section')
	section_list = []
	for section in sections:
		section_id = section.attrib['id']
		section_list.append((section_id,section))
	return section_list 

def _get_diag_detail(diag_node, parent_icd, table):
	icd = diag_node.find('name').text
	desc = diag_node.find('desc').text
	table.append([parent_icd, icd, desc])
	children = diag_node.findall('diag')
	if len(children) > 0:
		for child in children:
			_get_diag_detail(child, icd, table)

def export_data(data, path):
	df = pd.DataFrame(data, columns = ['parent', 'icd', 'description'])
	df.to_csv(path, index=False)

def main():
	root_node = importdata(XML_PATH)
	trim_tree(root_node)
	result = get_list(root_node)
	export_data(result, CSV_PATH)

if __name__ == "__main__":
	main()
