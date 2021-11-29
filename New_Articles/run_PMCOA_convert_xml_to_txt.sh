#!/usr/bin/env bash

all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'
ignorance_corpus_work_folder='Ignorance-Question-Work-Full-Corpus/'
new_articles='New_Articles/'
article_folder='Articles/'
pmcoa_full_info='PMCOA_full_info/'
FTP_output_folder='FTP_output/'
BioC_output_folder='BioC_output/'
article_extension='.nxml.gz.txt'

article_list='PMC4949713,PMC7547020,PMC7074265,PMC6712354,PMC5904225,PMC4438576,PMC7222517'
#articles='PMC4438576'

declare -a arr=('PMC4949713' 'PMC7547020' 'PMC7074265' 'PMC6712354' 'PMC5904225' 'PMC4438576' 'PMC7222517')

python3 PMCOA_convert_xml_to_txt.py -article_list=$article_list -pmcoa_BioC_folder=$all_file_path$ignorance_corpus_work_folder$new_articles$pmcoa_full_info$BioC_output_folder

for i in "${arr[@]}"
do
    echo $i
    cp $all_file_path$ignorance_corpus_work_folder$new_articles$pmcoa_full_info$BioC_output_folder$i$article_extension $all_file_path$ignorance_corpus_work_folder$new_articles$article_folder/

done