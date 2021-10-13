#!/usr/bin/env bash

##path to the main craft documents for training
all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'

corpus_path='/Ignorance-Question-Corpus/'

##folder to the articles within the craft path
articles='Articles/' #want files.txt

##folder to the concept annotations within the craft path
concept_annotation='Annotations/'



##list of ontologies that have annotations to preproess
ontologies='full_unknown,explicit_question,incomplete_evidence,probable_understanding,superficial_relationship,future_work,future_prediction,important_consideration,anomaly_curious_finding,alternative_options_controversy,difficult_task,problem_complication,question_answered_by_this_work,1_binary_combined' #0_all_combined

##output path for the BIO- format files that are tokenized
eval_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/Held_Out_Evaluation/'
output_results='Output_Results/'

##folder name for sentence files
pmcid_sentence_files_path='PMCID_files_sentences/' #the sentence files for the PMC articles'
tokenized_files='Tokenized_Files/' #preprocessed article files to be word tokenized for BIO- format

preprocess_corpus='Ignorance-Question-Work-Full-Corpus/Preprocess_Corpus/Output_Folders/'

corpus_construction='Ignorance-Question-Work-Full-Corpus/Corpus_Construction/'

##corpus name - craft here
corpus='ignorance'
all_lcs_path='Ontologies/Ontology_Of_Ignorance_all_cues_2021-07-30.txt'

##list of excluded files from training: held out eval files for larger corpus
eval_files='PMC6000839,PMC3800883,PMC2885310,PMC4311629,PMC3400371,PMC4897523,PMC3272870,PMC3313761,PMC3342123,PMC3427250,PMC4653418,PMC3279448,PMC6011374,PMC5812027,PMC2396486,PMC3915248,PMC3933411,PMC5240907,PMC4231606,PMC5539754,PMC5226708,PMC5524288,PMC3789799,PMC5546866,PMC5405375,PMC2722583'


training_files='PMC1247630,PMC1474522,PMC2009866,PMC4428817,PMC5501061,PMC6022422,PMC1533075,PMC1626394,PMC2265032,PMC2516588,PMC2672462,PMC2874300,PMC2889879,PMC2898025,PMC2999828,PMC3205727,PMC3348565,PMC3373750,PMC3513049,PMC3679768,PMC3914197,PMC4122855,PMC4304064,PMC4352710,PMC4377896,PMC4500436,PMC4564405,PMC4653409,PMC4683322,PMC4859539,PMC4954778,PMC4992225,PMC5030620,PMC5143410,PMC5187359,PMC5273824,PMC5540678,PMC5685050,PMC6029118,PMC6033232,PMC6039335,PMC6054603,PMC6056931,PMC2722408,PMC2727050,PMC2913107,PMC3075531,PMC3169551,PMC3271033,PMC3424155,PMC3470091,PMC3659910,PMC3710985,PMC3828574,PMC4037583,PMC4275682,PMC4327187,PMC4380518,PMC4488777,PMC4715834,PMC4973215,PMC5340372,PMC5439533,PMC5658906,PMC5732505'


###the algo and the corresponding results file
algos='CRF,BIOBERT'
results_folders='CRF_Classification_Results,BioBERT_Classification_Results'
output_folder='z_BIONLP_OUTPUT_FORMAT/'
separate_all_combined_output='13_separate_combined'


python3 final_output_knowtator_format.py -ontologies=$ontologies -algos=$algos -result_folders=$results_folders -results_path=$all_file_path$eval_path$output_results -output_folder=$output_folder -evaluation_files=$eval_files -separate_all_combined_output=$separate_all_combined_output