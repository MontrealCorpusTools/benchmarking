import os
import time
import logging
import platform
import csv
from datetime import datetime
import statistics
import sys
sys.path.insert(0,"/Users/mlml/Documents/GitHub/PolyglotDB/polyglotdb/acoustics")
from formant import analyze_formants_vowel_segments_new, get_mean_SD, refine_formants, extract_formants_full

import polyglotdb.io as pgio

from polyglotdb import CorpusContext
from polyglotdb.config import CorpusConfig
from polyglotdb.acoustics.analysis import generate_phone_segments_by_speaker

from acousticsim.analysis.praat import run_script

sys.path.insert(0,"/Users/mlml/Documents/transfer/Formants/")
from hand_formants import get_mean

graph_db = ({'graph_host':'localhost', 'graph_port': 7474,
	'graph_user': 'neo4j', 'graph_password': 'test'})

VOWELS = ['ae', 'ah', 'aw', 'eh', 'er', 'ey', 'ih', 'iy', 'oa', 'oo', 'uw']	# NOT TIMIT although looks similar!

def get_algorithm_data(corpus_name, nIterations, remove_short):
	beg = time.time()
	with CorpusContext(corpus_name, **graph_db) as g:

		# This is a hack - Chevre isn't encoding these, but other machines are
		try:
			print("Graph host:", g.graph_host)
		except:
			g.acoustic_host = 'localhost'
			g.acoustic_port = 8086
			g.graph_host = 'localhost'
			g.graph_port = 7474
			g.bolt_port = 7687
			g.config.praat_path = "/Applications/Praat.app/Contents/MacOS/Praat"

		prototype, metadata, data = extract_formants_full(g, VOWELS, remove_short=remove_short, nIterations=nIterations)
	end = time.time()
	duration = end - beg
	return prototype, metadata, data, duration

def get_hand_formants(audio_info, time_info, corpus_dir):
	print("corpus_dir is:", corpus_dir)
	with open(time_info, 'r') as t:
		time_text = t.readlines()[6:]
	time_text2 = []
	for item in time_text:
		item = item.split()
		time_text2.append(item)
	time_text = time_text2

	with open(audio_info, 'r') as a:
		audio_text = a.readlines()[43:]		# Get rid of header info
	audio_text2 = []
	for line in audio_text:
		line_list = line.split()
		file_id, vowel, F1, F2, F3 = line_list[0], line_list[0][-2:], line_list[12], line_list[13], line_list[14]
		for item in time_text:
			if file_id in item[0]:
				beg = item[1]
				end = item[2]
				break
		line = [file_id, vowel, beg, end, F1, F2, F3] 	# Only get relevant info
		audio_text2.append(line)
	audio_text = audio_text2
	return audio_text

def get_pairs(data, hand_checked):
	print(len(data), len(hand_checked))
	pairs = {}
	vowel_differences = {}
	for alg_point, values in data.items():
		f1_delta, f2_delta, f3_delta = 0, 0, 0
		for hand_point in hand_checked:
			smallest_diff = float('inf')
			if hand_point[0] in alg_point[0][0] and hand_point[1] in alg_point[0][4]:        # If file names and vowels match
				beg_diff = abs(float(hand_point[2]) - float(alg_point[0][1]))
				if beg_diff < smallest_diff:
					smallest_diff = beg_diff
					f1_delta = abs(float(hand_point[2]) - float(values['F1']))
					f2_delta = abs(float(hand_point[3]) - float(values['F2']))
					f3_delta = abs(float(hand_point[4])- float(values['F3']))
					pair = [values, hand_point]
		if [f1_delta, f2_delta, f3_delta] == [0, 0, 0]:
			continue
		else:
			pairs[alg_point] = pair
			vowel_differences[alg_point] = [f1_delta, f2_delta, f3_delta]
	return pairs, vowel_differences

def get_avg_error(vowel_differences):
	avg_error = {}
	for meta, values in vowel_differences.items():
		vowel_class = meta[0][-1]
		if vowel_class not in avg_error:
			avg_error[vowel_class] = {}
			avg_error[vowel_class]['F1'] = []
			avg_error[vowel_class]['F2'] = []
			avg_error[vowel_class]['F3'] = []
		avg_error[vowel_class]['F1'].append(values[0])
		avg_error[vowel_class]['F2'].append(values[1])
		avg_error[vowel_class]['F3'].append(values[2])

	for vowel_class, values in avg_error.items():
		values['F1'] = get_mean(values['F1'])
		values['F2'] = get_mean(values['F2'])
		values['F3'] = get_mean(values['F3'])

	return avg_error

