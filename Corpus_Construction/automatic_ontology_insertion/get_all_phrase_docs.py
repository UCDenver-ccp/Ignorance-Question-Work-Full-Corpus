import os
import random
from datetime import date


def get_docs_with_phrase(all_articles_path, phrase, output_path):
    with open('%s%s_%s.txt' %(output_path, phrase.replace(' ', '_'), 'all_docs'), 'w+') as output_file, open('%s%s.txt' %(output_path, 'all_docs'), 'w+') as all_docs_file:

        for root, directories, filenames in os.walk(all_articles_path):
            for filename in sorted(filenames):
                if filename.endswith('.nxml.gz.txt'):
                    all_docs_file.write('%s\n' %filename)

                    with open(root+filename, 'r') as article:
                        article_text = article.read().lower()
                        # average abstract is 100-500 words - july 3rd 2020
                        if phrase.lower() in article_text[0:500]:
                            output_file.write('%s\n' %filename)



def choose_random_phrase_doc(phrase_doc_path, phrase, output_docs_path, num_docs):

    with open(phrase_doc_path, 'r') as phrase_doc_file, open('%s%s_%s_%s.txt' %(output_docs_path, phrase.replace(' ', '_'), 'random_docs', date.today()), 'w+') as random_phrase_docs_file:
        lines = phrase_doc_file.readlines()
        random_phrase_docs = []
        while len(random_phrase_docs) < num_docs:
            random_phrase_file = random.choice(lines)
            if random_phrase_file not in random_phrase_docs:
                random_phrase_docs += [random_phrase_file]


        for f in random_phrase_docs:
            random_phrase_docs_file.write('%s\n' %f)



def choose_random_docs(all_docs_path, file_start_nums, output_docs_path, num_docs):
    with open(all_docs_path, 'r') as all_docs_file, open('%s%s_%s.txt' %(output_docs_path, 'random_docs', date.today()), 'w+') as random_doc_file:

        if file_start_nums:
            for num in file_start_nums:
                ##gather all the files with the correct start
                num_files = []
                all_docs_file.seek(0)
                for line in all_docs_file:
                    # print([line])
                    if line.startswith('%s%s' %('PMC', num)):
                        # print('got here')
                        num_files += [line]
        else:
            num_files = []
            all_docs_file.seek(0)
            for line in all_docs_file:
                # print([line])
                if line.startswith('%s' % ('PMC')):
                    # print('got here')
                    num_files += [line]


       ##pick a random file and output it
        # print(num_files)
        # print(num)
        for i in range(num_docs):
            random_doc_file.write('%s\n' %random.choice(num_files))







if __name__=='__main__':
    all_articles_path = '/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/1_First_Full_Annotation_Task_9_13_19/Articles/'
    phrase = 'vitamin D'
    output_path = '/Users/MaylaB/Dropbox/Documents/0_Thesis_stuff-Larry_Sonia/1_First_Full_Annotation_Task_9_13_19/'

    ##get docs with a specific phrase - here vitamin D
    get_docs_with_phrase(all_articles_path, phrase, output_path)


    ##get a random doc with the phrase in it - 1 doc
    phrase_doc_path = '%s%s_%s.txt' %(output_path, phrase.replace(' ', '_'), 'all_docs')
    num_docs = 3 #TODO: decide how many docs we want for vitamin D right now


    ##TODO: do this first and figure out what the articles are making sure we dont have duplicates
    # choose_random_phrase_doc(phrase_doc_path, phrase, output_path, num_docs) #got 3 and 4 this time!


    ##get generally random docs using the file_starts_num to specify the starting number
    all_docs_path = '%s%s.txt' %(output_path, 'all_docs')
    ##TODO: figure out what the vitamin D docs are and make these other ones and run it without the vitamin D runs
    # file_start_nums = ['2','4','6']
    file_start_num = None
    choose_random_docs(all_docs_path, file_start_num, output_path, num_docs)