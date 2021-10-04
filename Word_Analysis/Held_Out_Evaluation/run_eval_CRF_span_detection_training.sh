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
output_path='Output_Results/CRF_Training_Results/'

##folder name for sentence files
pmcid_sentence_files_path='Training_PMCID_files_sentences/' #the sentence files for the PMC articles'
tokenized_files='Training_Tokenized_Files/' #preprocessed article files to be word tokenized for BIO- format
save_models_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/CRF_Classification/SPAN_DETECTION_MODELS/'

##corpus name - craft here
corpus='ignorance'
all_lcs_path='/Ignorance-Question-Corpus/Ontologies/Ontology_Of_Ignorance_all_cues_2021-07-30.txt'

##list of excluded files from training: held out eval files for larger corpus
training_files='PMC1247630,PMC1474522,PMC2009866,PMC4428817,PMC5501061,PMC6022422,PMC1533075,PMC1626394,PMC2265032,PMC2516588,PMC2672462,PMC2874300,PMC2889879,PMC2898025,PMC2999828,PMC3205727,PMC3348565,PMC3373750,PMC3513049,PMC3679768,PMC3914197,PMC4122855,PMC4304064,PMC4352710,PMC4377896,PMC4500436,PMC4564405,PMC4653409,PMC4683322,PMC4859539,PMC4954778,PMC4992225,PMC5030620,PMC5143410,PMC5187359,PMC5273824,PMC5540678,PMC5685050,PMC6029118,PMC6033232,PMC6039335,PMC6054603,PMC6056931,PMC2722408,PMC2727050,PMC2913107,PMC3075531,PMC3169551,PMC3271033,PMC3424155,PMC3470091,PMC3659910,PMC3710985,PMC3828574,PMC4037583,PMC4275682,PMC4327187,PMC4380518,PMC4488777,PMC4715834,PMC4973215,PMC5340372,PMC5439533,PMC5658906,PMC5732505'

##if a gold standard exists (true or false)
gold_standard='True'
gs_tokenized_files='Ignorance-Question-Work-Full-Corpus/Preprocess_Corpus/Output_Folders/Tokenized_Files/'
algos='CRF'


##preprocess the articles (word tokenize) to prepare for span detection

##craft_path - not used
#concept_recognition_path - only if gold standard is true
#concept_annotation - not used
#concept_system_output = only if gold standard true
#python3 eval_preprocess_docs.py -craft_path=$all_file_path -concept_recognition_path=$all_file_path -eval_path=$all_file_path$eval_path -concept_system_output=$all_file_path -article_folder=$all_file_path$corpus_path$articles -tokenized_files=$tokenized_files -pmcid_sentence_files=$pmcid_sentence_files_path -concept_annotation=$concept_annotation -ontologies=$ontologies -evaluation_files=$evaluation_files --gold_standard=$gold_standard


##runs the span detection models locally - CRF
python3 eval_span_detection.py -ontologies=$ontologies -excluded_files=$training_files -tokenized_file_path=$all_file_path$eval_path$tokenized_files -save_models_path=$all_file_path$save_models_path -algos=$algos -output_path=$all_file_path$eval_path$output_path --pmcid_sentence_files_path=$pmcid_sentence_files_path --gold_standard=$gold_standard --gs_tokenized_files=$all_file_path$gs_tokenized_files