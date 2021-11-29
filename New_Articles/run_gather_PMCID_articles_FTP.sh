#!/usr/bin/env bash

all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'
ignorance_corpus_work_folder='Ignorance-Question-Work-Full-Corpus/'
new_articles='New_Articles/'
pmcoa_full_info='PMCOA_full_info/'
FTP_output_folder='FTP_output/'
BioC_output_folder='BioC_output/'

articles='PMC4949713,PMC7547020,PMC7074265,PMC6712354,PMC5904225,PMC4438576,PMC7222517'

#/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/Ignorance-Question-Work-Full-Corpus/New_Articles/PMCOA_full_info/

python3 gather_PMCID_articles_FTP.py -article_list=$articles -PMC_FTP_output=$all_file_path$ignorance_corpus_work_folder$new_articles$pmcoa_full_info$FTP_output_folder -PMC_BioC_output=$all_file_path$ignorance_corpus_work_folder$new_articles$pmcoa_full_info$BioC_output_folder