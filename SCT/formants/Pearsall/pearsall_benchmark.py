import os
import time
import logging
import platform
import csv
from datetime import datetime
import statistics
import xlrd
import sys
sys.path.insert(0,"/Users/mlml/Documents/GitHub/PolyglotDB/polyglotdb/acoustics")
from formant import analyze_formants_vowel_segments_new, get_mean_SD, get_stdev, refine_formants, extract_formants_full

import polyglotdb.io as pgio

from polyglotdb import CorpusContext
from polyglotdb.config import CorpusConfig
from polyglotdb.acoustics.analysis import generate_phone_segments_by_speaker

from acousticsim.analysis.praat import run_script

sys.path.insert(0,"/Users/mlml/Documents/transfer/Formants/")
from hand_formants import get_hand_formants, get_mean

graph_db = ({'graph_host':'localhost', 'graph_port': 7474,
	'graph_user': 'neo4j', 'graph_password': 'test'})

# Special cases: 'uw'
MONOPHTHONGS = ['I', 'E', 'ae', 'aeE', 'aeN', 'a', 'open o', 'wedge', 'ow', 'U', 'uw', 'owr', 'uwr', 'r']
DIPHTHONGS = ['ij', 'ej', 'uw', 'aiv', 'aio', 'au', 'oi', 'ir', 'er', 'ar', 'open o-r', ]

SPANISH_FILES = [
	"/Users/mlml/Documents/transfer/NorthTownVowelSpreadsheets/PTX0010bSVdata.xls",
	"/Users/mlml/Documents/transfer/NorthTownVowelSpreadsheets/PTX0060aSVdata.xls",
	"/Users/mlml/Documents/transfer/NorthTownVowelSpreadsheets/PTX0120aSVdata.xls",
	"/Users/mlml/Documents/transfer/NorthTownVowelSpreadsheets/PTX0160bSVdata.xls",
	"/Users/mlml/Documents/transfer/NorthTownVowelSpreadsheets/PTX0350bEVdata.xls"
]


def get_algorithm_data(corpus_name):
	beg = time.time()
	with CorpusContext(corpus_name, **graph_db) as g:

		# THIS IS HACKY, fix later! Find out why these aren't getting encoded on Chevre
		try:
			print(g.graph_host)
		except:
			g.acoustic_host = 'localhost'
			g.acoustic_port = 8086
			g.graph_host = 'localhost'
			g.graph_port = 7474
			g.bolt_port = 7687
			g.config.praat_path = "/Applications/Praat.app/Contents/MacOS/Praat"

		prototype, data = extract_formants_full(g, VOWELS)
	end = time.time()
	duration = end - beg
	return prototype, data, duration


def get_hand_formants(vowel_dir):
	for spreadsheet_file in os.listdir(vowel_dir):
		if spreadsheet_file.endswith(".xls"):
			file_id = spreadsheet_file[:-8]
			spreadsheet_file = vowel_dir + "/" + spreadsheet_file
			print("Looking at file:", spreadsheet_file)
			if spreadsheet_file in SPANISH_FILES:
				continue	# This file is in Spanish!
			print("The speaker is:", file_id)
			spreadsheet = xlrd.open_workbook(spreadsheet_file)
			print("The number of worksheets is {0}".format(spreadsheet.nsheets))


if __name__ == '__main__':
	vowel_dir = "/Users/mlml/Documents/transfer/NorthTownVowelSpreadsheets"

	"""# Get algorithm data
	prototype, data, duration = get_algorithm_data("Pearsall")
	print("-------------")
	print("The algorithm took:", duration, "seconds.")
	print()
	print("Prototype data:")
	print(prototype)
	print()
	print("Algorithm data:")
	print(data)"""


	# Load in hand-checked data
	hand_checked = get_hand_formants(vowel_dir)
	#print(hand_checked)


	"""# Make correspondence between algorithm and hand-checked data (find matching pairs)
	pairs, vowel_differences = get_pairs(data, hand_checked)


	# Get averages of error for each vowel class, for each value
	avg_error = get_avg_error(vowel_differences)
	print()
	print("Average errors per vowel:")
	print(avg_error)

	# Write to a file
	# Meta info about the pass
	meta_columns = ['Computer','Date','Corpus', 'Type of benchmark', 'Total time']
	dict_data = [{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': corpus_name, 'Type of benchmark': 'Initial pass', 'Total time': duration}]
	write_to_csv("meta", meta_columns, dict_data)

	# Prototype data
	prototype_columns = ['file_id', 'start', 'end', 'vowel', 'F1', 'F2', 'F3']
	prototype_csv = to_prototype_csv(prototype)
	write_to_csv("prototype", prototype_columns, prototype_csv)

	# Computed algorithm data
	algorithm_columns = ['Vowel instance', 'F1', 'F2', 'F3']
	alg_csv = data_to_csv_dict(data)
	write_to_csv("comp", algorithm_columns, alg_csv)

	# Vowel avg error data
	avg_columns = ['Vowel class', 'F1', 'F2', 'F3']
	avg_csv = data_to_csv_dict(avg_error)
	write_to_csv("vowelavg", avg_columns, avg_csv)"""