def data_to_csv_dict(data):
	to_return = []
	for vowel, formants in data.items():
		vowel_dict = {}
		vowel_dict['Vowel instance'] = vowel
		if isinstance(formants, dict):
			vowel_dict['F1'] = formants['F1']
			vowel_dict['F2'] = formants['F2']
			vowel_dict['F3'] = formants['F3']
		else:
			vowel_dict['F1'] = formants[0]
			vowel_dict['F2'] = formants[1]
			vowel_dict['F3'] = formants[2]
		to_return.append(vowel_dict)
	return to_return

def to_prototype_csv(prototype_data):
	to_return = []
	if isinstance(prototype_data, list):
		for item in prototype_data:
			if isinstance(item, list) and item != []:
					item = item[0]
			else:
				print("There was an error with this prototype generation instance.")
				continue
			prototype = {}
			prototype['file_id'] = item['tags']['discourse']
			prototype['start'] = item['begin']
			prototype['end'] = item['end']
			prototype['measurement_time'] = item['begin']+((item['end']-item['begin'])*0.33)
			prototype['vowel'] = item['fields']['phone']
			prototype['nformants'] = 5
			prototype['F1'] = item['fields']['F1']
			prototype['F2'] = item['fields']['F2']
			prototype['F3'] = item['fields']['F3']
			to_return.append(prototype)
	elif isinstance(prototype_data, dict):
		for key, value in prototype_data.items():
			prototype = {}
			file_id = key[0][0].split("/")[-2]
			prototype['file_id'] = file_id #...
			prototype['start'] = key[0][1]
			prototype['end'] = key[0][2]
			prototype['measurement_time'] = prototype['start']+((prototype['end']-prototype['start'])*0.33)
			prototype['vowel'] = key[0][4]
			prototype['nformants'] = 5
			prototype['F1'] = value['F1']
			prototype['F2'] = value['F2']
			prototype['F3'] = value['F3']
			to_return.append(prototype)

	return to_return

def to_comparison_csv(pair_data):
	to_return = []
	for meta, values in pair_data.items():
		comparison = {}
		comparison['file_id'] = meta[0][0].split("/")[-2]
		comparison['start'] = meta[0][1]
		comparison['end'] = meta[0][2]
		comparison['measurement_time'] = comparison['start']+((comparison['end']-comparison['start'])*0.33)
		comparison['vowel'] = meta[0][4]
		comparison['nformants'] = meta[1]
		comparison['measuredF1'] = values[0]['F1']
		comparison['realF1'] = values[1][4]
		comparison['measuredF2'] = values[0]['F2']
		comparison['realF2'] = values[1][5]
		comparison['measuredF3'] = values[0]['F3']
		comparison['realF3'] = values[1][6]
		to_return.append(comparison)
	return to_return

def to_cov_csv(metadata):
	to_return = []
	for vowel, values in metadata.items():
		cov_dict = {}
		cov_dict['vowel'] = vowel
		cov_dict['F1mean'] = values[0][0]
		cov_dict['F2mean'] = values[0][1]
		cov_dict['F3mean'] = values[0][2]
		cov_dict['B1mean'] = values[0][3]
		cov_dict['B2mean'] = values[0][4]
		cov_dict['B3mean'] = values[0][5]

		cov_dict['F1F1cov'] = values[1][0][0]
		cov_dict['F1F2cov'] = values[1][0][1]
		cov_dict['F1F3cov'] = values[1][0][2]
		cov_dict['F1B1cov'] = values[1][0][3]
		cov_dict['F1B2cov'] = values[1][0][4]
		cov_dict['F1B3cov'] = values[1][0][5]

		cov_dict['F2F2cov'] = values[1][1][1]
		cov_dict['F2F3cov'] = values[1][1][2]
		cov_dict['F2B1cov'] = values[1][1][3]
		cov_dict['F2B2cov'] = values[1][1][4]
		cov_dict['F2B3cov'] = values[1][1][5]

		cov_dict['F3F3cov'] = values[1][2][2]
		cov_dict['F3B1cov'] = values[1][2][3]
		cov_dict['F3B2cov'] = values[1][2][4]
		cov_dict['F3B3cov'] = values[1][2][5]

		cov_dict['B1B1cov'] = values[1][3][3]
		cov_dict['B1B2cov'] = values[1][3][4]
		cov_dict['B1B3cov'] = values[1][3][5]

		cov_dict['B2B2cov'] = values[1][4][4]
		cov_dict['B2B3cov'] = values[1][4][5]

		cov_dict['B3B3cov'] = values[1][5][5]

		to_return.append(cov_dict)
	return to_return

