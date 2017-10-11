import sys
import os
import platform
from datetime import datetime
import csv

# =============== USER CONFIGURATION ===============
polyglotdb_path = os.path.join('PolyglotDB')
# change these to run the benchmark on another corpus
corpus_name = "small_raleigh"
corpus_dir = "/home/samihuc/pgdb_corpora/small_raleigh"
# change these to encode a different phone class for the script to run on
segments = ['S', 'Z', 'SH', 'ZH']
phone_class_name = 'sibilant'
reset = False  # Setting to True will cause the corpus to re-import

# Paths to scripts and praat

praat_path = 'praat'
# change this to run the benchmark using a different praat script
script_path = os.path.join(polyglotdb_path, 'examples', 'sibilant_analysis', 'sibilant_jane.praat')
output_path = os.path.join(polyglotdb_path, 'examples', 'sibilant_analysis', 'all_sibilant_data.csv')
# ==================================================


sys.path.insert(0, polyglotdb_path)

import time

import polyglotdb.io as pgio

from polyglotdb import CorpusContext
from polyglotdb.utils import ensure_local_database_running
from polyglotdb.config import CorpusConfig


def call_back(*args):
    args = [x for x in args if isinstance(x, str)]
    if args:
        print(' '.join(args))


def loading(config):
    # Initial import of the corpus to PGDB
    # only needs to be done once. resets the corpus if it was loaded previously.
    with CorpusContext(config) as c:
        c.reset()
        parser = pgio.inspect_fave(corpus_dir)
        parser.call_back = call_back
        beg = time.time()
        c.load(parser, corpus_dir)
        end = time.time()
        print('Loading took: {}'.format(end - beg))


def acoustics(config):
    # Encode sibilant class and analyze sibilants using the praat script
    with CorpusContext(config) as c:
        c.encode_class(segments, phone_class_name)

        # c.reset_acoustics()

        # analyze all sibilants using the script found at script_path
        beg = time.time()
        c.analyze_script(phone_class_name, script_path)
        end = time.time()
        print('Analysis took: {}'.format(end - beg))
        return end - beg

# by default, analysis (which queries the database and exports a CSV) is not run for benchmarking
def analysis(config):
    with CorpusContext(config) as c:
        # export to CSV all the measures taken by the script, along with a variety of data about each phone
        print("querying")
        qr = c.query_graph(c.phone).filter(c.phone.subset == phone_class_name)
        # this exports data for all sibilants
        qr = qr.columns(c.phone.speaker.name.column_name('speaker'), c.phone.discourse.name.column_name('discourse'),
                        c.phone.id.column_name('phone_id'), c.phone.label.column_name('phone_label'),
                        c.phone.begin.column_name('begin'), c.phone.end.column_name('end'),
                        c.phone.following.label.column_name('following_phone'),
                        c.phone.previous.label.column_name('previous_phone'), c.phone.word.label.column_name('word'),
                        c.phone.cog.column_name('cog'), c.phone.peak.column_name('peak'),
                        c.phone.slope.column_name('slope'), c.phone.spread.column_name('spread'))
        qr.to_csv(output_path)
        print("Results written to " + output_path)


if __name__ == '__main__':
    with ensure_local_database_running('database') as config:
        conf = CorpusConfig(corpus_name, **config)
        conf.pitch_source = 'praat'
        conf.formant_source = 'praat'
        conf.intensity_source = 'praat'
        conf.praat_path = praat_path
        if reset:
            print('loading')
            loading(conf)
        print('analyzing')
        benchmark = acoustics(conf)
        # analysis(conf)
        csv_columns = ['Computer','Date','Corpus', 'Type of benchmark', 'Total time']
        dict_data = {'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': 'small_raleigh', 'Type of benchmark': 'Analyze all sibilants for 4 acoustic measures', 'Total time': benchmark}
        currentPath = os.getcwd()

        now = datetime.now()
        date = str(now.year)+str(now.month)+str(now.day)

        if not os.path.exists('praatscript_benchmark'+date+'.csv'):
            #open('benchmark'+date+'.csv', 'a')
            with open('praatscript_benchmark'+date+'.csv', 'a') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
                writer.writeheader()

        with open('praatscript_benchmark'+date+'.csv', 'a') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
            writer.writerow(dict_data)
