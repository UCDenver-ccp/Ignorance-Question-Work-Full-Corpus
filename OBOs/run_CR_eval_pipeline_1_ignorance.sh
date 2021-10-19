#!/usr/bin/env bash

##path to the main craft documents for training
all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'

##path to the held out 30 documents for gold standard evaluation
craft_st_path='../Concept-Recognition-as-Translation/craft-st-2019/'

##path to the concept recognition project
negacy_folder='Negacy_seq_2_seq_NER_model/'
concept_recognition_path='Concept-Recognition-as-Translation/'
code='Code/'

code_path=$all_file_path$negacy_folder$concept_recognition_path$code

##path to the evaluation files where all output will be stored during the evaluation
eval_path='Ignorance-Question-Work-Full-Corpus/OBOs/'
ignorance_corpus='Ignorance-Question-Corpus/'

##Folders for inputs and outputs
concept_system_output='concept_system_output/' #the folder for the final output of the full concept recognition run
article_folder='Articles/' #the folder with the PMC Articles text files
tokenized_files='Tokenized_Files/' #preprocessed article files to be word tokenized for BIO- format

#/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/Negacy_seq_2_seq_NER_model/Concept-Recognition-as-Translation/Models/SPAN_DETECTION/CHEBI
save_models_path='Models/SPAN_DETECTION/' #all the saved models for span detection
results_span_detection='Results_span_detection/' #results from the span detection runs
concept_norm_files='Concept_Norm_Files/' #the processed spans detected for concept normalization on the character level
pmcid_sentence_files_path='PMCID_files_sentences/' #the sentence files for the PMC articles
concept_annotation='concept-annotation/' #the concept annotations for CRAFT

##list of the ontologies of interest
ontologies="CHEBI,CL,GO_BP,GO_CC,GO_MF,MOP,NCBITaxon,PR,SO,UBERON"

##list of the files to run through the concept recognition pipeline
all_files='PMC6000839,PMC3800883,PMC2885310,PMC4311629,PMC3400371,PMC4897523,PMC3272870,PMC3313761,PMC3342123,PMC3427250,PMC4653418,PMC3279448,PMC6011374,PMC5812027,PMC2396486,PMC3915248,PMC3933411,PMC5240907,PMC4231606,PMC5539754,PMC5226708,PMC5524288,PMC3789799,PMC5546866,PMC5405375,PMC2722583,PMC1247630,PMC1474522,PMC2009866,PMC4428817,PMC5501061,PMC6022422,PMC1533075,PMC1626394,PMC2265032,PMC2516588,PMC2672462,PMC2874300,PMC2889879,PMC2898025,PMC2999828,PMC3205727,PMC3348565,PMC3373750,PMC3513049,PMC3679768,PMC3914197,PMC4122855,PMC4304064,PMC4352710,PMC4377896,PMC4500436,PMC4564405,PMC4653409,PMC4683322,PMC4859539,PMC4954778,PMC4992225,PMC5030620,PMC5143410,PMC5187359,PMC5273824,PMC5540678,PMC5685050,PMC6029118,PMC6033232,PMC6039335,PMC6054603,PMC6056931,PMC2722408,PMC2727050,PMC2913107,PMC3075531,PMC3169551,PMC3271033,PMC3424155,PMC3470091,PMC3659910,PMC3710985,PMC3828574,PMC4037583,PMC4275682,PMC4327187,PMC4380518,PMC4488777,PMC4715834,PMC4973215,PMC5340372,PMC5439533,PMC5658906,PMC5732505'

##if a gold standard exists (true or false)
gold_standard='False'

##the span detection algorithm to use
algos='CRF' ##CRF, LSTM, LSTM_CRF, CHAR_EMBEDDINGS, LSTM_ELMO, BIOBERT

