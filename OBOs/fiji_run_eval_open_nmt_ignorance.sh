#!/usr/bin/env bash

CR_models_base_path='/Users/mabo1182/negacy_project/'
all_file_path='/scratch/Users/mabo1182/'
concept_recognition_path='Concept-Recognition-as-Translation/'
code='Code/'
all_code_path=$CR_models_base_path$concept_recognition_path$code
concept_norm_models='Models/CONCEPT_NORMALIZATION/'
full_models='full_files/seq_2_seq_output/'


##path to the evaluation files where all output will be stored during the evaluation
eval_path='Ignorance-Question-Work-Full-Corpus/OBOs/'

##concept normalization folder
concept_norm_files='Concept_Norm_Files/'

##results from concept normalization folder
results_concept_norm_files='Results_concept_norm_files/'

##name of the model we are using for openNMT
declare -a mod=('model-char_step_100000')

##name of character source file that we want to predict the concept IDs for on the character level
char_file='_combo_src_file_char.txt'

##the output extension name for the predictions
char_file_output='_pred.txt'


##loop over each ontology openNMT model and run it for concept normalization
declare -a ont=('CHEBI' 'CL' 'GO_BP' 'GO_CC' 'GO_MF' 'MOP' 'NCBITaxon' 'PR' 'SO' 'UBERON')

for i in "${ont[@]}"
  do
    echo "$i"
      for j in "${mod[@]}"
      do
        ##runs the opennmt model for each ontology
        onmt_translate -model $CR_models_base_path$concept_recognition_path$concept_norm_models$i/$full_models$i-$j.pt -src $all_file_path$eval_path$concept_norm_files$i/$i$char_file -output $all_file_path$eval_path$results_concept_norm_files$i/$i-$j$char_file_output -replace_unk #-verbose #$i/
      done
  done
