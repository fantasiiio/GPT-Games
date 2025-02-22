# coding: utf-8

# lsprofcalltree.py: lsprof output which is readable by kcachegrind
# David Allouche
# Jp Calderone & Itamar Shtull-Trauring
# Johan Dahlin
# Sébastien Boisgérault

from __future__ import print_function

import optparse
import os
import sys

try:
    import cProfile
except ImportError:
    raise SystemExit("This script requires cProfile from Python 2.5")

def label(code):
    """
    Get label string for a code object.
    
    Arguments:
      code: Code object
    
    Returns:
      Label string  
    
    """
    if isinstance(code, str):
        return ('~', 0, code)    # built-in functions ('~' sorts at the end)
    else:
        return '%s %s:%d' % (code.co_name,
                             code.co_filename,
                             code.co_firstlineno)

class KCacheGrind(object):
    """
    KCacheGrind class to handle profiling data and output it in KCacheGrind format.
    
    Attributes:
      data: Profiling data
      out_file: Output file object
    
    """
    def __init__(self, profiler):
        """
        Initialize the KCacheGrind object.
        
        Arguments:
          profiler: Profiler object containing profiling data
        
        """
        self.data = profiler.getstats()
        self.out_file = None

    def output(self, out_file):
        """
        Output the profiling data to a file in KCacheGrind format.
        
        Arguments:
          out_file: File object to write output to
        
        """
        self.out_file = out_file
        print(u'events: Ticks', file=out_file)
        self._print_summary()
        for entry in self.data:
            self._entry(entry)

    def _print_summary(self):
        max_cost = 0
        for entry in self.data:
            totaltime = int(entry.totaltime * 1000)
            max_cost = max(max_cost, totaltime)
        print(u'summary: %d' % (max_cost,), file=self.out_file) 

    def _entry(self, entry):
        """
        Print profiling data for a single entry.
        
        Arguments:
          entry: Profiling entry
        
        """
        out_file = self.out_file

        code = entry.code
        #print(u'ob=%s' % (code.co_filename,), file=out_file)
        if isinstance(code, str):
            print(u'fi=~', file=out_file)
        else:
            print(u'fi=%s' % (code.co_filename,), file=out_file)
        print(u'fn=%s' % (label(code),), file=out_file)

        inlinetime = int(entry.inlinetime * 1000)
        if isinstance(code, str):
            if sys.version_info < (3, 0):
                inlinetime = unicode(inlinetime)
            print(u'0 ', inlinetime, file=out_file)
        else:
            print(u'%d %d' % (code.co_firstlineno, inlinetime), file=out_file)

        # recursive calls are counted in entry.calls
        if entry.calls:
            calls = entry.calls
        else:
            calls = []

        if isinstance(code, str):
            lineno = 0
        else:
            lineno = code.co_firstlineno

        for subentry in calls:
            self._subentry(lineno, subentry)
        print(u'', file=out_file)

    def _subentry(self, lineno, subentry):
        """
        Print profiling data for a subentry. 
        
        Arguments:
          lineno: Line number
          subentry: Subentry profiling data
        
        """
        out_file = self.out_file
        code = subentry.code
        #print(u'cob=%s' % (code.co_filename,), file=out_file)
        print(u'cfn=%s' % (label(code),), file=out_file)
        if isinstance(code, str):
            print(u'cfi=~', file=out_file)
            print(u'calls=%d 0' % (subentry.callcount,), file=out_file)
        else:
            print(u'cfi=%s' % (code.co_filename,), file=out_file)
            print(u'calls=%d %d' % (
                subentry.callcount, code.co_firstlineno), file=out_file)

        totaltime = int(subentry.totaltime * 1000)
        print(u'%d %d' % (lineno, totaltime), file=out_file)

def main(args):
    """
    Main function to run profiling and output KCacheGrind data.
    
    Arguments:
      args: Command line arguments
    
    """
    usage = "%s [-o output_file_path] scriptfile [arg] ..."
    parser = optparse.OptionParser(usage=usage % sys.argv[0])
    parser.allow_interspersed_args = False
    parser.add_option('-o', '--outfile', dest="outfile",
                      help="Save stats to <outfile>", default=None)

    if not sys.argv[1:]:
        parser.print_usage()
        sys.exit(2)

    options, args = parser.parse_args()

    if not options.outfile:
        options.outfile = '%s.log' % os.path.basename(args[0])

    sys.argv[:] = args

    prof = cProfile.Profile()
    try:
        try:
            with open(sys.argv[0], 'r') as f:
                code = f.read()
                prof = prof.run(f"exec({repr(code)})")
        except SystemExit:
            pass
    finally:
        kg = KCacheGrind(prof)
        try:
            out_file = open(options.outfile, 'w', encoding='utf-8') 
        except TypeError:
            out_file = open(options.outfile, 'w') 
        kg.output(out_file)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
