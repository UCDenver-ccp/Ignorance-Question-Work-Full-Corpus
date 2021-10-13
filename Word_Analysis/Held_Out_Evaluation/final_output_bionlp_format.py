import os
import pandas as pd
import datetime
import argparse
import ast

def split_up_0_all_combined_data(tokenized_file_path, ontology, shorthand_ont_dict, evaluation_files, output_folder):
    ##split up all the files from 0_all_combined into smaller folders so we can handle it

    for root, directories, filenames in os.walk(tokenized_file_path + ontology + '/'):
        for filename in sorted(filenames):
            print(filename)
            # print(evaluation_files)
            # print(filename.split('_')[-1].replace('.nxml.gz.txt', ''))

            ##per pmcid file - want to combine per ontology
            # print([filename.endswith('.nxml.gz.txt'), ontology in filename, 'local' in filename, 'pred' not in filename, (filename.split('_')[-1].replace('.txt','') in evaluation_files or evaluation_files == ['all'])])
            if filename.endswith(
                    '.nxml.gz.txt') and ontology in filename and 'local' in filename and 'pred' not in filename and ('crf_model_full' in filename or 'biobert' in filename) and (
                    filename.split('_')[-1].replace('.nxml.gz.txt', '') in evaluation_files or evaluation_files == ['all']):
                # print(filename)

                for shorthand, ont in shorthand_ont_dict.items():
                    # print(shorthand, ont)
                    ##columns = ['PMCID', 'SENTENCE_NUM', 'SENTENCE_START', 'SENTENCE_END', 'WORD', 'POS_TAG', 'WORD_START', 'WORD_END', 'BIO_TAG', 'PMC_MENTION_ID', 'ONTOLOGY_CONCEPT_ID', 'ONTOLOGY_LABEL']

                    pmc_tokenized_file_df = pd.read_csv(root + filename, sep='\t', header=0, quotechar='"',
                                                        quoting=3)  # , encoding='utf-8', engine='python')

                    for index, row in pmc_tokenized_file_df.iterrows():
                        ##concepts: ONTOLOGY_DICT - pmc_mention_id -> [sentence_num, [word], [(word_indices)], span_model, [biotags]]

                        span_model = filename.replace('.txt', '')
                        sentence_num = row['SENTENCE_NUM']
                        word = str(row['WORD'])
                        word_start = row['WORD_START']
                        word_end = row['WORD_END']
                        bio_tag = row['BIO_TAG']

                        ##all Nones!
                        pmc_mention_id = row['PMC_MENTION_ID']
                        ontology_concept_id = row['ONTOLOGY_CONCEPT_ID']
                        ontology_label = row['ONTOLOGY_LABEL']
                        # all_nones = {pmc_mention_id, ontology_concept_id, ontology_label}

                        # print('word', word, bio_tag, word_start, word_end)

                        ##the dataframe reads the word 'null' as a NaN which is bad and so we change it
                        if word == 'nan':
                            word = 'null'
                            # print('NULL WORD!')
                            # print(row)
                            # raise Exception('ERROR IN DATAFRAME WITH A WEIRD VALUE!')

                        if {pmc_mention_id, ontology_concept_id, ontology_label} != {'None'}:

                            print(pmc_mention_id, ontology_concept_id, ontology_label)
                            raise Exception('ERROR WITH SPAN DETECTION NONES AT THE END!')
                        else:
                            ##split up the files by ontology

                            ##beginning of a concept
                            if bio_tag == 'B-%s' %(shorthand.upper()):
                                ##set the value of pmc_mention_id also
                                pmc_tokenized_file_df.at[index, 'PMC_MENTION_ID'] = pmc_mention_id
                                pmc_tokenized_file_df.at[index, 'BIO_TAG'] = 'B'


                            ##continuation of a word - sometimes missing a B
                            elif bio_tag == 'I-%s' %(shorthand.upper()):

                                ##set the value of pmc_mention_id also
                                pmc_tokenized_file_df.at[index, 'PMC_MENTION_ID'] = pmc_mention_id
                                pmc_tokenized_file_df.at[index, 'BIO_TAG'] = 'I'

                            ##discontinuity
                            elif bio_tag == 'O-%s' %(shorthand.upper()):
                                pmc_tokenized_file_df.at[index, 'BIO_TAG'] = 'O-'

                            ##end of concept/ no concept
                            elif bio_tag == 'O':
                                pass

                            ##these are all the other tags for the other onts
                            elif bio_tag.split('-')[0] in ['B','I','O']:
                                pmc_tokenized_file_df.at[index, 'BIO_TAG'] = 'O'

                            else:  # 'O-' continuously
                                print(bio_tag)
                                raise Exception('ERROR WITH A WEIRD TAG OTHER THAN THE 4!')

                            # for pmc_mention_id in ontology_dict:
                            #     if '...' in ontology_dict[pmc_mention_id][1]:
                            #         # print(ontology_dict[pmc_mention_id])
                            #         pass

                    ##output the new updated dataframe with pmc_mention_id labels
                    pmc_tokenized_file_df.to_csv('%s%s/%s' % (output_folder, ont, filename.replace(ontology, '%s_%s' %(ontology, ont))), sep='\t', index=False)


