# Ignorance-Question-Work-Full-Corpus

All supporting documents and scripts for the Full Ignorance Corpus focusing on prenatal nutrition. 

## Folders:

1. Corpus_Construction: The python and bash scripts used to create the corpus including

	a. automatic_ontology_insertion: scripts for updating the ontology (taxonomy of ignorance) and the annotations after each round of annotation incorporating new lexical cues into both.

	b. IAA_calculations: scripts for calculating the inter-annotator agreement (IAA) while also creating .xml files of the combined annotations. IAA is calculated as F1 score.

2. Preprocess_Corpus: Python scripts and output folders for use in classification algorithms - PMCID sentence files and Tokenzied file
	
	a. run_preprcess_docs.sh: tokenizes all annotation files into sentences and BIO(-) tags by ignorance taxonomy category (preprocess_docs.py)

	b. run_combine_all_tokenized_files_by_pmcid.sh: combines all tokenized files into a binary ignorance or not and all combined (combine_all_tokenized_files_by_pmcid.py)

	c. Output_Folders: all folders for the outputs of the above two scripts

		i.  PMCID_files_sentences: all sentence files per pmcid

		ii. Tokenized_Files: all tokenized files by ignorance taxonomy category

3. Sentence_Analysis:

4. Word_Analysis: