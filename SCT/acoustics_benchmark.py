import time
import os
import logging
import platform
import statistics
import csv
from datetime import datetime

from polyglotdb import CorpusContext
from polyglotdb.corpus import AudioContext
from polyglotdb.config import CorpusConfig

from polyglotdb.io import (inspect_buckeye, inspect_textgrid, inspect_timit,
                        inspect_labbcat, inspect_mfa, inspect_fave,
                        guess_textgrid_format)

graph_db = {'graph_host':'localhost', 'graph_port': 7474,
            'user': 'neo4j', 'password': 'test'}


#amountofcorpus = 'full'
amountofcorpus = 'partial'

def call_back(*args):
    global lasttime
    print(args)
    if len(args) > 1:
        return
    if isinstance(args[0], int):
        logtime = time.time() - lasttime
        print(logtime)
        times.append(logtime)
        lasttime = time.time()

if not os.path.exists('exportbenchmark.csv'):
    open('exportbenchmark.csv', 'w')

def analyze_cog(data, script_path, phone_class, praat_path):
    beg = time.time()

    with CorpusContext(data, **graph_db) as c:
        c.config.praat_path = praat_path
        c.analyze_script(phone_class, script_path, 'COG', stop_check=None, call_back=None)
    end = time.time()
    return [(end-beg)]

praat_path = 'C:\\Users\\samih\\Documents\\0_SPADE_labwork\\praatcon.exe'
script_path = 'C:\\Users\\samih\\Documents\\0_SPADE_labwork\\PolyglotDB\\examples\\COG.praat'

def WriteDictToCSV(csv_file,csv_columns,dict_data):
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
        return

with CorpusContext('librispeech', **graph_db) as c:
    c.encode_class(['S', 'Z', 'SH', 'ZH'], 'sibilant')
    librispeech_medium_cog = analyze_cog('librispeech', script_path, 'sibilant', praat_path)

    csv_columns = ['Computer','Date','Corpus', 'Type of benchmark', 'Total time', 'Mean time per call back', 'sd time between call backs']
    dict_data = [
        {'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'librispeech', 'Type of benchmark': 'Analyze all sibiants for COG', 'Total time': librispeech_medium_cog[0], 'Mean time per call back': None, 'sd time between call backs': None},
        #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'buckeye', 'Type of benchmark': 'Export word-final consonants', 'Total time': buckeye_export_wfv[0], 'Mean time per call back': None, 'sd time between call backs': None},
	    #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'buckeye', 'Type of benchmark': 'Export polysyllabic shortening', 'Total time': buckeye_export_pss[0], 'Mean time per call back': None, 'sd time between call backs': None},
        #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': globalphone_cz, 'Type of benchmark': 'Export all vowels', 'Total time': globalphone_export_pt[0], 'Mean time per call back': None, 'sd time between call backs': None},
        #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': globalphone_cz, 'Type of benchmark': 'Export word-final consonants', 'Total time': globalphone_export_wfc[0], 'Mean time per call back': None, 'sd time between call backs': None},
        #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': globalphone_cz, 'Type of benchmark': 'Export polysyllabic shortening', 'Total time': globalphone_export_pss[0], 'Mean time per call back': None, 'sd time between call backs': None},
        #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpuc + 'sotc', 'Type of benchmark': 'Export all vowels', 'Total time': sotc_export_pt[0], 'Mean time per call back': None, 'sd time between call backs': None},
        #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'sotc', 'Type of benchmark': 'Export encoding word-final consonants', 'Total time': sotc_export_wfv[0], 'Mean time per call back': None, 'sd time between call backs': None},
        #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'sotc', 'Type of benchmark': 'Export polysyllabic shortening', 'Total time': sotc_export_pss[0], 'Mean time per call back': None, 'sd time between call backs': None},
        #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'timit', 'Type of benchmark': 'Export all vowels', 'Total time': timit_export_pt[0], 'Mean time per call back': None, 'sd time between call backs': None},
        #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'timit', 'Type of benchmark': 'Export word-final consonants', 'Total time': timit_export_wfv[0], 'Mean time per call back': None, 'sd time between call backs': None},
        #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'timit', 'Type of benchmark': 'Export polysyllabic shortening', 'Total time': timit_export_pss[0], 'Mean time per call back': None, 'sd time between call backs': None},
        ]

    currentPath = os.getcwd()

    now = datetime.now()
    date = str(now.year)+str(now.month)+str(now.day)

    if not os.path.exists('benchmark'+date+'.csv'):
        open('benchmark'+date+'.csv', 'a')
        with open('benchmark'+date+'.csv', 'a') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
            writer.writeheader()

    csv_file = 'benchmark'+date+'.csv'

    with open('benchmark'+date+'.csv', 'a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writerow(dict_data[0])
        #writer.writerow(dict_data[1])
        #writer.writerow(dict_data[2])
        #writer.writerow(dict_data[3])
        #writer.writerow(dict_data[4])
        #writer.writerow(dict_data[5])
	    #writer.writerow(dict_data[6])
    	#writer.writerow(dict_data[7])
	    #writer.writerow(dict_data[8])
    	#writer.writerow(dict_data[9])
	    #writer.writerow(dict_data[10])
        #writer.writerow(dict_data[11])