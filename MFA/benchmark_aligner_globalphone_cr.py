import sys
import shutil, os
sys.path.insert(0, os.path.expanduser('/data/mmcauliffe/dev/Montreal-Forced-Aligner'))

import time
import logging
import platform
import csv
import statistics
from datetime import datetime

from aligner.command_line.train_and_align import align_corpus, align_corpus_no_dict

corpus_dir = '/media/share/corpora/GP_for_MFA/CR'
dict_path = os.path.expanduser('/media/share/corpora/GP_for_MFA/CR/dict/CR_dictionary.txt')
output_directory = '/data/mmcauliffe/aligner-output/CR'
temp_dir = '/data/mmcauliffe/temp/MFA'
output_model_path = os.path.expanduser('/data/mmcauliffe/aligner-models/cr_models.zip')

class DummyArgs(object):
    def __init__(self):
        self.num_jobs = 12
        self.fast = False
        self.speaker_characters = 0
        self.verbose = False
        self.clean = True
        self.no_speaker_adaptation = False

args = DummyArgs()

def benchmark_align_corpus():
    beg = time.time()
    align_corpus(corpus_dir, dict_path, output_directory, temp_dir, output_model_path, args)
    end = time.time()
    return [(end - beg)]

def benchmark_align_corpus_no_dict(corpus_dir, output_directory):
    beg = time.time()
    align_corpus_no_dict(corpus_dir, output_directory, temp_dir, output_model_path, args)
    end = time.time()
    return [(end - beg)]

if dict_path == None:
    nodict = benchmark_align_corpus_no_dict()
else:
    yesdict = benchmark_align_corpus()

def WriteDictToCSV(csv_file,csv_columns,dict_data):
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
        return

csv_columns = ['Computer','Date','Corpus', 'Type of benchmark', 'Total time', 'Num_jobs']
if dict_path == None:
        dict_data = [
        {'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': corpus_dir, 'Type of benchmark': 'train and align', 'Total time': nodict[0], 'Num_jobs': args.num_jobs}
        ]
else:
    dict_data = [
        {'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': corpus_dir, 'Type of benchmark': 'train and align', 'Total time': yesdict[0], 'Num_jobs': args.num_jobs}
        ]

now = datetime.now()
date = str(now.year)+str(now.month)+str(now.day)

if not os.path.exists('aligner_benchmark'+date+'.csv'):
    open('aligner_benchmark'+date+'.csv', 'a')
    with open('aligner_benchmark'+date+'.csv', 'a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()

csv_file = 'aligner_benchmark'+date+'.csv'

with open('aligner_benchmark'+date+'.csv', 'a') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
    writer.writerow(dict_data[0])


