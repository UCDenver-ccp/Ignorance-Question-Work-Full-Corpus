# Ignorance-Question-Work-Full-Corpus: Word_Analysis

1. CRF_Classification

    a. fiji_run_span_detection.sh: a bash script to run the CRF training to both do hyperparameterization and run the final model with the best performing parameters with 5-fold cross-validation (runs span_detection.py)
        i.  All iterations incldue: fiji_run_span_detection_all_onts_combined.py and fiji_run_span_detection_all_onts_combined_binary.sh
    
    b. SPAN_DETECTION_MODELS: a folder with all the outputs from the CRF model with folders for each ignorance category and the 2 combined (0_all_combined and 1_binary_combined)

2. BioBERT Classification
    
    a. biobert: a folder with all the scripts for training the classifier with a few modified scripts due to errors and the nature of my data
        
        i.   run_ner_original.py - the original NER python script
        ii.  run_ner.py - my modified NER script to allow for more tags besides B,I,O. I added O- to denote the words in between a discontinuity
        iii. run_ner_all_combined.py - another modified NER script to allow for tags along with the ignorance category the words belong to. 
    
    b. run_span_detection_biobert.sh: a bash script that runs the preprocessing for BioBERT in the correct input format (runs span_detection.py)
    
    c. fiji_run_biobert.sh: a bash script that trains a BioBERT model for each ignorance category separately (runs things in biobert/)
        i.  All iterations include: fiji_run_biober_all_onts_combined.py and fiji_run_biobert_all_onts_combined_binary.py
    
    d. SPAN_DETECTION_MODELS: a folder with all the outputs from the BioBERT model with folders for each ignorance category and the 2 combined (0_all_combined and 1_binary_combined)
    
    
    
       
        

3. General shared python scripts
    
    a. span_detection.py: a python script for multiple types of classification algorithms including CRF, BioBERT, and LSTMs.

