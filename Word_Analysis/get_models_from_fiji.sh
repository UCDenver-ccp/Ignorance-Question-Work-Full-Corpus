#!/usr/bin/env bash


#algo='char_embeddings'
#algo='CRF'
algo='BIOBERT'

declare -a arr=('full_unknown' 'explicit_question' 'incomplete_evidence' 'probable_understanding' 'superficial_relationship' 'future_work' 'future_prediction' 'important_consideration' 'anomaly_curious_finding' 'alternative_options_controversy' 'difficult_task' 'problem_complication' 'question_answered_by_this_work' '0_all_combined' '1_binary_combined')

#declare -a arr=('0_all_combined' '1_binary_combined')

fiji_path='/Users/mabo1182/'

local_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'

CRF_models_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/CRF_Classification/SPAN_DETECTION_MODELS/'

BioBERT_models_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/BioBERT_Classification/SPAN_DETECTION_MODELS/'




## now loop through the above array
crf='CRF'
biobert='BIOBERT'

for i in "${arr[@]}"
do
    echo $i


    ##CRF models and information
    if [ "$algo" == "$crf" ]; then
        scp mabo1182@fiji.colorado.edu:$fiji_path$CRF_models_path$i/*  $local_path$CRF_models_path$i/

    fi

    ##BIOBERT:
    if [ "$algo" == "$biobert" ]; then
        scp mabo1182@fiji.colorado.edu:$fiji_path$BioBERT_models_path$i/$algo/output/*.txt  $local_path$BioBERT_models_path$i/$algo/output/

    fi



done
