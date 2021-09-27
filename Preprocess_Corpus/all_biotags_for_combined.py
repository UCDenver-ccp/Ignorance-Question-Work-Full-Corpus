import argparse
import os
import pandas as pd
pd.set_option('display.max_columns', 30)
import pickle


def create_all_biotag_combos(biotags, ontologies_shortnames):
    all_biotag_combos = []
    biotag_duplicate_dict = {} #dict from double one way to the other
    for tag in biotags:
        for s1 in ontologies_shortnames:
            ##single biotag things
            if tag == 'O-': #only want one - with O-
                all_biotag_combos += ['%s%s' %(tag, s1)]
            else:
                all_biotag_combos += ['%s-%s' %(tag, s1)]

            ##double biotags
            for s2 in ontologies_shortnames:
                ##if they are the same move on
                if s1 == s2:
                    continue
                else:
                    #only want one - with O-
                    if tag == 'O-':
                        new_combo = '%s%s-%s' % (tag, s1, s2)
                        reverse_new_combo = '%s%s-%s' % (tag, s2, s1)
                    else:
                        new_combo = '%s-%s-%s' %(tag, s1, s2)
                        reverse_new_combo = '%s-%s-%s' %(tag, s2, s1)

                    if reverse_new_combo in all_biotag_combos:
                        if biotag_duplicate_dict.get(reverse_new_combo):
                            raise Exception('ERROR: Issue with biotag combos for 2 things!')
                        else:
                            biotag_duplicate_dict[reverse_new_combo] = new_combo
                    else:
                        all_biotag_combos += [new_combo]

    if len(set(all_biotag_combos)) != len(all_biotag_combos):
        raise Exception('ERROR: Issue with duplicates in all_biotag_combos!')
    else:
        pass

    if len(set(biotag_duplicate_dict.keys())) != len(biotag_duplicate_dict.keys()):
        raise Exception('ERROR: Issue with duplicate dictionary')
    else:
        pass


    return all_biotag_combos, biotag_duplicate_dict











if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-biotags', type=str, help='a list of the possible biotags (delimited with , no spaces')
    parser.add_argument('-ontologies', type=str, help='a list of ontologies to combine by pmcid (delimited with , no spaces)')
    parser.add_argument('-output_path', type=str, help='file path to output the resulting tokenized files by pmcid')
    args = parser.parse_args()


    ontologies = args.ontologies.split(',')

    biotags = args.biotags.split(',')

    ##ontology acronyms
    ontologies_shortnames= []
    for o in ontologies:
        abbreviation = o.upper().split()
        shortcut = ''.join([s[0] for s in o.split('_')])
        ontologies_shortnames += [shortcut.upper()]



    all_biotag_combos, biotag_duplicate_dict = create_all_biotag_combos(biotags, ontologies_shortnames)
    print(len(all_biotag_combos))
    print(all_biotag_combos[:15])
    print('%s' %all_biotag_combos[:15])
    print(len(biotag_duplicate_dict))


    ##output the list of the biotag combos in list form
    with open('%s%s.txt' %(args.output_path,'BIOTAGS_ALL_COMBOS'), 'w+') as all_combos_output_file:
        all_combos_output_file.write('%s\n' %('LIST OF ALL BIOTAG COMBOS FOR THE ALL COMBINED BIOBERT RUN'))
        all_combos_output_file.write('%s' %(all_biotag_combos))

    ##pickle the biotage_duplicate_dict
    biotag_duplicate_dict_pkl = open('%s%s.pkl' % (args.output_path, 'BIOTAG_DUPLICATE_DICT'),'wb')
    pickle.dump(biotag_duplicate_dict, biotag_duplicate_dict_pkl)
    biotag_duplicate_dict_pkl.close()

    ##output the dict also for review
    with open('%s%s.txt' %(args.output_path, 'BIOTAG_DUPLICATE_DICT'), 'w+') as dict_output_file:
        dict_output_file.write('%s\t%s\n' % ('USED_TAG', 'OTHER_TAG'))
        for used_tag, other_tag in biotag_duplicate_dict.items():
            dict_output_file.write('%s\t%s\n' %(used_tag, other_tag))










