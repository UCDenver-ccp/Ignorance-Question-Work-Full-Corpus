#!/usr/bin/env bash

##path to the main craft documents for training
all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'


corpus_path='/Ignorance-Question-Corpus/'

##folder to the articles within the craft path
articles='Articles/' #want files.txt

##folder to the concept annotations within the craft path
concept_annotation='Annotations/'

##list of ontologies that have annotations to preproess
ontologies='full_unknown,explicit_question,incomplete_evidence,probable_understanding,superficial_relationship,future_work,future_prediction,important_consideration,anomaly_curious_finding,alternative_options_controversy,difficult_task,problem_complication,question_answered_by_this_work,0_all_combined,1_binary_combined'

##output path for the BIO- format files that are tokenized
eval_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/Held_Out_Evaluation/'
new_articles_path='Ignorance-Question-Work-Full-Corpus/New_Articles/'


##folder name for sentence files
pmcid_sentence_files_path='PMCID_files_sentences/' #the sentence files for the PMC articles'
tokenized_files='Tokenized_Files/' #preprocessed article files to be word tokenized for BIO- format

##corpus name - craft here
corpus='ignorance'
all_lcs_path='/Ignorance-Question-Corpus/Ontologies/Ontology_Of_Ignorance_all_cues_2021-07-30.txt'

##list of excluded files from training: held out eval files for larger corpus
new_article_files='PMC7222517'

##if a gold standard exists (true or false)
gold_standard='False'
#gs_tokenized_files='Ignorance-Question-Work-Full-Corpus/Preprocess_Corpus/Output_Folders/Tokenized_Files/'




##runs the span detection models locally - CRF
algos='CRF'
output_path='Word_Analysis_Output_Results/CRF_Classification_Results/'
save_models_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/CRF_Classification/SPAN_DETECTION_MODELS/'


python3 $all_file_path$eval_path/eval_span_detection.py -ontologies=$ontologies -excluded_files=$new_article_files -tokenized_file_path=$all_file_path$new_articles_path$tokenized_files -save_models_path=$all_file_path$save_models_path -algos=$algos -output_path=$all_file_path$new_articles_path$output_path --pmcid_sentence_files_path=$pmcid_sentence_files_path --gold_standard=$gold_standard #--gs_tokenized_files=$all_file_path$gs_tokenized_files


##preprocess the articles for BioBERT to create the train, test files and so on in the BioBERT input format
##does not run span detection but preprocessing for it because we already have the tokenized files
## save models_path - not used
algos='BIOBERT'
output_path='Word_Analysis_Output_Results/BioBERT_Classification_Results/'
save_models_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/BioBERT_Classification/SPAN_DETECTION_MODELS/'

python3 $all_file_path$eval_path/eval_span_detection.py -ontologies=$ontologies -excluded_files=$new_article_files -tokenized_file_path=$all_file_path$new_articles_path$tokenized_files -save_models_path=$all_file_path$save_models_path -algos=$algos -output_path=$all_file_path$new_articles_path$output_path --pmcid_sentence_files_path=$pmcid_sentence_files_path --gold_standard=$gold_standard #--gs_tokenized_files=$all_file_path$gs_tokenized_files


##COPY THE TRAIN AND TRAIN_DEV FILES TO THE BIOBERT TOKENIZED FILES BECAUSE IT NEEDS IT TO RUN PREDICTION - DOESNT USE IT (ISSUE)
#/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/Ignorance-Question-Work-Full-Corpus/Word_Analysis/BioBERT_Classification/SPAN_DETECTION_MODELS/1_binary_combined/BIOBERT
biobert_classification_train_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/BioBERT_Classification/SPAN_DETECTION_MODELS/1_binary_combined/BIOBERT/'
train='train.tsv'
train_dev='train_dev.tsv'
biobert='BIOBERT/'
cp $all_file_path$biobert_classification_train_path$train $all_file_path$new_articles_path$tokenized_files$biobert
cp $all_file_path$biobert_classification_train_path$train_dev $all_file_path$new_articles_path$tokenized_files$biobert