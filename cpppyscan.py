#! python2

from os import walk, path
from operator import itemgetter
import sys, getopt, re, argparse, threading, Queue, copy

parser = argparse.ArgumentParser(description='Do stuff with files.', prog='cpppyscan.py', usage='%(prog)s [-h, -r, -v, -z, -e <extension(s)>, -i <filename>, -o <filename>] -d|-f <directory|filename>', \
    formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=65, width =150))
group = parser.add_mutually_exclusive_group(required=True)
parser.add_argument("-i", "--infile", default="rules.txt", action='store_true', help="File for all regex rules. Default is 'rules.txt'")
parser.add_argument("-r", "--recursive", action='store_false', help="Do not recursively search all files in the given directory")
parser.add_argument("-v", "--verbose", action='store_true', help="Turn on (extremely) verbose mode")
parser.add_argument("-e", "--extension", nargs='?', default=None, help="filetype(s) to restrict search to. seperate lists via commas with no spaces")
parser.add_argument("-o", "--outfile", default="results.txt", nargs='?', help="specify output file. Default is 'results.txt'. NOTE: will overwrite file if it currently exists")
group.add_argument("-d", "--directory", default=None, help="directory to search")
group.add_argument("-f", "--file", default=None, help="file to search")
parser.add_argument("-t", "--threads", default=5)
parser.add_argument("-z", "--disableerrorhandling", action='store_true', help="disable error handling to see full stack traces on errors")
args = parser.parse_args()

tosearch = None
targettype = None
searchrules = None
extfilter = None
verbose = False
recursive = True
errorhandling = False
resultdict = {}
progresstracker = None
numthreads = 5
threads = []

def printline(str):
    global outfile
    with open(outfile, 'a') as f:
        f.write(str(str)+"\n")

def vprint(str):
    global verbose
    if verbose:
        print(str)

def main():
    global outfile,infile,tosearch,targettype,searchrules,extfilter,verbose,recursive,errorhandling,recursive,resultdict,numthreads,threads

    if args.infile:
        infile = args.infile

    with open(infile,'r') as f:
        searchrules = [l.strip() for l in f]

    for rule in searchrules:
        resultdict[rule] = []

    if args.outfile:
        outfile = args.outfile

    if args.threads:
        numthreads = int(args.threads)

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

    if errorhandling:
        start()
    else:
        try:
            start()
        except:
            print('[!] An error ocurred:\n')
            for e in sys.exc_info():
                print(e)
            print('[*] Note that this script may break on some filetypes when run with 3.4. Please use 2.7')
            try:
                progresstracker.done = True
                for t in threads:
                    t.done = True
            except:
                pass
           
def start():
    global tosearch,targettype,searchrules,progresstracker,numthreads,threads
            
    if targettype == 'd':
        print('[*] Enumerating all files to search...')
        files = findfiles(tosearch)
    else:
        files = [tosearch]

    print('[*] Files to check: %s'%len(files))

    progresstracker = Progress(len(files),len(searchrules))
    progresstracker.start()

    filequeue = Queue.Queue()
    resqueue = Queue.Queue()

    for f in files:
        filequeue.put(f)

    lock = threading.Lock()
    for i in range(numthreads):
        threads.append(Seeker(filequeue,resqueue,searchrules,progresstracker,lock,i))
        threads[i].start()

    while not arethreadsdone(threads):
        pass

    while not resqueue.empty():
        newdict = resqueue.get()
        for k,v in newdict.iteritems():
            resultdict[k].extend(v)

    progresstracker.done = True
    dumpresults()
    
def arethreadsdone(threads):
    for t in threads:
        if t.done == False:
            return False
    return True

def linecount(files):
    count = 0
    for file in files:
        with open(file,'r') as f:
            count += sum([1 for l in f])

    return count

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

def dumpresults():
    global outfile,resultdict

    with open(outfile,'w') as f:
        for key,values in resultdict.iteritems():
            f.write('%s\n'%key)
            for value in values:
                f.write('%s\n'%value)

class Seeker(threading.Thread):
    def __init__(self,filequeue,resqueue,searchrules,progresstracker,lock,id):
        threading.Thread.__init__(self)
        self.filequeue = filequeue
        self.resqueue = resqueue
        self.searchrules = copy.deepcopy(searchrules)
        self.progresstracker = progresstracker
        self.lock = lock
        self.done = False
        self.id = id

        self.resultdict = {}
        for rule in searchrules:
            self.resultdict[rule] = []

    def run(self):
        while not self.done and not self.filequeue.empty():
            try:
                self.searchfile(self.filequeue.get(timeout=0.1))
            except Queue.Empty:
                pass
        self.done = True

    def searchfile(self,file):
        self.cleardict()

        with open(file) as f:
            for rule in self.searchrules:
                self.linenum = 1
                f.seek(0)
                prog = re.compile(rule)
                for l in f:
                    if prog.search(l):
                        self.resultdict[rule].append('"%s","%s","%s"'%(file,self.linenum,l.strip()))
                    self.linenum += 1
                self.lock.acquire()
                self.progresstracker.checksdone += 1
                self.lock.release()
        self.resqueue.put(self.resultdict)

    def cleardict(self):
        for k,v in self.resultdict.iteritems():
            self.resultdict[k] = []

class Progress(threading.Thread):
    def __init__(self,numfiles,numrules):
        threading.Thread.__init__(self)
        self.numchecks = float(numfiles * numrules)
        self.checksdone = 0.0
        self.done = False

    def run(self):
        while not self.done:
            self.progress = self.checksdone / self.numchecks
            barLength = 20 # Modify this to change the length of the progress bar
            if isinstance(self.progress, int):
                self.progress = float(self.progress)
            if self.progress >= 1:
                self.progress = 1
            block = int(round(barLength*self.progress))
            text = "\r[{0}] {1:.2f}%".format( "#"*block + "-"*(barLength-block), self.progress*100)
            sys.stdout.write(text)
            sys.stdout.flush()

        print('\n')

if __name__ == "__main__":
    main()