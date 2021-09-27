#!/usr/bin/env bash

##list of ontologies that have annotations to preproess
ontologies='full_unknown,explicit_question,incomplete_evidence,probable_understanding,superficial_relationship,future_work,future_prediction,important_consideration,anomaly_curious_finding,alternative_options_controversy,difficult_task,problem_complication,question_answered_by_this_work'

all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'

article_path='Ignorance-Question-Corpus/Articles/'

##BIO tags that we use from the BIO- format
biotags_to_change='B,I,O-'

##BIOtags to prioritize
closer_biotags='B,I'

##Path to the BIO- format tokenized files that were preprocessed
tokenized_file_path='Ignorance-Question-Work-Full-Corpus/Preprocess_Corpus/Output_Folders/Tokenized_Files/'

biotag_dict_file_path='Ignorance-Question-Work-Full-Corpus/Preprocess_Corpus/Output_Folders/BIOTAG_DUPLICATE_DICT.pkl'

##output folder - in tokenized file path
combined_folder='0_all_combined/'
binary_combined_folder='1_binary_combined/'


python3 combine_all_tokenized_files_by_pmcid.py -ontologies=$ontologies -article_path=$all_file_path$article_path -biotags_to_change=$biotags_to_change -biotag_combined_dict=$all_file_path$biotag_dict_file_path -tokenized_file_path=$all_file_path$tokenized_file_path -output_path=$all_file_path$tokenized_file_path -combined_folder=$combined_folder -binary_combined_folder=$binary_combined_folder
