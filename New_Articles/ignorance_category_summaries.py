import os
import pandas as pd
import datetime
import argparse
import ast




def read_in_bionlp_files(bionlp_path, algo, article):
	##output dictionary from ignorance category to list of concepts with text and span - pandas!
	##bionlp file line
	#T0	full_unknown 1697 1702	novel

	article_info_list = []
	if type(algo) == list:
		for a in algo:
			try:
				article_bionlp_file = open('%s%s_%s.bionlp' %(bionlp_path, a.upper(), article), 'r+')
			except FileNotFoundError:
				continue
	else:
		article_bionlp_file = open('%s%s_%s.bionlp' %(bionlp_path, algo, article), 'r+')
	# with open('%s%s_%s.bionlp' %(bionlp_path, algo, article), 'r+') as article_bionlp_file:


	if article_bionlp_file:
		for line in article_bionlp_file:
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
						indices_list += [(int(s1), int(e1))]
					else:
						# print(line)
						# print(d)
						s, e = d.split(' ')
						indices_list += [(int(s), int(e))]

			else:
				ignorance_category, text_start, text_end = line_info[1].split(' ')

				indices_list = [(int(text_start), int(text_end))]

			##add the current info to our full df list - initialize with sentence stuff empty for now.
			article_info_list += [[ignorance_category, article, indices_list, text, None, None]]

	return article_info_list




def read_in_sentence_files(sentence_path, article):
	##output dictionary from sentence_id (PMC+sentence number) to sentence text and span
	#PMC4438576.nxml.gz	0	['Identification of targets for rational pharmacological therapy in childhood craniopharyngioma\n\nAbstract\n\nIntroduction\n\nPediatric adamantinomatous craniopharyngioma (ACP) is a histologically benign but clinically aggressive brain tumor that arises from the sellar/suprasellar region.']	(0, 282)

	article_sentence_info_dict = {} #dictionary from sentence_id (PMC+sentence number) to sentence text and span
	with open('%s%s.nxml.gz_sentence_info.txt' %(sentence_path, article,), 'r+') as article_sentence_file:
		# print(article_sentence_file)
		next(article_sentence_file)
		for line in article_sentence_file:
			pmc_file, sent_num, sentence_text_list, sent_span = line.strip('\n').split('\t')
			sent_id = '%s_%s' %(pmc_file.split('.')[0], sent_num)
			sent_span = ast.literal_eval(sent_span) #tuple and ints!
			# print(sent_span, type(sent_span), type(sent_span[0]))
			# raise Exception('hold')
			article_sentence_info_dict[sent_id] = [sentence_text_list, sent_span]

	return article_sentence_info_dict


def combine_sentence_bionlp(evaluation_files, bionlp_path, algo, sentence_path):
	##use the sentence diciontary to add sentence information to the concept pandas
	# cue_columns = ['IGNORANCE CATEGORY', 'ARTICLE', 'CUE SPAN', 'CUE',  'SENTENCE', 'SENTENCE SPAN'] #6 TOTAL THINGS WE NEED
	# no_cue_columns = ['ARTICLE', 'SENTENCE_NUMBER', 'SENTENCE', 'SENTENCE_INDICES']
	full_cue_info_list = [] #list of list of all the columns!
	sentences_no_cues = []


	for article in evaluation_files:
		print(article)
		article_info_list = read_in_bionlp_files(bionlp_path, algo, article) #[ignorance_category, article, indices_list, text, None, None]
		article_sentence_info_dict = read_in_sentence_files(sentence_path, article) #sent_id -> [sentence_text_list, sent_span]

		cue_sentences_set = set() ##list of sent_ids that we used!

		##add sentence info for each cue
		for i, info in enumerate(article_info_list):
			ignorance_category, article, indices_list, cue_text, sent_text_null, sent_span_null = info
			# print(indices_list)
			min_cue_start = min([s[0] for s in indices_list])
			max_cue_end = max([e[1] for e in indices_list])

			for j in range(len(article_sentence_info_dict.keys())):

				sent_text, sent_span = article_sentence_info_dict['%s_%s' %(article, j)]
				sent_start, sent_end = sent_span
				if sent_start <= min_cue_start and max_cue_end <= sent_end:
					#found the sentence! - keep the info and keep going for the next cues which could be in any of the sentences!
					article_info_list[i][-2] = sent_text
					article_info_list[i][-1] = sent_span
					##can be repeats
					cue_sentences_set.add('%s_%s' %(article, j)) #sent_id
					# print(j, len(article_sentence_info_dict.keys()))
					break
				else:
					pass

				if j == len(article_sentence_info_dict.keys()) - 1:
					##make sure we always find the sentence - meaning it should never get here!
					raise Exception('ERROR: Issue with not finding the sentence for each cue!')
				else:
					pass


		##capture all sentences with cues!
		full_cue_info_list += article_info_list

		##capture all the sentneces with no cues
		for sent_id in article_sentence_info_dict.keys():
			if sent_id in list(cue_sentences_set):
				pass
			else:

				###TODO: sent_id.split('_')[-1]
				sentences_no_cues += [[article, sent_id.split('_')[-1], article_sentence_info_dict[sent_id][0], article_sentence_info_dict[sent_id][1]]]



	##output the full stuff for all articles!
	return full_cue_info_list, sentences_no_cues






