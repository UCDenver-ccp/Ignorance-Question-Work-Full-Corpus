#!/usr/bin/env bash

algo='BIOBERT'

declare -a arr=('full_unknown' 'explicit_question' 'incomplete_evidence' 'probable_understanding' 'superficial_relationship' 'future_work' 'future_prediction' 'important_consideration' 'anomaly_curious_finding' 'alternative_options_controversy' 'difficult_task' 'problem_complication' 'question_answered_by_this_work' '0_all_combined' '1_binary_combined')

#declare -a arr=('0_all_combined' '1_binary_combined')

fiji_local_path='/Users/mabo1182/'

fiji_scratch_path='/scratch/Users/mabo1182/'



output_models_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/Held_Out_Evaluation/Output_Results/'
biobert_folder='BioBERT_Training_Results/'
crf_folder='CRF_Training_Results/'




## now loop through the above array
crf='CRF'
biobert='BIOBERT'

for i in "${arr[@]}"
do
    echo $i


    ##CRF models and information
    if [ "$algo" == "$crf" ]; then
        cp -r $fiji_scratch_path$output_models_path$crf_folder$i/*  $fiji_local_path$output_models_path$crf_folder$i/

    fi

    ##BIOBERT:
    if [ "$algo" == "$biobert" ]; then
        cp -r $fiji_scratch_path$output_models_path$biobert_folder$i/$biobert/* $fiji_local_path$output_models_path$biobert_folder$i/$biobert/

    fi



done