def write_to_csv(metric, columns, data):
	now = datetime.now()
	clocktime = str(now.hour) + str(now.minute)
	date = str(now.year)+str(now.month)+str(now.day)+"_"+str(clocktime)

	with open(metric+'_benchmark'+date+'.csv', 'w+') as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=columns)
		writer.writeheader()
		for row in data:
			writer.writerow(row)


if __name__ == '__main__':
	audio_info = "/Users/mlml/Documents/transfer/Hillenbrand/bigdata.dat.txt"
	time_info = "/Users/mlml/Documents/transfer/Hillenbrand/timedata.dat.txt"
	corpus_dir = "/Users/mlml/Documents/transfer/Hillenbrand"
	corpus_name = "Hillenbrand"

	nIterations = 2
	remove_short = 0.05

	# Get algorithm data
	prototype, metadata, data, duration = get_algorithm_data(corpus_name, nIterations, remove_short)
	print("-------------")
	print("The algorithm took:", duration, "seconds.")
	print()
	print("Prototype data:")
	print(prototype)
	print()
	print("Algorithm data:")
	print(data)


	# Load in hand-checked data
	hand_checked = get_hand_formants(audio_info, time_info, corpus_dir)
	print("Hand-checked data:")
	print(hand_checked)


	# Make correspondence between algorithm and hand-checked data (find matching pairs)
	print(len(data), len(hand_checked))
	pairs, vowel_differences = get_pairs(data, hand_checked)
	print("PAIRS:")
	for pair1, pair2 in pairs.items():
		print({pair1 : pair2})


	# Get averages of error for each vowel class, for each value
	avg_error = get_avg_error(vowel_differences)
	print()
	print("Average errors per vowel:")
	print(avg_error)

	# Write to a file
	# Meta info about the pass
	meta_columns = ['Computer','Date','Corpus', 'Algorithm type:', 'Total time']
	dict_data = [{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': corpus_name, 'Algorithm type:': '1st pass FAVE-like', 'Total time': duration}]
	write_to_csv("meta", meta_columns, dict_data)

	# Prototype data
	prototype_columns = ['file_id', 'start', 'end', 'measurement_time', 'vowel', 'nformants', 'F1', 'F2', 'F3']
	prototype_csv = to_prototype_csv(prototype)
	write_to_csv("prototype", prototype_columns, prototype_csv)

	# Computed algorithm data
	algorithm_columns = ['file_id', 'start', 'end', 'measurement_time', 'vowel', 'nformants', 'measuredF1', 'realF1', 'measuredF2', 'realF2', 'measuredF3', 'realF3']
	alg_csv = to_comparison_csv(pairs)
	write_to_csv("comp", algorithm_columns, alg_csv)

	# Vowel avg error data
	avg_columns = ['Vowel instance', 'F1', 'F2', 'F3']
	avg_csv = data_to_csv_dict(avg_error)
	write_to_csv("vowelavg", avg_columns, avg_csv)

	# Mean and cov data
	cov_columns = cov_columns = ['vowel', 'F1mean', 'F2mean', 'F3mean', 'B1mean', 'B2mean', 'B3mean', 'F1F1cov', 'F1F2cov', 'F1F3cov', 'F1B1cov', 'F1B2cov', 'F1B3cov', 'F2F2cov', 'F2F3cov', 'F2B1cov', 'F2B2cov', 'F2B3cov', 'F3F3cov', 'F3B1cov', 'F3B2cov', 'F3B3cov', 'B1B1cov', 'B1B2cov', 'B1B3cov', 'B2B2cov', 'B2B3cov', 'B3B3cov']
	cov_csv = to_cov_csv(metadata)
	write_to_csv("cov", cov_columns, cov_csv)
