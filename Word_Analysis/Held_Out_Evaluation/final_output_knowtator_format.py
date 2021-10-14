import os
import re
import gzip
import argparse
import numpy as np
import nltk.data
import sys
# import termcolor
# from termcolor import colored, cprint
from xml.etree import ElementTree as ET
from xml.dom import minidom
import multiprocessing as mp
import functools
import resource, sys
from emoji import UNICODE_EMOJI
import demoji
# demoji.download_codes()
from datetime import date
from lxml import etree
from nltk.tokenize.punkt import PunktSentenceTokenizer

##based on automatic_ontology_insertion.py script in corpus construction under IAA


def read_in_all_lcs_path(all_lcs_file_path, ontologies, broad_categories, ontology_file_path):
	all_lcs_dict = {}  # lc -> [ignorance_type]
	all_ignorance_types = []

	# create all_lcs_dict: lc -> [regex, ignorance_type]
	with open('%s' % all_lcs_file_path, 'r') as all_lcs_file:
		next(all_lcs_file)
		for line in all_lcs_file:
			lc, regex, it = line.strip('\n').split('\t')
			if it.lower() in ontologies:
				all_ignorance_types += [it]
				if all_lcs_dict.get(lc):
					print('multiple ignorance types for lexical cue', lc, it)
					all_lcs_dict[lc] += [it]

				else:
					all_lcs_dict[lc] = [it]
			elif it.lower() in broad_categories:
				pass
			else:
				raise Exception('ERROR: Issue with the all_lcs_file missing ontologies!')

	##gather all lcs that have a 0_ in front of it and save them for later to insert into the ontology
	all_weird_lcs = [] #list of all lcs with 0_ in front

	parser = etree.XMLParser(ns_clean=True, attribute_defaults=True, dtd_validation=True, load_dtd=True,
							 remove_blank_text=True, recover=True)
	ontology_of_ignorance_tree = etree.parse(ontology_file_path)
	doc_info = ontology_of_ignorance_tree.docinfo

	root = ontology_of_ignorance_tree.getroot()

	for declaration in root.iter('{http://www.w3.org/2002/07/owl#}Declaration'):
		for i, child in enumerate(declaration):
			if '0_' in child.attrib['IRI'].replace('#',''):
				# print('got here', child.attrib['IRI'].replace('#',''))
				all_weird_lcs += [child.attrib['IRI'].replace('#','')]

	return all_lcs_dict, all_weird_lcs




def read_in_bionlp_data(pmc_bionlp_file_path):
	#read in the bionlp data and output a dictionary from the relation # (T#) to the information (ignorance_category, span, text)
	pmc_bionlp_dict = {} #dict from relation (T#) -> (ignorance_categry, span, text)

	with open(pmc_bionlp_file_path, 'r+') as pmc_biolp_file:
		for line in pmc_biolp_file:
			line_info = line.strip('\n').split('\t')
			t_num = line_info[0]
			text = line_info[2]

			if ';' in line_info[1]:
				indices_list = []
				disc_info = line_info[1].split(';')
				for j, d in enumerate(disc_info):
					if j == 0:
						ignorance_category, s1, e1 = d.split(' ')
						# indices1 = (s1,e1)
						indices_list += [(s1,e1)]
					else:
						s, e = d.split(' ')
						indices_list += [(s,e)]

			else:
				ignorance_category, text_start, text_end = line_info[1].split(' ')
				indices_list = [(text_start, text_end)]


			if pmc_bionlp_dict.get(t_num):
				raise Exception('ERROR: Issue with the t num repeating!')
			else:
				pmc_bionlp_dict[t_num] = (ignorance_category, indices_list, text)

	return pmc_bionlp_dict



