#!/usr/bin/env bash

##biobert requirement information: https://github.com/dmis-lab/biobert
## $ git clone https://github.com/dmis-lab/biobert.git
#$ cd biobert; pip install -r requirements.txt

all_file_path='/scratch/Users/mabo1182/'

##biobert model directory and model name
BIOBERT_DIR='Ignorance-Question-Work-Full-Corpus/Word_Analysis/BioBERT_Classification/biobert_v1.0_pubmed_pmc' #pubmed and pmc is the closest model to our data
biobert_model='biobert_model.ckpt' #the beginning of the model name up until .ckpt


##output information for the biobert models
span_detection_models='Ignorance-Question-Work-Full-Corpus/Word_Analysis/BioBERT_Classification/SPAN_DETECTION_MODELS/'
biobert='/BIOBERT'
output='/output'

##the biotags we are using
biotags='B,I,O,O-'

##array of all the ontologies of interest
declare -a ont=('full_unknown' 'explicit_question' 'incomplete_evidence' 'probable_understanding' 'superficial_relationship' 'future_work' 'future_prediction' 'important_consideration' 'anomaly_curious_finding' 'alternative_options_controversy' 'difficult_task' 'problem_complication' 'question_answered_by_this_work')


##loop over each ontology model and train them
for i in "${ont[@]}"
  do
    echo "$i"
    ##named entitity recognition directory and output directory for the final models
    NER_DIR=$all_file_path$span_detection_models$i$biobert
    OUTPUT_DIR=$all_file_path$span_detection_models$i$biobert$output

    #need to delete all the stuff in the folder so that it will retrain the model
	rm -rf $OUTPUT_DIR
	mkdir $OUTPUT_DIR/

	#run the ner stuff with BERT tuning
	python3 run_ner.py --do_train=true --do_eval=true --do_predict=true --vocab_file=$all_file_path$BIOBERT_DIR/vocab.txt --bert_config_file=$all_file_path$BIOBERT_DIR/bert_config.json --init_checkpoint=$all_file_path$BIOBERT_DIR/$biobert_model --mmax_seq_length=410 --train_batch_size=32 --eval_batch_size=8 --predict_batch_size=8 --learning_rate=1e-5 --num_train_epochs=10.0 --data_dir=$NER_DIR --output_dir=$OUTPUT_DIR


#	#detokenize to put the BERT format back together into Conll format (updated the original detokenized file)
#	python3 biobert_ner_detokenize_updated.py --token_test_path=$OUTPUT_DIR/token_test.txt --label_test_path=$OUTPUT_DIR/label_test.txt --answer_path=$NER_DIR/test.tsv --output_dir=$OUTPUT_DIR

  done



#tensorboard          1.11.0
#tensorflow           2.1.0
#tensorflow-estimator 2.1.0
#tensorflow-gpu       1.11.0
#tensorflow-hub       0.7.0