import time
from datetime import datetime
import os
import logging
import platform
import csv
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
#globalphonebenchmark = 'globalphonebenchmark'
globalphonebenchmark = 'globalphone_cz'
sotcbenchmark = 'sotcbenchmark'
timitbenchmark = 'timitbenchmark'

lasttime = time.time()
times = []

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

def pause_encoding_run_query(data):
    beg = time.time()
    with CorpusContext(data, **graph_db) as c:
        c.encode_pauses('^[<{].*$', call_back=call_back)
    end = time.time()
    if len(times) >1:
        avgtime = sum(times)/len(times)
        sd = statistics.stdev(times)
    else:
        avgtime = times[0]
        sd = statistics.stdev(times)
    return [(end - beg), avgtime, sd]

#buckeye_pauses = pause_encoding_run_query(buckeyebenchmark)
globalphone_pauses = pause_encoding_run_query(globalphonebenchmark)
#sotc_pauses = pause_encoding_run_query(sotcbenchmark)
#timit_pauses = pause_encoding_run_query(timitbenchmark)

def WriteDictToCSV(csv_file,csv_columns,dict_data):
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)   
        return            

csv_columns = ['Computer','Date','Corpus', 'Type of benchmark', 'Total time', 'Mean time per call back', 'sd time between call backs']
dict_data = [
    #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'buckeye', 'Type of benchmark': 'Pause encoding', 'Total time': buckeye_pauses[0], 'Mean time per call back': buckeye_pauses[1], 'sd time between call backs': buckeye_pauses[2]},
    {'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': globalphonebenchmark, 'Type of benchmark': 'Pause encoding', 'Total time': globalphone_pauses[0], 'Mean time per call back': globalphone_pauses[1], 'sd time between call backs': globalphone_pauses[2]},
    #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'sotc', 'Type of benchmark': 'Pause encoding', 'Total time': sotc_pauses[0], 'Mean time per call back': sotc_pauses[1], 'sd time between call backs': sotc_pauses[2]},
    #{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': amountofcorpus + 'timit', 'Type of benchmark': 'Pause encoding', 'Total time': timit_pauses[0], 'Mean time per call back': timit_pauses[1], 'sd time between call backs': timit_pauses[2]},
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


