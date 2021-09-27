import argparse
import os
import pandas as pd
pd.set_option('display.max_columns', 30)
import pickle


def get_all_articles_of_interest(article_path, output_path):
    all_articles_list = []
    print(article_path)
    print(output_path)
    with open('%s%s.txt' %(output_path, 'all_article_list'), 'w+') as all_article_file:
        for root, directories, filenames in os.walk('%s' % (article_path)):
            for filename in sorted(filenames):
                if filename.startswith('PMC'):
                    all_article_file.write('%s\n' %(filename))
                    all_articles_list += [filename]
                else:
                    pass

    return all_articles_list



def combine_tokenized_file_by_pmcid(pmcid_filename, tokenized_file_path, ontologies, ontology_shortcut_dict, biotag_duplicate_dict, biotags_to_change, full_output_path):
    biotags_count_per_pmcid = 0
    overlap_count_per_pmcid = 0
    for o, ontology in enumerate(ontologies):
        # print(ontology)
        ##initialize the full dataframe with the first ontology one
        if o == 0:
            pmcid_full_df = pd.read_pickle('%s%s/%s' %(tokenized_file_path, ontology, pmcid_filename.replace('.txt', '.pkl'))).copy()

            column_names = list(pmcid_full_df.columns.values.tolist())

            ##find the rows with B, I, O- and add the correct ontology shortcut to it -
            for biotag in biotags_to_change:
                biotag_indices_list = pmcid_full_df.loc[pmcid_full_df['BIO_TAG'] == biotag].index.values
                for i in biotag_indices_list: ##TODO: fix the order so its standard
                    pmcid_full_df.at[i, 'BIO_TAG'] = '%s-%s' %(biotag.replace('-', ''), ontology_shortcut_dict[ontology]) #want to ensure that we get rid of the extra dash from O-
                    # print(pmcid_full_df.loc[[i]])
                biotags_count_per_pmcid += len(biotag_indices_list)

        ##TODO: need to combine all the others together - finding the correct column and updating - need to also prioritize things if overlaps - quantify overlaps
        else:
            # print('got here')
            ##columns to update: BIO_TAG, PMC_MENTION_ID, ONTOLOGY_CONCEPT_ID, ONTOLOGY_LABEL (LAST 3 ARE LISTS)

            ##read in the ontology dataframe to add data from
            ontology_data_to_add_df = pd.read_pickle('%s%s/%s' %(tokenized_file_path, ontology, pmcid_filename.replace('.txt', '.pkl')))

            ##find the rows with B, I, O-:
            for biotag in biotags_to_change:
                #find all indices
                biotag_indices_list = ontology_data_to_add_df.loc[ontology_data_to_add_df['BIO_TAG'] == biotag].index.values
                biotags_count_per_pmcid += len(biotag_indices_list)
                # print(biotag_indices_list)
                ##loop over all indices and update the rows as long as they are O
                for i in biotag_indices_list:
                    ##Check that everything lines up for the rows
                    for n in column_names[:column_names.index('BIO_TAG')]:
                        if pmcid_full_df.iloc[i][n] != ontology_data_to_add_df.iloc[i][n]:
                            print(i, n)
                            raise Exception('ERROR: issue with matching data for all columns before BIO_TAG!')
                        else:
                            pass



                    ##if 'O' then we can easily add the information from the new ontology
                    if pmcid_full_df.at[i, 'BIO_TAG'] == 'O':
                        pmcid_full_df.at[i, 'BIO_TAG'] = '%s-%s' % (biotag.replace('-', ''), ontology_shortcut_dict[ontology]) #want to ensure that we get rid of the extra dash from O-
                        ##update all the rest of the columns with the info
                        for c in column_names[column_names.index('BIO_TAG')+1:]:
                            pmcid_full_df.at[i, c] = ontology_data_to_add_df.iloc[i][c]

                    ##TODO: overlap!!! - need to deal with this - prioritize B, I, O-?
                    else:
                        # print('OVERLAP!!')
                        # print(ontology)
                        # # print(ontology_data_to_add_df.iloc[i:i+2])
                        # # print(pmcid_full_df.iloc[i:i+2])
                        #
                        # print(ontology_data_to_add_df.iloc[i]['BIO_TAG'])
                        # print(pmcid_full_df.iloc[i]['BIO_TAG'])
                        overlap_count_per_pmcid += 1

                        ##list of competing biotags - current one (go back to the base tag) and then new one to add possibly
                        current_biotag = pmcid_full_df.iloc[i]['BIO_TAG']
                        competing_biotags = [current_biotag.split('-')[0], biotag]
                        if competing_biotags[0] == 'O':
                            competing_biotags[0] = 'O-'
                        else:
                            pass

                        ##check if the biotags are the same - add another and add to the list
                        if len(set(competing_biotags)) == 1:
                            pmcid_full_df.at[i, 'BIO_TAG'] = '%s-%s' % (current_biotag, ontology_shortcut_dict[
                                ontology])  # add another dash of the other ontology
                            ##update all the rest of the columns with the info
                            for c in column_names[column_names.index('BIO_TAG') + 1:]:
                                ##add the new element for each one no BIOTAGs
                                pmcid_full_df.at[i, c] += ontology_data_to_add_df.iloc[i][c]
                            # print(pmcid_full_df.iloc[i])
                            # raise Exception('Hold')

                        ##not the same: prioritize B, then I

                        ##change to B or I over O- - full update everything
                        elif 'O-' in competing_biotags:
                            if current_biotag.startswith('O-'):
                                ##full update to the new stuff
                                pmcid_full_df.at[i, 'BIO_TAG'] = '%s-%s' % (biotag.replace('-', ''),ontology_shortcut_dict[ontology])  # want to ensure that we get rid of the extra dash from O-
                                ##update all the rest of the columns with the info
                                for c in column_names[column_names.index('BIO_TAG') + 1:]:
                                    pmcid_full_df.at[i, c] = ontology_data_to_add_df.iloc[i][c]

                            else:
                                ##new biotag is O- and so we do nothing
                                pass

                        ##otherwise prioritize B
                        elif 'B' in competing_biotags:
                            if current_biotag.startswith('B'):
                                #don't change the biotag if it is B in the full one
                                pass
                            else:
                                ##change the biotag to the new one if the new one is B
                                ##full update to the new stuff
                                pmcid_full_df.at[i, 'BIO_TAG'] = '%s-%s' % (biotag.replace('-', ''),ontology_shortcut_dict[ontology])  # want to ensure that we get rid of the extra dash from O-
                                ##update all the rest of the columns with the info
                                for c in column_names[column_names.index('BIO_TAG') + 1:]:
                                    pmcid_full_df.at[i, c] = ontology_data_to_add_df.iloc[i][c]
                        else:
                            raise Exception('ERROR: Missing biotag to deal with (should never get here)!')




                        # raise Exception('ERROR: Overlaps exist and should not between ontologies!')


    if overlap_count_per_pmcid > 0:
        print('overlap count for pmicd:', overlap_count_per_pmcid)
    else:
        pass

    ##need to fix the double biotags to be standard in the correct way from the biotag all combined creation
    #https://stackoverflow.com/questions/20250771/remap-values-in-pandas-column-with-a-dict
    pmcid_full_df.replace({'BIO_TAG' : biotag_duplicate_dict})


    ##print out the new pmcid_full_df dataframe with the information
    pmcid_full_df.to_pickle('%s%s' %(full_output_path, pmcid_filename.replace('.txt', '.pkl')))
    pmcid_full_df.to_csv('%s%s' %(full_output_path, pmcid_filename.replace('.txt', '.tsv')), '\t')



    return biotags_count_per_pmcid, overlap_count_per_pmcid, pmcid_full_df



