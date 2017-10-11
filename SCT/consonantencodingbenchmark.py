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

#buckeyeconsonants = ['aa', 'aan','ae', 'aen','ah', 'ahn','ay', 'ayn','aw','awn','ao', 'aon',
 #           'iy','iyn','ih', 'ihn',
  #          'uw', 'uwn','uh', 'uhn',
   #         'eh', 'ehn','ey', 'eyn', 'er','el','em', 'eng',
    #        'ow','own', 'oy', 'oyn']
globalphoneconsonants = ['b','bj','d','dj','f','fj','g','gj','k','kj','p','pj','s','sj','S', 't','tj','v','vj','z','zj','Z','x','dz','dZ','ts','tS']
#sotcconsonants = ['C', 'F', 'H', 'P', 'I', 'E', '{', 'V', 'Q', 'U', '@', 'i', '#', '$', 'u', '3', '1', '2', '4', '5', '6', '7', '8', '9', 'c', 'q', '0', '"']
#timitconsonants = ['aa', 'ae', 'ah', 'ao', 'aw', 'ax', 'ax-h', 'axr', 'ay',
     #       'eh', 'el', 'em', 'en', 'eng', 'er', 'ey',
      #      'ih', 'ix', 'iy',
       #     'ow',' oy',
        #    'uh', 'uw', 'ux']


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

def consonantal_encoding_run_query(data, consonant):
    beg = time.time()
    with CorpusContext(data, **graph_db) as c:
        c.reset_class('consonantal')
        c.encode_class(consonant, 'consonantal')
    end = time.time()
    #avgtime = sum(times)/len(times)
    return [(end - beg), None]

#buckeye_consonantal = consonantal_encoding_run_query(buckeyebenchmark, buckeyesyllabic)
globalphone_consonantal = consonantal_encoding_run_query(globalphonebenchmark, globalphoneconsonants)
#sotc_consonantal = consonantal_encoding_run_query(sotcbenchmark, sotcsyllabic)
#timit_consonantal = consonantal_encoding_run_query(timitbenchmark, timitsyllabic)

def WriteDictToCSV(csv_file,csv_columns,dict_data):
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)   
        return            

csv_columns = ['Computer','Date','Corpus', 'Type of benchmark', 'Total time', 'Mean time per call back', 'sd time between call backs']
dict_data = [
    #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'buckeye', 'Type of benchmark': 'Consonant encoding', 'Total time': buckeye_consonantal[0], 'Mean time per call back': None, 'sd time between call backs': None},
    {'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': globalphonebenchmark, 'Type of benchmark': 'Consonant encoding', 'Total time': globalphone_consonantal[0], 'Mean time per call back': None, 'sd time between call backs': None},
    #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'sotc', 'Type of benchmark': 'Consonant encoding', 'Total time': sotc_consonantal[0], 'Mean time per call back': None, 'sd time between call backs': None},
    #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'timit', 'Type of benchmark': 'Consonant encoding', 'Total time': timit_consonantal[0], 'Mean time per call back': None, 'sd time between call backs': None},
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

