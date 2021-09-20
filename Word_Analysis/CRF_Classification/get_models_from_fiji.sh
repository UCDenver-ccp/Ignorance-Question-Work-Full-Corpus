#!/usr/bin/env bash


#algo='char_embeddings'
algo='CRF'
#algo='BIOBERT'

declare -a arr=('full_unknown' 'explicit_question' 'incomplete_evidence' 'probable_understanding' 'superficial_relationship' 'future_work' 'future_prediction' 'important_consideration' 'anomaly_curious_finding' 'alternative_options_controversy' 'difficult_task' 'problem_complication' 'question_answered_by_this_work')

declare -a arr=('0_all_combined' '1_binary_combined')


## now loop through the above array
crf='CRF'
biobert='BIOBERT'

for i in "${arr[@]}"
do
    echo $i


    ##CRF models and information
    if [ "$algo" == "$crf" ]; then
        scp mabo1182@fiji.colorado.edu:/Users/mabo1182/epistemic_classification/Models/SPAN_DETECTION/$i/*  /Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/0_Gold_Standard_Annotation/Concept-Recognition-as-Translation-master/Models/SPAN_DETECTION/$i/

    fi

    ##BIOBERT:
    if [ "$algo" == "$biobert" ]; then
        scp mabo1182@fiji.colorado.edu:/Users/mabo1182/epistemic_classification/Models/SPAN_DETECTION/$i/$algo/output/*.txt  /Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/0_Gold_Standard_Annotation/Concept-Recognition-as-Translation-master/Models/SPAN_DETECTION/$i/$algo/output/

    fi



done
