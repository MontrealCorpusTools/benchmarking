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
from aligner.g2p.trainer import PhonetisaurusTrainer

from aligner.dictionary import Dictionary

now = datetime.now()
date = str(now.year)+str(now.month)+str(now.day)

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
            ('SA', 'swahili'),
            ('SW', 'swedish'),
            ('TA', 'tamil'),
            ('TH', 'thai'),
            ('TU', 'turkish'),
            ('UA', 'ukrainian'),
            ('VN', 'vietnamese'),
            ('WU', 'wu'),
            ]

csv_path = 'g2p_benchmark.csv'

csv_columns = ['Computer','Date','Dictionary', 'Version', 'Language', 'Window size', 'Type of benchmark', 'Total time']

if not os.path.exists(csv_path):
    with open(csv_path, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()

dict_data = {'Computer': platform.node(),
        'Date': date,
        'Version': aligner.__version__,
        'Type of benchmark': 'train_g2p'}

def g2p_gp(lang_code, full_name):
    dictionary_path = '/media/share/corpora/GP_for_MFA/{0}/dict/{0}_dictionary.txt'.format(lang_code)
    output_model_path = '/data/mmcauliffe/aligner-models/g2p/{}_g2p.zip'.format(full_name)
    temp_directory = '/data/mmcauliffe/temp/MFA'
    dictionary = Dictionary(dictionary_path, '')
    best_acc = 0
    best_size = 0
    for s in [2,3,4]:
        begin = time.time()
        t = PhonetisaurusTrainer(dictionary, output_model_path, temp_directory=temp_directory, window_size=s)
        acc = t.validate()
        duration = time.time() - begin
        line_dict = {'Dictionary': dictionary_path, 'Language': lang_code, 'Total time': duration, 'Window size': s}
        line_dict.update(dict_data)

        with open(csv_path, 'a') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
            writer.writerow(line_dict)
        if acc > best_acc:
            best_acc = acc
            best_size = s

    t = PhonetisaurusTrainer(dictionary, output_model_path, temp_directory=temp_directory, window_size=best_size)
    t.train()




if __name__ == '__main__':

    fix_path()
    for code, name in languages:
        print(name)
        g2p_gp(code, name)
    unfix_path()
