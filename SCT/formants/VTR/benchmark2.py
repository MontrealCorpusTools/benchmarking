import os
import time
import logging
import platform
import csv
from datetime import datetime
import statistics
import sys
#sys.path.insert(0,"/Users/acoles/Documents/PolyglotDB-master-3/polyglotdb/acoustics")
sys.path.insert(0,"/Users/mlml/Documents/GitHub/PolyglotDB/polyglotdb/acoustics")
from formant import analyze_formants_vowel_segments_new, get_mean_SD, get_stdev, refine_formants, extract_formants_full

import polyglotdb.io as pgio

from polyglotdb import CorpusContext
from polyglotdb.config import CorpusConfig
from polyglotdb.acoustics.analysis import generate_phone_segments_by_speaker

from acousticsim.analysis.praat import run_script

#sys.path.insert(0,"/Users/acoles/Documents/Formants/")
sys.path.insert(0,"/Users/mlml/Documents/transfer/Formants/")
from hand_formants import get_hand_formants, get_mean


graph_db = ({'graph_host':'localhost', 'graph_port': 7474,
	'graph_user': 'neo4j', 'graph_password': 'test'})

VOWELS = ['iy', 'ih', 'eh', 'ey', 'ae', 'aa', 'aw', 'ay', 'ah', 'ao', 'oy', 'ow', 'uh', 'uw', 'ux', 'er', 'ax', 'ix', 'axr', 'ax-h']
#VOWELS = ['ih','iy','ah','uw','er','ay','aa','ae','eh','ow']

def WriteDictToCSV(csv_file,csv_columns,dict_data):
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
        return

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


def to_prototype_csv(prototype_data):
	to_return = []
	for item in prototype_data:
		print(item)
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
		prototype['B1'] = item['fields']['B1']
		prototype['B2'] = item['fields']['B2']
		prototype['B3'] = item['fields']['B3']
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
		comparison['realF1'] = values[1][0]
		comparison['measuredF2'] = values[0]['F2']
		comparison['realF2'] = values[1][1]
		comparison['measuredF3'] = values[0]['F3']
		comparison['realF3'] = values[1][2]
		comparison['measuredB1'] = values[0]['B1']
		comparison['realB1'] = values[1][3]
		comparison['measuredB2'] = values[0]['B2']
		comparison['realB2'] = values[1][4]
		comparison['measuredB3'] = values[0]['B3']
		comparison['realB3'] = values[1][5]
		to_return.append(comparison)
	return to_return


def data_to_csv_dict(data):
	to_return = []
	for vowel, formants in data.items():
		vowel_dict = {}
		vowel_dict['Vowel instance'] = vowel
		if isinstance(formants, dict):
			vowel_dict['F1'] = formants['F1']
			vowel_dict['F2'] = formants['F2']
			vowel_dict['F3'] = formants['F3']
			vowel_dict['B1'] = formants['B1']
			vowel_dict['B2'] = formants['B2']
			vowel_dict['B3'] = formants['B3']
		else:
			vowel_dict['F1'] = formants[0]
			vowel_dict['F2'] = formants[1]
			vowel_dict['F3'] = formants[2]
			vowel_dict['B1'] = formants[3]
			vowel_dict['B2'] = formants[4]
			vowel_dict['B3'] = formants[5]
		to_return.append(vowel_dict)
	return to_return

def clean_algorithm_data(data):
	clean_data = {}
	for key, value in data.items():
		formants_bandwidths = []
		for key2, value2 in data[key].items():
			for key3, value3 in data[key][key2].items():
				formants_bandwidths.append(data[key][key2][key3]['F1'])
				formants_bandwidths.append(data[key][key2][key3]['F2'])
				formants_bandwidths.append(data[key][key2][key3]['F3'])
				formants_bandwidths.append(data[key][key2][key3]['B1'])
				formants_bandwidths.append(data[key][key2][key3]['B2'])
				formants_bandwidths.append(data[key][key2][key3]['B3'])
				break
			break
		clean_data[key] = formants_bandwidths
	return clean_data

