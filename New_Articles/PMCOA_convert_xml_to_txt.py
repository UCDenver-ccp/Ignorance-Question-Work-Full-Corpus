import argparse
import xml.etree.ElementTree as ET
import os


def convert_xml_to_txt(xml_file_path, article):
	##output PMC####.nxml.gz.txt
	# print(xml_file_path.split('.BioC-full')[0])
	# raise Exception('break')
	with open(xml_file_path.split('.BioC-full')[0], 'w+') as text_file_output:
		# print(text_file_output)
		tree = ET.parse(xml_file_path)
		root = tree.getroot()

		section_type = None
		current_section = None
		same_section = False
		fig_count = 1
		table_count = 1
		##loop over each passage and provide the section type and offset (span start of the passage)
		for passage in root.iter('passage'):

			for child in passage:
				if child.tag == 'infon':
					if child.attrib['key'] == 'section_type':
						section_type = child.text
						# print(section_type)
						# print(current_section)
						if current_section is None:
							current_section = section_type
						elif current_section == section_type:
							same_section = True
						else:
							current_section = section_type
							same_section = False




					else:
						pass
				elif child.tag == 'text':
					if section_type:
						# print('TEXT INFO!')
						# print('CURENT_SECTION', current_section)
						# print('SAME SECTION', same_section)
						text = child.text
						# print(text)

						##print out stuff
						if section_type.upper() == 'TITLE':
							text_file_output.write('%s\n\n' %text)

						elif section_type.upper() == 'ABSTRACT':
							if not same_section:
								text_file_output.write('%s\n\n' %('Abstract'))
							else:
								pass

							text_file_output.write('%s\n\n' %(text))

						elif section_type.upper() in ['FIG', 'TABLE']:
							if section_type.upper() == 'FIG':
								parens_text = 'Fig'
								count = fig_count
								fig_count += 1
								text_file_output.write('%s (%s): %s %s\n\n' % ('Caption', parens_text, section_type.upper(), count))
							else:
								parens_text = 'TABLE-WRAP'
								count = table_count

								##only print out for the table if the first time!
								if not same_section:
									text_file_output.write('%s (%s): %s %s\n\n' % ('Caption', parens_text, section_type.upper(), count))
									table_count += 1
								else:
									pass

							text_file_output.write('%s\n\n' %(text))

						#not including references
						elif section_type.upper() == 'REF':
							pass

						else:
							# if not same_section:
							text_file_output.write('%s\n\n' %text)




					else:
						raise Exception('ERROR: Issue with section type occuring!')

				else:
					pass

			# # print(section_type, offset)
			# if section_type and offset:
			# 	if pmc_section_dict.get(section_type):
			# 		pass
			# 	else:
			# 		pmc_section_dict[section_type] = int(offset)
			#
			#
			# else:
			# 	raise Exception('ERROR: POSSIBLE ERROR WITH SECTION TYPE INFORMATION!')


if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('-article_list', type=str, help='the list of articles delimited with , and no spaces between them (include PMC)')
	parser.add_argument('-pmcoa_BioC_folder', type=str, help='the file path to the BioC folder')

	args = parser.parse_args()

	article_list = args.article_list.split(',')
	print(article_list)

	for article in article_list:
		BioC_file = '%s%s' %(article,'.nxml.gz.txt.BioC-full_text.xml')
		convert_xml_to_txt('%s%s' %(args.pmcoa_BioC_folder, BioC_file), article)