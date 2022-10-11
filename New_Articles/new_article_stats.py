import os
from datetime import date
import argparse
import gzip
import xml.etree.ElementTree as ET
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tokenize import WordPunctTokenizer
from statistics import mean, median




def sentence_count(pmcid_sentence_file_path):
	total_sentence_count = 0
	total_ignorance_count = 0
	pmcid_total_dict = {} #dict from pmcid filename to total sentence, total ignorance

	for root, directories, filenames in os.walk(pmcid_sentence_file_path):
		for filename in sorted(filenames):
			# print(filename)
			if filename.endswith('sentence_info.txt'):
				with open(root+filename, 'r+') as pmcid_sentence_file:
					for line in pmcid_sentence_file:
						# print(line)
						if len(line.split('\t')) != 5:
							raise Exception('ERROR: Issue with providing the wrong sentence files - the sentnece files must have the ONTOLOGY_CONCEPT_IDS_LIST')
						elif 'ONTOLOGY_CONCEPT_IDS_LIST' in line:
							pass
						else:
							##total sentence count
							total_sentence_count += 1
							if pmcid_total_dict.get(filename):
								pmcid_total_dict[filename][0] += 1
							else:
								pmcid_total_dict[filename] = [1, 0]

							##total ignorance count
							if line.split('\t')[-1].replace('\n', '') == '[]':
								pass
							else:
								# print([line.split('\t')[-1]])
								# print(pmcid_total_dict[filename][-1])
								pmcid_total_dict[filename][-1] = pmcid_total_dict[filename][-1] + 1
								# print(pmcid_total_dict[filename][-1])
								total_ignorance_count += 1


	return total_sentence_count, total_ignorance_count, pmcid_total_dict



def get_all_lcs(all_lcs_path):
	all_lcs_dict = {} #lexical cue -> ignorance type (all caps)
	unique_its = set()
	with open(all_lcs_path, 'r') as all_lcs_file:
		next(all_lcs_file)
		#header: LEXICAL CUE	SYNONYMS	IGNORANCE TYPE
		for line in all_lcs_file:
			(lc, synonyms, it) = line.strip('\n').split('\t')
			##weirdly future opportunities is in it too
			if it == 'FUTURE_OPPORTUNITIES':
				it = lc.upper()
			else:
				pass

			if all_lcs_dict.get(lc):
				all_lcs_dict[lc] += [it]
			else:
				all_lcs_dict[lc] = [it]

			##collect all the unique ignorance types
			unique_its.add(it)


	##collect the number of cues per ignorance type
	lc_count_per_it = {} #it -> # unique lcs
	for it in unique_its:
		lc_count_per_it[it] = 0
	for (key_lc, value_list_it) in all_lcs_dict.items():
		for v in value_list_it:
			lc_count_per_it[v] += 1
	# print('lc count per it')
	# print(lc_count_per_it)


	return all_lcs_dict, unique_its, lc_count_per_it




def annotation_information(all_lcs_dict, unique_its, annotation_path):
	##count of annotations for each it

	# all_lcs_set = set(all_lcs_dict.keys())
	total_lcs_not_in_taxonomy = set()
	lcs_not_in_taxonomy_dict = {} #dict from pmcid -> [total lcs, not in taxonomy]


	##loop over the annotation fles

	for root, directories, filenames in os.walk(annotation_path):
		for filename in sorted(filenames):
			if filename.endswith('.xml'):

				with open(root+filename, 'r+') as annotation_file:
					lcs_not_in_taxonomy_dict[filename] = [0, 0]

					tree = ET.parse(annotation_file)
					tree_root = tree.getroot()
					# print(root)

					##loop over all annotations
					for annotation in tree_root.iter('annotation'):
						empty_annotation = False
						weird_cues = False
						full_annotation = False
						spanned_text = ''
						##loop over all annotation information
						for child in annotation:
							if child.tag == 'class':
								ont_lc = child.attrib['id'] #lexical cue

								# print('ont_lc', ont_lc)

								if ont_lc:
									# if ont_lc.lower() == 'subject_scope':
									# 	print(ont_lc)
									# 	raise Exception('break!')

									if ont_lc.lower() == 'subject_scope' or all_lcs_dict.get(ont_lc.strip('0_')) or ont_lc.strip('0_').upper() in unique_its:

										continue

									else:
										print('weird cue', ont_lc)
										weird_cues = True
										# raise Exception('ERROR: MISSING LEXICAL CUE FOR SOME REASON!')
								else:
									empty_annotation = True

							elif child.tag == 'span':
								#if no text then an empty annotation
								if not child.text:
									# print(child)
									empty_annotation = True
								else:
									full_annotation = True
									if spanned_text:
										spanned_text += '...%s' %child.text
									else:
										spanned_text += '%s' %child.text






							else:
								print('got here weirdly')
								raise Exception('ERROR WITH READING IN THE ANNOTATION FILES!')
								pass


						##check if an empty annotation or not
						if empty_annotation or not full_annotation:
							continue
						else:
							if weird_cues:
								# print(all_lcs_dict['0_alternative_options'])
								# print(ont_lc)
								raise Exception('ERROR: MISSING LEXICAL CUES!')

							##check if the ont_lc is in the lcs set
							#ont_lc.lower() == 'subject_scope' or all_lcs_dict.get(ont_lc.strip('0_')) or ont_lc.strip('0_').upper()
							if all_lcs_dict.get(ont_lc.lower().strip('0_')):
								lcs_not_in_taxonomy_dict[filename][0] += 1
							elif ont_lc.upper() in unique_its:
								if all_lcs_dict.get(spanned_text.lower()) or all_lcs_dict.get(spanned_text.lower().replace(' ', '...')) or all_lcs_dict.get(spanned_text.lower().replace(' ', '_')):
									lcs_not_in_taxonomy_dict[filename][0] += 1
								elif ont_lc.lower() == 'subject_scope':
									pass
								else:
									lcs_not_in_taxonomy_dict[filename][0] += 1
									lcs_not_in_taxonomy_dict[filename][1] += 1
									total_lcs_not_in_taxonomy.add(spanned_text.lower())
							elif ont_lc.lower() == 'subject_scope':
								pass
							else:
								lcs_not_in_taxonomy_dict[filename][0] += 1
								lcs_not_in_taxonomy_dict[filename][1] += 1
								total_lcs_not_in_taxonomy.add(ont_lc)


	return lcs_not_in_taxonomy_dict, total_lcs_not_in_taxonomy


