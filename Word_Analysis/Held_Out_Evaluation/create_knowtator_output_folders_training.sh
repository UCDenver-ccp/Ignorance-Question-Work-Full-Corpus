#!/usr/bin/env bash

##path to the main craft documents for training
all_file_path='/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/'

corpus_path='/Ignorance-Question-Corpus/'
corpus_name='Ignorance-Question-Corpus'

##folder to the articles within the craft path
articles='Articles/' #want files.txt

##folder to the concept annotations within the craft path
concept_annotation='Annotations/'
ontology_folder='Ontologies/'
profiles_folder='Profiles/'

ontology_file_path='Ontologies/Ontology_Of_Ignorance.owl'
all_lcs_path='Ontologies/Ontology_Of_Ignorance_all_cues_2021-07-30.txt'

##list of ontologies that have annotations to preproess
ontologies='full_unknown,explicit_question,incomplete_evidence,probable_understanding,superficial_relationship,future_work,future_prediction,important_consideration,anomaly_curious_finding,alternative_options_controversy,difficult_task,problem_complication,question_answered_by_this_work,1_binary_combined' #0_all_combined

broad_categories='epistemics,barriers,levels_of_evidence,future_opportunities'

##output path for the BIO- format files that are tokenized
eval_path='Ignorance-Question-Work-Full-Corpus/Word_Analysis/Held_Out_Evaluation/'
output_results='Output_Results/'

##folder name for sentence files
pmcid_sentence_files_path='PMCID_files_sentences/' #the sentence files for the PMC articles'
tokenized_files='Tokenized_Files/' #preprocessed article files to be word tokenized for BIO- format

preprocess_corpus='Ignorance-Question-Work-Full-Corpus/Preprocess_Corpus/Output_Folders/'

corpus_construction='Ignorance-Question-Work-Full-Corpus/Corpus_Construction/'

##corpus name - craft here
corpus='ignorance'
all_lcs_path='Ontologies/Ontology_Of_Ignorance_all_cues_2021-07-30.txt'

##list of excluded files from training: held out eval files for larger corpus
eval_files='PMC6000839,PMC3800883,PMC2885310,PMC4311629,PMC3400371,PMC4897523,PMC3272870,PMC3313761,PMC3342123,PMC3427250,PMC4653418,PMC3279448,PMC6011374,PMC5812027,PMC2396486,PMC3915248,PMC3933411,PMC5240907,PMC4231606,PMC5539754,PMC5226708,PMC5524288,PMC3789799,PMC5546866,PMC5405375,PMC2722583'


training_files='PMC1247630,PMC1474522,PMC2009866,PMC4428817,PMC5501061,PMC6022422,PMC1533075,PMC1626394,PMC2265032,PMC2516588,PMC2672462,PMC2874300,PMC2889879,PMC2898025,PMC2999828,PMC3205727,PMC3348565,PMC3373750,PMC3513049,PMC3679768,PMC3914197,PMC4122855,PMC4304064,PMC4352710,PMC4377896,PMC4500436,PMC4564405,PMC4653409,PMC4683322,PMC4859539,PMC4954778,PMC4992225,PMC5030620,PMC5143410,PMC5187359,PMC5273824,PMC5540678,PMC5685050,PMC6029118,PMC6033232,PMC6039335,PMC6054603,PMC6056931,PMC2722408,PMC2727050,PMC2913107,PMC3075531,PMC3169551,PMC3271033,PMC3424155,PMC3470091,PMC3659910,PMC3710985,PMC3828574,PMC4037583,PMC4275682,PMC4327187,PMC4380518,PMC4488777,PMC4715834,PMC4973215,PMC5340372,PMC5439533,PMC5658906,PMC5732505'


###the algo and the corresponding results file
algos='CRF,BIOBERT'
results_folders='CRF_Training_Results,BioBERT_Training_Results'
output_folder='z_KNOWTATOR_OUTPUT_FORMAT/'
bionlp_folder='z_BIONLP_OUTPUT_FORMAT/'
file_types='0_all_combined,1_binary_combined,13_separate_combined'
knowator_projects='KNOWTATOR_PROJECTS/'
underscore='_'
article_ext='.nxml.gz.txt'
annotation_ext='.nxml.gz.xml.'
annotation_ext2='.xml'
profiles_file='Default.xml'
knowtator_ext='.knowtator'

declare -a arr=('CRF_Training_Results' 'BioBERT_Training_Results')
declare -a files=('0_all_combined' '1_binary_combined' '13_separate_combined')
declare -a train=('PMC1247630' 'PMC1474522' 'PMC2009866' 'PMC4428817' 'PMC5501061' 'PMC6022422' 'PMC1533075' 'PMC1626394' 'PMC2265032' 'PMC2516588' 'PMC2672462' 'PMC2874300' 'PMC2889879' 'PMC2898025' 'PMC2999828' 'PMC3205727' 'PMC3348565' 'PMC3373750' 'PMC3513049' 'PMC3679768' 'PMC3914197' 'PMC4122855' 'PMC4304064' 'PMC4352710' 'PMC4377896' 'PMC4500436' 'PMC4564405' 'PMC4653409' 'PMC4683322' 'PMC4859539' 'PMC4954778' 'PMC4992225' 'PMC5030620' 'PMC5143410' 'PMC5187359' 'PMC5273824' 'PMC5540678' 'PMC5685050' 'PMC6029118' 'PMC6033232' 'PMC6039335' 'PMC6054603' 'PMC6056931' 'PMC2722408' 'PMC2727050' 'PMC2913107' 'PMC3075531' 'PMC3169551' 'PMC3271033' 'PMC3424155' 'PMC3470091' 'PMC3659910' 'PMC3710985' 'PMC3828574' 'PMC4037583' 'PMC4275682' 'PMC4327187' 'PMC4380518' 'PMC4488777' 'PMC4715834' 'PMC4973215' 'PMC5340372' 'PMC5439533' 'PMC5658906' 'PMC5732505')


for i in "${arr[@]}"
do
    echo $i
    algo=$(echo $i | cut -d'_' -f 1)
    algo=$(echo $algo | tr [a-z] [A-Z])

    for j in "${files[@]}"
    do
        echo $j
        mkdir $all_file_path$eval_path$output_results$knowator_projects$i$underscore$j
        cd $all_file_path$eval_path$output_results$knowator_projects$i$underscore$j

        mkdir $articles
        mkdir $concept_annotation
        mkdir $ontology_folder
        mkdir $profiles_folder
        cp $all_file_path$corpus_path/$corpus_name$knowtator_ext .
        mv $corpus_name$knowtator_ext $i$underscore$j$knowtator_ext


        for t in "${train[@]}"
        do
            cp $all_file_path$corpus_path$articles$t$article_ext $articles
            cp $all_file_path$eval_path$output_results$i/$output_folder$j/$t$annotation_ext$algo$annotation_ext2 $concept_annotation
            cp $all_file_path$corpus_path$ontology_file_path $ontology_folder
            cp $all_file_path$corpus_path$profiles_folder$profiles_file $profiles_folder


        done




#    ##CRF models and information
#    if [ "$algo" == "$crf" ]; then
#
#    fi

     done


done