def preprocess_data(tokenized_file_path, ontology, ontology_dict, evaluation_files):
    pmc_mention_id_index = 0  ##provide an id for it to use as its unique identifier - with pmcid

    for root, directories, filenames in os.walk(tokenized_file_path + ontology + '/'):
        for filename in sorted(filenames):
            # print(filename)
            # print(evaluation_files)
            # print(filename.split('_')[-1].replace('.nxml.gz.txt', ''))

            ##per pmcid file - want to combine per ontology
            # print([filename.endswith('.nxml.gz.txt'), ontology in filename, 'local' in filename, 'pred' not in filename, (filename.split('_')[-1].replace('.txt','') in evaluation_files or evaluation_files == ['all'])])
            if filename.endswith(
                    '.nxml.gz.txt') and ontology in filename and 'local' in filename and 'pred' not in filename and ('crf_model_full' in filename or 'biobert' in filename) and (
                    filename.split('_')[-1].replace('.nxml.gz.txt', '') in evaluation_files or evaluation_files == ['all']):
                # print(filename)
                pmc_mention_id_index += 1  ##need to ensure we go up one always

                ##columns = ['PMCID', 'SENTENCE_NUM', 'SENTENCE_START', 'SENTENCE_END', 'WORD', 'POS_TAG', 'WORD_START', 'WORD_END', 'BIO_TAG', 'PMC_MENTION_ID', 'ONTOLOGY_CONCEPT_ID', 'ONTOLOGY_LABEL']

                pmc_tokenized_file_df = pd.read_csv(root + filename, sep='\t', header=0, quotechar='"',
                                                    quoting=3)  # , encoding='utf-8', engine='python')

                for index, row in pmc_tokenized_file_df.iterrows():
                    ##concepts: ONTOLOGY_DICT - pmc_mention_id -> [sentence_num, [word], [(word_indices)], span_model, [biotags]]

                    span_model = filename.replace('.txt', '')
                    sentence_num = row['SENTENCE_NUM']
                    word = str(row['WORD'])
                    word_start = row['WORD_START']
                    word_end = row['WORD_END']
                    bio_tag = row['BIO_TAG']

                    ##all Nones!
                    pmc_mention_id = row['PMC_MENTION_ID']
                    ontology_concept_id = row['ONTOLOGY_CONCEPT_ID']
                    ontology_label = row['ONTOLOGY_LABEL']
                    # all_nones = {pmc_mention_id, ontology_concept_id, ontology_label}

                    # print('word', word, bio_tag, word_start, word_end)

                    ##the dataframe reads the word 'null' as a NaN which is bad and so we change it
                    if word == 'nan':
                        word = 'null'
                        # print('NULL WORD!')
                        # print(row)
                        # raise Exception('ERROR IN DATAFRAME WITH A WEIRD VALUE!')

                    if {pmc_mention_id, ontology_concept_id, ontology_label} != {'None'}:

                        print(pmc_mention_id, ontology_concept_id, ontology_label)
                        raise Exception('ERROR WITH SPAN DETECTION NONES AT THE END!')
                    else:
                        ##TODO: issues here!
                        ##update pmc_mention_id to be an actual id: Ontology_yyyy_mm_dd_Instance_#####
                        str_date = datetime.date.today()

                        str_date = str_date.strftime("%Y-%m-%d")

                        pmc_mention_id = '%s_%s_%s_%s' % (ontology, str_date.replace('-', '_'), 'Instance',
                                                          pmc_mention_id_index)  # create a pmc_mention_id for future reference

                        ##beginning of a concept
                        if bio_tag == 'B':
                            if ontology_dict.get(pmc_mention_id):
                                pmc_mention_id_index += 1
                                pmc_mention_id = '%s_%s_%s_%s' % (
                                ontology, str_date.replace('-', '_'), 'Instance', pmc_mention_id_index)
                                ontology_dict[pmc_mention_id] = [sentence_num, [word], [(word_start, word_end)],
                                                                 span_model]
                            else:
                                ontology_dict[pmc_mention_id] = [sentence_num, [word], [(word_start, word_end)],
                                                                 span_model]

                            ##set the value of pmc_mention_id also
                            pmc_tokenized_file_df.at[index, 'PMC_MENTION_ID'] = pmc_mention_id


                        ##continuation of a word - sometimes missing a B
                        elif bio_tag == 'I':
                            # print('word', word, word_start, word_end)
                            ##TODO: error because there is no B nearby - the ontology_dict doesn't have it!
                            if ontology_dict.get(pmc_mention_id):
                                ontology_dict[pmc_mention_id][1] += [word]  # ' %s' %word
                                ontology_dict[pmc_mention_id][2] += [(word_start, word_end)]
                            else:  ##error because its missing a B to start
                                ontology_dict[pmc_mention_id] = [sentence_num, ['%s%s' % ('...', word)],
                                                                 [(word_start, word_end)], span_model]  # ' %s' %word

                            ##set the value of pmc_mention_id also
                            pmc_tokenized_file_df.at[index, 'PMC_MENTION_ID'] = pmc_mention_id

                        ##discontinuity
                        elif bio_tag == 'O-':
                            if ontology_dict.get(
                                    pmc_mention_id):  # and not ontology_dict[pmc_mention_id][1].endswith('...'):
                                # print('DISCONTINUITY! MADE IT HERE!')
                                ontology_dict[pmc_mention_id][1] += ['...']  # ' ...'
                                ontology_dict[pmc_mention_id][2] += [(word_start, word_end)]
                            else:  ##weird error where the concept is missing a B
                                ontology_dict[pmc_mention_id] = [sentence_num, ['...'], [(word_start, word_end)],
                                                                 span_model]

                        ##end of concept/ no concept
                        elif bio_tag == 'O':
                            if ontology_dict.get(pmc_mention_id):
                                # print('pmc_mention_id', pmc_mention_id)
                                # print('sentence num', sentence_num)
                                # print('updated concept:', ontology_dict[pmc_mention_id][1])
                                pmc_mention_id_index += 1

                            ##no concept at all
                            else:
                                pass

                        else:  # 'O-' continuously
                            raise Exception('ERROR WITH A WEIRD TAG OTHER THAN THE 4!')

                # for pmc_mention_id in ontology_dict:
                #     if '...' in ontology_dict[pmc_mention_id][1]:
                #         # print(ontology_dict[pmc_mention_id])
                #         pass

                ##output the new updated dataframe with pmc_mention_id labels
                pmc_tokenized_file_df.to_pickle(
                    '%s%s/%s_%s.pkl' % (tokenized_file_path, ontology, filename.replace('.txt', ''), 'updated'))
                pmc_tokenized_file_df.to_csv(
                    '%s%s/%s_%s.tsv' % (tokenized_file_path, ontology, filename.replace('.txt', ''), 'updated'),
                    '\t')

    return ontology_dict


