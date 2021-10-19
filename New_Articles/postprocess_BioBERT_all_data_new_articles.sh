#!/usr/bin/env bash


##path to the main craft documents for training
all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'
fiji_path='/Users/mabo1182/'

corpus_path='/Ignorance-Question-Corpus/'

##folder to the articles within the craft path
articles='Articles/' #want files.txt

##folder to the concept annotations within the craft path
concept_annotation='Annotations/'

##list of ontologies that have annotations to preproess
ontologies='full_unknown,explicit_question,incomplete_evidence,probable_understanding,superficial_relationship,future_work,future_prediction,important_consideration,anomaly_curious_finding,alternative_options_controversy,difficult_task,problem_complication,question_answered_by_this_work,0_all_combined,1_binary_combined'

##output path for the BIO- format files that are tokenized
eval_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/Held_Out_Evaluation/'
output_path='Word_Analysis_Output_Results/BioBERT_Classification_Results/'
new_articles_path='Ignorance-Question-Work-Full-Corpus/New_Articles/'


##folder name for sentence files
pmcid_sentence_files_path='PMCID_files_sentences/' #the sentence files for the PMC articles'
tokenized_files='Tokenized_Files/' #preprocessed article files to be word tokenized for BIO- format
save_models_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/BioBERT_Classification/SPAN_DETECTION_MODELS/'

biobert_scripts_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/BioBERT_Classification/biobert/'

##corpus name - craft here
corpus='ignorance'
all_lcs_path='/Ignorance-Question-Corpus/Ontologies/Ontology_Of_Ignorance_all_cues_2021-07-30.txt'

##list of excluded files from training: held out eval files for larger corpus
#evaluation_files="all" #TODO
new_article_files='PMC7222517'

##if a gold standard exists (true or false)
gold_standard='false' #TODO!!!
gs_tokenized_files='Ignorance-Question-Work-Full-Corpus/Preprocess_Corpus/Output_Folders/Tokenized_Files/'

biotags='B,I,O-,O' #ordered for importance
true='true'

algos='BIOBERT'



#FOR BIOBERT
biobert='BIOBERT'

if [ $algos == $biobert ]; then
#    ##move test.tsv file to fiji for predictions and bring it local when done - label_test.txt are the labels

#
#    #GO TO FIJI_RUN_EVAL_BIOBERT!
#    ##TODO: biobert run classification algorithm - fiji_run_eval_biobert_all_data.sh and fiji_run_eval-biobert_all_data_all_combined.sh on fiji!!!
#    #sbatch GPU_run_fiji_eval_biobert_all_data.sbatch - runs fiji_run_eval_biobert_all_data.sh
#    #sbatch GPU_run_fiji_eval_biobert_all_data_all_combined.sbatch - runs fiji_run_eval_biobert_all_data_all_combined.sh



    ##BRING ALL OUTPUT LOCALLY FOR BIOBERT
    declare -a arr=('full_unknown' 'explicit_question' 'incomplete_evidence' 'probable_understanding' 'superficial_relationship' 'future_work' 'future_prediction' 'important_consideration' 'anomaly_curious_finding' 'alternative_options_controversy' 'difficult_task' 'problem_complication' 'question_answered_by_this_work' '0_all_combined' '1_binary_combined')

#    declare -a arr=('0_all_combined' '1_binary_combined')
#
#    ##loop over each ontology and run the corresponding model

    for i in "${arr[@]}"
    do
        ##results for prediction
        echo $i
        results_path=$fiji_path$new_articles_path$output_path$i/$biobert
        local_path=$all_file_path$new_articles_path$output_path$i/$biobert
        scp mabo1182@fiji.colorado.edu:$results_path/*.txt $local_path/
        rm $local_path/logits_test.txt
    done

    ###ner_detokenize_updated for predictions only
    #updated detokenize to put all stuff back together to CONLL format!


    declare -a ont=('full_unknown' 'explicit_question' 'incomplete_evidence' 'probable_understanding' 'superficial_relationship' 'future_work' 'future_prediction' 'important_consideration' 'anomaly_curious_finding' 'alternative_options_controversy' 'difficult_task' 'problem_complication' 'question_answered_by_this_work' '0_all_combined' '1_binary_combined')

#    declare -a ont=('0_all_combined' '1_binary_combined')


    for i in "${ont[@]}"
    do
        echo "$i"
#        tokenized_files='Tokenized_Files'
#        results_span_detection='Results_span_detection/'
        NER_DIR=$all_file_path$new_articles_path$tokenized_files$biobert
        OUTPUT_DIR=$all_file_path$new_articles_path$output_path$i/$biobert

        python3 $all_file_path$biobert_scripts_path/biobert_ner_detokenize_updated.py --token_test_path=$OUTPUT_DIR/token_test.txt --label_test_path=$OUTPUT_DIR/label_test.txt --answer_path=$NER_DIR/test.tsv --output_dir=$OUTPUT_DIR --biotags=$biotags --gold_standard=$gold_standard

        echo 'DONE WITH TEST.TSV'


        ##if gold standard then we also want the gold standard information using the ontology_test.tsv files
        if [ $gold_standard == $true ]; then
            ont_test='_test.tsv'
            python3 $all_file_path$biobert_scripts_path/biobert_ner_detokenize_updated.py --token_test_path=$OUTPUT_DIR/token_test.txt --label_test_path=$OUTPUT_DIR/label_test.txt --answer_path=$NER_DIR/$i$ont_test --output_dir=$OUTPUT_DIR --biotags=$biotags --gold_standard=$gold_standard


            ##classification report if gold standard

            python3 $all_file_path$eval_path/biobert_classification_report.py --ner_conll_results_path=$OUTPUT_DIR/ --biotags=$biotags --ontology=$i --output_path=$OUTPUT_DIR/ --gold_standard=$gold_standard

            #copy the classification report to the main results with ontology name
            biobert_class_report='_biobert_local_eval_files_classification_report_full.txt'

            cp $OUTPUT_DIR/biobert_classification_report.txt $all_file_path$eval_path$output_path$i/$i$biobert_class_report



        fi

    done


#    tokenized_files='Tokenized_Files/'
#    results_span_detection='Results_span_detection/'
#    biobert_prediction_results=$concept_recognition_master_path$output_folders$results_span_detection
#    ontologies='1_binary_combined'

    ##create the evaluation dataframe!
    python3 $all_file_path$eval_path/biobert_eval_dataframe_output.py -ontologies=$ontologies -excluded_files=$new_article_files -tokenized_file_path=$all_file_path$new_articles_path$tokenized_files -biobert_prediction_results=$all_file_path$new_articles_path$output_path -output_path=$all_file_path$new_articles_path$output_path -algos=$algos --pmcid_sentence_files_path=$pmcid_sentence_files_path

fi





###preprocess to get all the concepts for the next steps - preprocess so we can see all the terms for all ontologies
#
#ontologies='1_binary_combined'
#python3 eval_preprocess_concept_norm_files.py -ontologies=$ontologies -results_span_detection_path=$concept_recognition_master_path$output_folders$results_span_detection -concept_norm_files_path=$concept_recognition_master_path$output_folders$concept_norm_files -evaluation_files=$evaluation_files
#
#
#
###run the open_nmt to predict
##run_eval_open_nmt.sh
