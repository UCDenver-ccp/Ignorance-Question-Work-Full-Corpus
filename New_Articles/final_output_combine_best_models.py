import os
import pandas as pd
import datetime
import argparse
import ast


def create_new_bionlp_files_best_model(article, algos, result_folders, results_path, best_model_dict, best_model_type, output_path):
	##output file
	new_bionlp_file = open('%s%s_%s.bionlp' %(output_path, 'BEST', article), 'w+')
	T_count = 0
	##read in other files
	for i, algo in enumerate(algos):
		algo_folder = result_folders[i]
		ont_categories = best_model_dict[algo.upper()]
		# print(type(ont_categories))
		full_results_path = '%s%s/%s/%s_%s.bionlp' %(results_path, algo_folder, best_model_type, algo, article)
		with open(full_results_path, 'r+') as results_file:
			for line in results_file:
				# print(line.split('\t')[1].split(' ')[0].lower())
				if line.split('\t')[1].split(' ')[0].lower() in ont_categories:
					new_T = '%s%s' %('T', T_count)
					T_count += 1
					# print(line[line.index('\t')+1:])
					# raise Exception('break')
					new_bionlp_file.write('%s\t%s' %(new_T , line[line.index('\t')+1:]))
					# print('got here')
				else:
					pass









if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('-ontologies', type=str, help='a list of ontologies to use delimited with ,')
	parser.add_argument('-algos', type=str, help='a list of the algorithms to use delimited with ,')
	parser.add_argument('-result_folders', type=str,help='a list of folders to the results of the span detection models matching the algos list delimited with , in order of the algos')
	parser.add_argument('-results_path', type=str,help='file path to the results folders')
	parser.add_argument('-output_path', type=str, help='the file path for the bionlp format output files')
	parser.add_argument('-evaluation_files', type=str, help='a list of the files to be evaluated delimited with ,')
	parser.add_argument('-best_model_type', type=str, help='folder name of the output for all the separate categories combined')
	parser.add_argument('-best_model_dict', type=str, help='a string of a dictionary for the algorithm to a list of the ontologies that use this algorithm all in string with no spaces')
	args = parser.parse_args()

	# ontologies = ['CHEBI', 'CL', 'GO_BP', 'GO_CC', 'GO_MF', 'MOP', 'NCBITaxon', 'PR', 'SO', 'UBERON']


	# results_span_detection_path = '/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/Negacy_seq_2_seq_NER_model/ConceptRecognition/Evaluation_Files/Results_span_detection/'

	# concept_norm_files_path = '/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/Negacy_seq_2_seq_NER_model/ConceptRecognition/Evaluation_Files/Concept_Norm_Files/'

	algos = args.algos.split(',')
	result_folders = args.result_folders.split(',')
	ontologies = args.ontologies.split(',')
	evaluation_files = args.evaluation_files.split(',')
	# print(args.best_model_dict)
	best_model_dict = ast.literal_eval(args.best_model_dict)
	print(best_model_dict)

	print(evaluation_files)

	for article in evaluation_files:
		create_new_bionlp_files_best_model(article, algos, result_folders, args.results_path, best_model_dict, args.best_model_type, args.output_path)