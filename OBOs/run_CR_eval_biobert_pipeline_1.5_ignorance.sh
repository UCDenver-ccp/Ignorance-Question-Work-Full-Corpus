#!/usr/bin/env bash



fiji_path='/Users/mabo1182/'
all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'

negacy_folder='Negacy_seq_2_seq_NER_model/'
concept_recognition_path='Concept-Recognition-as-Translation/'
code='Code/'
code_path=$all_file_path$negacy_folder$concept_recognition_path$code


eval_path='Ignorance-Question-Work-Full-Corpus/OBOs/'
tokenized_files='Tokenized_Files/' #preprocessed article files to be word tokenized for BIO- format
results_span_detection='Results_span_detection/' #results from the span detection runs
concept_norm_files='Concept_Norm_Files/'
pmcid_sentence_files_path='PMCID_files_sentences/'


biobert_path='BIOBERT/'
output='output/'

save_models_path='Models/SPAN_DETECTION/'

model='model.ckpt-' ##TODO: need highest number found - need to gather this from eval_results

biobert_original='biobert_v1.0_pubmed_pmc/'

##list of the ontologies of interest
ontologies="CHEBI,CL,GO_BP,GO_CC,GO_MF,MOP,NCBITaxon,PR,SO,UBERON"

##list of the files to run through the concept recognition pipeline
all_files='PMC6000839,PMC3800883,PMC2885310,PMC4311629,PMC3400371,PMC4897523,PMC3272870,PMC3313761,PMC3342123,PMC3427250,PMC4653418,PMC3279448,PMC6011374,PMC5812027,PMC2396486,PMC3915248,PMC3933411,PMC5240907,PMC4231606,PMC5539754,PMC5226708,PMC5524288,PMC3789799,PMC5546866,PMC5405375,PMC2722583,PMC1247630,PMC1474522,PMC2009866,PMC4428817,PMC5501061,PMC6022422,PMC1533075,PMC1626394,PMC2265032,PMC2516588,PMC2672462,PMC2874300,PMC2889879,PMC2898025,PMC2999828,PMC3205727,PMC3348565,PMC3373750,PMC3513049,PMC3679768,PMC3914197,PMC4122855,PMC4304064,PMC4352710,PMC4377896,PMC4500436,PMC4564405,PMC4653409,PMC4683322,PMC4859539,PMC4954778,PMC4992225,PMC5030620,PMC5143410,PMC5187359,PMC5273824,PMC5540678,PMC5685050,PMC6029118,PMC6033232,PMC6039335,PMC6054603,PMC6056931,PMC2722408,PMC2727050,PMC2913107,PMC3075531,PMC3169551,PMC3271033,PMC3424155,PMC3470091,PMC3659910,PMC3710985,PMC3828574,PMC4037583,PMC4275682,PMC4327187,PMC4380518,PMC4488777,PMC4715834,PMC4973215,PMC5340372,PMC5439533,PMC5658906,PMC5732505'

##if a gold standard exists (true or false)
gold_standard='False'

##the algorithm we are focusing on - specifically BioBERT due to running
algos='BIOBERT'  ##CRF, LSTM, LSTM_CRF, CHAR_EMBEDDINGS, LSTM_ELMO, BIOBERT



##FOR BIOBERT
biobert='BIOBERT'
if [ $algos == $biobert ]; then
    ##0. you have just run the BioBERT models on fiji for span detection
    ##1. Bring the results files local for each ontology - all files with "*_test.txt*"
    declare -a arr=('CHEBI' 'CL' 'GO_BP' 'GO_CC' 'GO_MF' 'MOP' 'NCBITaxon' 'PR' 'SO' 'UBERON')

    ##loop over each ontology and run the corresponding model


    ##Grab all files with "*_test.txt*" local with fiji
    for i in "${arr[@]}"
    do
       echo $i
       results_path=$fiji_path$eval_path$results_span_detection$i/$biobert_path
       local_path=$all_file_path$eval_path$results_span_detection$i/$biobert_path
       scp mabo1182@fiji.colorado.edu:$results_path/*_test.txt* $local_path
       rm $local_path/logits_test.txt

    done


    ##2. Detokenize all BioBERT results files (updated the detokenize script)

    biotags='B,I,O-,O' #ordered for importance
    gold_standard='false'
    true='true'

    declare -a ont=('CHEBI' 'CL' 'GO_BP' 'GO_CC' 'GO_MF' 'MOP' 'NCBITaxon' 'PR' 'SO' 'UBERON')

    ##loop over each ontology and reformat the BioBERT output files to match the input
    for i in "${ont[@]}"
    do
        echo "$i"

        NER_DIR=$all_file_path$eval_path$tokenized_files$biobert/
        OUTPUT_DIR=$all_file_path$eval_path$results_span_detection$i/$biobert/

        ##detokenize the bioBERT results files
        python3 $code_path/biobert_ner_detokenize_updated.py --token_test_path=$OUTPUT_DIR/token_test.txt --label_test_path=$OUTPUT_DIR/label_test.txt --answer_path=$NER_DIR/test.tsv --output_dir=$OUTPUT_DIR --biotags=$biotags --gold_standard=$gold_standard

        echo 'DONE WITH TEST.TSV'


        ##if gold standard then we also want the gold standard information using the ontology_test.tsv files
        if [ $gold_standard == $true ]; then
            ont_test='_test.tsv'
            python3 $code_path/biobert_ner_detokenize_updated.py --token_test_path=$OUTPUT_DIR/token_test.txt --label_test_path=$OUTPUT_DIR/label_test.txt --answer_path=$NER_DIR/$i$ont_test --output_dir=$OUTPUT_DIR --biotags=$biotags --gold_standard=$gold_standard


            ##classification report if gold standard
            python3 $code_path/biobert_classification_report.py --ner_conll_results_path=$OUTPUT_DIR/ --biotags=$biotags --ontology=$i --output_path=$OUTPUT_DIR/ --gold_standard=$gold_standard

            #copy the classification report to the main results with ontology name
            biobert_class_report='_biobert_local_eval_files_classification_report.txt'
            cp $OUTPUT_DIR/biobert_classification_report.txt $eval_path$results_span_detection$i/$i$biobert_class_report


        fi

    done



    biobert_prediction_results=$all_file_path$eval_path$results_span_detection

    ##create the evaluation dataframe!
    python3 $code_path/biobert_eval_dataframe_output.py -ontologies=$ontologies -excluded_files=$all_files -tokenized_file_path=$all_file_path$eval_path$tokenized_files -biobert_prediction_results=$biobert_prediction_results -output_path=$biobert_prediction_results -algos=$algos --pmcid_sentence_files_path=$pmcid_sentence_files_path

fi





##preprocess to get all the concepts for the next steps
python3 $code_path/eval_preprocess_concept_norm_files.py -ontologies=$ontologies -results_span_detection_path=$all_file_path$eval_path$results_span_detection -concept_norm_files_path=$all_file_path$eval_path$concept_norm_files -evaluation_files=$all_files


##run the open_nmt to predict
#run_eval_open_nmt.sh
