import os
import argparse



def all_cues_train_eval(ontologies, gs_bionlp_path, evaluation_files, training_files):

	##evaluation file information
	evaluation_all_dicts = {}
	training_all_dicts = {}
	for ont in ontologies:
		evaluation_all_dicts[ont.lower()] = dict()
		training_all_dicts[ont.lower()] = dict()



	for root, directories, filenames in os.walk(gs_bionlp_path):
		for filename in sorted(filenames):
			# print(filename)
			if filename.split('.nxml')[0] in evaluation_files:
				with open(root+filename) as eval_file:
					for line in eval_file:
						# print(line)
						#T0	full_unknown 185 188	new
						split_line = line.replace('\n','').split('\t')
						# print(split_line)
						ignorance_cat = split_line[1].split(' ')[0]
						span = split_line[1].split('%s ' %(ignorance_cat))[-1]
						text = split_line[-1]
						if evaluation_all_dicts[ignorance_cat.lower()].get(text.lower()):
							evaluation_all_dicts[ignorance_cat.lower()][text.lower()] += [span]
						else:
							evaluation_all_dicts[ignorance_cat.lower()][text.lower()] = [span]

			elif filename.split('.nxml')[0] in training_files:
				with open(root+filename) as train_file:
					for line in train_file:
						split_line = line.replace('\n','').split('\t')
						ignorance_cat = split_line[1].split(' ')[0]
						span = split_line[1].split('%s ' % (ignorance_cat))[-1]
						text = split_line[-1]
						if training_all_dicts[ignorance_cat.lower()].get(text.lower()):
							training_all_dicts[ignorance_cat.lower()][text.lower()] += [span]
						else:
							training_all_dicts[ignorance_cat.lower()][text.lower()] = [span]

			else:
				pass


	# print(training_all_dicts['difficult_task'])
	# print(evaluation_all_dicts['future_work'])

	return evaluation_all_dicts, training_all_dicts



def set_difference(set1, set2):
	unique_set1 = set1.difference(set2)
	return unique_set1



def all_cues_best_model(ontologies, eval_bionlp_path, evaluation_files):

	##evaluation file information
	eval_classifier_all_dicts = {}
	for ont in ontologies:
		eval_classifier_all_dicts[ont.lower()] = dict()

	for root, directories, filenames in os.walk(eval_bionlp_path):
		for filename in sorted(filenames):
			# print(filename)
			if filename.replace('BEST_','').split('.bionlp')[0] in evaluation_files:
				with open(root + filename) as eval_file:
					for line in eval_file:
						# print(line)
						# T0	full_unknown 185 188	new
						split_line = line.replace('\n', '').split('\t')
						# print(split_line)
						ignorance_cat = split_line[1].split(' ')[0]
						span = split_line[1].split('%s ' % (ignorance_cat))[-1]
						text = split_line[-1]
						if eval_classifier_all_dicts[ignorance_cat.lower()].get(text.lower()):
							eval_classifier_all_dicts[ignorance_cat.lower()][text.lower()] += [span]
						else:
							eval_classifier_all_dicts[ignorance_cat.lower()][text.lower()] = [span]
			else:
				pass


	return eval_classifier_all_dicts



def compare_annotations(ontologies, gs_eval_dict, classifier_eval_dict, unique_cues_dict):
	all_ont_scores_dict = {}

	for ont in ontologies:
		tp = 0
		fp = 0
		fn = 0


		for gs_text, gs_span_list in gs_eval_dict[ont].items():
			if gs_text.lower() in unique_cues_dict[ont]:
				if classifier_eval_dict[ont].get(gs_text.lower()):
					c_span_list = classifier_eval_dict[ont][gs_text.lower()]
					for span in gs_span_list:
						if span in c_span_list:
							tp += 1
						else:
							fp += 1
				else:
					##in gold standard but not classifier at all!
					fn += len(gs_span_list) #include all the spans that were missed

			##not unique
			else:
				pass
		if fp+tp == 0:
			precision = 0
		else:
			precision = float(tp)/float(tp+fp)
		if tp+fn == 0:
			recall = 0
		else:
			recall = float(tp)/float(tp+fn)
		if precision + recall == 0:
			fscore = 0
		else:
			fscore = (float(2)*float(precision)*float(recall))/float(precision+recall)


		all_ont_scores_dict[ont] = [tp, fp, fn, precision, recall, fscore] #list of tp, fp, fn



	return all_ont_scores_dict





if __name__=='__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-ontologies', type=str, help='a list of ontologies to use delimited with , no spaces')
	parser.add_argument('-evaluation_files', type=str, help='a list of the files used for a held out evaluation delimited with ,')
	parser.add_argument('-training_files', type=str, help='a list of the files that were used for training delimited with ,')
	parser.add_argument('-gs_bionlp_path', type=str, help='the file path to the gold standard bionlp files')
	parser.add_argument('-eval_bionlp_path', type=str, help='the file path to the evaluation final bionlp files')
	parser.add_argument('-output_path', type=str, help='file path to for the results to output')

	args = parser.parse_args()



	ontologies = args.ontologies.split(',')
	evaluation_files = args.evaluation_files.split(',')
	training_files = args.training_files.split(',')

	##1. gather the unseen cues between training and evaluation
	evaluation_all_dicts, training_all_dicts = all_cues_train_eval(ontologies, args.gs_bionlp_path, evaluation_files, training_files)

	##unique cues
	unique_cues_dict = {}

	for ont in ontologies:
		# print(ont)
		unique_cues_dict[ont] = set_difference(set(evaluation_all_dicts[ont.lower()].keys()), set(training_all_dicts[ont.lower()].keys()))
		# print(unique_cues_dict[ont])





	##2 gather the evaluation from classifiers
	eval_classifier_all_dicts = all_cues_best_model(ontologies, args.eval_bionlp_path, evaluation_files)

	# print(eval_classifier_all_dicts['difficult_task'])


	##3. compare all cues between gold standard evaluation and classified evaluation for unique cues only
	all_ont_scores_dict = compare_annotations(ontologies, evaluation_all_dicts, eval_classifier_all_dicts, unique_cues_dict)
	# print(all_ont_scores_dict)

	unique_cue_output_file = open('%s%s.txt' % (args.output_path, 'IGNORANCE_UNIQUE_EVAL_CUES'), 'w+')
	#tp, fp, fn, precision, recall, fscore
	unique_cue_output_file.write(
		'%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % ('IGNORANCE CATEGORY', 'TOTAL UNIQUE CUES TRAIN', 'TOTAL UNIQUE CUES EVAL', 'UNIQUE COUNT', 'UNIQUE SET', 'TRUE POSITIVES', 'FALSE POSITIVES', 'FALSE NEGATIVES', 'PRECISION', 'RECALL', 'FSCORE'))

	for ont in ontologies:
		tp, fp, fn, precision, recall, fscore = all_ont_scores_dict[ont]
		unique_cue_output_file.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%.3f\t%.3f\t%.3f\n' % (
		ont.lower(), len(training_all_dicts[ont.lower()].keys()), len(evaluation_all_dicts[ont.lower()].keys()), len(unique_cues_dict[ont]), unique_cues_dict[ont], tp, fp, fn, precision, recall, fscore))





