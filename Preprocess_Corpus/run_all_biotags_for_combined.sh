#!/usr/bin/env bash

##list of ontologies that have annotations to preproess
ontologies='full_unknown,explicit_question,incomplete_evidence,probable_understanding,superficial_relationship,future_work,future_prediction,important_consideration,anomaly_curious_finding,alternative_options_controversy,difficult_task,problem_complication,question_answered_by_this_work'

all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'

output_path='Ignorance-Question-Work-Full-Corpus/Preprocess_Corpus/Output_Folders/'

##BIO tags that we use from the BIO- format
biotags_to_change='B,I,O-'


python3 all_biotags_for_combined.py -biotags=$biotags_to_change -ontologies=$ontologies -output_path=$all_file_path$output_path
