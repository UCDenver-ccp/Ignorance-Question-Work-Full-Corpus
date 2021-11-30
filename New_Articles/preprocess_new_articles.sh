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
new_article_files='PMC4949713,PMC7547020,PMC7074265,PMC6712354,PMC5904225,PMC4438576,PMC7222517'

##if a gold standard exists (true or false)
gold_standard='False'


##preprocess the articles (word tokenize) to prepare for span detection

##craft_path - not used
#concept_recognition_path - only if gold standard is true
#concept_annotation - not used
#concept_system_output = only if gold standard true
python3 $all_file_path$eval_path/eval_preprocess_docs.py -craft_path=$all_file_path -concept_recognition_path=$all_file_path -eval_path=$all_file_path$new_articles_path -concept_system_output=$all_file_path -article_folder=$all_file_path$new_articles_path$articles -tokenized_files=$tokenized_files -pmcid_sentence_files=$pmcid_sentence_files_path -concept_annotation=$concept_annotation -ontologies=$ontologies -evaluation_files=$new_article_files --gold_standard=$gold_standard
