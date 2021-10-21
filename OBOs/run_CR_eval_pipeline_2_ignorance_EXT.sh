#!/usr/bin/env bash

##list of all ontologies of interest
ontologies="CHEBI_EXT,CL_EXT,GO_BP_EXT,GO_CC_EXT,GO_MF_EXT,MOP_EXT,NCBITaxon_EXT,PR_EXT,SO_EXT,UBERON_EXT"

##code path
all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'
negacy_folder='Negacy_seq_2_seq_NER_model/'
concept_recognition_path='Concept-Recognition-as-Translation/'
code='Code/'
all_code_path=$all_file_path$negacy_folder$concept_recognition_path$code

##evaluation path
eval_path='Ignorance-Question-Work-Full-Corpus/OBOs/'
##results from concept normalization path
results_concept_norm_files='Results_concept_norm_files/'
##concept normalization path with files to link the results with the word tokenized PMC articles
concept_norm_files='Concept_Norm_Files/'
##the full concept recognition output folder
concept_system_output='concept_system_output/'
##if there is a gold standard, the gold standard folder for evaluation
gold_standard='None'

##evaluation files we are working with
all_files='PMC6000839,PMC3800883,PMC2885310,PMC4311629,PMC3400371,PMC4897523,PMC3272870,PMC3313761,PMC3342123,PMC3427250,PMC4653418,PMC3279448,PMC6011374,PMC5812027,PMC2396486,PMC3915248,PMC3933411,PMC5240907,PMC4231606,PMC5539754,PMC5226708,PMC5524288,PMC3789799,PMC5546866,PMC5405375,PMC2722583,PMC1247630,PMC1474522,PMC2009866,PMC4428817,PMC5501061,PMC6022422,PMC1533075,PMC1626394,PMC2265032,PMC2516588,PMC2672462,PMC2874300,PMC2889879,PMC2898025,PMC2999828,PMC3205727,PMC3348565,PMC3373750,PMC3513049,PMC3679768,PMC3914197,PMC4122855,PMC4304064,PMC4352710,PMC4377896,PMC4500436,PMC4564405,PMC4653409,PMC4683322,PMC4859539,PMC4954778,PMC4992225,PMC5030620,PMC5143410,PMC5187359,PMC5273824,PMC5540678,PMC5685050,PMC6029118,PMC6033232,PMC6039335,PMC6054603,PMC6056931,PMC2722408,PMC2727050,PMC2913107,PMC3075531,PMC3169551,PMC3271033,PMC3424155,PMC3470091,PMC3659910,PMC3710985,PMC3828574,PMC4037583,PMC4275682,PMC4327187,PMC4380518,PMC4488777,PMC4715834,PMC4973215,PMC5340372,PMC5439533,PMC5658906,PMC5732505'

##perform the evaluation analysis
evaluate='False'



##run the open_nmt to predict
#run_eval_open_nmt.sh


#if evaluate is false -> dont need a gold standard option because it is not used
##full concept system output for the full run of concept recognition
python3 $all_code_path/eval_concept_system_output.py -ontologies=$ontologies -concept_norm_results_path=$all_file_path$eval_path$results_concept_norm_files -concept_norm_link_path=$all_file_path$eval_path$concept_norm_files -output_file_path=$all_file_path$eval_path$concept_system_output -gold_standard_path=$gold_standard -eval_path=$all_file_path$eval_path -evaluation_files=$all_files -evaluate=$evaluate


