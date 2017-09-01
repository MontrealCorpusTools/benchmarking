# Benchmarking VTR for formant analysis

### Configuration
Before running the benchmark, you need to set parameters in the code of the benchmarking script, `hillenbrand_benchmark.py`.

In line 9, change the path to where your PolyglotDB directory is located (making sure to keep the path pointed to the `acoustics` subfolder inside).

In line 20, change the path to where your `hand_formants.py` script is located (it should be located in the same directory as `hillenbrand_benchmark.py` if you pulled these scripts from GitHub).

Starting in line 244, there are a number of parameters for you to set:

* `audio_info` - set this to the absolute path of the location of ```bigdata.dat.txt```, which should be inside the directory where the Hillenbrand corpus data is stored.
* `time_info` - set this to the absolute path of the location of ```timedata.dat.txt```, which should be inside the directory where the Hillenbrand corpus data is stored.
* `corpus_dir` - set this to the absolute path of the directory where the Hillenbrand corpus data is stored.
* `nIterations` - set this to the number of times you would like the formant algorithm to iterate before returning values.
* `remove_short` - set this to the minimum length (in milliseconds) of segment that you would like the formant algorithm to analyze. Segments below this length will not be analyzed.


### Running the benchmark

First, make sure the server has been started by navigating to the root of the PolyglotDB directory and commanding:

`python3 bin/pgdb.py start`

Next, make sure that the corpus has been imported into PolyglotDB. If it has not, navigate back to the root of Hillenbrand benchmarking directory and command (after pointing the directories inside the code to your own directories, as detailed above):

`python3 import.py`

Then, benchmark the corpus by running the command:

`python3 hillenbrand_benchmark.py`

Finally, when finished, you can close the server by navigating again to the root of the PolyglotDB directory and commanding:

`python3 bin/pgdb.py stop`

(Depending on how PolyglotDB was installed, you may need to preface these commands with `sudo`.)

### Output

The benchmarking script will output 5 text CSV files to the benchmarking directory, with filenames containing their types and time of benchmarking. The 5 types are:

*  `meta_benchmark` - contains meta information about the pass (computer, date, time taken, algorithm type, etc.).
*  `prototype_benchmark` - contains measurements used to generate prototypes  (the "zeroth pass" of the algorithm); returns measured values with a fixed number of formants per vowel token as measured by Praat.
*  `cov_benchmark` - contains means of measurements and covariance matrices that constitute the prototypes per vowel class.
*  `comp_benchmark` - contains algorithm-computed "best" measurements per vowel token.
*  `vowelavg_benchmark` - contains the average disparities per vowel class between algorithm-computed data and gold standard data.
