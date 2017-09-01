import sys
import os
import math
from random import randint
from statistics import mean
import chardet

# TIMIT has 16000 sampling/frame rate
# .phn files are in units of 1/16000 of a second
# From VTR documentation: "The left column shows the frame number (10 msec each)"
# Let's work in seconds - easier to keep straight

VOWELS = ['iy', 'ih', 'eh', 'ey', 'ae', 'aa', 'aw', 'ay', 'ah', 'ao', 'oy', 'ow', 'uh', 'uw', 'ux', 'er', 'ax', 'ix', 'axr', 'ax-h']

def get_mean(data):
	avg = 0
	data[:] = [x for x in data if x != "undef"]
	data = list(filter(None, data))

	if len(data) > 1:
		avg = mean(data)
	elif len(data) == 1:	# Return the one number
		avg = data[0]
	else:
		avg = None
	return avg

"""def convert_encoding(f, encoding=None, min_confidence=0.5):
    #Return the contents of 'filename' as unicode, or some encoding.
    text = f.read()
    guess = chardet.detect(text)
    if guess["confidence"] < min_confidence:
        raise UnicodeDecodeError
    text = unicode(text, guess["encoding"])
    if encoding is not None:
        text = text.encode(encoding)
    return text"""

def get_hand_formants(formant_file, phone_file):
	with open(formant_file, 'r') as formants_by_frame:
		#formants_by_frame_text = convert_encoding(formants_by_frame)
		#formant_raw = formants_by_frame_text.split("\n")
		formant_raw = formants_by_frame.readlines()
		formant_info = []
		for index, line in enumerate(formant_raw):
			start_time = float(index) * (float(10)/float(1000))			# Each frame is 10msec, then get in sec
			end_time = start_time + (float(10)/float(1000))
			start_end = [start_time, end_time]
			line = line.strip().split(" ")
			line = list(filter(None, line))
			to_append = [start_end, line]
			formant_info.append(to_append)

	with open(phone_file, 'r') as phones_by_time:
		#phone_raw_text = convert_encoding(phones_by_time)
		#phone_raw = phone_raw_text("\n")
		phone_raw = phones_by_time.readlines()
		phone_info = []
		for line in phone_raw:
			line = line.split(" ")
			phone_info.append(line)

	num_frames = len(formant_info)	# Each is 10msec
	duration_msec = num_frames * 10
	duration_sec = duration_msec / 1000

	# Get a dictionary of {vowel_instance: [start_time, end_time]}
	vowel_times = {}
	for vowel in VOWELS:
		for line in phone_info:
			if vowel in line[2]:
				start_time = float(line[0]) / 16000
				end_time = float(line[1]) / 16000
				start_end = [start_time, end_time]

				counter = 1
				vowel_instance = vowel + str(counter)
				while vowel_instance in vowel_times:
					counter = counter + 1
					vowel_instance = vowel + str(counter)
				vowel_times[vowel_instance] = start_end

	# Get frames that fall within each vowel's time from the formant data
	vowel_instance_formants = []
	vowel_formants = []
	for vowel_instance in vowel_times:
		frames = []
		vowel_start = vowel_times[vowel_instance][0]
		vowel_end = vowel_times[vowel_instance][1]
		for line in formant_info:
			formant_start = line[0][0]
			formant_end = line[0][1]
			#print("formant start", formant_start, "formant end", formant_end)
			#print("vowel start", vowel_start, "vowel end", vowel_end)
			if formant_start >= vowel_start and formant_end <= vowel_end:
				frames.append(line)

		# Get frame that's closest to 1/3 of the way through
		#print("frames:", frames)
		if not frames:
			print("Error with this corpus file:", formant_file, phone_file)
			continue
		whole_vowel_start = frames[0][0][0]
		whole_vowel_end = frames[-1][0][0]
		third = whole_vowel_start + (float(whole_vowel_end - whole_vowel_start) / float(3))
		smallest_diff = float('inf')
		for frame in frames:
			diff = abs(third - frame[0][0])
			if diff < smallest_diff:
				smallest_diff = diff
				closest_to_third = frame

		# Get formants
		F1 = float(frame[1][0]) * 1000		# In Hz
		F2 = float(frame[1][1]) * 1000
		F3 = float(frame[1][2]) * 1000
		B1 = get_log(float(frame[1][3]) * 1000)
		B2 = get_log(float(frame[1][4]) * 1000)
		B3 = get_log(float(frame[1][5]) * 1000)
		formants = [F1, F2, F3, B1, B2, B3]

		# Make new list: [start, end, vowel, F1, F2, F3, B1, B2, B3]
		vowel_instance_formants = [whole_vowel_start, whole_vowel_end, vowel_instance.strip('0123456789'), formants]
		"""if abs(whole_vowel_end - whole_vowel_start) <= 0.07:	# Magic number - consult later
			#print("too short")
			continue
		else:"""
		vowel_formants.append(vowel_instance_formants)

	return vowel_formants

def get_log(number):
	try:
		logged = math.log(number)
	except:
		logged = "undef"
	return logged

def get_speaker_formants(speaker_dir):
	utterance_list = []
	for file in os.listdir(speaker_dir):
		if file.endswith(".phn"):
			phone_file = file
			formant_file = phone_file.split(".")[0] + ".txt"
			phone_path = speaker_dir + "/" + phone_file
			formant_path = speaker_dir + "/" + formant_file
			toAppend = get_hand_formants(formant_path, phone_path)
			utterance_list.append(toAppend)

	mean_formants_per_speaker = {}

	for vowel in VOWELS:
		print(vowel)
		vowel_f1, vowel_f2, vowel_f3 = [], [], []
		for utterance in utterance_list:
			for vowels, formants in utterance.items():
				if vowels == vowel:
					vowel_f1.append(formants[0])
					vowel_f2.append(formants[1])
					vowel_f3.append(formants[2])

		f1_mean = get_mean(vowel_f1)
		f2_mean = get_mean(vowel_f2)
		f3_mean = get_mean(vowel_f3)
		mean_formants = [f1_mean, f2_mean, f3_mean]
		mean_formants_per_speaker[vowel] = mean_formants

	return mean_formants_per_speaker


if __name__ == '__main__':	# Testing
	formant_file = "/Volumes/data/datasets/sct_benchmarks/VTRFormants/Test/dr1/felc0/si756.txt"
	phone_file = "/Volumes/data/datasets/sct_benchmarks/VTRFormants/Test/dr1/felc0/si756.phn"

	#print(get_hand_formants(formant_file, phone_file))

	speaker_dir = "/Volumes/data/datasets/sct_benchmarks/VTRFormants/Test/dr1/felc0/"

	print(get_speaker_formants(speaker_dir))
