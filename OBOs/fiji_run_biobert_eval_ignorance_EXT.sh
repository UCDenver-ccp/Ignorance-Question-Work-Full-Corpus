#!/usr/bin/env bash

####move test.tsv file to fiji for predictions
#prediction_file='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/Negacy_seq_2_seq_NER_model/ConceptRecognition/Evaluation_Files/Tokenized_Files/BIOBERT/test.tsv'
#scp $prediction_file mabo1182@fiji.colorado.edu:/Users/mabo1182/negacy_project/Evaluation_Files/Tokenized_Files/BIOBERT/
#scratch_CR_models_base_path='/scratch/Users/mabo1182/negacy_project/'
CR_models_base_path='/scratch/Users/mabo1182/negacy_project/'
all_file_path='/scratch/Users/mabo1182/'
non_scratch_file_path='/Users/mabo1182/'

concept_recognition_path='Concept-Recognition-as-Translation/'
code='Code/'
all_code_path=$CR_models_base_path$concept_recognition_path$code

eval_path='Ignorance-Question-Work-Full-Corpus/OBOs/'
tokenized_files='Tokenized_Files/' #preprocessed article files to be word tokenized for BIO- format
results_span_detection='Results_span_detection/' #results from the span detection runs

biobert_path='BIOBERT/'
output='output/'

save_models_path='Models/SPAN_DETECTION/'

model='model.ckpt-' ##TODO: need highest number found - need to gather this from eval_results

biobert_original='biobert_v1.0_pubmed_pmc/'

algo='BIOBERT'


##loop over each ontology and run the corresponding model
##biobert run classification algorithm
declare -a arr=('CHEBI_EXT' 'CL_EXT' 'GO_BP_EXT' 'GO_CC_EXT' 'GO_MF_EXT' 'MOP_EXT' 'NCBITaxon_EXT' 'PR_EXT' 'SO_EXT' 'UBERON_EXT')
#declare -a arr=('CHEBI_EXT')



for i in "${arr[@]}"
do
    echo $i
    model_file_path=$CR_models_base_path$concept_recognition_path$save_models_path$i/$biobert_path$output

    NER_DIR=$all_file_path$eval_path$tokenized_files$biobert_path
    OUTPUT_DIR=$all_file_path$eval_path$results_span_detection$i/$biobert_path


    cp $model_file_path/* $OUTPUT_DIR
    cp $model_file_path/* $non_scratch_file_path$eval_path$results_span_detection$i/$biobert_path



    ##get the global step num for the final algorithm from the results of training!
    python3 $all_code_path/biobert_model_eval_result.py -eval_results_path=$model_file_path -ontology=$i -algo=$algo
    global_step_file='global_step_num.txt'
    eval_global_step_file=$model_file_path$global_step_file

    global_step=$(<$eval_global_step_file)
    echo $global_step



    #https://blog.insightdatascience.com/using-bert-for-state-of-the-art-pre-training-for-natural-language-processing-1d87142c29e7
    python3 $all_code_path/biobert/run_ner.py --do_train=true --do_predict=true --vocab_file=$all_code_path$biobert_original/vocab.txt --bert_config_file=$all_code_path$biobert_original/bert_config.json --init_checkpoint=$OUTPUT_DIR$model$global_step  --mmax_seq_length=410 --num_train_epochs=1.0 --data_dir=$NER_DIR --output_dir=$OUTPUT_DIR


done


###move label_test.txt and token_test.txt locally to do ner_detokenize and create dataframe for next 