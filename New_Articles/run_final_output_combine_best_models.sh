#!/usr/bin/env bash

##path to the main craft documents for training
all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'

corpus_path='/Ignorance-Question-Corpus/'
corpus_name='Ignorance-Question-Corpus'


##folder to the articles within the craft path
articles='Articles/' #want files.txt

##folder to the concept annotations within the craft path
concept_annotation='Annotations/'
all_lcs_path='Ontologies/Ontology_Of_Ignorance_all_cues_2021-07-30.txt'
ontology_file_path='Ontologies/Ontology_Of_Ignorance.owl'
ontology_folder='Ontologies/'
profiles_folder='Profiles/'


##list of ontologies that have annotations to preproess
ontologies='full_unknown,explicit_question,incomplete_evidence,probable_understanding,superficial_relationship,future_work,future_prediction,important_consideration,anomaly_curious_finding,alternative_options_controversy,difficult_task,problem_complication,question_answered_by_this_work,1_binary_combined,0_all_combined'
#ontologies='0_all_combined'
#ontologies='1_binary_combined'

broad_categories='epistemics,barriers,levels_of_evidence,future_opportunities'


best_model_dict="{'CRF':['full_unknown','difficult_task'],'BIOBERT':['explicit_question','incomplete_evidence','probable_understanding','superficial_relationship','future_work','future_prediction','important_consideration','anomaly_curious_finding','alternative_options_controversy','problem_complication','question_answered_by_this_work']}"

##output path for the BIO- format files that are tokenized
eval_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/Held_Out_Evaluation/'
new_articles_path='Ignorance-Question-Work-Full-Corpus/New_Articles/'
output_results='Word_Analysis_Output_Results/'


##folder name for sentence files
pmcid_sentence_files_path='PMCID_files_sentences/' #the sentence files for the PMC articles'
tokenized_files='Tokenized_Files/' #preprocessed article files to be word tokenized for BIO- format

preprocess_corpus='Ignorance-Question-Work-Full-Corpus/Preprocess_Corpus/Output_Folders/'

corpus_construction='Ignorance-Question-Work-Full-Corpus/Corpus_Construction/'

##corpus name - craft here
corpus='ignorance'



##list of excluded files from training: held out eval files for larger corpus
new_article_files='PMC4949713,PMC7547020,PMC7074265,PMC6712354,PMC5904225,PMC4438576,PMC7222517'



###the algo and the corresponding results file
algos='CRF,BIOBERT'
#algos='BIOBERT'
#results_folders='BioBERT_Classification_Results'
results_folders='CRF_Classification_Results,BioBERT_Classification_Results'
bionlp_folder='z_BIONLP_OUTPUT_FORMAT/'
knowtator_folder='z_KNOWTATOR_OUTPUT_FORMAT/'
separate_all_combined_output='13_separate_combined'
bionlp_best_models_folder='z_BIONLP_BEST_MODELS/'
knowtator_best_models_folder='z_KNOWTATOR_BEST_MODELS/'
file_types=''
best_algo='BEST'


python3 final_output_combine_best_models.py -ontologies=$ontologies -algos=$algos -result_folders=$results_folders -results_path=$all_file_path$new_articles_path$output_results -output_path=$all_file_path$new_articles_path$output_results$bionlp_best_models_folder -evaluation_files=$new_article_files -best_model_type=$bionlp_folder$separate_all_combined_output -best_model_dict=$best_model_dict



python3 $all_file_path$eval_path/final_output_knowtator_format.py -ontologies=$ontologies -all_lcs_path=$all_file_path$corpus_path$all_lcs_path -ontology_file_path=$all_file_path$corpus_path$ontology_file_path -broad_categories=$broad_categories -article_path=$all_file_path$new_articles_path$articles -xml_folder=$knowtator_best_models_folder -bionlp_folder=$bionlp_best_models_folder -algos=$best_algo -result_folders=$results_folders -results_path=$all_file_path$new_articles_path$output_results -file_types=$file_types -evaluation_files=$new_article_files




##final knowtator project
knowtator_projects='z_KNOWTATOR_PROJECTS/'
model='BEST_Classification_Results'
underscore='_'
article_ext='.nxml.gz.txt'
annotation_ext='.nxml.gz.xml.'
annotation_ext2='.xml'
profiles_file='Default.xml'
knowtator_ext='.knowtator'


declare -a eval=('PMC4949713' 'PMC7547020' 'PMC7074265' 'PMC6712354' 'PMC5904225' 'PMC4438576' 'PMC7222517')

mkdir $all_file_path$new_articles_path$output_results$knowtator_projects$model$underscore$separate_all_combined_output
cd $all_file_path$new_articles_path$output_results$knowtator_projects$model$underscore$separate_all_combined_output
##create all the files and folders for the knowtator project
mkdir $articles
mkdir $concept_annotation
mkdir $ontology_folder
mkdir $profiles_folder
cp $all_file_path$corpus_path/$corpus_name$knowtator_ext .
mv $corpus_name$knowtator_ext $model$underscore$separate_all_combined_output$knowtator_ext



for e in "${eval[@]}"
    do
        cp $all_file_path$new_articles_path$articles$e$article_ext $articles
        cp $all_file_path$new_articles_path$output_results$knowtator_best_models_folder$e$annotation_ext$best_algo$annotation_ext2  $concept_annotation
        cp $all_file_path$corpus_path$ontology_file_path $ontology_folder
        cp $all_file_path$corpus_path$profiles_folder$profiles_file $profiles_folder


    done
