import sys
#sys.path.insert(0,"/Users/acoles/Documents/PolyglotDB-master-3")
#sys.path.insert(0, "/Users/mlml/Documents/GitHub/PolyglotDB")
sys.path.insert(0, "/users/mlml/Documents/transfer/PolyglotDB-master-3")
import os
import time
import logging

import polyglotdb.io as pgio

from polyglotdb import CorpusContext
from polyglotdb.config import CorpusConfig
from polyglotdb.io.parsers import FilenameSpeakerParser
from polyglotdb.io.enrichment import enrich_speakers_from_csv, enrich_lexicon_from_csv

from polyglotdb.utils import get_corpora_list

graph_db = ({'graph_host':'localhost', 'graph_port': 7474,
	'graph_user': 'neo4j', 'graph_password': 'test'})

def call_back(*args):
    args = [x for x in args if isinstance(x, str)]
    if args:
        print(' '.join(args))

if __name__ == '__main__':
	with CorpusContext("VTRSubset", **graph_db) as c:
		print ("Loading...")
		c.reset()
		#parser = pgio.inspect_timit('/Volumes/data/datasets/sct_benchmarks/VTRFormants')
		parser = pgio.inspect_timit('/Users/mlml/Documents/transfer/VTRSubset')
		parser.call_back = call_back
		#c.load(parser, '/Volumes/data/datasets/sct_benchmarks/VTRFormants')
		c.load(parser, '/Users/mlml/Documents/transfer/VTRSubset')