def get_average_hand_checked(hand_checked_list):
	averaged_hand_checked = {}
	for vowel in VOWELS:
		f1, f2, f3, b1, b2, b3 = [], [], [], [], [] ,[]
		for hand_checked in hand_checked_list:
			if vowel in hand_checked and hand_checked[vowel] != [None, None, None, None, None, None]:
				f1.append(float(hand_checked[vowel][0]))
				f2.append(float(hand_checked[vowel][1]))
				f3.append(float(hand_checked[vowel][2]))
				b1.append(hand_checked[vowel][3])
				b2.append(hand_checked[vowel][4])
				b3.append(hand_checked[vowel][5])
		F1, F2, F3, B1, B2, B3 = get_mean(f1), get_mean(f2), get_mean(f3), get_mean(b1), get_mean(b2), get_mean(b3)
		if vowel in hand_checked and hand_checked[vowel] != [None, None, None, None, None, None]:
			formants = [F1, F2, F3, B1, B2, B3]
			averaged_hand_checked[vowel] = formants
	return averaged_hand_checked

if __name__ == '__main__':
	# Get algorithm data
	corpus_name = 'VTRSubset'

	beg = time.time()
	with CorpusContext(corpus_name, **graph_db) as g:
		prototype, metadata, data = extract_formants_full(g, VOWELS)
	end = time.time()
	duration = end - beg
	print("-------------")
	print("The algorithm took:", duration, "seconds.")
	print()
	print("Prototype data:")
	print(prototype)
	print()
	print("Prototype metadata:")
	print(metadata)
	print("Algorithm data:")
	print(data)

	# Load in hand-checked comparison data and clean it
	clean_hand_checked = {}
	#corpus_dir = '/Volumes/data/datasets/sct_benchmarks/' + corpus_name
	corpus_dir = '/Users/mlml/Documents/transfer/' + corpus_name
	hand_checked_list = []
	for root, dirs, files in os.walk(corpus_dir):
		for file in files:
			if file.endswith(".txt"):
				file_id = file.split(".")[0]
				formant_file = root + "/" + file
				phone_file = root + "/" + file_id + ".phn"
				speaker = phone_file.split("/")[-2]
				file_id = speaker + "_" + file_id
				hand_checked = get_hand_formants(formant_file, phone_file)
				for item in hand_checked:
					meta = (file_id, item[0], item[1], item[2])		# (file, start, end, vowel)
					clean_hand_checked[meta] = item[3]

	print()
	print("Hand-checked data:")
	print(clean_hand_checked)


	# Make correspondence between algorithm and hand-checked data (find matching pairs)
	pairs = {}
	vowel_differences = {}
	for alg_point, values in data.items():
		f1_delta, f2_delta, f3_delta, b1_delta, b2_delta, b3_delta = 0, 0, 0, 0, 0, 0
		for hand_point, values2 in clean_hand_checked.items():
			smallest_diff = float('inf')
			if hand_point[0] in alg_point[0][0] and hand_point[3] in alg_point[0][4]:		# If file names and vowels match
				beg_diff = abs(hand_point[1] - alg_point[0][1])
				if beg_diff < smallest_diff:
					smallest_diff = beg_diff
					formants = values2
					f1_delta = abs(values2[0] - values['F1'])
					f2_delta = abs(values2[1] - values['F2'])
					f3_delta = abs(values2[2] - values['F3'])
					try:
						b1_delta = abs(float(values2[3] - values['B1']))
					except:
						b1_delta = "undef"
					try:
						b2_delta = abs(float(values2[4] - values['B2']))
					except:
						b2_delta = "undef"
					try:
						b3_delta = abs(float(values2[5] - values['B3']))
					except:
						b3_delta = "undef"
					pair = [values, values2]
		if [f1_delta, f2_delta, f3_delta, b1_delta, b2_delta, b3_delta] == [0, 0, 0, 0, 0, 0]:
			continue
		else:
			pairs[alg_point] = pair
			vowel_differences[alg_point] = [f1_delta, f2_delta, f3_delta, b1_delta, b2_delta, b3_delta]

	print()
	"""print("PAIRS:", pairs)
	print()"""
	print("Deltas (absolute distance):")
	print(vowel_differences)


	# Get averages of error for each vowel class, for each value
	avg_error = {}
	for meta, values in vowel_differences.items():
		vowel_class = meta[0][-1]
		if vowel_class not in avg_error:
			avg_error[vowel_class] = {}
			avg_error[vowel_class]['F1'] = []
			avg_error[vowel_class]['F2'] = []
			avg_error[vowel_class]['F3'] = []
			avg_error[vowel_class]['B1'] = []
			avg_error[vowel_class]['B2'] = []
			avg_error[vowel_class]['B3'] = []
		avg_error[vowel_class]['F1'].append(values[0])
		avg_error[vowel_class]['F2'].append(values[1])
		avg_error[vowel_class]['F3'].append(values[2])
		avg_error[vowel_class]['B1'].append(values[3])
		avg_error[vowel_class]['B2'].append(values[4])
		avg_error[vowel_class]['B3'].append(values[5])

	#print("intermediate:", avg_error)
	for vowel_class, values in avg_error.items():
		values['F1'] = get_mean(values['F1'])
		values['F2'] = get_mean(values['F2'])
		values['F3'] = get_mean(values['F3'])
		values['B1'] = get_mean(values['B1'])
		values['B2'] = get_mean(values['B2'])
		values['B3'] = get_mean(values['B3'])

	print()
	print("Average errors per vowel:")
	print(avg_error)




	# Write to a file
	csv_columns = ['Computer','Date','Corpus', 'Algorithm type', 'Total time']
	dict_data = [{'Computer': platform.node(), 'Date': str(datetime.now()), 'Corpus': corpus_name, 'Algorithm type': '1st pass FAVE-like', 'Total time': duration}]

	prototype_columns = ['file_id', 'start', 'end', 'measurement_time', 'vowel', 'nformants', 'F1', 'F2', 'F3', 'B1', 'B2', 'B3']
	algorithm_columns = ['Vowel instance', 'F1', 'F2', 'F3', 'B1', 'B2', 'B3']
	avg_columns = ['Vowel class', 'F1', 'F2', 'F3', 'B1', 'B2', 'B3']

	comparison_columns = ['file_id', 'start', 'end', 'measurement_time', 'vowel', 'nformants', 'measuredF1', 'realF1', 'measuredF2', 'realF2', 'measuredF3', 'realF3', 'measuredB1', 'realB1', 'measuredB2', 'realB2', 'measuredB3', 'realB3']
	cov_columns = ['vowel', 'F1mean', 'F2mean', 'F3mean', 'B1mean', 'B2mean', 'B3mean', 'F1F1cov', 'F1F2cov', 'F1F3cov', 'F1B1cov', 'F1B2cov', 'F1B3cov', 'F2F2cov', 'F2F3cov', 'F2B1cov', 'F2B2cov', 'F2B3cov', 'F3F3cov', 'F3B1cov', 'F3B2cov', 'F3B3cov', 'B1B1cov', 'B1B2cov', 'B1B3cov', 'B2B2cov', 'B2B3cov', 'B3B3cov']

	prototype_csv = to_prototype_csv(prototype)
	algorithm_csv = data_to_csv_dict(data)
	hand_csv = data_to_csv_dict(clean_hand_checked)
	delta_csv = data_to_csv_dict(vowel_differences)
	comparison_csv = to_comparison_csv(pairs)
	avgerr_csv = data_to_csv_dict(avg_error)
	cov_csv = to_cov_csv(metadata)

	currentPath = os.getcwd()

	now = datetime.now()
	clocktime = str(now.hour) + str(now.minute)
	date = str(now.year)+str(now.month)+str(now.day)+"_"+str(clocktime)
	csv_file = 'benchmark'+date+'.csv'

	# Writes metadata of the pass
	with open('meta_benchmark'+date+'.csv', 'w+') as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
		writer.writeheader()
		writer.writerow(dict_data[0])
		csv_file.write("\n")

	with open('prototype_benchmark'+date+'.csv', 'w+') as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=prototype_columns)
		writer.writeheader()
		for row in prototype_csv:
			writer.writerow(row)

	with open('comp_benchmark'+date+'.csv', 'w+') as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=comparison_columns)
		writer.writeheader()
		for row in comparison_csv:
			writer.writerow(row)

	with open('vowelavg_benchmark'+date+'.csv', 'w+') as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=algorithm_columns)
		writer.writeheader()
		for row in avgerr_csv:
			writer.writerow(row)

	with open('cov_benchmark'+date+'.csv', 'w+') as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=cov_columns)
		writer.writeheader()
		for row in cov_csv:
			writer.writerow(row)
