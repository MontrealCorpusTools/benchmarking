import os
import sys
import re
from textgrid import TextGrid, IntervalTier
from scipy.io import wavfile

wav_dir = sys.argv[1]
output_dir = sys.argv[2]
time_data = sys.argv[3]

# Function to get length of a wav file
def getWavLength(wav, wavDir):
	sampFreq, snd = wavfile.read(os.path.join(wavDir, wav))
	bit = 0
	if snd.dtype == "int16":
		bit = 15
	elif snd.dtype == "int32":
		bit = 31
	snd = snd / float((2.**bit))
	duration = snd.shape[0] / float(sampFreq) # Returns in milliseconds
	return duration


if __name__ == '__main__':
	for file in os.listdir(wav_dir):
		if file.endswith(".wav"):
			print("Processing", file, "...")
			file_id = file.split(".")[0]
			speaker = file_id[:-2]
			duration = getWavLength(file, wav_dir)
			vowel = file_id[-2:]
			word = "h" + vowel + "d"
			tg = TextGrid(maxTime=duration)  # Make a textgrid
		else:
			continue

		# Get the timeframe for the vowel
		with open(time_data, 'r') as times:
			time_list = times.readlines()[6:]
			for line in time_list:
				line_split = line.split()
				#print(line_split[0], file_id)
				if line_split[0] in file_id:
					start = float(line_split[1])/1000
					end = float(line_split[2])/1000
					break
				else:
					continue

		# Make word and speaker tiers
		intervalTiers = {}

		word_name = speaker + " - words"
		word_tier = IntervalTier(word_name, 0, duration)
		intervalTiers[word_name] = word_tier
		intervalTiers[word_name].add(0, duration, word)

		phone_name = speaker + " - phones"
		phone_tier = IntervalTier(phone_name, 0, duration)
		intervalTiers[phone_name] = phone_tier
		intervalTiers[phone_name].add(0, start, "h")
		intervalTiers[phone_name].add(start, end, vowel)
		intervalTiers[phone_name].add(end, duration, "d")

		for key, value in intervalTiers.items():
			tg.append(value)

		export_name = file_id + ".TextGrid"
		tg.write(os.path.join(output_dir, export_name))
