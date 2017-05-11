import sys
import shutil, os
import subprocess

import time
import logging
import platform
import traceback
import csv
import statistics
from datetime import datetime

mfa_path = '/data/mmcauliffe/dev/Montreal-Forced-Aligner'

current_commit = subprocess.check_output(['git', 'describe', '--always'], cwd=mfa_path)

sys.path.insert(0, mfa_path)

import aligner
from aligner.command_line.train_and_align import align_corpus, align_corpus_no_dict, fix_path, unfix_path


languages = [('BG','bulgarian'),
            ('CH', 'mandarin'),
            ('CR', 'croatian'),
            ('CZ', 'czech'),
            ('FR', 'french'),
            ('GE', 'german'),
            ('HA', 'hausa'),
            ('JA', 'japanese'),
            ('KO', 'korean'),
            ('PL', 'polish'),
            ('PO', 'portuguese'),
            ('RU', 'russian'),
            ('SP', 'spanish'),
            ('SA', 'swahili'),
            ('SW', 'swedish'),
            ('TA', 'tamil'),
            ('TH', 'thai'),
            ('TU', 'turkish'),
            ('UA', 'ukrainian'),
            ('VN', 'vietnamese'),
            ('WU', 'wu'),
            ]

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


def align_gp(lang_code, full_name):

    if lang_code == 'FR':
        args = DummyArgs()
        args.corpus_directory = '/media/share/corpora/GP_for_MFA/{}'.format(lang_code)
        args.dictionary_path = '/media/share/corpora/GP_for_MFA/{0}/dict/lexique.dict'.format(lang_code)
        args.output_directory = '/data/mmcauliffe/aligner-output/{}'.format(lang_code)
        args.output_model_path = '/data/mmcauliffe/aligner-models/{}_lexique.zip'.format(full_name)
        if not os.path.exists(args.output_model_path):
            try:
                align_corpus(args)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print('{} encountered an error!'.format(full_name))
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                            file=sys.stdout)

    elif lang_code == 'GE':
        args = DummyArgs()
        args.corpus_directory = '/media/share/corpora/GP_for_MFA/{}'.format(lang_code)
        args.dictionary_path = '/media/share/corpora/GP_for_MFA/{0}/dict/de.dict'.format(lang_code)
        args.output_directory = '/data/mmcauliffe/aligner-output/{}'.format(lang_code)
        args.output_model_path = '/data/mmcauliffe/aligner-models/{}_prosodylab.zip'.format(full_name)
        if not os.path.exists(args.output_model_path):
            try:
                align_corpus(args)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print('{} encountered an error!'.format(full_name))
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                            file=sys.stdout)

    args = DummyArgs()
    args.corpus_directory = '/media/share/corpora/GP_for_MFA/{}'.format(lang_code)
    args.dictionary_path = '/media/share/corpora/GP_for_MFA/{0}/dict/{0}_dictionary.txt'.format(lang_code)
    args.output_directory = '/data/mmcauliffe/aligner-output/{}'.format(lang_code)
    args.output_model_path = '/data/mmcauliffe/aligner-models/{}.zip'.format(full_name)

    if os.path.exists(args.output_model_path):
        print('skipping {}, output  model already exists'.format(full_name))
        return

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
        return

    csv_columns = ['Computer','Date','Corpus', 'Version', 'Language', 'Type of benchmark', 'Total time', 'Num_jobs']

    now = datetime.now()
    date = str(now.year)+str(now.month)+str(now.day)

    dict_data = {'Computer': platform.node(),
            'Date': date,
            'Corpus': args.corpus_directory,
            'Version': aligner.__version__,
            'Language': lang_code,
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

if __name__ == '__main__':

    fix_path()
    for code, name in languages:
        print(name)
        align_gp(code, name)
    unfix_path()
