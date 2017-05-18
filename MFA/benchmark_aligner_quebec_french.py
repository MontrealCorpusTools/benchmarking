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


csv_path = 'aligner_benchmark.csv'

class DummyArgs(object):
    def __init__(self):
        self.num_jobs = 12
        self.fast = False
        self.speaker_characters = 0
        self.verbose = False
        self.clean = True
        self.no_speaker_adaptation = False
        self.temp_directory = '/data/mmcauliffe/temp/MFA'

args = DummyArgs()
args.corpus_directory = '/media/share/datasets/aligner_benchmarks/sorted_quebec_french'
args.dictionary_path = '/media/share/corpora/GP_for_MFA/FR/dict/fr.dict'
args.output_directory = '/data/mmcauliffe/aligner-output/aligned_quebec_french'
args.output_model_path = '/data/mmcauliffe/aligner-models/french_qc.zip'

if not os.path.exists(args.output_model_path):
    try:
        beg = time.time()
        align_corpus(args)
        end = time.time()
        duration = end - beg
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print('{} encountered an error!'.format(full_name))
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                    file=sys.stdout)

csv_columns = ['Computer','Date','Corpus', 'Version', 'Language', 'Type of benchmark', 'Total time', 'Num_jobs']

now = datetime.now()
date = str(now.year)+str(now.month)+str(now.day)

dict_data = {'Computer': platform.node(),
        'Date': date,
        'Corpus': args.corpus_directory,
        'Version': aligner.__version__,
        'Language': 'QC',
        'Type of benchmark': 'train and align',
        'Total time': duration,
        'Num_jobs': args.num_jobs}



if not os.path.exists(csv_path):
    with open(csv_path, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()


with open(csv_path, 'a') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
    writer.writerow(dict_data)
