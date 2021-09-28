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
output_path='Output_Results/BioBERT_Classification_Results/'

##folder name for sentence files
pmcid_sentence_files_path='PMCID_files_sentences/' #the sentence files for the PMC articles'
tokenized_files='Tokenized_Files/' #preprocessed article files to be word tokenized for BIO- format
save_models_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/BioBERT_Classification/SPAN_DETECTION_MODELS/'

##corpus name - craft here
corpus='ignorance'
all_lcs_path='/Ignorance-Question-Corpus/Ontologies/Ontology_Of_Ignorance_all_cues_2021-07-30.txt'

##list of excluded files from training: held out eval files for larger corpus
evaluation_files='PMC6000839,PMC3800883,PMC2885310,PMC4311629,PMC3400371,PMC4897523,PMC3272870,PMC3313761,PMC3342123,PMC3427250,PMC4653418,PMC3279448,PMC6011374,PMC5812027,PMC2396486,PMC3915248,PMC3933411,PMC5240907,PMC4231606,PMC5539754,PMC5226708,PMC5524288,PMC3789799,PMC5546866,PMC5405375,PMC2722583'

##if a gold standard exists (true or false)
gold_standard='true'
gs_tokenized_files='Ignorance-Question-Work-Full-Corpus/Preprocess_Corpus/Output_Folders/Tokenized_Files/'
algos='BIOBERT'


##preprocess the articles (word tokenize) to prepare for span detection - if you have not done so already!
##craft_path - not used
##concept_recognition_path - only if gold standard is true
##concept_annotation - not used
##concept_system_output = only if gold standard true
##TODO: if have run the preprocessing already for CRF, run it here by commenting out the next line
#python3 eval_preprocess_docs.py -craft_path=$all_file_path -concept_recognition_path=$all_file_path -eval_path=$all_file_path$eval_path -concept_system_output=$all_file_path -article_folder=$all_file_path$corpus_path$articles -tokenized_files=$tokenized_files -pmcid_sentence_files=$pmcid_sentence_files_path -concept_annotation=$concept_annotation -ontologies=$ontologies -evaluation_files=$evaluation_files --gold_standard=$gold_standard



##preprocess the articles for BioBERT to create the train, test files and so on in the BioBERT input format
##does not run span detection but preprocessing for it because we already have the tokenized files
## save models_path - not used
python3 eval_span_detection.py -ontologies=$ontologies -excluded_files=$evaluation_files -tokenized_file_path=$all_file_path$eval_path$tokenized_files -save_models_path=$all_file_path$save_models_path -algos=$algos -output_path=$all_file_path$eval_path$output_path --pmcid_sentence_files_path=$pmcid_sentence_files_path --gold_standard=$gold_standard --gs_tokenized_files=$all_file_path$gs_tokenized_files