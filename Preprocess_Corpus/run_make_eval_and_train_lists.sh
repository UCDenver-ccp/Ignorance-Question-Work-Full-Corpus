#!/usr/bin/env bash

all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'

output_path='Ignorance-Question-Work-Full-Corpus/Preprocess_Corpus/Output_Folders/'

copy_to_path='Ignorance-Question-Work-Full-Corpus/'

eval_input_file='ALL_EVALUATION_DOCUMENTS_09_14_21.txt'

train_input_file='ALL_TRAINING_DOCUMENTS_09_14_21.txt'

eval_list_output_file='ALL_EVALUATION_DOCUMENTS_09_14_21_LIST.txt'

train_list_output_file='ALL_TRAINING_DOCUMENTS_09_14_21_LIST.txt'

python3 make_eval_and_train_lists.py -eval_list_path=$all_file_path$output_path$eval_input_file -train_list_path=$all_file_path$output_path$train_input_file -output_path=$all_file_path$output_path


##copy them to the main directory
cp $all_file_path$output_path$eval_list_output_file $all_file_path$copy_to_path

cp $all_file_path$output_path$train_list_output_file $all_file_path$copy_to_path



