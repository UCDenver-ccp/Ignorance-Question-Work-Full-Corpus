import os
import numpy as np
import pandas as pd
import argparse
import ast
from lxml import etree
import xml
import xml.etree.ElementTree as ET
import random
from datetime import date



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



def article_date_info(article, date_info_path, file_extension):
	tree = ET.parse('%s%s%s' %(date_info_path, article, file_extension))
	root = tree.getroot()

	i = 0
	for passage in root.iter('passage'):
		for child in passage:
			if child.tag == 'infon':
				if child.attrib['key'] == 'year':
					pmc_date = child.text
					i += 1
					break
				else:
					pass
		break
	if i > 1:
		print(pmc_date)
		print(i)
		raise Exception('ERROR: There may be more than one date!!')
	else:
		pass

	print(pmc_date)
	# raise Exception('/hold')
	return pmc_date




def article_OBO_info(article, OBO_bionlp_file_path, OBO_ontologies, OBO_model_dict):
	#initialize dictionary
	article_OBO_dict = {}
	article_OBO_unique_dict = {} #OBO -> unique OBO_ids



	for OBO in OBO_ontologies:
		article_OBO_dict[OBO] = [] #list of (OBO_ID, text, span)
		article_OBO_unique_dict[OBO] = set()

		##grab all OBO info for each article
		OBO_model = OBO_model_dict[OBO]

		#CHEBI_biobert_model_local_PMC1247630.nxml.gz.bionlp
		if OBO_model.lower() == 'biobert':
			article_file_name = '%s_%s_%s_%s%s' %(OBO, OBO_model.lower(), 'model_local', article, '.nxml.gz.bionlp')

		#CHEBI_crf_model_full_5cv_local_PMC2722408.nxml.gz.bionlp
		elif OBO_model.lower() == 'crf':
			article_file_name = '%s_%s_%s_%s%s' %(OBO, OBO_model.lower(), 'model_full_5cv_local', article, '.nxml.gz.bionlp')

		else:
			raise Exception('ERROR: Model not supported: right now only biobert or crf')

		try:
			with open('%s%s/%s' %(OBO_bionlp_file_path, OBO, article_file_name), 'r+') as OBO_article_file:
				#T1457	CHEBI:51277 668 679	soft drinks (31225 31232;31237 31242)
				for line in OBO_article_file:
					num_id, info, text = line.strip('\n').split('\t')
					info = info.strip(';') #get rid of trailing ;
					OBO_id = info[:info.find(' ')]
					span = [s.split(' ') for s in info[info.find(' ') + 1:].split(';')] #list of the lists of spans if discontinuous more than one - [['31225', '31232'], ['31237', '31242']] or [['19530', '19534']]

					# print(span)

					article_OBO_dict[OBO] += [(num_id, OBO_id, span, text)]
					article_OBO_unique_dict[OBO].add(OBO_id)

		except FileNotFoundError:
			#the file does not exist meaning that there are no annotations so it will be empty
			continue


	article_OBO_counts = [len(article_OBO_dict[OBO]) for OBO in article_OBO_dict.keys()]
	article_OBO_unique_counts = [len(article_OBO_unique_dict[OBO]) for OBO in article_OBO_unique_dict.keys()]


	return article_OBO_dict, article_OBO_counts, article_OBO_unique_dict, article_OBO_unique_counts



def get_ignorance_statement_info_per_article(article, ignorance_sentence_folder_path, ignorance_ontologies, ignorance_all_lcs_dict, ignorance_all_weird_lcs, ignorance_extra_ontology_concepts):
	##output all ignorance statements with info
	article_ignorance_statements_info = [] #list of all info
	article_sentence_id_dict = {}  # sentence_id -> [(sentence_text, sentence_indicies, ont_concept_list, ignorance_category_concept_list)]

	with open('%s%s%s' %(ignorance_sentence_folder_path, article, '.nxml.gz_sentence_info.txt')) as ignorance_sentence_file:
		next(ignorance_sentence_file)
		for line in ignorance_sentence_file:
			#PMCID	SENTENCE_NUMBER	SENTENCE	SENTENCE_INDICES	ONTOLOGY_CONCEPT_IDS_LIST
			#PMC6039335.nxml.gz	0	['Genetic, management, and nutritional factors affecting intramuscular fat deposition in beef cattle — A review\n\nAbstract\nIntramuscular fat (IMF) content in skeletal muscle including the longissimus dorsi muscle (LM), also known as marbling fat, is one of the most important factors determining beef quality in several countries including Korea, Japan, Australia, and the United States.']	(0, 384)	['affecting', 'important']

			pmcid, sentence_num, sentence_list, sent_indices, ont_concepts_list  = line.strip('\n').split('\t')
			sentence_text = ast.literal_eval(sentence_list)[0] #sentence text = string
			sent_indices = ast.literal_eval(sent_indices) #tuple
			ont_concepts_list = ast.literal_eval(ont_concepts_list) #list

			# print(type(sent_indices), type(sentence_text), type(ont_concepts_list))

			##collect only the ignorance statements
			if ont_concepts_list:
				##gather all the categories for the concepts - set() - we dont care about duplicates just the classification of the sentence
				ignorance_category_concept_list = []
				for c in ont_concepts_list:
					##c is an ignorance category already
					if c in ignorance_ontologies:
						ignorance_category_concept_list += [c.upper()]
					#c in the dictionary
					elif ignorance_all_lcs_dict.get(c):
						if len(ignorance_all_lcs_dict[c]) > 1:
							print('MULTIPLE LABLES:', c, ignorance_all_lcs_dict[c])
						else:
							pass

						ignorance_category_concept_list += [ignorance_all_lcs_dict[c][0].upper()]
					elif c in ignorance_all_weird_lcs:
						if len(ignorance_all_lcs_dict[c.replace('0_','')]) > 1:
							print('MULTIPLE LABLES:', c, ignorance_all_lcs_dict[c.replace('0_', '')])
						else:
							pass
						ignorance_category_concept_list += [ignorance_all_lcs_dict[c.replace('0_', '')][0].upper()]
					elif ignorance_extra_ontology_concepts.get(c):
						ignorance_category_concept_list += [ignorance_extra_ontology_concepts[c].upper()]
					else:
						print(c)
						raise Exception('ERROR: issue with ignorance ontology concepts being outside of the things!')

				if len(ont_concepts_list) != len(ignorance_category_concept_list):
					raise Exception('ERROR: Issue with finding all the ignorance categories')
				else:
					pass


				##we only need the set of ignorance_category_concept_list - (sentence_text, sent_indices, ont_concept_list, ignorance_category_concept_list)
				article_ignorance_statements_info += [('%s_%s' %(article, sentence_num), sentence_text, sent_indices, ont_concepts_list, ignorance_category_concept_list)]

				article_sentence_id_dict['%s_%s' %(article, sentence_num)] = (sentence_text, sent_indices, ont_concepts_list, ignorance_category_concept_list)

			#not ignorance statements
			else:
				article_sentence_id_dict['%s_%s' %(article, sentence_num)] = (sentence_text, sent_indices, ont_concepts_list, [])


	return article_ignorance_statements_info, int(sentence_num)+1, article_sentence_id_dict



