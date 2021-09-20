#!/usr/bin/env bash

##list of ontologies that have annotations to preproess
ontologies='full_unknown,explicit_question,incomplete_evidence,probable_understanding,superficial_relationship,future_work,future_prediction,important_consideration,anomaly_curious_finding,alternative_options_controversy,difficult_task,problem_complication,question_answered_by_this_work,0_all_combined,1_binary_combined'


##list of excluded files from training: held out eval files for larger corpus
excluded_files='PMC6000839,PMC3800883,PMC2885310,PMC4311629,PMC3400371,PMC4897523,PMC3272870,PMC3313761,PMC3342123,PMC3427250,PMC4653418,PMC3279448,PMC6011374,PMC5812027,PMC2396486,PMC3915248,PMC3933411,PMC5240907,PMC4231606,PMC5539754,PMC5226708,PMC5524288,PMC3789799,PMC5546866,PMC5405375,PMC2722583'

##BIO tags that we use from the BIO- format
biotags='B,I,O,O-'

##BIOtags to prioritize
closer_biotags='B,I'

all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'

word_analysis_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis'

##Path to the BIO- format tokenized files that were preprocessed
tokenized_file_path='Ignorance-Question-Work-Full-Corpus/Preprocess_Corpus/Output_Folders/Tokenized_Files/'

pmcid_sentence_files_path='Ignorance-Question-Work-Full-Corpus/Preprocess_Corpus/Output_Folders/PMCID_files_sentences/'

all_lcs_path='Ignorance-Question-Work-Full-Corpus/Ontology_Of_Ignorance_all_cues_2021-07-30.txt'

##Path to for where to save the models
save_models_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/BioBERT_Classification/SPAN_DETECTION_MODELS/'

##the algorithm to use
algo='BIOBERT' #CRF, LSTM, LSTM-CRF, char_embeddings, LSTM_ELMO, BIOBERT

##Corpus we are using
corpus='ignorance'

##LSTM hyperparameter options for training
batch_size_list='18,36,53,106'
optimizer_list='rmsprop'
loss_list='categorical_crossentropy'
epochs_list='10,100' #10, 100, 500, 1000
neurons_list='3,12' #3, 12, 25, 50




##Run span detection training for all ontologies over the preprocessed tokenized files

##RUN BIOBERT PREPROCESS VIA SPAN_DETECTION.PY
python3 $all_file_path$word_analysis_path/span_detection.py -ontologies=$ontologies -excluded_files=$excluded_files -biotags=$biotags -closer_biotags=$closer_biotags -tokenized_file_path=$all_file_path$tokenized_file_path -save_models_path=$all_file_path$save_models_path -algo=$algo -corpus=$corpus --pmcid_sentence_files_path=$all_file_path$pmcid_sentence_files_path --all_lcs_path=$all_file_path$all_lcs_path  --batch_size_list=$batch_size_list --optimizer_list=$optimizer_list --loss_list=$loss_list --epochs_list=$epochs_list --neurons_list=$neurons_list