##copy all the articles to OBOs/Articles/ folder
cp $all_file_path$ignorance_corpus$article_folder/* $all_file_path$eval_path$article_folder

##preprocess the articles (word tokenize) to prepare for span detection no matter the algorithm
#craft_path - not used (only eval_path)
#concept_recognition_path - not used unless gold standard
#concept_annotation - not used
python3 $code_path/eval_preprocess_docs.py -craft_path=$craft_st_path -concept_recognition_path=$all_file_path$negacy_folder$concept_recognition_path -eval_path=$all_file_path$eval_path -concept_system_output=$concept_system_output -article_folder=$article_folder -tokenized_files=$tokenized_files -pmcid_sentence_files=$pmcid_sentence_files_path -concept_annotation=$concept_annotation -ontologies=$ontologies -evaluation_files=$all_files --gold_standard=$gold_standard


declare -a algos=('CRF' 'BIOBERT')
for algo in "${algos[@]}"
do


    biobert='BIOBERT'
    lstm_elmo='LSTM_ELMO'

    if [ $algo == $biobert ]; then

        ##creates the biobert test.tsv file
        python3 $code_path/eval_span_detection.py -ontologies=$ontologies -excluded_files=$all_files -tokenized_file_path=$all_file_path$eval_path$tokenized_files -save_models_path=$all_file_path$negacy_folder$concept_recognition_path$save_models_path -algos=$algo -output_path=$all_file_path$eval_path$results_span_detection --pmcid_sentence_files_path=$pmcid_sentence_files_path --gold_standard=$gold_standard

        ##copy train.tsv and train_dev.tsv
        ignorance_biobert_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/BioBERT_Classification/SPAN_DETECTION_MODELS/1_binary_combined/BIOBERT/'
        train='train.tsv'
        train_dev='train_dev.tsv'
        cp $all_file_path$ignorance_biobert_path$train  $all_file_path$eval_path$tokenized_files$algo/
        cp $all_file_path$ignorance_biobert_path$train_dev  $all_file_path$eval_path$tokenized_files$algo/


        ## 1. Move ONTOLOGY_test.tsv (where ONTOLOGY are all the ontologies) file to supercomputer for predictions (Fiji)
        ## 2. On the supercomputer run 0_craft_fiji_run_eval_biobert.sh
        ## 3. Move the biobert models local to save for each ontology
        ## 4. Move label_test.txt and token_test.txt locally for each ontology
        ## 5. Run 0_craft_run_eval_biobert_pipepine_1.5.sh to process the results from BioBERT



    ##Run lstm-elmo on supercomputer because issues locally (ideally with GPUs)
    elif [ $algos == $lstm_elmo ]; then
        tokenized_files_updated='Tokenized_Files'
        pmcid_sentence_files_path_updated='PMCID_files_sentences'

        ## 1. Move tokenized files to supercomputer (fiji)
        ## 2. Move sentence files (PMCID_files_sentences/) to supercomputer (fiji)
        ## 3. Run 0_craft_fiji_run_eval_pipeline_1.sh (ONTOLOGY is the ontologies of choice) on supercomputer
        ## 4. Move the /Output_Folders/Evaluation_Files/Results_span_detection/ files for LSTM_ELMO local: ONTOLOGY_LSTM_ELMO_model_weights_local_PMCARTICLE.txt where ONTOLOGY is the ontology of interest and PMCARTICLE is the PMC article ID
        ## 5. Run 0_craft_run_eval_LSTM_ELMO_pipeline_1.5.sh to process the results from LSTM_ELMO


    ## the rest of the span detection algorithms can be run locally
    else

        ##runs the span detection models locally
        python3 $code_path/eval_span_detection.py -ontologies=$ontologies -excluded_files=$all_files -tokenized_file_path=$all_file_path$eval_path$tokenized_files -save_models_path=$all_file_path$negacy_folder$concept_recognition_path$save_models_path -algos=$algo -output_path=$all_file_path$eval_path$results_span_detection --pmcid_sentence_files_path=$pmcid_sentence_files_path --gold_standard=$gold_standard

        ##process the spans to run through concept normalization
        python3 $code_path/eval_preprocess_concept_norm_files.py -ontologies=$ontologies -results_span_detection_path=$all_file_path$eval_path$results_span_detection -concept_norm_files_path=$all_file_path$eval_path$concept_norm_files -evaluation_files=$all_files



    ##run the open_nmt to predict
    #run_eval_open_nmt.sh

    fi


done