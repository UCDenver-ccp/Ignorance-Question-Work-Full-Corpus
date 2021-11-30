#!/usr/bin/env bash


##local
all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'
new_articles_path='Ignorance-Question-Work-Full-Corpus/New_Articles/'
##folder name for sentence files
article_folder='Articles'
pmcid_sentence_files_path='PMCID_files_sentences/' #the sentence files for the PMC articles'
tokenized_files='Tokenized_Files/' #preprocessed article files to be word tokenized for BIO- format
word_analysis_output_path='Word_Analysis_Output_Results/'



##fiji
fiji_local_path='/Users/mabo1182/'
fiji_scratch_path='/scratch/Users/mabo1182/'

scp -r $all_file_path$new_articles_path$article_folder mabo1182@fiji.colorado.edu:$fiji_local_path$new_articles_path

scp -r $all_file_path$new_articles_path$article_folder mabo1182@fiji.colorado.edu:$fiji_scratch_path$new_articles_path


scp -r $all_file_path$new_articles_path$pmcid_sentence_files_path mabo1182@fiji.colorado.edu:$fiji_local_path$new_articles_path

scp -r $all_file_path$new_articles_path$pmcid_sentence_files_path mabo1182@fiji.colorado.edu:$fiji_scratch_path$new_articles_path



scp -r $all_file_path$new_articles_path$tokenized_files mabo1182@fiji.colorado.edu:$fiji_local_path$new_articles_path

scp -r $all_file_path$new_articles_path$tokenized_files mabo1182@fiji.colorado.edu:$fiji_scratch_path$new_articles_path



scp -r $all_file_path$new_articles_path$word_analysis_output_path mabo1182@fiji.colorado.edu:$fiji_local_path$new_articles_path

scp -r $all_file_path$new_articles_path$word_analysis_output_path mabo1182@fiji.colorado.edu:$fiji_scratch_path$new_articles_path