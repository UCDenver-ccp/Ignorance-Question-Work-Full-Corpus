#!/usr/bin/env bash

##path to the main craft documents for training
all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'


##path to the evaluation files where all output will be stored during the evaluation
eval_path='Ignorance-Question-Work-Full-Corpus/OBOs/'
ignorance_corpus='Ignorance-Question-Corpus/'
ignorance_preprocess='Ignorance-Question-Work-Full-Corpus/Preprocess_Corpus/Output_Folders/'

##Folders for inputs and outputs
concept_system_output='concept_system_output/' #the folder for the final output of the full concept recognition run
article_folder='Articles/' #the folder with the PMC Articles text files
tokenized_files='Tokenized_Files/' #preprocessed article files to be word tokenized for BIO- format


ignorance_ontology_file_path='Ontologies/Ontology_Of_Ignorance.owl'
ignorance_all_lcs_path='Ontologies/Ontology_Of_Ignorance_all_cues_2021-07-30.txt'

##list of ontologies that have annotations to preproess
ignorance_ontologies='full_unknown,explicit_question,incomplete_evidence,probable_understanding,superficial_relationship,future_work,future_prediction,important_consideration,anomaly_curious_finding,alternative_options_controversy,difficult_task,problem_complication,question_answered_by_this_work' #0_all_combined

ignorance_broad_categories='epistemics,barriers,levels_of_evidence,future_opportunities'

ignorance_extra_ontology_concepts="{'urgent_call_to_action':'important_consideration','than':'alternative_options_controversy','alternative_options':'alternative_options_controversy','is':'explicit_question','epistemics':'epistemics'}"



save_models_path='Models/SPAN_DETECTION/' #all the saved models for span detection
results_span_detection='Results_span_detection/' #results from the span detection runs
concept_norm_files='Concept_Norm_Files/' #the processed spans detected for concept normalization on the character level
pmcid_sentence_files_path='PMCID_files_sentences/' #the sentence files for the PMC articles
concept_annotation='concept-annotation/' #the concept annotations for CRAFT

##list of the ontologies of interest
OBO_ontologies="CHEBI,CL,GO_BP,GO_CC,GO_MF,MOP,NCBITaxon,PR,SO,UBERON"
#OBO_ontologies='CHEBI'

##list of the files to run through the concept recognition pipeline
all_files='PMC6000839,PMC3800883,PMC2885310,PMC4311629,PMC3400371,PMC4897523,PMC3272870,PMC3313761,PMC3342123,PMC3427250,PMC4653418,PMC3279448,PMC6011374,PMC5812027,PMC2396486,PMC3915248,PMC3933411,PMC5240907,PMC4231606,PMC5539754,PMC5226708,PMC5524288,PMC3789799,PMC5546866,PMC5405375,PMC2722583,PMC1247630,PMC1474522,PMC2009866,PMC4428817,PMC5501061,PMC6022422,PMC1533075,PMC1626394,PMC2265032,PMC2516588,PMC2672462,PMC2874300,PMC2889879,PMC2898025,PMC2999828,PMC3205727,PMC3348565,PMC3373750,PMC3513049,PMC3679768,PMC3914197,PMC4122855,PMC4304064,PMC4352710,PMC4377896,PMC4500436,PMC4564405,PMC4653409,PMC4683322,PMC4859539,PMC4954778,PMC4992225,PMC5030620,PMC5143410,PMC5187359,PMC5273824,PMC5540678,PMC5685050,PMC6029118,PMC6033232,PMC6039335,PMC6054603,PMC6056931,PMC2722408,PMC2727050,PMC2913107,PMC3075531,PMC3169551,PMC3271033,PMC3424155,PMC3470091,PMC3659910,PMC3710985,PMC3828574,PMC4037583,PMC4275682,PMC4327187,PMC4380518,PMC4488777,PMC4715834,PMC4973215,PMC5340372,PMC5439533,PMC5658906,PMC5732505'

#all_files='PMC6000839'

OBO_model_dict="{'CHEBI':'BIOBERT','CL':'BIOBERT','GO_BP':'CRF','GO_CC':'BIOBERT','GO_MF':'BIOBERT','MOP':'BIOBERT','NCBITaxon':'CRF','PR':'BIOBERT','SO':'BIOBERT','UBERON':'BIOBERT'}"



python3 OBO_stats.py -OBO_bionlp_file_path=$all_file_path$eval_path$concept_system_output -ignorance_ontologies=$ignorance_ontologies -ignorance_broad_categories=$ignorance_broad_categories -ignorance_all_lcs_path=$all_file_path$ignorance_corpus$ignorance_all_lcs_path -ignorance_extra_ontology_concepts=$ignorance_extra_ontology_concepts -ignorance_ontology_file_path=$all_file_path$ignorance_corpus$ignorance_ontology_file_path -ignorance_article_path=$all_file_path$ignorance_preprocess$article_folder -ignorance_tokenized_files_path=$all_file_path$ignorance_preprocess$tokenized_files -ignorance_sentence_folder_path=$all_file_path$ignorance_preprocess$pmcid_sentence_files_path -OBO_ontologies=$OBO_ontologies -evaluation_files=$all_files -OBO_model_dict=$OBO_model_dict -OBO_output_path=$all_file_path$eval_path