#!/usr/bin/env bash

algo='BIOBERT'

declare -a arr=('CHEBI' 'CL' 'GO_BP' 'GO_CC' 'GO_MF' 'MOP' 'NCBITaxon' 'PR' 'SO' 'UBERON')

#declare -a arr=('0_all_combined' '1_binary_combined')

fiji_local_path='/Users/mabo1182/'

fiji_scratch_path='/scratch/Users/mabo1182/'



output_models_path='Ignorance-Question-Work-Full-Corpus/OBOs/Results_span_detection/'
not_here='We only have this working for Biobert but feel free to add'



## now loop through the above array
crf='CRF'
biobert='BIOBERT'

for i in "${arr[@]}"
do
    echo $i


    ##BIOBERT:
    if [ "$algo" == "$biobert" ]; then
        cp -r $fiji_scratch_path$output_models_path$i/$biobert/* $fiji_local_path$output_models_path$i/$biobert/

    else

        echo $not_here

    fi



done
