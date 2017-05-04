import sys
import shutil, os
import subprocess

import time
import logging
import platform
import csv
import statistics
from datetime import datetime

mfa_path = '/data/mmcauliffe/dev/Montreal-Forced-Aligner'

current_commit = subprocess.check_output(['git', 'describe', '--always'], cwd=mfa_path)

sys.path.insert(0, mfa_path)

import aligner
from aligner.command_line.train_and_align import align_corpus, align_corpus_no_dict, fix_path, unfix_path

fix_path()

lang_code = 'BG'
full_name = 'bulgarian'

corpus_dir = '/media/share/corpora/GP_for_MFA/{}'.format(lang_code)
dict_path = os.path.expanduser('/media/share/corpora/GP_for_MFA/{0}/dict/{0}_dictionary.txt'.format(lang_code))
output_directory = '/data/mmcauliffe/aligner-output/{}'.format(lang_code)
temp_dir = '/data/mmcauliffe/temp/MFA'
output_model_path = '/data/mmcauliffe/aligner-models/bulgarian.zip'

class DummyArgs(object):
    def __init__(self):
        self.corpus_directory = corpus_dir
        self.dictionary_path = dict_path
        self.output_directory = output_directory
        self.output_model_path = output_model_path
        self.num_jobs = 12
        self.fast = False
        self.speaker_characters = 0
        self.verbose = False
        self.clean = True
        self.no_speaker_adaptation = False
        self.temp_directory = temp_dir

args = DummyArgs()

beg = time.time()
align_corpus(args)
end = time.time()
duration = end - beg

csv_columns = ['Computer','Date','Corpus', 'Type of benchmark', 'Total time', 'Num_jobs']


dict_data = {'Computer': platform.node(),
        'Date': str(datetime.now()),
        'Corpus': corpus_dir,
        'Version': aligner.__version__,
        'Language': lang_code,
        'Type of benchmark': 'train and align',
        'Total time': duration,
        'Num_jobs': args.num_jobs}

now = datetime.now()
date = str(now.year)+str(now.month)+str(now.day)

csv_file = 'aligner_benchmark.csv'

if not os.path.exists(csv_file):
    with open(csv_file, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()


with open(csv_file, 'a') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
    writer.writerow(dict_data)


unfix_path()
