import time
import os
import logging
import platform
import csv
from datetime import datetime
import statistics

from polyglotdb import CorpusContext
from polyglotdb.config import CorpusConfig

from polyglotdb.io import (inspect_buckeye, inspect_textgrid, inspect_timit,
                        inspect_labbcat, inspect_mfa, inspect_fave,
                        guess_textgrid_format)

graph_db = {'graph_host':'localhost', 'graph_port': 7474,
            'user': 'neo4j', 'password': 'test'}

amountofcorpus = 'full'
#amountofcorpus = 'partial'

buckeyebenchmark = 'buckeyebenchmark'
globalphonebenchmark = 'globalphone_cz'
#globalphonebenchmark = 'globalphonebenchmark'
sotcbenchmark = 'sotcbenchmark'
timitbenchmark = 'timitbenchmark'

buckeyesyllabic = ['aa', 'aan','ae', 'aen','ah', 'ahn','ay', 'ayn','aw','awn','ao', 'aon',
            'iy','iyn','ih', 'ihn',
            'uw', 'uwn','uh', 'uhn',
            'eh', 'ehn','ey', 'eyn', 'er','el','em', 'eng',
            'ow','own', 'oy', 'oyn']
globalphonesyllabic = ['i', 'y', 'u', 'e', 'EU', 'o', 'E', 'OE', 'AX', 'O', 'a', 'A~', 'E~', 'o~', 'OE~']
sotcsyllabic = ['C', 'F', 'H', 'P', 'I', 'E', '{', 'V', 'Q', 'U', '@', 'i', '#', '$', 'u', '3', '1', '2', '4', '5', '6', '7', '8', '9', 'c', 'q', '0', '"']
timitsyllabic = ['aa', 'ae', 'ah', 'ao', 'aw', 'ax', 'ax-h', 'axr', 'ay',
            'eh', 'el', 'em', 'en', 'eng', 'er', 'ey',
            'ih', 'ix', 'iy',
            'ow',' oy',
            'uh', 'uw', 'ux']


lasttime = time.time()

def call_back(*args):
    global lasttime
    print(*args)
    if len(args) > 1:
    	return
    if isinstance(args[0], int):
        logtime = time.time() - lasttime
        print(logtime)
        times.append(logtime)
        lasttime = time.time()

def syllabic_encoding_run_query(data, syllabic):
    beg = time.time()
    with CorpusContext(data, **graph_db) as c:
        c.reset_class('syllabic')
        c.encode_class(syllabic, 'syllabic')
    end = time.time()
    #avgtime = sum(times)/len(times)
    return [(end - beg), None]

def syllable_encoding_run_query(data):
    beg = time.time()
    algorithm = 'maxonset'
    with CorpusContext(data, **graph_db) as c:
        c.encode_syllables(algorithm = algorithm)
    end = time.time()
    return [(end - beg), None]

#buckeye_syllabic = syllabic_encoding_run_query(buckeyebenchmark, buckeyesyllabic)
globalphone_syllabic = syllabic_encoding_run_query(globalphonebenchmark, globalphonesyllabic)
#sotc_syllabic = syllabic_encoding_run_query(sotcbenchmark, sotcsyllabic)
#timit_syllabic = syllabic_encoding_run_query(timitbenchmark, timitsyllabic)

#buckeye_syllables = syllable_encoding_run_query(buckeyebenchmark)
globalphone_syllables = syllable_encoding_run_query(globalphonebenchmark)
#sotc_syllables = syllable_encoding_run_query(sotcbenchmark)
#timit_syllales = syllable_encoding_run_query(timitbenchmark)

def WriteDictToCSV(csv_file,csv_columns,dict_data):
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)
    return

csv_columns = ['Computer','Date','Corpus', 'Type of benchmark', 'Total time', 'Mean time per call back', 'sd time between call backs']
dict_data = [
    #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'buckeye', 'Type of benchmark': 'Syllabic encoding', 'Total time': buckeye_syllabic[0], 'Mean time per call back': buckeye_syllabic[1], 'sd time between call backs': buckeye_syllabic[1]},
    {'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': globalphonebenchmark, 'Type of benchmark': 'Syllabic encoding', 'Total time': globalphone_syllabic[0], 'Mean time per call back': globalphone_syllabic[1], 'sd time between call backs': globalphone_syllabic[1]},
    #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'sotc', 'Type of benchmark': 'Syllabic encoding', 'Total time': sotc_syllabic[0], 'Mean time per call back': sotc_syllabic[1], 'sd time between call backs': sotc_syllabic[1]},
    #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'timit', 'Type of benchmark': 'Syllabic encoding', 'Total time': timit_syllabic[0], 'Mean time per call back': timit_syllabic[1], 'sd time between call backs': timit_syllabic[1]},
    #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'buckeye', 'Type of benchmark': 'Syllable encoding', 'Total time': buckeye_syllables[0], 'Mean time per call back': buckeye_syllables[1], 'sd time between call backs': buckeye_syllables[1]},
    {'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': globalphonebenchmark, 'Type of benchmark': 'Syllable encoding', 'Total time': globalphone_syllables[0], 'Mean time per call back': globalphone_syllables[1], 'sd time between call backs': globalphone_syllables[1]},]
    #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'sotc', 'Type of benchmark': 'Syllable encoding', 'Total time': sotc_syllables[0], 'Mean time per call back': sotc_syllables[1], 'sd time between call backs': sotc_syllables[1]},]
    #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'timit', 'Type of benchmark': 'Syllable encoding', 'Total time': timit_syllables[0], 'Mean time per call back': timit_syllables[1], 'sd time between call backs': 1},
    #]

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
    writer.writerow(dict_data[1])
    #writer.writerow(dict_data[2])
    #writer.writerow(dict_data[3])
    #writer.writerow(dict_data[4])
    #writer.writerow(dict_data[5])
    #writer.writerow(dict_data[6])
    #writer.writerow(dict_data[7])

