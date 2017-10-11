import sys
sys.path.insert(0,"/Users/mlml/Documents/transfer/Git/PolyglotDB")
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
	with CorpusContext("Hillenbrand", **graph_db) as c:
		print ("Loading...")
		c.reset()
		parser = pgio.inspect_mfa('/Users/mlml/Documents/transfer/Hillenbrand/textgrid-wav')
		parser.call_back = call_back
		#beg = time.time()
		c.load(parser, '/Users/mlml/Documents/transfer/Hillenbrand/textgrid-wav')
		#end = time.time()
		#time = end-beg
		#logger.info('Loading took: ' + str(time))
