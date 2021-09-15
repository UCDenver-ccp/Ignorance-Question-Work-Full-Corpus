import os

import nltk
# nltk.download()
import nltk.data

import xml.etree.ElementTree as ET

from nltk.tokenize import sent_tokenize, word_tokenize
import pandas as pd

from nltk.tokenize import WordPunctTokenizer
import copy
import pickle
import csv
import argparse
import string
import ast
import random
import datetime


def get_all_articles_of_interest(all_article_list_path):
    all_articles_list = []
    print(all_article_list_path)
    with open('%s' %(all_article_list_path), 'r+') as all_article_file:
        for line in all_article_file:
            all_articles_list += [line.split('.nxml')[0]] #only capture the PMC-ID

    return all_articles_list

def split_articles_into_original_sets(annotator_lists, annotator_lists_names, annotation_path):
    annotator_pmcid_dict = {} #dict from name of annotator -> list of pmcids
    for name in annotator_lists_names:
        annotator_pmcid_dict[name] = []

    for root, directories, filenames in os.walk('%s' % (annotation_path)):
        for filename in sorted(filenames):
            if filename.startswith('PMC') and filename.endswith('.xml'):
                found = False
                for i, annotator_list in enumerate(annotator_lists):

                    for annotator in annotator_list:
                        if annotator.upper() in filename:
                            annotator_pmcid_dict[annotator_lists_names[i]] += [filename]
                            found = True
                            break #take the first one you find
                        else:
                            pass
                    if found:
                        found = False
                        break
                    else:
                        pass
            else:
                pass

    return annotator_pmcid_dict




def train_eval_split(pmcid_doc_list, eval_split_size):
    eval_docs = random.sample(pmcid_doc_list, eval_split_size)
    train_docs = [doc for doc in pmcid_doc_list if doc not in eval_docs]

    return train_docs, eval_docs




if __name__=='__main__':
    parser = argparse.ArgumentParser(description='')



    parser.add_argument('-article_path', type=str, help='file path to all the articles of interest')

    parser.add_argument('-annotation_path', type=str, help='the file path to all the annotations of interest')

    parser.add_argument('-all_article_list_path', type=str, help='the file path to the file with all the articles listed out')

    parser.add_argument('-annotator_lists', type=str, help='a list of all the annotators for each set of annotation')

    parser.add_argument('-annotator_lists_names', type=str, help='a list of the names of the annotation set corresponding to the annotator_lists')

    parser.add_argument('-output_path', type=str, help='file path to output the resulting tokenized files by pmcid')


    args = parser.parse_args()

    all_article_list = get_all_articles_of_interest(args.all_article_list_path)


    annotator_lists = ast.literal_eval(args.annotator_lists)

    annotator_lists_names = ast.literal_eval(args.annotator_lists_names)

    # save by date so we know when it is from
    today = datetime.datetime.now()
    d = today.strftime('%x').replace('/', '_')

    print(annotator_lists)

    print(len(all_article_list))

    annotator_pmcid_dict = split_articles_into_original_sets(annotator_lists, annotator_lists_names, args.annotation_path)

    # print(annotator_pmcid_dict)

    # split is 2/3 and 1/3 for each set of annotations (65 and 26 total for train and eval)
    eval_split_size = [2, 15, 9]  ##lines up with the annotator_list functions

    all_train_docs = []
    all_eval_docs = []
    #make sure we are in the same order as the names and everything else
    for i, name in enumerate(annotator_lists_names):
        print(name, len(annotator_pmcid_dict[name]))
        pmcid_doc_list = annotator_pmcid_dict[name]

        ##selecting the random articles for each set for the eval set to start and the rest is for the train set
        current_eval_split_size = eval_split_size[i]

        ##this will change with every run!
        train_docs, eval_docs = train_eval_split(pmcid_doc_list, current_eval_split_size)
        all_train_docs += train_docs
        all_eval_docs += eval_docs


        if len(train_docs) + len(eval_docs) != len(pmcid_doc_list):
            raise Exception('ERROR: Issue with splitting docs!')

        else:
            pass
    if len(all_train_docs) != 65:
        print(len(all_train_docs))
        raise Exception('ERROR: Issue with the number of training documents!')
    else:
        pass

    if len(all_eval_docs) != 26:
        print(len(all_eval_docs))
        raise Exception('ERROR: Issue with the number of evaluation documents!')
    else:
        pass

    ##write out the documents!
    with open('%s%s_%s.txt' %(args.output_path, 'ALL_TRAINING_DOCUMENTS', d), 'w+') as train_docs_file:
        for t_doc in all_train_docs:
            train_docs_file.write('%s\n' %(t_doc))

    with open('%s%s_%s.txt' %(args.output_path, 'ALL_EVALUATION_DOCUMENTS', d), 'w+') as eval_docs_file:
        for e_doc in all_eval_docs:
            eval_docs_file.write('%s\n' %(e_doc))