def binarize_df(pmcid_filename, pmcid_df, biotags_to_binarize, total_biotags_per_pmcid_dict, output_path):

    ##copy the current pmcid_df for binary
    binary_pmcid_df = pmcid_df.copy()


    ##find the rows with B, I, O- and add the correct ontology shortcut to it -
    for biotag in biotags_to_binarize:

        ##find the index of the now changed biotags - biotag is in the dataframe column BIO_TAG
        if '-' in biotag:
            old_biotag = biotag
        else:
            old_biotag = '%s-' %biotag
        biotag_df = pmcid_full_df['BIO_TAG'].str.startswith(old_biotag) ##string containment - binary true or false df

        ##grab all the true ones
        biotag_indices_list = biotag_df.loc[biotag_df == True].index.values

        ##total of this type of biotag for the pmcid
        total_biotags_per_pmcid_dict[pmcid_filename] += [len(biotag_indices_list)] ##update the counts

        ##update the biotags to now be the original biotag
        for i in biotag_indices_list:
            binary_pmcid_df.at[i, 'BIO_TAG'] = '%s' % (biotag)  ##change the biotag to the original ones

    ##print out the new pmcid_full_df dataframe with the information
    binary_pmcid_df.to_pickle('%s%s' % (output_path, pmcid_filename.replace('.txt', '.pkl')))
    binary_pmcid_df.to_csv('%s%s' % (output_path, pmcid_filename.replace('.txt', '.tsv')), '\t')



    return total_biotags_per_pmcid_dict, len(binary_pmcid_df.index)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-tokenized_file_path', type=str, help='file path to the tokenized files in general')
    parser.add_argument('-biotags_to_change', type=str, help='a list of the possible biotags (delimited with , no spaces')
    parser.add_argument('-biotag_combined_dict', type=str, help='path to the pkl file with the dictionary for used biotags for classification')
    parser.add_argument('-ontologies', type=str, help='a list of ontologies to combine by pmcid (delimited with , no spaces)')
    parser.add_argument('-output_path', type=str, help='file path to output the resulting tokenized files by pmcid')
    parser.add_argument('-combined_folder', type=str, help='folder to output the combined files (combine with output path)')
    parser.add_argument('-binary_combined_folder', type=str,
                        help='folder to output the binary combined files (combine with output path)')
    parser.add_argument('-article_path', type=str, help='file path to all the articles of interest')
    args = parser.parse_args()


    ontologies = args.ontologies.split(',')
    biotags_to_change = args.biotags_to_change.split(',')
    full_output_path = args.output_path + args.combined_folder
    full_output_path_binary = args.output_path + args.binary_combined_folder

    ##get all the articles of interest to combine
    all_articles_list = get_all_articles_of_interest(args.article_path, args.output_path)
    print('Number of articles:', len(all_articles_list))

    ##create shortcuts for the ontology names
    ontology_shortcut_dict = {}
    for ontology in ontologies:
        shortcut = ''.join([s[0] for s in ontology.split('_')])
        # print(ontology, shortcut)
        ontology_shortcut_dict[ontology] = shortcut.upper()

    ##read in the duplicate dict to be able to make sure we have the correct pairing
    biotag_duplicate_dict_file = open(args.biotag_combined_dict, "rb")

    biotag_duplicate_dict = pickle.load(biotag_duplicate_dict_file)
    print(len(biotag_duplicate_dict))



    ##loop over each article and combine all tokenized file for that pmcid
    total_biotags_count = 0
    total_overlap_count = 0
    total_biotags_per_pmcid_dict = {} #dict from pmcid -> list of biotag counts

    print('BIOTAGS TO CHANGE:', biotags_to_change)

    for pmcid_filename in all_articles_list:
        print('PMCID:', pmcid_filename.split('.')[0])

        biotags_count_per_pmcid, overlap_count_per_pmcid, pmcid_full_df = combine_tokenized_file_by_pmcid(pmcid_filename, args.tokenized_file_path, ontologies, ontology_shortcut_dict, biotag_duplicate_dict, biotags_to_change, full_output_path)
        total_biotags_count += biotags_count_per_pmcid
        total_overlap_count += overlap_count_per_pmcid

        ##also binarize the df
        total_biotags_per_pmcid_dict[pmcid_filename] = []

        ##TODO: output this information per pmcid - how many biotags of each type (use total_len_binary_pmcid_df to get at how many 'O's there are
        total_biotags_per_pmcid_dict, total_len_binary_pmcid_df = binarize_df(pmcid_filename, pmcid_full_df, biotags_to_change, total_biotags_per_pmcid_dict, full_output_path_binary)
        print('total biotags to change per pmcid:', total_biotags_per_pmcid_dict[pmcid_filename])
        print('total num rows of df:', total_len_binary_pmcid_df)



    print('FINAL BIOTAGS COUNT:', total_biotags_count)
    print('FINAL OVERLAP COUNT:', total_overlap_count)