#TODO!!
def output_all_files(pmcid_output_dict, ontology, ontology_dict, disc_error_output_file):


    ##ONTOLOGY_DICT - pmc_mention_id -> [sentence_num, [word], [(word_indices)], span_model, [biotag]]
    disc_error_dict = {}  # span_model -> count
    for pmc_mention_id in ontology_dict.keys():
        # print(pmc_mention_id)
        # print(ontology_dict[pmc_mention_id])
        sentence_num = ontology_dict[pmc_mention_id][0]
        current_pmcid = sentence_num.split('.nxml')[0]
        word_list = ontology_dict[pmc_mention_id][1]  # list of words
        word_indices_list = ontology_dict[pmc_mention_id][2]
        span_model = ontology_dict[pmc_mention_id][3]


        # print(sentence_num, word_list, word_indices_list, span_model)
        ##only taking the full model for CRF and then the local BioBERT
        if 'crf_model_full' in span_model.lower() or 'biobert_model_local' in span_model.lower():

            #check the lists of the words and word indices are the same
            if len(word_list) != len(word_indices_list):
                print(len(word_list), len(word_indices_list))
                print(word_list)
                print(word_indices_list)
                raise Exception('ERROR WITH COLLECTING ALL WORDS AND INDICES!')

            ##put the concept together:
            # a concept based on O- only and so we capture this in disc_error_output
            if word_list == ['...']:
                # discontinuity_error_count += 1
                if disc_error_dict.get(span_model):
                    disc_error_dict[span_model] += 1
                else:
                    disc_error_dict[span_model] = 1
                ##skip this because no concept!

            else:
                updated_word = ''
                updated_word_indices_list = []  # [(start,end)]
                disc_sign = False
                for i, w in enumerate(word_list):
                    ##I is first with no B
                    if i == 0:  # always take the first word to start
                        updated_word += '%s' % w
                        updated_word_indices_list += [word_indices_list[i]]
                        if w == '...':
                            disc_sign = True

                    elif w == '...' and not disc_sign:
                        updated_word += ' %s' % w
                        updated_word_indices_list += [word_indices_list[i]] #don't add the parantheses!!
                        disc_sign = True

                    elif w != '...':
                        # if i == 1 and updated_word.endswith('...'):
                        #     updated_word += '%s' %w
                        # else:
                        updated_word += ' %s' % w

                        updated_word_indices_list += [word_indices_list[i]]
                        disc_sign = False
                    else:
                        # print('GOT HERE!!')
                        pass

                # if len(updated_word.split(' ')) not in (len(updated_word_indices_list), len(updated_word_indices_list)-1):
                if len(updated_word.split(' ')) != len(updated_word_indices_list):
                    raise Exception('ERROR WITH UPDATING THE WORD TO GET THE FULL CONCEPT WITH INDICES!')
                else:
                    updated_word_indices_list_short = []
                    for i, w in enumerate(updated_word.split(' ')):
                        if w == '...':
                            pass
                        else:
                            updated_word_indices_list_short += [updated_word_indices_list[i]]


                #final output
                word_indices_output = ''
                #output: T5674	CL:0000598 17097 17106;17119 17123	pyramidal ... cell
                # or T5656	CL:0000540 9966 9972	Neuron

                ##loop over and check if they are consecutive and combine if they are
                first_s = updated_word_indices_list[0][0]
                last_e = updated_word_indices_list[-1][-1]
                current_e = last_e
                current_s = first_s
                final_word_indices_list = []
                if len(updated_word_indices_list_short) == 1:
                    final_word_indices_list = updated_word_indices_list_short
                else:
                    for j in range(len(updated_word_indices_list_short)-1):
                        s1, e1 = updated_word_indices_list_short[j]
                        s2, e2 = updated_word_indices_list_short[j+1]

                        # if e2 == last_e:
                        #     final_word_indices_list += [(current_s, e2)]

                        if (int(e1) + 1 == int(s2) or int(e1) == int(s2)) and updated_word.split(' ')[j+1] != '...':
                            pass
                        else:
                            if final_word_indices_list:
                                final_word_indices_list += [(current_s, e1)]
                                current_s = s2
                            else:
                                final_word_indices_list += [(first_s, e1)]
                                current_s = s2

                    ##add the final info to the end here
                    final_word_indices_list += [(current_s, last_e)]

                if len(updated_word.split(' ... ')) != len(final_word_indices_list):
                    print(updated_word)
                    print(updated_word_indices_list)
                    print(updated_word_indices_list_short)
                    print(final_word_indices_list)
                    print(current_s, e2, last_e)
                    raise Exception('ERROR: Issue with the final word indices list being the wrong length!')
                else:
                    pass



                for (s, e) in final_word_indices_list:
                    word_indices_output += '%s %s;' % (s, e)
                word_indices_output = word_indices_output[:len(word_indices_output) - 1]  ##get rid of the last ;
                # print('PROCESSED')
                # print(updated_word, updated_word_indices_list, word_indices_output)

                ##update the word indices to reflect whether it is discontinuous or not



                #output to the dictionary per pmcid
                # print(pmcid_output_dict)
                # if pmcid_output_dict.get(current_pmcid):
                pmcid_output_dict[current_pmcid] += [(sentence_num, ontology, word_indices_output, updated_word)]
                # else:
                #     print(current_pmcid)
                #     raise Exception('ERROR: Issue with pmcid not in list matching pmcid annotation information')

        else:
            pass


    # print('DISCONTINUITY ERROR COUNT:', discontinuity_error_count)
    for sm in disc_error_dict.keys():
        disc_error_output_file.write('%s\t%s\n' % (sm, disc_error_dict[sm]))

    return pmcid_output_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-ontologies', type=str, help='a list of ontologies to use delimited with ,')
    parser.add_argument('-algos', type=str, help='a list of the algorithms to use delimited with ,')
    parser.add_argument('-result_folders', type=str,
                        help='a list of folders to the results of the span detection models matching the algos list delimited with ,')
    parser.add_argument('-results_path', type=str,
                        help='file path to the results folders')
    parser.add_argument('-output_folder', type=str, help='the file path for the bionlp format output files')
    parser.add_argument('-evaluation_files', type=str, help='a list of the files to be evaluated delimited with ,')
    parser.add_argument('-separate_all_combined_output', type=str, help='folder name of the output for all the separate categories combined')
    parser.add_argument('-shorthand_ont_dict', type=str, help='a string of a dictionary for all the shorthands from 0_all_combined to the ontology information')
    args = parser.parse_args()

    # ontologies = ['CHEBI', 'CL', 'GO_BP', 'GO_CC', 'GO_MF', 'MOP', 'NCBITaxon', 'PR', 'SO', 'UBERON']


    # results_span_detection_path = '/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/Negacy_seq_2_seq_NER_model/ConceptRecognition/Evaluation_Files/Results_span_detection/'

    # concept_norm_files_path = '/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/Negacy_seq_2_seq_NER_model/ConceptRecognition/Evaluation_Files/Concept_Norm_Files/'

    algos = args.algos.split(',')
    result_folders = args.result_folders.split(',')
    ontologies = args.ontologies.split(',')
    evaluation_files = args.evaluation_files.split(',')
    shorthand_ont_dict = ast.literal_eval(args.shorthand_ont_dict)

    print(evaluation_files)


    ##output_dictionary for each pmcid -> [(sentence_num, ignorance_category, word_indices, word)]
    pmcid_output_dict = {}
    pmcid_all_combined_dict = {}
    for e in evaluation_files:
        pmcid_output_dict[e] = []
        pmcid_all_combined_dict[e] = []

    for i, algo in enumerate(algos):
        result_folder = result_folders[i]
        results_span_detection_path = args.results_path+result_folder+'/'
        concept_norm_files_path = args.results_path+result_folder+'/'+args.output_folder+'/'

        for ontology in ontologies:
            # if ontology == 'CHEBI':
            print('PROGRESS:', ontology)
            ontology_dict = {}
            disc_error_output_file = open(
                '%s%s/%s_DISC_ERROR_SUMMARY.txt' % (results_span_detection_path, ontology, ontology), 'w+')
            disc_error_output_file.write('%s\t%s\n' % ('MODEL', 'NUM DISCONTINUITY ERRORS'))

            if ontology.lower() == '0_all_combined':
                ##need to first split all of this up
                split_all_combined_output_folder = concept_norm_files_path + ontology + '/'

                split_up_0_all_combined_data(results_span_detection_path, ontology, shorthand_ont_dict, evaluation_files, split_all_combined_output_folder)

                for shorthand, ont in shorthand_ont_dict.items():

                    all_combined_ontology_dict = preprocess_data(split_all_combined_output_folder, ont, ontology_dict, evaluation_files)
                    pmcid_all_combined_dict = output_all_files(pmcid_all_combined_dict, ont, all_combined_ontology_dict,
                                                         disc_error_output_file)

            else:
                # ONTOLOGY_DICT - pmc_mention_id -> [sentence_num, word, [(word_indices)], span_model]
                ontology_dict = preprocess_data(results_span_detection_path, ontology, ontology_dict, evaluation_files)

                # od_indices = [1, 2, 3, -1, 0]


                ##TODO!!! TODO: make all of them lowercase and uniform! also duplicates!
                pmcid_output_dict = output_all_files(pmcid_output_dict, ontology, ontology_dict, disc_error_output_file)


        ##final pmcid_output_dict
        for pmcid in pmcid_output_dict:
            #output files:
            separate_all_combined_file = open('%s%s/%s_%s.bionlp' %(concept_norm_files_path, args.separate_all_combined_output, algo, pmcid), 'w+')
            binary_combined_file = open('%s%s/%s_%s.bionlp' %(concept_norm_files_path, '1_binary_combined', algo, pmcid), 'w+')

            all_combined_file = open('%s%s/%s_%s.bionlp' % (concept_norm_files_path, '0_all_combined', algo, pmcid), 'w+')
            binary_count = 0
            all_combined_count = 0
            separate_all_combined_count = 0

            ##now output per type of ontology gathered
            for info in pmcid_output_dict[pmcid]:
                sentence_num, ignorance_category, word_indices, word = info

                if ignorance_category.lower() == '1_binary_combined':
                    binary_combined_file.write('T%s\t%s %s\t%s\n' %(binary_count, 'IGNORANCE', word_indices, word))
                    binary_count += 1

                ##all separate ignorance categories combined
                else:
                    separate_all_combined_file.write('T%s\t%s %s\t%s\n' %(separate_all_combined_count, ignorance_category, word_indices, word))
                    separate_all_combined_count += 1

            for info in pmcid_all_combined_dict[pmcid]:
                sentence_num, ignorance_category, word_indices, word = info
                all_combined_file.write('T%s\t%s %s\t%s\n' %(all_combined_count, ignorance_category, word_indices, word))
                all_combined_count += 1




    print('PROGRESS: FINISHED CONCEPT NORMALIZATION PROCESSING FOR ALL FILES!')