def article_OBO_ignorance_overlap_info(article, OBO_ontologies, article_OBO_dict, ignorance_ontologies, article_ignorance_statements_info, total_ignorance_sentences, article_sentence_id_dict):
	#inputs
	##article_OBO_dict: article_OBO_dict[OBO] += [(num_id, OBO_id, span, text)]
	##article_ignorance_statements_info and total_ignorance_sentence: (sentence_text, sent_indices, ont_concept_list, ignorance_category_concept_list) and total_sentences

	#output
	full_article_OBO_id_dict = {} #OBO_id -> [(num_id, span, text)]

	article_OBO_ignorance_connect_dict = {} #dict from OBO -> [(OBO_num_ID, ignorance_sentence_ID)]
	for ont in OBO_ontologies:
		article_OBO_ignorance_connect_dict[ont] = []

	article_OBO_id_sentence_connect = {} #OBO_id + OBO_num_id -> sentence_id
	article_OBO_ids_no_ignorance = [] #list of OBO_id + OBO_num_ids

	article_OBO_ignorance_overlap_dict = {} #dict from ignorance category -> [[list of OBO_ids in order of OBOs]]
	for ignorance_category in ignorance_ontologies:
		article_OBO_ignorance_overlap_dict[ignorance_category.upper()] = [[] for a in OBO_ontologies]

	article_OBO_id_dict = {} #OBO_id -> [in_ignorance_count, out_ignorance_count]


	random_sentences_to_review = [] #(ignorance_sentence_id, sentence_text -> uppercase OBOs, OBO_text, OBO_id, ignorance_category_concept_list)


	for OBO in OBO_ontologies:
		# print(OBO)
		##TODO: per OBO_id: determine counts of if in an ignorance statement or not in one!!!

		all_OBO_info_list = article_OBO_dict[OBO]
		for OBO_info in all_OBO_info_list:
			OBO_num_ID, OBO_id, OBO_span, OBO_text = OBO_info

			# print(OBO_num_ID, OBO_id, OBO_span, OBO_text, OBO, article)
			if full_article_OBO_id_dict.get(OBO_id):
				full_article_OBO_id_dict[OBO_id] += [(OBO_num_ID, OBO_span, OBO_text)]
			else:
				full_article_OBO_id_dict[OBO_id] = [(OBO_num_ID, OBO_span, OBO_text)]

			OBO_span_flat_list = [int(a) for a in list(np.concatenate(OBO_span).flat)]
			# print(OBO_span_flat_list)
			OBO_min_start = min(OBO_span_flat_list)
			OBO_max_end = max(OBO_span_flat_list)

			random_sentence_num = random.randint(0, len(article_ignorance_statements_info)-1)
			no_OBOs = True #initialize

			for j, ignorance_info in enumerate(article_ignorance_statements_info):
				ignorance_sentence_id, ignorance_sentence_text, ignorance_sent_indices, ignorance_ont_concept_list, ignorance_category_concept_list = ignorance_info
				ignorance_category_concept_set = set(ignorance_category_concept_list)
				ignorance_sent_start, ignorance_sent_end = ignorance_sent_indices


				if ignorance_sent_start <= OBO_min_start and OBO_max_end <= ignorance_sent_end:
					##check that the OBO concept is in the sentence
					if '...' in OBO_text:
						disc_OBO_text = OBO_text.strip(' ...').split(' ... ')
						for d in disc_OBO_text:
							if d in ignorance_sentence_text:
								pass
							else:
								print(ignorance_sentence_text, ignorance_sent_indices)
								print(d, OBO_text, OBO_span_flat_list)
								raise Exception('ERROR: Issue with OBO text not in sentence text DISCONTINUOUS!!!')
					elif OBO_text in ignorance_sentence_text:
						pass
					else:
						print(ignorance_sentence_text, ignorance_sent_indices)
						print(OBO_text, OBO_span_flat_list)
						raise Exception('ERROR: Issue with OBO text not in sentence text!!!')

					##now we collect all the information
					article_OBO_ignorance_connect_dict[OBO] += [(OBO_num_ID, ignorance_sentence_id)]


					if article_OBO_id_sentence_connect.get('%s_%s' %(OBO_id, OBO_num_ID)):
						##duplicate entries in each ontology with combos
						#SO_EXT PMC3279448 T152 PMC3279448_13 also in GO_MF_EXT T152 but in same sentence so we are good!
						# enzymes CHEBI_GO_SO_EXT:enzyme
						if article_OBO_id_sentence_connect['%s_%s' %(OBO_id, OBO_num_ID)] == ignorance_sentence_id:
							print('DUPLICATE!')
							pass
						else:
							print('LABEL DUPLICATES DIFFERENT SENTENCES - LIST!')
							print(OBO_id, OBO_num_ID)
							print(ignorance_sentence_id)
							article_OBO_id_sentence_connect['%s_%s' % (OBO_id, OBO_num_ID)] = [article_OBO_id_sentence_connect['%s_%s' % (OBO_id, OBO_num_ID)], ignorance_sentence_id]
							print(article_OBO_id_sentence_connect['%s_%s' % (OBO_id, OBO_num_ID)])


					else:
						# print(OBO, OBO_num_ID, OBO_id)
						article_OBO_id_sentence_connect['%s_%s' %(OBO_id, OBO_num_ID)] = ignorance_sentence_id
						# raise Exception('hold')


					for ic in ignorance_category_concept_set:
						OBO_index = OBO_ontologies.index(OBO)
						article_OBO_ignorance_overlap_dict[ic.upper()][OBO_index] += [OBO_id]


					no_OBOs = False
					current_j = j
					break

				else:
					##collect the sentence the OBO_id is in no matter if ignorance or not
					no_OBOs = True



			##article_OBO_id_dict collect
			if no_OBOs:
				found_OBO_sentence = False
				##outside ignorance collect
				article_OBO_ids_no_ignorance += ['%s_%s' % (OBO_id, OBO_num_ID)]
				# if article_OBO_id_dict.get(OBO_id):
				# 	article_OBO_id_dict[OBO_id][1] += 1
				# else:
				# 	article_OBO_id_dict[OBO_id] = [0, 1]  # initialize outside ignorance statement and 0 for inside_count

				##collect sentence informaiton for the OBO:
				for sent_id in article_sentence_id_dict.keys():
					sent_text = article_sentence_id_dict[sent_id][0]
					sent_start, sent_end = article_sentence_id_dict[sent_id][1]
					# print(article_sentence_id_dict[sent_id])

					if sent_start <= OBO_min_start and OBO_max_end <= sent_end:
					##check that the OBO concept is in the sentence
						if '...' in OBO_text:
							disc_OBO_text = OBO_text.strip(' ...').split(' ... ')
							for d in disc_OBO_text:
								if d in sent_text.replace('\n',' ').replace('\u2002', ' '):
									pass
								else:
									print([sent_text.replace('\n',' ').replace('\u2002', ' ')], sent_start, sent_end)
									print(d, OBO_text, OBO_span_flat_list)
									raise Exception('ERROR: Issue with OBO text not in sentence text DISCONTINUOUS!!!')
						elif OBO_text in sent_text.replace('\n', ' ').replace('\u2002', ' ').replace('\u2009',' '):
							pass
						else:
							print([sent_text.replace('\n',' ').replace('\u2002', ' ').replace('\u2009',' ')])
							print([sent_text], sent_start, sent_end)
							print(OBO_text, OBO_span_flat_list)
							raise Exception('ERROR: Issue with OBO text not in sentence text!!!')

						##collect all the info
						if article_OBO_id_sentence_connect.get('%s_%s' % (OBO_id, OBO_num_ID)):
							if article_OBO_id_sentence_connect['%s_%s' % (OBO_id, OBO_num_ID)] == sent_id:
								print('DUPLICATE!')
								pass
							else:
								print('NO IGNORANCE: LABEL DUPLICATES DIFFERENT SENTENCES - LIST!')
								print(OBO_id, OBO_num_ID)
								print(sent_id)

								article_OBO_id_sentence_connect['%s_%s' %(OBO_id, OBO_num_ID)] = [article_OBO_id_sentence_connect['%s_%s' %(OBO_id, OBO_num_ID)] , sent_id]

								print(article_OBO_id_sentence_connect['%s_%s' %(OBO_id, OBO_num_ID)])

								# print('Error here!')
								# print(OBO, article, OBO_num_ID, sent_id)
								# print(OBO_text, OBO_id)
								# print(sent_text)
								# print(article_OBO_id_sentence_connect['%s_%s' % (OBO_id, OBO_num_ID)])
								# raise Exception(
								# 	'ERROR: there should be no duplicate OBO_num_IDs especially using the article PMCID outside of ignorance statements')
							found_OBO_sentence = True
							# print(OBO_id, OBO_num_ID, OBO_span, OBO_text)
							# print(sent_start, sent_end, sent_text)
							break
						else:
							article_OBO_id_sentence_connect['%s_%s' % (OBO_id, OBO_num_ID)] = sent_id
							found_OBO_sentence = True
							# print(OBO_id, OBO_num_ID, OBO_span, OBO_text)
							# print(sent_start, sent_end, sent_text)
							break
					else:
						##continue through
						pass
				##check that we found the sentence for the OBO - TODO!!!
				if found_OBO_sentence:
					# print('BEFORE', article_OBO_id_dict[OBO_id])
					if article_OBO_id_dict.get(OBO_id):
						# if article in ['PMC2727050','PMC2396486']:
						# 	print('BEFORE', article_OBO_id_dict[OBO_id])
						article_OBO_id_dict[OBO_id][1] += 1
					else:
						article_OBO_id_dict[OBO_id] = [0, 1]  # initialize outside ignorance statement and 0 for inside
					# pass
					# if article in ['PMC2727050','PMC2396486']:
					# 	print(article_OBO_id_dict[OBO_id])
				else:
					print(OBO_id, OBO_min_start, OBO_max_end, OBO_num_ID)
					raise Exception('ERROR: Issue with finding the sentence that contains the OBO without ignorance')

			else:
				#inside ignorance collect
				if article_OBO_id_dict.get(OBO_id):
					article_OBO_id_dict[OBO_id][0] += 1
				else:
					article_OBO_id_dict[OBO_id] = [1, 0]  # initialize in ignorance statement and 0 for outside


			##collect ignorance sentence for random check
			rand_ignorance_sentence_id, rand_ignorance_sentence_text, rand_ignorance_sent_indices, rand_ignorance_ont_concept_list, rand_ignorance_category_concept_list = article_ignorance_statements_info[random_sentence_num]
			if rand_ignorance_sentence_id in [b for (a,b) in article_OBO_ignorance_connect_dict[OBO]]:
				random_sentences_to_review += [[rand_ignorance_sentence_id, [rand_ignorance_sentence_text], rand_ignorance_ont_concept_list,rand_ignorance_category_concept_list, OBO_text, OBO_id, OBO_num_ID, OBO]]
			else:
				random_sentences_to_review += [[rand_ignorance_sentence_id, [rand_ignorance_sentence_text], rand_ignorance_ont_concept_list, rand_ignorance_category_concept_list]]



	##article_OBO_id_dict: #OBO_id -> [in_ignorance_count, out_ignorance_count]

	OBO_id_inside_ignorance_list = []
	OBO_id_outside_ignorance_list = []
	for OBO_id in article_OBO_id_dict.keys():
		OBO_id_sum = sum(article_OBO_id_dict[OBO_id])
		inside, outside = article_OBO_id_dict[OBO_id]

		if OBO_id_sum != 0:
			OBO_id_inside_ignorance_list += [(OBO_id, float(inside)/float(OBO_id_sum), OBO_id_sum)]
			OBO_id_outside_ignorance_list += [(OBO_id, float(outside)/float(OBO_id_sum), OBO_id_sum)]
		else:
			print(OBO_id, inside, outside)
			OBO_id_inside_ignorance_list += [(OBO_id, 0, inside)]
			OBO_id_outside_ignorance_list += [(OBO_id, 0, outside)]


	OBO_id_inside_ignorance_list_sorted = sorted(OBO_id_inside_ignorance_list, key=lambda x: x[1], reverse=True)
	OBO_id_outside_ignorance_list_sorted = sorted(OBO_id_outside_ignorance_list, key=lambda x: x[1], reverse=True)


	return article_OBO_ignorance_connect_dict, article_OBO_id_sentence_connect, article_OBO_ids_no_ignorance, article_OBO_ignorance_overlap_dict, random_sentences_to_review, OBO_id_inside_ignorance_list_sorted, OBO_id_outside_ignorance_list_sorted, full_article_OBO_id_dict







