import os
import numpy as np
import pandas as pd
import argparse
import ast
from lxml import etree
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

			#not ignorance statements
			else:
				pass


	return article_ignorance_statements_info, int(sentence_num)+1



def article_OBO_ignorance_overlap_info(article, OBO_ontologies, article_OBO_dict, ignorance_ontologies, article_ignorance_statements_info, total_ignorance_sentences):
	#inputs
	##article_OBO_dict: article_OBO_dict[OBO] += [(num_id, OBO_id, span, text)]
	##article_ignorance_statements_info and total_ignorance_sentence: (sentence_text, sent_indices, ont_concept_list, ignorance_category_concept_list) and total_sentences

	#output
	article_OBO_ignorance_connect_dict = {} #dict from OBO -> [(OBO_num_ID, ignorance_sentence_ID)]
	for ont in OBO_ontologies:
		article_OBO_ignorance_connect_dict[ont] = []

	article_OBO_ignorance_overlap_dict = {} #dict from ignorance category -> [counts of OBOs in order of OBOs]
	for ignorance_category in ignorance_ontologies:
		article_OBO_ignorance_overlap_dict[ignorance_category.upper()] = [0 for a in OBO_ontologies]

	random_sentences_to_review = [] #(ignorance_sentence_id, sentence_text -> uppercase OBOs, OBO_text, OBO_id, ignorance_category_concept_list)

	for OBO in OBO_ontologies:
		# print(OBO)
		all_OBO_info_list = article_OBO_dict[OBO]
		for OBO_info in all_OBO_info_list:
			OBO_num_ID, OBO_id, OBO_span, OBO_text = OBO_info
			# print(OBO_span, OBO_text, OBO, article)
			OBO_span_flat_list = [int(a) for a in list(np.concatenate(OBO_span).flat)]
			# print(OBO_span_flat_list)
			OBO_min_start = min(OBO_span_flat_list)
			OBO_max_end = max(OBO_span_flat_list)

			random_sentence_num = random.randint(0, len(article_ignorance_statements_info))

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
					for ic in ignorance_category_concept_set:
						OBO_index = OBO_ontologies.index(OBO)
						article_OBO_ignorance_overlap_dict[ic.upper()][OBO_index] += 1

					no_OBOs = False
				else:
					no_OBOs = True

				##collect ignorance sentence for random check
				if random_sentence_num == j:
					if no_OBOs:
						random_sentences_to_review += [[ignorance_sentence_id, [ignorance_sentence_text], ignorance_ont_concept_list, ignorance_category_concept_list]]
					else:
						random_sentences_to_review += [[ignorance_sentence_id, [ignorance_sentence_text], ignorance_ont_concept_list, ignorance_category_concept_list, OBO_text, OBO_id, OBO_num_ID, OBO]]



	return article_OBO_ignorance_connect_dict, article_OBO_ignorance_overlap_dict, random_sentences_to_review









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
	parser.add_argument('-OBO_ontologies', type=str, help='a list of ontologies to use delimited with ,')
	parser.add_argument('-evaluation_files', type=str, help='a list of files to evaluate delimited with ,')
	parser.add_argument('-OBO_model_dict', type=str, help='a dictionary for each OBO ontology to the correct model to use based on performance, OBOs should be all uppercase')
	parser.add_argument('-OBO_output_path', type=str, help='output folder path')


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


	full_OBO_ignorance_overlap_dict = {} #dict from ignorance category -> [counts of OBOs]
	for ic in ignorance_ontologies:
		full_OBO_ignorance_overlap_dict[ic.upper()] = [0 for o in OBO_ontologies]


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
		article_ignorance_statements_info, total_ignorance_sentences = get_ignorance_statement_info_per_article(article, args.ignorance_sentence_folder_path, ignorance_ontologies, ignorance_all_lcs_dict, ignorance_all_weird_lcs, ignorance_extra_ontology_concepts)
		print(article, len(article_ignorance_statements_info), total_ignorance_sentences)



		##combine all the OBO and ignorance stuff
		article_OBO_ignorance_connect_dict, article_OBO_ignorance_overlap_dict, random_sentences_to_review = article_OBO_ignorance_overlap_info(article, OBO_ontologies, article_OBO_dict, ignorance_ontologies, article_ignorance_statements_info, total_ignorance_sentences)

		all_random_sentences_to_review += random_sentences_to_review

		for ic in ignorance_ontologies:
			# print(full_OBO_ignorance_overlap_dict[ic.upper()])
			updated_info = [a + b for a, b in zip(full_OBO_ignorance_overlap_dict[ic.upper()], article_OBO_ignorance_overlap_dict[ic.upper()])]
			full_OBO_ignorance_overlap_dict[ic.upper()] = updated_info
			# print(updated_info)

	# print(full_OBO_ignorance_overlap_dict)





	##outputs!

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
	OBO_ignorance_overlap_counts_df = pd.DataFrame(full_OBO_ignorance_overlap_dict, columns=OBO_ignorance_columns)
	OBO_ignorance_overlap_counts_df.index = OBO_ontologies
	# print(OBO_ignorance_overlap_counts_df)
	row_sums_2 = list(OBO_ignorance_overlap_counts_df.sum(axis=1))
	OBO_ignorance_overlap_counts_df['OBO_IGNORANCE_SUMS'] = row_sums_2
	OBO_ignorance_overlap_counts_df.loc['IGNORANCE_OBO_SUM'] = OBO_ignorance_overlap_counts_df.sum()
	OBO_ignorance_overlap_counts_df.loc['IGNORANCE_OBO_AVERAGE'] = OBO_ignorance_overlap_counts_df.mean()
	OBO_ignorance_overlap_counts_df.loc['IGNORANCE_OBO_MEDIAN'] = OBO_ignorance_overlap_counts_df.median()



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




	##output the count dataframe if EXT or not
	if 'EXT' in args.OBO_ontologies:
		ext = '_EXT'
	else:
		ext = ''


	article_OBO_count_df.to_csv('%s%s%s.txt' % (args.OBO_output_path, 'OBO_overall_article_counts', ext), sep='\t', columns=OBO_columns)

	article_OBO_count_unique_df.to_csv('%s%s%s.txt' % (args.OBO_output_path, 'OBO_overall_article_counts_unique', ext), sep='\t', columns=OBO_colunms_unique)

	OBO_ignorance_overlap_counts_df.to_csv('%s%s%s.txt' % (args.OBO_output_path, 'OBO_ignorance_overlap_counts', ext), sep='\t', columns=OBO_ignorance_columns)

	OBO_ignorance_overlap_counts_top3_df.to_csv('%s%s%s.txt' % (args.OBO_output_path, 'OBO_overall_article_counts_top3', ext), sep='\t',
								columns=OBO_ignorance_columns_top3)

	##random sentences to review
	with open('%s%s%s_%s.txt' % (args.OBO_output_path, 'OBO_ignorance_random_sentences_review', ext, date.today()),
			  'w+') as random_sentence_file:
		for sentence_info in all_random_sentences_to_review:
			for i, info in enumerate(sentence_info):
				if i == len(sentence_info)-1:
					random_sentence_file.write('%s\n' % (info))
				else:
					random_sentence_file.write('%s\t' % (info))


	# else:
	# 	article_OBO_count_df.to_csv('%s%s.txt' %(args.OBO_output_path,'OBO_overall_article_counts'), sep='\t', columns=OBO_columns)
	# 	OBO_ignorance_overlap_counts_df.to_csv('%s%s.txt' % (args.OBO_output_path, 'OBO_ignorance_overlap_counts'), sep='\t', columns=OBO_ignorance_columns)
	# 	OBO_ignorance_overlap_counts_top3_df.to_csv(
	# 		'%s%s.txt' % (args.OBO_output_path, 'OBO_overall_article_counts_top3'), sep='\t',
	# 		columns=OBO_ignorance_columns_top3)
	#
	# 	##random sentences to review
	# 	with open('%s%s.txt' % (args.OBO_output_path, 'OBO_ignorance_random_sentences_review'),
	# 			  'w+') as random_sentence_file:
	# 		for sentence_info in all_random_sentences_to_review:
	# 			for i, info in enumerate(sentence_info):
	# 				if i == len(sentence_info)-1:
	# 					random_sentence_file.write('%s\n' % (info))
	# 				else:
	# 					random_sentence_file.write('%s\t' % (info))
	#
	#
	#
