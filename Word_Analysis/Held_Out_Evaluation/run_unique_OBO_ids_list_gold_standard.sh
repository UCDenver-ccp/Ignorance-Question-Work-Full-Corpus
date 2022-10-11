#!/usr/bin/env bash


##list of all ontologies of interest
ontologies="CHEBI,CL,GO_BP,GO_CC,GO_MF,MOP,NCBITaxon,PR,SO,UBERON"

##code path
all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'
fiji_path='/Users/mabo1182/'
scratch_path='/scratch/Users/mabo1182/'

##evaluation path
eval_path='Ignorance-Question-Work-Full-Corpus/OBOs/'
ignorance_corpus='Ignorance-Question-Corpus/'
ignorance_base_path='3_Ignorance_Base/'
ignorance_base_corpus='Ignorance-Base/Automated_Data_Corpus/'
ignorance_base_all_data_corpus='Ignorance-Base/All_Data_Corpus/'
output_results='Word_Analysis_Output_Results/'
obos='OBOs/'


##results from concept normalization path
results_concept_norm_files='Results_concept_norm_files/'
##concept normalization path with files to link the results with the word tokenized PMC articles
concept_norm_files='Concept_Norm_Files/'
##the full concept recognition output folder
concept_system_output='concept_system_output/'
##if there is a gold standard, the gold standard folder for evaluation
gold_standard='None'

##evaluation files we are working with
all_files='all'

##perform the evaluation analysis
evaluate='False'


python3 $all_file_path$ignorance_base_path$ignorance_base_corpus$obos/unique_OBO_ids_list.py -ontologies=$ontologies -OBO_file_path=$all_file_path$eval_path$concept_system_output -evaluation_files=$all_files -output_path=$all_file_path$eval_path$concept_system_output