if __name__=='__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('-OBO_bionlp_file_path', type=str, help='the file path to the bionlp output files')
	parser.add_argument('-ignorance_ontologies', type=str, help='list of the ignorance ontologies delimited with , no spaces')
	parser.add_argument('-ignorance_broad_categories', type=str, help='list of the ignorance ontologies broad categories delimited with , no spaces')
	parser.add_argument('-ignorance_all_lcs_path', type=str, help='file path to the ignorance all_lcs_file')
	parser.add_argument('-ignorance_ontology_file_path', type=str, help='file path to the ignorance ontology file')
	parser.add_argument('-ignorance_extra_ontology_concepts', type=str, help='string dictionary of extra ignorance ontology concepts')
	parser.add_argument('-ignorance_article_path', type=str, help='path to the ignorance article text')
	parser.add_argument('-ignorance_tokenized_files_path', type=str, help='path to the ignnorance tokenized files')
	parser.add_argument('-ignorance_sentence_folder_path', type=str, help='folder for the pmcid sentence files for the ignorance sentences')
	parser.add_argument('-ignorance_date_info_path', type=str, help='path to the BioC section info with the date information in it')
	parser.add_argument('-ignorance_date_info_extension', type=str, help='the file extension for the date information')
	parser.add_argument('-OBO_ontologies', type=str, help='a list of ontologies to use delimited with ,')
	parser.add_argument('-evaluation_files', type=str, help='a list of files to evaluate delimited with ,')
	parser.add_argument('-OBO_model_dict', type=str, help='a dictionary for each OBO ontology to the correct model to use based on performance, OBOs should be all uppercase')
	parser.add_argument('-OBO_output_path', type=str, help='output folder path')
	parser.add_argument('-OBO_ignorance_overlap_path', type=str, help='the file path to the output for the OBO_ignorance_overlap path')


	args = parser.parse_args()


	OBO_ontologies = args.OBO_ontologies.split(',')
	evaluation_files = args.evaluation_files.split(',')
	OBO_model_dict = ast.literal_eval(args.OBO_model_dict)
	ignorance_ontologies = args.ignorance_ontologies.split(',')
	ignorance_broad_categories = args.ignorance_broad_categories.split(',')
	ignorance_extra_ontology_concepts = ast.literal_eval(args.ignorance_extra_ontology_concepts)


	##get all the ignorance lcs and ontology information
	ignorance_all_lcs_dict, ignorance_all_weird_lcs = read_in_all_lcs_path(args.ignorance_all_lcs_path, ignorance_ontologies, ignorance_broad_categories, args.ignorance_ontology_file_path)




	##output dataframes

	OBO_columns = OBO_ontologies + ['ARTICLE_SUMS']
	article_OBO_count_df = pd.DataFrame([], columns = OBO_columns)
	# print(article_OBO_count_df)

	OBO_colunms_unique = OBO_ontologies + ['UNIQUE_ARTICLE_SUMS']
	article_OBO_count_unique_df = pd.DataFrame([], columns = OBO_colunms_unique)
	all_article_OBO_unique_dict = {} #OBO -> sets of all OBO_ids
	for OBO in OBO_ontologies:
		all_article_OBO_unique_dict[OBO] = set()

	all_article_OBO_id_dict = {} #article -> OBO_id_dict
	all_article_OBO_ignorance_connect_dict = {} #article -> article_OBO_ignorance_connect_dict
	all_article_sentence_id_dict = {} #article -> article_sentence_id_dict
	all_article_OBO_sentence_connect = {} #article -> article_OBO_id_sentence_connect
	all_article_OBO_ids_no_ignorance = {} #article -> list of article_OBO_ids_no_ignorance

	full_OBO_ignorance_overlap_dict = {} #dict from ignorance category -> [[lists of OBO_ids]
	for ic in ignorance_ontologies:
		full_OBO_ignorance_overlap_dict[ic.upper()] = [[] for o in OBO_ontologies]

	article_OBO_id_inside_ignorance_dict = {} #article -> list of inside info
	article_OBO_id_outside_ignorance_dict = {} #artcile -> list of outside info

	article_date_dict = {} #article -> date


	all_random_sentences_to_review = []

	##per article information
	for article in evaluation_files:

		#article_OBO_dict[OBO] += [(num_id, OBO_id, span, text)]
		article_OBO_dict, article_OBO_counts, article_OBO_unique_dict, article_OBO_unique_counts = article_OBO_info(article, args.OBO_bionlp_file_path, OBO_ontologies, OBO_model_dict)
		# print(article_OBO_counts)
		article_OBO_count_df.loc[(len(article_OBO_count_df))] = article_OBO_counts + [0]
		article_OBO_count_unique_df.loc[len(article_OBO_count_unique_df)] = article_OBO_unique_counts + [0]
		for OBO in OBO_ontologies:
			all_article_OBO_unique_dict[OBO] = all_article_OBO_unique_dict[OBO].union(article_OBO_unique_dict[OBO])


		##(sentence_text, sent_indices, ont_concept_list, ignorance_category_concept_list) and total_sentences
		article_ignorance_statements_info, total_ignorance_sentences, article_sentence_id_dict = get_ignorance_statement_info_per_article(article, args.ignorance_sentence_folder_path, ignorance_ontologies, ignorance_all_lcs_dict, ignorance_all_weird_lcs, ignorance_extra_ontology_concepts)
		print(article, len(article_ignorance_statements_info), total_ignorance_sentences)
		all_article_sentence_id_dict[article] = article_sentence_id_dict



		##combine all the OBO and ignorance stuff
		article_OBO_ignorance_connect_dict, article_OBO_id_sentence_connect, article_OBO_ids_no_ignorance, article_OBO_ignorance_overlap_dict, random_sentences_to_review, OBO_id_inside_ignorance_list_sorted, OBO_id_outside_ignorance_list_sorted, full_article_OBO_id_dict = article_OBO_ignorance_overlap_info(article, OBO_ontologies, article_OBO_dict, ignorance_ontologies, article_ignorance_statements_info, total_ignorance_sentences, article_sentence_id_dict)

		all_article_OBO_id_dict[article] = full_article_OBO_id_dict
		all_article_OBO_ignorance_connect_dict[article] = article_OBO_ignorance_connect_dict
		all_article_OBO_sentence_connect[article] = article_OBO_id_sentence_connect
		all_article_OBO_ids_no_ignorance[article] = article_OBO_ids_no_ignorance

		article_OBO_id_inside_ignorance_dict[article] = OBO_id_inside_ignorance_list_sorted
		article_OBO_id_outside_ignorance_dict[article] = OBO_id_outside_ignorance_list_sorted

		all_random_sentences_to_review += random_sentences_to_review

		for ic in ignorance_ontologies:
			# print(article_OBO_ignorance_overlap_dict)
			for o in range(len(OBO_ontologies)):
				full_OBO_ignorance_overlap_dict[ic.upper()][o] += article_OBO_ignorance_overlap_dict[ic.upper()][o]

			# print(full_OBO_ignorance_overlap_dict)


		##all date information for each article
		#PMC1247630.nxml.gz.txt.BioC-full_text.xml
		##output the date!
		article_date_dict[article] = article_date_info(article, args.ignorance_date_info_path, args.ignorance_date_info_extension)


	##GET THE FULL COUNTS FOR THE OVERLAP BOTH FULL AND UNIQUE
	full_OBO_ignorance_overlap_count_dict = {}
	full_OBO_ignorance_overlap_count_unique_dict = {}
	sum_full_OBO_ignorance_overlap_unique_dict = {} #ignorance category -> [[set OBO_ids list]]
	sum_full_OBO_ignorance_overlap_count_unique_list = [set() for o in OBO_ontologies] #list of lists all sums over ignorance categories for each ontology in order of OBOs


	for ic in ignorance_ontologies:
		sum_full_OBO_ignorance_overlap_unique_dict[ic.upper()] = [set() for o in range(len(OBO_ontologies))]
	# print(full_OBO_ignorance_overlap_dict['FULL_UNKNOWN'][2])

	for ic in ignorance_ontologies:

		full_OBO_ignorance_overlap_count_dict[ic.upper()] = [len(full_OBO_ignorance_overlap_dict[ic.upper()][o]) for o in range(len(OBO_ontologies))]

		full_OBO_ignorance_overlap_count_unique_dict[ic.upper()] = [len(set(full_OBO_ignorance_overlap_dict[ic.upper()][o])) for o in range(len(OBO_ontologies))]

		for o in range(len(OBO_ontologies)):
			# print(set(full_OBO_ignorance_overlap_dict[ic.upper()][o]))
			# print(sum_full_OBO_ignorance_overlap_unique_dict[ic.upper()][o])
			sum_full_OBO_ignorance_overlap_count_unique_list[o] = sum_full_OBO_ignorance_overlap_count_unique_list[o].union(set(full_OBO_ignorance_overlap_dict[ic.upper()][o]))

	# print(sum_full_OBO_ignorance_overlap_count_unique_list[0])




	# raise Exception('hold')



	##outputs!

	##article date output
	# print(article_date_dict)
	# raise Exception('hold')
	article_date_df = pd.DataFrame(article_date_dict, index=[0])


	##change the indices of the columns to the articles
	article_OBO_count_df.index = evaluation_files

	##add new columns summing totals of the OBOs per article
	row_sums = list(article_OBO_count_df.sum(axis = 1))
	# print(row_sums)
	article_OBO_count_df['ARTICLE_SUMS'] = row_sums

	#add summary information by column adding a new row to the bottom - TODO!!!! (sum on columns and rows but be careful with EXT and not EXT since combined!)
	article_OBO_count_df.loc['OBO_SUM'] = article_OBO_count_df.sum()
	article_OBO_count_df.loc['OBO_AVERAGE'] = article_OBO_count_df.mean()
	article_OBO_count_df.loc['OBO_MEDIAN'] = article_OBO_count_df.median()


	##unique info
	article_OBO_count_unique_df.index = evaluation_files
	row_sums_1 = list(article_OBO_count_unique_df.sum(axis = 1))
	article_OBO_count_unique_df['UNIQUE_ARTICLE_SUMS'] = row_sums_1
	article_OBO_count_unique_df.loc['UNIQUE_OBO_SUMS (SET)'] = [len(all_article_OBO_unique_dict[OBO]) for OBO in OBO_ontologies] + [sum([len(all_article_OBO_unique_dict[OBO]) for OBO in OBO_ontologies])]
	article_OBO_count_unique_df.loc['UNIQUE_OBO_AVERAGE'] = article_OBO_count_unique_df.mean()
	article_OBO_count_unique_df.loc['UNIQUE_OBO_MEDIAN'] = article_OBO_count_unique_df.median()



	##ignorance and OBO overlaps!
	OBO_ignorance_columns = [i.upper() for i in ignorance_ontologies] + ['OBO_IGNORANCE_SUMS']
	OBO_ignorance_overlap_counts_df = pd.DataFrame(full_OBO_ignorance_overlap_count_dict, columns=OBO_ignorance_columns)
	OBO_ignorance_overlap_counts_df.index = OBO_ontologies
	# print(OBO_ignorance_overlap_counts_df)
	row_sums_2 = list(OBO_ignorance_overlap_counts_df.sum(axis=1))
	OBO_ignorance_overlap_counts_df['OBO_IGNORANCE_SUMS'] = row_sums_2
	OBO_ignorance_overlap_counts_df.loc['IGNORANCE_OBO_SUM'] = OBO_ignorance_overlap_counts_df.sum()
	OBO_ignorance_overlap_counts_df.loc['IGNORANCE_OBO_AVERAGE'] = OBO_ignorance_overlap_counts_df.mean()
	OBO_ignorance_overlap_counts_df.loc['IGNORANCE_OBO_MEDIAN'] = OBO_ignorance_overlap_counts_df.median()


	#unique
	OBO_ignorance_columns_unique = [i.upper() for i in ignorance_ontologies] + ['UNIQUE_OBO_IGNORANCE_SUMS (SET)']
	OBO_ignorance_overlap_counts_unique_df = pd.DataFrame(full_OBO_ignorance_overlap_count_unique_dict, columns=OBO_ignorance_columns_unique)
	OBO_ignorance_overlap_counts_unique_df.index = OBO_ontologies
	# print(OBO_ignorance_overlap_counts_df)
	row_sums_2 = [len(sum_full_OBO_ignorance_overlap_count_unique_list[o]) for o in range(len(OBO_ontologies))]
	OBO_ignorance_overlap_counts_unique_df['UNIQUE_OBO_IGNORANCE_SUMS (SET)'] = row_sums_2
	OBO_ignorance_overlap_counts_unique_df.loc['UNIQUE_IGNORANCE_OBO_SUM'] = OBO_ignorance_overlap_counts_unique_df.sum()
	OBO_ignorance_overlap_counts_unique_df.loc['UNIQUE_IGNORANCE_OBO_AVERAGE'] = OBO_ignorance_overlap_counts_unique_df.mean()
	OBO_ignorance_overlap_counts_unique_df.loc['UNIQUE_IGNORANCE_OBO_MEDIAN'] = OBO_ignorance_overlap_counts_unique_df.median()




	##top 3 for each ignorance category listed (OBO, count)
	top3_dict = {} #ignorance cateogry -> [(OBO, count)]
	for ic in ignorance_ontologies:
		OBO_overlap_counts = full_OBO_ignorance_overlap_dict[ic.upper()]
		zipped_lists = zip(OBO_ontologies, OBO_overlap_counts)
		# print(OBO_ontologies)
		# print(OBO_overlap_counts)
		zipped_pairs_list = list(zipped_lists) #tuples
		sorted_pairs = sorted(zipped_pairs_list, key=lambda x: x[1], reverse=True)

		top3_list = sorted_pairs[:3]
		top3_dict[ic.upper()] = top3_list

	OBO_ignorance_columns_top3 = [i.upper() for i in ignorance_ontologies]
	OBO_ignorance_overlap_counts_top3_df = pd.DataFrame(top3_dict, columns=OBO_ignorance_columns_top3)


	##relative ranked OBO list for overlap - for all OBOs
	relative_rankings_OBO_ignorance_overlap_dict = {} #ic -> [rankings]
	relative_rankings_OBO_ignorance_overlap_unique_dict = {} #ic -> [rankings]

	#full info
	full_OBO_sums = list(article_OBO_count_df.loc['OBO_SUM'])[:-1]
	# print(full_OBO_sums)

	#unique info
	full_OBO_sums_unique = list(article_OBO_count_unique_df.loc['UNIQUE_OBO_SUMS (SET)'])[:-1]
	# print(full_OBO_sums_unique)

	for ic in ignorance_ontologies:
		#initialize
		relative_rankings_OBO_ignorance_overlap_dict[ic.upper()] = []
		relative_rankings_OBO_ignorance_overlap_unique_dict[ic.upper()] = []

		for o in range(len(OBO_ontologies)):
			OBO_ignorance_overlap_count = full_OBO_ignorance_overlap_count_dict[ic.upper()][o]
			OBO_sum = full_OBO_sums[o]
			relative_rankings_OBO_ignorance_overlap_dict[ic.upper()] += [(float(OBO_ignorance_overlap_count)/float(OBO_sum))*100]

			OBO_ignorance_overlap_count_unique = full_OBO_ignorance_overlap_count_unique_dict[ic.upper()][o]
			OBO_sum_unique = full_OBO_sums_unique[o]
			relative_rankings_OBO_ignorance_overlap_unique_dict[ic.upper()] += [(float(OBO_ignorance_overlap_count_unique) / float(OBO_sum_unique))*100]

		##sort each list descending order
		zipped_lists_1 = zip(OBO_ontologies, relative_rankings_OBO_ignorance_overlap_dict[ic.upper()])
		zipped_pairs_list_1 = list(zipped_lists_1)  # tuples
		sorted_pairs_1 = sorted(zipped_pairs_list_1, key=lambda x: x[1], reverse=True)

		sorted_pairs_1_strings = [(obo, '%0.2f%%' %(ranking)) for obo, ranking in sorted_pairs_1]

		relative_rankings_OBO_ignorance_overlap_dict[ic.upper()] = sorted_pairs_1_strings

		zipped_lists_2 = zip(OBO_ontologies, relative_rankings_OBO_ignorance_overlap_unique_dict[ic.upper()])
		zipped_pairs_list_2 = list(zipped_lists_2)  # tuples
		sorted_pairs_2 = sorted(zipped_pairs_list_2, key=lambda x: x[1], reverse=True)

		sorted_pairs_2_strings = [(obo, '%0.2f%%' % (ranking)) for obo, ranking in sorted_pairs_2]

		relative_rankings_OBO_ignorance_overlap_unique_dict[ic.upper()] = sorted_pairs_2_strings


	# print(relative_rankings_OBO_ignorance_overlap_dict)
	# print(relative_rankings_OBO_ignorance_overlap_unique_dict)

	relative_rankings_OBO_ignorance_overlap_df = pd.DataFrame(relative_rankings_OBO_ignorance_overlap_dict, columns=OBO_ignorance_columns_top3)
	relative_rankings_OBO_ignorance_overlap_unique_df = pd.DataFrame(relative_rankings_OBO_ignorance_overlap_unique_dict, columns=OBO_ignorance_columns_top3)


	#TODO: figure out how to show this or what to say?
	##OBO_ids inside and outside of ignorance statement
	#need to make the lists the same lengths
	max_length_inside = max([len(article_OBO_id_inside_ignorance_dict[a]) for a in article_OBO_id_inside_ignorance_dict.keys()])
	max_length_outside = max([len(article_OBO_id_outside_ignorance_dict[a]) for a in article_OBO_id_outside_ignorance_dict.keys()])

	##take OBO_id if it meets specific criteria
	OBO_id_inside_article_list_dict = {} #OBO_id -> ([(article, inside_count, total)], count, total, ratio, set(OBO_text))
	OBO_id_outside_article_list_dict = {} #OBO_id -> ([(article, outside_count, total)], count, total, ratio, set(OBO_text))

	##pad the length for the dataframe with NA
	for article in evaluation_files:
		##output by OBO_id

		OBO_id_inside_info = article_OBO_id_inside_ignorance_dict[article]
		OBO_id_outside_info = article_OBO_id_outside_ignorance_dict[article]
		# print(OBO_id_inside_info[:10])
		for (OBO_id, inside_ratio, total) in OBO_id_inside_info:
			# if inside_ratio >= 0.8 and total > 1:
			if OBO_id_inside_article_list_dict.get(OBO_id):
				OBO_id_inside_article_list_dict[OBO_id][0] += [(article, inside_ratio * total, total)]
				OBO_id_inside_article_list_dict[OBO_id][1] += inside_ratio * total
				OBO_id_inside_article_list_dict[OBO_id][2] += total
			else:
				OBO_id_inside_article_list_dict[OBO_id] = [[(article, inside_ratio * total, total)], inside_ratio * total, total, 0, set()]
			# else:
			# 	pass

		for (OBO_id, outside_ratio, total) in OBO_id_outside_info:
			# if outside_ratio > 0.8 and total > 1:
			if OBO_id_outside_article_list_dict.get(OBO_id):
				OBO_id_outside_article_list_dict[OBO_id][0] += [(article, outside_ratio * total, total)]
				OBO_id_outside_article_list_dict[OBO_id][1] += outside_ratio * total
				OBO_id_outside_article_list_dict[OBO_id][2] += total
			else:
				OBO_id_outside_article_list_dict[OBO_id] = [[(article, outside_ratio * total, total)], outside_ratio * total, total, 0, set()]
			# else:
			# 	pass

		##pad all the information so we have the same length columns
		pad_num_inside = max_length_inside - len(article_OBO_id_inside_ignorance_dict[article])
		for p in range(pad_num_inside):
			article_OBO_id_inside_ignorance_dict[article] += ['NA']


		pad_num_outside = max_length_outside - len(article_OBO_id_outside_ignorance_dict[article])
		for p in range(pad_num_outside):
			article_OBO_id_outside_ignorance_dict[article] += ['NA']



	##rankings for all OBO_ids
	OBO_id_inside_ignorance_df = pd.DataFrame(article_OBO_id_inside_ignorance_dict, columns=evaluation_files)
	OBO_id_inside_ignorance_df.replace('NA',np.NaN)
	OBO_id_outside_ignorance_df = pd.DataFrame(article_OBO_id_outside_ignorance_dict, columns=evaluation_files)
	OBO_id_outside_ignorance_df.replace('NA',np.NaN)


	##OBO_ids in multiple articles, above 0.8, and in multiple sentences
	#	OBO_id_inside_article_list_dict = {} #OBO_id -> ([(article, inside_count, total)], count, total, ratio, set(OBO_text))
	# TODO: work with this to output the table overtime by OBO_id!
	for OBO_id, info in OBO_id_inside_article_list_dict.items():




		article_list, inside_count, inside_total, empty_ratio, OBO_text_set = info
		OBO_id_inside_article_list_dict[OBO_id][-2] = float(inside_count)/float(inside_total)

		# if len(article_list) > 1:
		if 'EXT' in args.OBO_ontologies:
			ext = 'EXT_'
		else:
			ext = ''


		##overlap full infor per OBO_id with all sentences!
		# if len(article_list) > 1:
		OBO_ignorance_article_overlap_inside_file = open('%s%s%s_%s_%s.txt' %(args.OBO_ignorance_overlap_path, ext, 'inside_ignorance', len(article_list), OBO_id.replace(':','-')), 'w+')

		OBO_ignorance_article_overlap_inside_file.write('%s:\t%s\n' %('OBO_ID', OBO_id))
		OBO_ignorance_article_overlap_inside_file.write('%s:\t%s\n\n' % ('NUMBER OF ARTICLES', len(article_list)))

		OBO_ignorance_article_overlap_inside_file.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' %('SENTENCE_ID', 'SENTENCE INDICES', 'SENTENCE', 'OBO CONCEPT', 'OBO SPAN', 'OBO NUM ID',  'IGNORANCE CONCEPTS', 'IGNORANCE CATEGORIES'))
		# else:
		# 	pass

		##timeline for specific OBO_ids
		OBO_id_specific_ignorance_info_file = open(
			'%s%s%s_%s_%s.txt' % (args.OBO_ignorance_overlap_path, ext, 'article_journey', len(article_list), OBO_id.replace(':', '-')), 'w+')

		OBO_id_specific_ignorance_info_file.write('%s\t%s\n' %('OBO_ID', OBO_id))




		# print(article_list)
		for a, (article, inside_count, total) in enumerate(article_list):

			#[('T2670', [['10327', '10333']], 'citrus'), ('T2672', [['10807', '10813']], 'citrus')]
			# print(all_article_OBO_id_dict[article][OBO_id])
			#{'PMC6000839_0': ('Major Maternal Dietary Patterns during Early Pregnancy and Their Association with Neonatal Anthropometric Measurement\n\nAbstract\n\nBackground\nAnthropometric measurements of newborn infant are widely assessed as determinants of maternal nutrition.', (0, 244), ['incomplete_evidence', 'association', 'association', 'determinants'], ['INCOMPLETE_EVIDENCE', 'SUPERFICIAL_RELATIONSHIP', 'SUPERFICIAL_RELATIONSHIP', 'SUPERFICIAL_RELATIONSHIP'])
			# print(all_article_sentence_id_dict[article])

			#use article_OBO_id_sentence_connect[OBO_obo_num_id] -> setnence_id
			for OBO_num_id, OBO_span, OBO_text in all_article_OBO_id_dict[article][OBO_id]:
				# print(article)
				full_obo_num_id = '%s_%s' %(OBO_id, OBO_num_id)
				sentence_id = all_article_OBO_sentence_connect[article][full_obo_num_id]
				# if article == 'PMC2396486':
				# 	print(full_obo_num_id) #CHEBI_PR_EXT:protein T141
				# 	print(type(sentence_id))
				# raise Exception('hold')
				if type(sentence_id) == list:
					for s in sentence_id:
						##TODO!!
						sentence_info = all_article_sentence_id_dict[article][s]
						if OBO_text:
							OBO_text_set.add(OBO_text)
							OBO_id_inside_article_list_dict[OBO_id][-1] = OBO_text_set
						else:
							print(OBO_num_id, OBO_span, OBO_text)
							raise Exception('ERROR: there is no OBO_text inside!?')

						if full_obo_num_id in all_article_OBO_ids_no_ignorance[article]:
							pass
						# elif len(article_list) > 1:
						else:
							OBO_ignorance_article_overlap_inside_file.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
							s, sentence_info[1], [sentence_info[0]], OBO_text, OBO_span, OBO_num_id,
							sentence_info[2], sentence_info[3]))
						# else:
							# pass
				else:
					sentence_info = all_article_sentence_id_dict[article][sentence_id]
					if OBO_text:
						OBO_text_set.add(OBO_text)
						OBO_id_inside_article_list_dict[OBO_id][-1] = OBO_text_set
					else:
						print(OBO_num_id, OBO_span, OBO_text)
						raise Exception('ERROR: there is no OBO_text inside!?')

					if full_obo_num_id in all_article_OBO_ids_no_ignorance[article]:
						pass
					# elif len(article_list) > 1:
					else:
						OBO_ignorance_article_overlap_inside_file.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (sentence_id, sentence_info[1], [sentence_info[0]], OBO_text, OBO_span, OBO_num_id, sentence_info[2], sentence_info[3]))
					# else:
					# 	pass


			## OBO id specific information over time with article info
			##'ARTICLE', 'YEAR', 'INSIDE IGNORANCE COUNT', 'OUTSIDE IGNORANCE COUNT', 'TOTAL', '% INSIDE', '% OUTSIDE'
			if a == 0:
				OBO_id_specific_ignorance_info_file.write('%s\t%s\n\n' %('OBO TEXT SET:', OBO_text_set))
				OBO_id_specific_ignorance_info_file.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
					'ARTICLE', 'YEAR', 'INSIDE IGNORANCE COUNT', 'OUTSIDE IGNORANCE COUNT', 'TOTAL', '% INSIDE',
					'% OUTSIDE'))
			else:
				pass


			OBO_id_specific_ignorance_info_file.write('%s\t%s\t%s\t%s\t%s\t%.2f\t%.2f\n' % (article, article_date_dict[article], round(inside_count), round(total-inside_count), total, float(inside_count)/float(total), float(total-inside_count)/float(total)))


	# raise Exception('hold')


	##OUTSIDE IGNORANCE STATEMENTS
	##OBO_ids in multiple articles, above 0.8, and in multiple sentences
	# 	OBO_id_outside_article_list_dict = {} #OBO_id -> ([article list], count, total, ratio, set(OBO_text))
	for OBO_id, info in OBO_id_outside_article_list_dict.items():
		article_list, outside_count, outside_total, empty_ratio, OBO_text_set = info
		OBO_id_outside_article_list_dict[OBO_id][-2] = float(outside_count)/float(outside_total)

		# if len(article_list) > 1:
		if 'EXT' in args.OBO_ontologies:
			ext = 'EXT_'
		else:
			ext = ''

		# if len(article_list) > 1:
		OBO_ignorance_article_overlap_outside_file = open('%s%s%s_%s_%s.txt' % (args.OBO_ignorance_overlap_path, ext, 'outside_ignorance', len(article_list), OBO_id.replace(':','-')),'w+')

		OBO_ignorance_article_overlap_outside_file.write('%s:\t%s\n' % ('OBO_ID', OBO_id))
		OBO_ignorance_article_overlap_outside_file.write('%s:\t%s\n\n' % ('NUMBER OF ARTICLES', len(article_list)))

		OBO_ignorance_article_overlap_outside_file.write('%s\t%s\t%s\t%s\t%s\t%s\n' % ('SENTENCE_ID', 'SENTENCE INDICES', 'SENTENCE', 'OBO CONCEPT', 'OBO SPAN', 'OBO NUM ID'))
		# else:
		# 	pass

		for (article, article_outside_count, total) in article_list:
			# [('T2670', [['10327', '10333']], 'citrus'), ('T2672', [['10807', '10813']], 'citrus')]
			# print(all_article_OBO_id_dict[article][OBO_id])
			# {'PMC6000839_0': ('Major Maternal Dietary Patterns during Early Pregnancy and Their Association with Neonatal Anthropometric Measurement\n\nAbstract\n\nBackground\nAnthropometric measurements of newborn infant are widely assessed as determinants of maternal nutrition.', (0, 244), ['incomplete_evidence', 'association', 'association', 'determinants'], ['INCOMPLETE_EVIDENCE', 'SUPERFICIAL_RELATIONSHIP', 'SUPERFICIAL_RELATIONSHIP', 'SUPERFICIAL_RELATIONSHIP'])
			# print(all_article_sentence_id_dict[article])

			# use article_OBO_id_sentence_connect[OBO_obo_num_id] -> setnence_id
			confirm_outside_count = 0
			for OBO_num_id, OBO_span, OBO_text in all_article_OBO_id_dict[article][OBO_id]:
				# print(article)
				full_obo_num_id = '%s_%s' % (OBO_id, OBO_num_id)
				if full_obo_num_id in all_article_OBO_ids_no_ignorance[article]:
					confirm_outside_count += 1
					sentence_id = all_article_OBO_sentence_connect[article][full_obo_num_id]
					# print(OBO_num_id)
					# print(sentence_id)

					if type(sentence_id) == list:

						# print('got here!')
						# confirm_outside_count -= 1
						#dupicate information accidentally that causes problems
						for s in sentence_id:
							sentence_info = all_article_sentence_id_dict[article][s]
							if OBO_text:
								OBO_text_set.add(OBO_text)
								OBO_id_outside_article_list_dict[OBO_id][-1] = OBO_text_set
							else:
								print(OBO_num_id, OBO_span, OBO_text)
								raise Exception('ERROR: there is no OBO_text outside!?')

							# if len(article_list) > 1:
							OBO_ignorance_article_overlap_outside_file.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (s, sentence_info[1], [sentence_info[0]], OBO_text, OBO_span, OBO_num_id))
							# else:
							# 	pass
					else:
						# confirm_outside_count += 1
						sentence_info = all_article_sentence_id_dict[article][sentence_id]
						if OBO_text:
							OBO_text_set.add(OBO_text)
							OBO_id_outside_article_list_dict[OBO_id][-1] = OBO_text_set
						else:
							print(OBO_num_id, OBO_span, OBO_text)
							raise Exception('ERROR: there is no OBO_text outside!?')


						# if len(article_list) > 1:
						OBO_ignorance_article_overlap_outside_file.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (sentence_id, sentence_info[1], [sentence_info[0]], OBO_text, OBO_span, OBO_num_id))
						# else:
						# 	pass

				#OBO_id + OBO_num_ID in ignorance!
				else:
					pass



			##confirm that we got all the outside OBO_id + OBO_num_IDs
			##TODO: unclear what the weirdness is but def with the duplicate scenario problem
			if article in ['PMC2727050', 'PMC2396486']:
				# print(article)
				# print(confirm_outside_count, round(article_outside_count))
				pass
			elif confirm_outside_count != round(article_outside_count):
				print(article)
				print(confirm_outside_count, round(article_outside_count))
				raise Exception('ERROR: Issue with counts of concepts not matching')
			else:
				pass



	##create dataframes with the summary stats
	# OBO_id_inside_article_list_dict = {}  # OBO_id -> ([article list], count, total, ratio, set(OBO_text))
	# OBO_id_outside_article_list_dict = {}  # OBO_id -> ([article list], count, total, ratio, set(OBO_text))

	OBO_id_inside_summary_dict = {}
	for OBO_id, info in OBO_id_inside_article_list_dict.items():
		# print(info)
		article_list, count, total, ratio, set_obo_text = info
		# if len(article_list) > 1:
		if set_obo_text:
			OBO_id_inside_summary_dict[OBO_id] = [len(article_list), count, total, ratio, set_obo_text]
		else:
			print(len(article_list), count, total, ratio, set_obo_text)
			raise Exception('ERROR: Issue with set obo text inside')
		# else:
		# 	pass

	OBO_id_outside_summary_dict = {}
	for OBO_id, info in OBO_id_outside_article_list_dict.items():
		article_list, count, total, ratio, set_obo_text = info
		# if len(article_list) > 1:

		##if a true outside OBO_id + OBO_num_ID it has set_obo_text otherwise it is empty
		if set_obo_text:
			OBO_id_outside_summary_dict[OBO_id] = [len(article_list), count, total, ratio, set_obo_text]

		##the
		else:
			if int(count) == 0:
				pass
			else:
				print(len(article_list), count, total, ratio, set_obo_text)
				raise Exception('ERROR: Issue with set obo text outside that should have stuff because of count!')
		# else:
		# 	pass


	row_indices = ['NUM ARTICLES', 'OBO COUNT', 'OBO TOTAL', 'RATIO', 'OBO_SET']
	OBO_id_inside_summary_df = pd.DataFrame(OBO_id_inside_summary_dict)
	OBO_id_inside_summary_df.index = row_indices

	OBO_id_outside_summary_df = pd.DataFrame(OBO_id_outside_summary_dict)
	OBO_id_outside_summary_df.index = row_indices




	##output the count dataframe if EXT or not
	if 'EXT' in args.OBO_ontologies:
		ext = '_EXT'
	else:
		ext = ''

	article_date_output_path_list = args.ignorance_date_info_path.split('/')[:-2]
	article_date_output_path = ''
	for a in article_date_output_path_list:
		article_date_output_path = article_date_output_path + a + '/'


	article_date_df.to_csv('%s%s.txt' %(article_date_output_path, 'article_date_info'), sep='\t')


	article_OBO_count_df.to_csv('%s%s%s.txt' % (args.OBO_output_path, 'OBO_overall_article_counts', ext), sep='\t', columns=OBO_columns)

	article_OBO_count_unique_df.to_csv('%s%s%s.txt' % (args.OBO_output_path, 'OBO_overall_article_counts_unique', ext), sep='\t', columns=OBO_colunms_unique)

	OBO_ignorance_overlap_counts_df.to_csv('%s%s%s.txt' % (args.OBO_output_path, 'OBO_ignorance_overlap_counts', ext), sep='\t', columns=OBO_ignorance_columns)

	OBO_ignorance_overlap_counts_unique_df.to_csv('%s%s%s.txt' % (args.OBO_output_path, 'OBO_ignorance_overlap_counts_unique', ext),
										   sep='\t', columns=OBO_ignorance_columns_unique)


	OBO_ignorance_overlap_counts_top3_df.to_csv('%s%s%s.txt' % (args.OBO_output_path, 'OBO_overall_article_counts_top3', ext), sep='\t',
								columns=OBO_ignorance_columns_top3)

	relative_rankings_OBO_ignorance_overlap_df.to_csv('%s%s%s.txt' % (args.OBO_output_path, 'OBO_overall_article_counts_ranked', ext), sep='\t',
													  columns=OBO_ignorance_columns_top3)

	relative_rankings_OBO_ignorance_overlap_unique_df.to_csv('%s%s%s.txt' % (args.OBO_output_path, 'OBO_overall_article_counts_unique_ranked', ext), sep='\t', columns=OBO_ignorance_columns_top3)

	OBO_id_inside_ignorance_df.to_csv('%s%s%s.txt' % (args.OBO_output_path, 'OBO_id_inside_ignorance_statements', ext), sep='\t', columns=evaluation_files)
	OBO_id_outside_ignorance_df.to_csv('%s%s%s.txt' % (args.OBO_output_path, 'OBO_id_outside_ignorance_statements', ext), sep='\t', columns=evaluation_files)



	OBO_id_inside_summary_df.to_csv('%s%s%s.txt' % (args.OBO_output_path, 'OBO_id_inside_ignorance_summary', ext), sep='\t')
	OBO_id_outside_summary_df.to_csv('%s%s%s.txt' % (args.OBO_output_path, 'OBO_id_outside_ignorance_summary', ext), sep='\t')



	##random sentences to review
	with open('%s%s%s_%s.txt' % (args.OBO_output_path, 'OBO_ignorance_random_sentences_review', ext, date.today()),
			  'w+') as random_sentence_file:
		for sentence_info in all_random_sentences_to_review:
			for i, info in enumerate(sentence_info):
				if i == len(sentence_info)-1:
					random_sentence_file.write('%s\n' % (info))
				else:
					random_sentence_file.write('%s\t' % (info))