def xml_creation(pmc_doc_path, pmc_article_file_path, algo, file_type, pmc_bionlp_dict, all_lcs_dict, xml_output_path, weird_lcs):
	"""
	Create a new xml file of annotations based on the regex automatic preprocessing for one document at a time to paralellize
	:param pmc_doc_path: pmc file path to know what document we have and how to name the annotation file:
	:param all_occurrence_dict: a dictionary from (ontology_cue, ignorance_type) -> [regex, occurrences_list] to be used in the creation of the xml files automatically
	:param xml_output_path: the output file path for the xml files (ideally to the Annotations folder for knowtator)
	:param all_lcs: a list of all the linguistic cues inserted into the ontology from the previous script all_linguistic_cues()
	:return:


	<?xml version="1.0" encoding="UTF-8" standalone="no"?>
	<knowtator-project>
	  <document id="PMC6056931.nxml.gz" text-file="PMC6056931.nxml.gz.txt">
		<annotation annotator="Default" id="PMC6056931.nxml.gz-1" type="identity">
		  <class id="important"/>
		  <span end="192" id="PMC6056931.nxml.gz-2" start="183">important</span>
		</annotation>
	  </document>
	</knowtator-project>

	"""


	##FILE OUTPUT NAME
	# print(pmc_doc_path)
	print(pmc_doc_path)
	pmc_output_name = pmc_doc_path.split('/')[-1].replace('.bionlp', '').split('_')[-1]
	print(pmc_output_name)

	##THE FULL TEXT DOCUMENT
	pmc_full_text_file = open(pmc_article_file_path, 'r+')
	pmc_full_text = pmc_full_text_file.read()  # the whole pmc file text - all lowercase
	# raise Exception('hold')

	##CREATE THE XML FILE WITH HEADERS AND STRUCTURE
	##TODO: need to add the encoding and standalone as node declarations!!!


		#SET THE ELEMENTS OF THE TREE:


	knowtator_project = ET.Element('knowtator-project') #root element
	doc_element = ET.SubElement(knowtator_project, 'document')

		##WITHIN THE DOCUMENT SET ALWAYS


	##ADD IN EACH ANNOTATION - MAKING SURE TO TAKE ONLY ONES WITH OCCURRENCES OF LCS
		# PUT IN TEXT - SET = ADDING AN ATTRIBUTE
		# all_occurrence_dict[(ontology_cue, ignorance_type)] = [regex_cue, cue_occurrence_list]


	#<document id="PMC4488777.nxml.gz" text-file="PMC4488777.nxml.gz.txt">
	doc_element.set('id', '%s.nxml.gz' %(pmc_output_name))
	doc_element.set('text-file', '%s.nxml.gz.txt' %(pmc_output_name))

	##loop over all occurrences to get them all under the documents: # (ontology_cue, ignorance_type, index_to_keep) -> [regex, occurrences_list]
	iterator = 1
	new_pred_lcs_count = 0 #count of how many new lcs predicted

	# dict from relation (T#) -> (ignorance_categry, [span], text)
	for t_num, info in pmc_bionlp_dict.items():
		##setting up the annotation xml portion
		annotation = ET.SubElement(doc_element, 'annotation')
		class_id = ET.SubElement(annotation, 'class')

		annotation.set('annotator', 'Default')
		annotation.set('id', '%s.nxml.gz-%s' % (pmc_output_name, iterator))
		annotation.set('type', 'identity')

		iterator += 1 #update the iterator since we used it



		##all the info from the pmc_bionlp_dict
		ignorance_category, span_list, text = info
		if ignorance_category.lower() == 'ignorance' and 'binary' in file_type.lower():
			ignorance_category = 'Epistemics' #the top of the hierarchy of the ignorance taxonomy
		elif ignorance_category.lower() not in ontologies:
			print(info)
			print(file_type)
			print(ignorance_category)
			raise Exception('ERROR: Issue with ignorance category not in the ontologies list!')
		else:
			pass

		##fix the trailing ... or leading ... #TODO: move this up - need to add .replace(' ','_')
		lexical_cue_text = text.replace(' ... ', '...').replace(' ...', '...').replace('... ', '...')
		if lexical_cue_text.startswith('...'):
			lexical_cue_text = lexical_cue_text[3:]
		elif lexical_cue_text.endswith('...'):
			lexical_cue_text = lexical_cue_text[:-3]
		elif lexical_cue_text.endswith(' '):
			lexical_cue_text = lexical_cue_text[:-1]
		else:
			pass

		spanned_text_list = lexical_cue_text.split('...')

		final_lc_list = [] #list of all the pieces with no spaces for lexical cue stuff
		final_spanned_text_list = [] #list of all the pieces with spaces
		##confirm the span is good and we have the correct lexical cue
		for j, indices in enumerate(span_list):
			s, e = indices
			spanned_text = spanned_text_list[j]


			#check that the text is the same as from the article - confirming the indices
			if spanned_text.lower() != pmc_full_text[int(s):int(e)].lower():
				# print(spanned_text.lower())
				# print(pmc_full_text[int(s):int(e)].lower())
				#dash issue
				if '-' in spanned_text.lower() and (spanned_text.lower().replace(' - ','-') == pmc_full_text[int(s):int(e)].lower() or spanned_text.lower().replace('- ','-') == pmc_full_text[int(s):int(e)].lower() or spanned_text.lower().replace(' -','-') == pmc_full_text[int(s):int(e)].lower()):
					# print('got here')
					spanned_text = pmc_full_text[int(s):int(e)]
				elif '–' in spanned_text.lower() and (spanned_text.lower().replace(' – ','–') == pmc_full_text[int(s):int(e)].lower() or spanned_text.lower().replace('– ','–') == pmc_full_text[int(s):int(e)].lower() or spanned_text.lower().replace(' –','–') == pmc_full_text[int(s):int(e)].lower()):
					spanned_text = pmc_full_text[int(s):int(e)]
				#comma issue
				elif ',' in spanned_text.lower() and spanned_text.lower().replace(' ,', ',') == pmc_full_text[int(s):int(e)].lower():
					spanned_text = pmc_full_text[int(s):int(e)]
				##contraction issue
				elif '’' in spanned_text.lower() and (spanned_text.lower().replace(' ’ ', '’') == pmc_full_text[int(s):int(e)].lower() or spanned_text.lower().replace('’ ', '’') == pmc_full_text[int(s):int(e)].lower()):
					spanned_text = pmc_full_text[int(s):int(e)]
				##parentheses issue
				elif ')' in spanned_text.lower() and spanned_text.lower().replace(' )', ')').replace('( ', '(') == pmc_full_text[int(s):int(e)].lower():
					spanned_text = pmc_full_text[int(s):int(e)]
				elif '[' in spanned_text.lower() and spanned_text.lower().replace('[ ', '[').replace(' ]', ']') == pmc_full_text[int(s):int(e)].lower():
					spanned_text = pmc_full_text[int(s):int(e)]
				##slash issue
				elif '/' in spanned_text.lower() and spanned_text.lower().replace(' / ', '/') == pmc_full_text[int(s):int(e)].lower():
					spanned_text = pmc_full_text[int(s):int(e)]
				else:

					print(pmc_doc_path)
					print(algo)

					print(indices)
					print([lexical_cue_text])
					print(span_list)
					print([spanned_text.lower()])
					print([pmc_full_text[int(s):int(e)].lower()])
					raise Exception('ERROR: Issue with spanned text continuing throughout!')
			else:
				pass

			final_lc_list += [spanned_text.replace(' ', '_').lower()]
			final_spanned_text_list += [spanned_text]

		##put everything together
		final_lc = '...'.join(final_lc_list)
		final_spanned_text = '...'.join(final_spanned_text_list)


		##check if the lc is weird or not - #TODO: fix the text here so that the final_lc is good - knowtator_text below
		if '0_%s' %(final_lc) in weird_lcs:
			final_lc = '0_%s' %(final_lc)
		else:
			pass


		##set the class_id for the lexical cue
		if all_lcs_dict.get(final_lc):
			possible_it_list = all_lcs_dict[final_lc]
			#confirm that we only have one possible it per lexical cue from all_lcs_dict
			if len(possible_it_list) > 2:
				print(len(possible_it_list))
				raise Exception('ERROR: Issue with multiple options for ignorance categories')
			else:
				possible_it = possible_it_list[0]

			##determine if the lexical cue is to the same ignorance category or not
			# same ignorance types so we are good
			if possible_it.lower() == ignorance_category.lower():
				final_it = possible_it.lower()
				class_id.set('id', '%s' % (final_lc))

			# different ignorance types so we put it to the ignorance category at large instead of the default (exception)
			else:
				if 'binary' in file_type:
					final_it = ignorance_category #Epistemics with an upper case E
				else:
					final_it = ignorance_category.lower() #otherwise lower case

				class_id.set('id', '%s' % (final_it))


		#a new lexical prediction outputted as the ignorance category
		else:
			if 'binary' in file_type:
				class_id.set('id', '%s' % (ignorance_category)) #Epistemics with capital E
			else:
				class_id.set('id', '%s' % (ignorance_category.lower())) #otherwise lowercase

			new_pred_lcs_count += 1 ##new prediction not in lcs



		# print(pmc_full_text[start:end])
		# print(all_starts)
		# print(all_ends)
		for j, indices in enumerate(span_list):
			span = ET.SubElement(annotation, 'span')
			s, e = indices
			spanned_text = final_spanned_text_list[j]
			# set all span information in xml tree
			span.set('end', '%s' % (e))
			span.set('id', '%s.nxml.gz-%s' % (pmc_output_name, iterator))
			span.set('start', '%s' % (s))
			span.text = '%s' % spanned_text

			iterator += 1 #update it since we used it




	##OUTPUT THE XML FILE TO THE ANNOTATIONS FILE

	xml_annotations_file = minidom.parseString(ET.tostring(knowtator_project)).toprettyxml(indent="   ")
	with open('%s%s.nxml.gz.xml.%s.xml' %(xml_output_path, pmc_output_name, algo), "w") as file_output:
		file_output.write(xml_annotations_file)



	return new_pred_lcs_count