if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('-corpus_path', type=str, help='the file path to the gold standard data')
	parser.add_argument('-article_path', type=str, help='the file for the articles')
	parser.add_argument('-annotation_path', type=str, help='the file for the annotations')
	parser.add_argument('-all_lcs_path', type=str, help='the file path to the all_lcs_path starting with the ontology file')
	parser.add_argument('-pmcid_sentence_file_path', type=str, help='the file path to the sentences with annotation information included')
	parser.add_argument('--automated_corpus_path', type=str, help='the file path to the corpus that was automatically created')


	args = parser.parse_args()


	##sentence count for ignorance and stuff
	total_sentence_count, total_ignorance_count, pmcid_total_dict = sentence_count(args.corpus_path+args.pmcid_sentence_file_path)
	# print(total_sentence_count)
	# print(total_ignorance_count)
	# print(pmcid_total_dict)

	with open('%s%s.txt'%(args.corpus_path, 'sentence_type_counts'), 'w+') as sentence_count_file:
		sentence_count_file.write('%s\t%s\n' %('TOTAL SENTENCE COUNT', total_sentence_count))
		sentence_count_file.write('%s\t%s\n\n' %('TOTAL IGNORANCE COUNT', total_ignorance_count))
		sentence_count_file.write('%s\t%s\t%s\n' %('ARTICLE', 'TOTAL SENTENCE COUNT', 'TOTAL IGNORANCE COUNT'))
		for pmcid in pmcid_total_dict:
			sentence_count_file.write('%s\t%s\t%s\n' %(pmcid, pmcid_total_dict[pmcid][0], pmcid_total_dict[pmcid][1]))



	##gather all lexical cues and unique its
	all_lcs_dict, unique_its, lc_count_per_it = get_all_lcs(args.corpus_path + args.all_lcs_path)
	unique_its.add('SUBJECT_SCOPE')
	print(type(unique_its))

	print('UNIQUE ITS', unique_its)

	print(len(unique_its))
	# raise Exception('break!')

	all_lcs_dict['is'] = ['EXPLICIT_QUESTION']  ##we took this out later
	all_lcs_dict['than'] = ['ALTERNATIVE_OPTIONS_CONTROVERSY']  ##we took this out later
	all_lcs_dict['alternative_options'] = ['ALTERNATIVE_OPTIONS_CONTROVERSY']
	all_lcs_dict['urgent_call_to_action'] = ['IMPORTANT_CONSIDERATION']

	# print(unique_its)
	#gather all annotation information for each ignorance type
	lcs_not_in_taxonomy_dict, total_lcs_not_in_taxonomy = annotation_information(all_lcs_dict, unique_its, args.corpus_path + args.annotation_path)
	print(lcs_not_in_taxonomy_dict)
	print(total_lcs_not_in_taxonomy)
	print(len(total_lcs_not_in_taxonomy))

	with open('%s%s.txt' %(args.corpus_path, 'lexical_cues_not_in_taxonomy'), 'w+') as lc_not_in_taxonomy_file:
		lc_not_in_taxonomy_file.write('%s\t%s\n\n' %('TOTAL UNIQUE LCS NOT IN TAXONOMY', len(total_lcs_not_in_taxonomy)))
		lc_not_in_taxonomy_file.write('%s\t%s\n\n' %('UNIQUE LEXICAL CUES NOT IN TAXNOMY', total_lcs_not_in_taxonomy))
		lc_not_in_taxonomy_file.write('%s\t%s\t%s\n' %('PMCID', 'TOTAL LEXICAL CUES', 'TOTAL LEXICAL CUE ANNOTATIONS NOT IN TAXONOMY'))
		for pmcid in lcs_not_in_taxonomy_dict.keys():
			lc_not_in_taxonomy_file.write('%s\t%s\t%s\n' %(pmcid, lcs_not_in_taxonomy_dict[pmcid][0], lcs_not_in_taxonomy_dict[pmcid][-1]))










