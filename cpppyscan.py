#! python2

from os import walk, path
from operator import itemgetter
import sys, getopt, re, argparse

parser = argparse.ArgumentParser(description='Do stuff with files.', prog='cpppyscan.py', usage='%(prog)s [-h, -r, -v, -z, -e <extension(s)>, -i <filename>, -o <filename>] -d|-f <directory|filename>', \
    formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=65, width =150))
group = parser.add_mutually_exclusive_group(required=True)
parser.add_argument("-i", "--infile", action='store_true', help="File for all regex rules. Default is 'rules.txt'")
parser.add_argument("-r", "--recursive", action='store_false', help="Do not recursively search all files in the given directory")
parser.add_argument("-v", "--verbose", action='store_true', help="Turn on (extremely) verbose mode")
parser.add_argument("-e", "--extension", nargs='?', default=None, help="filetype(s) to restrict search to. seperate lists via commas with no spaces")
parser.add_argument("-o", "--outfile", nargs='?', default=None, help="specify output file. Default is 'results.txt'. NOTE: will overwrite file if it currently exists")
group.add_argument("-d", "--directory", default=None, help="directory to search")
group.add_argument("-f", "--file", default=None, help="file to search")
parser.add_argument("-z", "--disableerrorhandling", action='store_true', help="disable error handling to see full stack traces on errors")
args = parser.parse_args()

outfile = 'results.txt'
infile = 'rules.txt'
tosearch = None
targettype = None
searchrules = None
extfilter = None
verbose = False
recursive = True
errorhandling = False
resultdict = {}

lcount = 0
fcount = 0
rcount = 0

def printline(str):
    global outfile
    with open(outfile, 'a') as f:
        f.write(str(str)+"\n")

def vprint(str):
    global verbose
    if verbose:
        print(str)

def main():
    global outfile,infile,tosearch,targettype,searchrules,extfilter,verbose,recursive,errorhandling,recursive,resultdict

    if args.infile:
        infile = args.infile

    with open(infile,'r') as f:
        searchrules = [l for l in f]

    for rule in searchrules:
        resultdict[rule] = []

    if args.outfile:
        outfile = args.outfile

    try:
        tosearch = args.directory
        targettype = 'd'
    except:
        tosearch = args.file
        targettype = 'f'
            
    try:
        extfilter = args.extension.split(',')
        for i,e in enumerate(extfilter):
            if e[0] == '.':
                extfilter[i] = e[1:]
    except:
        extfilter = []

    recursive = args.recursive
    verbose = args.verbose

    errorhandling = args.disableerrorhandling

    if (((type != None) and (tosearch != None)) or linecount or typecount):
        if errorhandling:
            start()
        else:
            try:
                start()
            except:
                printline('[!] An error ocurred:\n')
                for e in sys.exc_info():
                    printline(e)
                printline('[*] Note that this script may break on some filetypes when run with 3.4. Please use 2.7')
    elif help != 1:
            print('USAGE:\tcpppyscan.py [-h, -r, -v, -p, -c, -t, -z, -l, -e <extension(s)>, -o <filename>, -s <searchterm>] -d|-f <directory|filename>')
            
def start():
    global tosearch,targettype,lcount,rcount,fcount
             
    #Determine appropriate search
    if targettype == 'd':
        for f in findfiles(tosearch):
            searchfile(f)
    elif targettype == 'f':
        searchfile(tosearch)
    dumpresults()
    
    #Print appropriate results
    #printline('[*] Search complete. %s lines searched across %s files with %s occurrences found.' % (prettynumbers(lcount), prettynumbers(fcount), prettynumbers(rcount)))

def findfiles(dir):
    global recursive,extfilter
    flist = []

    for (dirpath,dirname,filenames) in walk(dir):
        flist.extend(['%s/%s'%(dirpath,filename) for filename in filenames])
        if not recursive:
            break

    if len(extfilter) > 0:
        flist2 = []
        for f in flist:
            if f.split('.')[-1] in extfilter:
                flist2.append(f)

    try:
        return flist2
    except:
        return flist

def searchfile(file):
    global searchrules,resultdict

    with open(file) as f:
        for rule in searchrules:
            prog = re.compile(rule)
            linenum = 1
            for l in f:
                if prog.search(l):
                    resultdict[rule].append('%s,%s,%s'%(file,linenum,l.strip()))
                linenum += 1

def dumpresults():
    global outfile,resultdict

    with open(outfile,'w') as f:
        for key,values in resultdict.iteritems():
            f.write('%s\n'%key)
            for value in values:
                f.write('%s\n'%value)

if __name__ == "__main__":
    main()