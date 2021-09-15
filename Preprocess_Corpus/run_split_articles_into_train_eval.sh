#!/usr/bin/env bash

all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'

article_path='Ignorance-Question-Corpus/Articles/'

annotation_path='Ignorance-Question-Corpus/Annotations/'

all_article_list_path='Ignorance-Question-Work-Full-Corpus/Preprocess_Corpus/Output_Folders/Tokenized_Files/all_article_list.txt'

annotator_lists="[['GOLD_STANDARD'],['ELIZABETH','EMILY'],['KATIE','STEPHANIE']]"

annotator_lists_names="['GOLD_STANDARD','FIRST_ANNOTATION_ROUND','SECOND_ANNOTATION_ROUND']"

output_path='Ignorance-Question-Work-Full-Corpus/Preprocess_Corpus/Output_Folders/'

output_file_name='ALL'
working_path='Ignorance-Question-Work-Full-Corpus/'

##copy the all_articles file from the tokenized file to the general output folders
cp $all_file_path$all_article_list_path $all_file_path$output_path

##run the split
python3 split_articles_into_train_eval.py -article_path=$all_file_path$article_path -annotation_path=$all_file_path$annotation_path -all_article_list_path=$all_file_path$all_article_list_path -annotator_lists=$annotator_lists -annotator_lists_names=$annotator_lists_names -output_path=$all_file_path$output_path

cp $all_file_path$output_path$output_file_name* $all_file_path$working_path