def output_summaries_df(df_list, columns, output_file):
	##output the pandas dataframe
	if type(df_list) == pd.DataFrame:
		df_list.to_csv(output_file, sep='\t', columns=columns)
		return df_list

	else:
		df = pd.DataFrame(df_list, columns=columns)
		df.to_csv(output_file, sep='\t', columns=columns)

		return df




if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('-ontologies', type=str, help='a list of ontologies to use delimited with ,')
	parser.add_argument('-algos', type=str, help='a list of the algorithms to use delimited with ,')
	parser.add_argument('-bionlp_path', type=str,help='path to the bionlp files to use')
	parser.add_argument('-sentence_path', type=str,help='file path to the sentence folder')
	parser.add_argument('-output_path', type=str, help='the file path for the output of the summaries')
	parser.add_argument('-evaluation_files', type=str, help='a list of the files to be evaluated delimited with ,')
	parser.add_argument('--article_path', type=str,
						help='the file path to all of the txt articles if you do not provide a list of the articles',
						default=None)
	args = parser.parse_args()


	ontologies = args.ontologies.split(',')
	# evaluation_files = args.evaluation_files.split(',')
	try:
		algos_list = ast.literal_eval(args.algos)
	except ValueError:
		algos_list = None
		algos = args.algos.split(',')


	# print(args.best_model_dict)


	if args.evaluation_files.lower() == 'all':
		evaluation_files = []
		if args.article_path:
			for root, directories, filenames in os.walk(args.article_path):
				for filename in sorted(filenames):
					if filename.endswith('.nxml.gz.txt'):
						evaluation_files += [filename.replace('.nxml.gz.txt', '')]
					else:
						pass
		else:
			raise Exception('NEED TO PROVIDE ARTICLE PATH SO WE CAN GATHER THE LIST OF ARTICLES!')

	else:
		evaluation_files = args.evaluation_files.split(',')

	print(evaluation_files)

	cue_columns = ['IGNORANCE CATEGORY', 'ARTICLE', 'CUE SPAN', 'CUE', 'SENTENCE',
				   'SENTENCE SPAN']  # 6 TOTAL THINGS WE NEED
	no_cue_columns = ['ARTICLE', 'SENTENCE_NUMBER', 'SENTENCE', 'SENTENCE_INDICES']

	if algos_list:
		full_cue_info_list, sentences_no_cues = combine_sentence_bionlp(evaluation_files, args.bionlp_path, algos_list,args.sentence_path)

		full_cue_info_list_df = output_summaries_df(full_cue_info_list, cue_columns,
													'%s%s.txt' % (args.output_path, 'ALL_CUES_FULL_SUMMARY'))

		##separate out by ignorance category:
		for ont in ontologies:
			# print(ont)
			ont_specific_df = full_cue_info_list_df.loc[full_cue_info_list_df['IGNORANCE CATEGORY'] == ont.lower()]
			# print(ont_specific_df)
			ont_specific_df = output_summaries_df(ont_specific_df, cue_columns,
												  '%s%s_%s.txt' % (args.output_path, ont.upper(), 'CUES_FULL_SUMMARY'))

		sentences_no_cues_df = output_summaries_df(sentences_no_cues, no_cue_columns,  '%s%s.txt' % (args.output_path, 'NO_CUES_FULL_SUMMARY'))


	else:
		for algo in algos:
			full_cue_info_list, sentences_no_cues = combine_sentence_bionlp(evaluation_files, args.bionlp_path, algo, args.sentence_path)

			full_cue_info_list_df = output_summaries_df(full_cue_info_list, cue_columns, '%s%s.txt' %(args.output_path, 'ALL_CUES_FULL_SUMMARY'))

			##separate out by ignorance category:
			for ont in ontologies:
				# print(ont)
				ont_specific_df = full_cue_info_list_df.loc[full_cue_info_list_df['IGNORANCE CATEGORY'] == ont.lower()]
				# print(ont_specific_df)
				ont_specific_df = output_summaries_df(ont_specific_df, cue_columns, '%s%s_%s.txt' %(args.output_path, ont.upper(), 'CUES_FULL_SUMMARY'))


			sentences_no_cues_df = output_summaries_df(sentences_no_cues, no_cue_columns, '%s%s.txt' %(args.output_path, 'NO_CUES_FULL_SUMMARY'))

