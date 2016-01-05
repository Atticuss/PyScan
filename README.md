# CPPPyScan
Quick and dirty regex scanner for dangerous C++ code

# Usage
	python cpppyscan.py [-h, -r, -v, -z, -e <extension(s)>, -i <filename>, -o <filename>] -d|-f <directory|filename>

# Args

	optional arguments:
	  -h, --help                               show this help message and exit
	  -i, --infile                             File for all regex rules. Default is 'rules.txt'
	  -r, --recursive                          Do not recursively search all files in the given directory
	  -v, --verbose                            Turn on (extremely) verbose mode
	  -e [EXTENSION], --extension [EXTENSION]  filetype(s) to restrict search to. seperate lists via commas with no spaces
	  -o [OUTFILE], --outfile [OUTFILE]        specify output file. Default is 'results.csv'. NOTE: will overwrite file if it currently exists
	  -d DIRECTORY, --directory DIRECTORY      directory to search
	  -f FILE, --file FILE                     file to search
	  -t THREADS, --threads THREADS
	  -z, --disableerrorhandling               disable error handling to see full stack traces on errors

