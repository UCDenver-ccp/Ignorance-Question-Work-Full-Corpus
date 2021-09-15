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


def make_pmcid_list_file(input_file, output_file):
    comma_delimited_list = ''
    with open(input_file, 'r+') as input:
        for line in input:
            pmcid = line.split('.nxml')[0]
            if pmcid.startswith('PMC'):
                comma_delimited_list += '%s,' %(pmcid)
            else:
                raise Exception('ERROR: Issue with PMCID list files')

    with open(output_file, 'w+') as output:
        output.write('%s' %(comma_delimited_list[:-1]))

    return comma_delimited_list[:-1] #getting rid of the last extra comma



if __name__=='__main__':

    # current_BIO_hierarchy = ['B', 'B-', 'I', 'I-', 'O']



    parser = argparse.ArgumentParser()
    parser.add_argument('-eval_list_path', type=str, help='a string file path to the corpus annotations')
    parser.add_argument('-train_list_path', type=str, help='a string file name to the plain text articles')

    parser.add_argument('-output_path', type=str, help='a file path to the output for the tokenized files')

    args = parser.parse_args()

    eval_output_file_name = 'ALL_EVALUATION_DOCUMENTS_09_14_21_LIST.txt'
    eval_comma_delimited_list = make_pmcid_list_file(args.eval_list_path, args.output_path + eval_output_file_name)


    train_output_file_name = 'ALL_TRAINING_DOCUMENTS_09_14_21_LIST.txt'
    train_comma_delimited_list = make_pmcid_list_file(args.train_list_path, args.output_path + train_output_file_name)