if __name__=='__main__':
	# all_ontology_inserted_lcs_path = '/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/0_Development_Pre_natal_nutrition/Prenatal_Nutrition_Python_Scripts/ALL_ONTOLOGY_INSERTED_LCS.txt'

	parser = argparse.ArgumentParser()

	parser.add_argument('-ontologies', type=str, help='a list of ontologies to use delimited with , no spaces')
	parser.add_argument('-all_lcs_path', type=str, help='the file path to the all_lcs current ontology file')
	parser.add_argument('-ontology_file_path', type=str, help='file path to the ontology owl file')
	parser.add_argument('-broad_categories', type=str, help='a list of the broad ontology categories delimited with , no spaces')
	parser.add_argument('-article_path', type=str, help='file path the articles')
	parser.add_argument('-xml_folder', type=str, help='folder for the output xml files for knowtator')
	parser.add_argument('-algos', type=str, help='a list of the algorithms to use delimited with ,')
	parser.add_argument('-bionlp_folder', type=str,
						help='folder for the .bionlp formats')
	parser.add_argument('-result_folders', type=str,
						help='a list of folders to the results of the span detection models matching the algos list delimited with ,')
	parser.add_argument('-results_path', type=str,
						help='file path to the results folders')
	parser.add_argument('-evaluation_files', type=str, help='a list of the files to be evaluated delimited with ,')
	parser.add_argument('-file_types', type=str,
						help='folder names of the output for all the different categories to output')

	args = parser.parse_args()


	##grab everything from the newest ontology
	# ontology_file_path = '/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/1_First_Full_Annotation_Task_9_13_19/Ontologies/Ontology_Of_Ignorance.owl'

	# broad_categories = ['EPISTEMICS', 'BARRIERS', 'LEVELS_OF_EVIDENCE']
	broad_categories = args.broad_categories.split(',')
	ontologies = args.ontologies.split(',')
	result_folders = args.result_folders.split(',')
	algos = args.algos.split(',')
	evaluation_files = args.evaluation_files.split(',')
	file_types = args.file_types.split(',')


	##grab all lexical cues!
	all_lcs_dict, all_weird_lcs = read_in_all_lcs_path(args.all_lcs_path, ontologies, broad_categories, args.ontology_file_path)
	print('Weird LCs with 0_ at the beginning:', all_weird_lcs)

	# weird_lcs = ['unexpected_observation', 'difficult_task', 'important_considerations', 'claim', 'model', 'possible_understanding']


	### PER ALGORITHM WE READ IN THE BIONLP FILES AND CREATE THE XML FILES
	for i, algo in enumerate(algos):
		# bionlp_file_path = args.results_path + result_folders[i] + '/' + args.bionlp_folder
		# xml_output_file_path =  args.results_path + result_folders[i] + '/' + args.xml_folder

		##loop over the type of files - '0_all_combined,1_binary_combined,13_separate_combined'
		for file_type in file_types:
			print(file_type)
			bionlp_file_path = args.results_path + result_folders[i] + '/' + args.bionlp_folder + file_type + '/'
			xml_output_file_path = args.results_path + result_folders[i] + '/' + args.xml_folder + file_type + '/'

			##read in the bionlp files - make sure we only take the evaluation files
			directory_new_pred_count_lcs_count = 0
			for root, directories, filenames in os.walk(bionlp_file_path):
				for filename in sorted(filenames):
					if filename.endswith('.bionlp') and algo.upper() in filename and filename.replace('.bionlp', '').split('_')[
						-1] in evaluation_files:
						print(filename)

						##read in the bionlp files
						pmc_bionlp_dict = read_in_bionlp_data(root+filename) #dict from relation (T#) -> (ignorance_categry, [span], text)

						print(len(pmc_bionlp_dict.keys()))

						pmc_article_file_path =  '%s%s' %(args.article_path, filename.split('_')[-1].replace('bionlp', 'nxml.gz.txt'))
						##use these to create the xml file
						new_pred_lcs_count = xml_creation(root+filename, pmc_article_file_path, algo, file_type, pmc_bionlp_dict, all_lcs_dict, xml_output_file_path, all_weird_lcs)
						directory_new_pred_count_lcs_count += new_pred_lcs_count
						# raise Exception('hold')


			print('new lexical cue predictions count:', directory_new_pred_count_lcs_count)




	##TODO: add summary stats for the files processed possibly

	# with open('%spreprocess_summary_info_%s.txt' %(output_summary_path, date.today()), 'w+') as preprocess_summary_file:
	# 	preprocess_summary_file.write('%s\n' %'SUMMARY FILE FOR PREPROCESS USING REGULAR EXPRESSIONS')
	# 	preprocess_summary_file.write('\t%s\n' %('preprocess rules to get rid of: or, is, if, even, here, how  in the middle of a sentence'))
	# 	preprocess_summary_file.write('\t%s\n\n' %'preprocess rules to only keep the largest span if the starts are the same')
	#
	# 	preprocess_summary_file.write('%s\n' %('SUMMARY INFORMATION:'))
	# 	preprocess_summary_file.write('\t%s\t%s\n\n' %('total number of preprocessed documents (docs with cues):',f))
	#
	#
	#
	# 	##pmc_id -> [num_cues_per_doc, num_unique_ignorance_types, list of unique_ignorance_types, num_cues_per_section, unique_ignorance_types_per_section]
	#
	# 	preprocess_summary_file.write('%s\t%s\t%s\t%s\t%s\n' %('FILENAME', 'NUMBER OF CUES PER DOCUMENT', 'NUMBER OF UNIQUE IGNORANCE TYPES PER DOCUMENT','LIST OF UNIQUE IGNORANCE TYPES', 'PER SECTION INFORMATION BELOW'))
	# 	for doc in info_per_doc.keys():
	# 		preprocess_summary_file.write('%s\t%s\t%s\t%s\n' %(doc, info_per_doc[doc][0], info_per_doc[doc][1], info_per_doc[doc][2]))
	#
	# 		##section info
	# 		for p in range(len(info_per_doc[doc][3])):
	# 			preprocess_summary_file.write('\t%s' % info_per_doc[doc][3][p][0])
	# 		preprocess_summary_file.write('\n')
	#
	# 		##number of cues per section
	# 		for p in range(len(info_per_doc[doc][3])):
	# 			preprocess_summary_file.write('\t%s' % info_per_doc[doc][4][p])
	# 		preprocess_summary_file.write('\n')
	#
	# 		# number of unique ignorance types per section
	# 		for p in range(len(info_per_doc[doc][3])):
	# 			preprocess_summary_file.write('\t%s' % len(info_per_doc[doc][5][p]))
	# 		preprocess_summary_file.write('\n')
	#





