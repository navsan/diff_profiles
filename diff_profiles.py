#!/usr/bin/env python

from DotFileParser import DotFileParser
from DotFileCombiner import DotFileCombiner
from CombinedDotFileWriter import CombinedDotFileWriter

import re
import sys, getopt

default_output_filename = 'diff.dot'
default_diff_attribute = 'cumulative_percentage'
default_diff_threshold = 5

def print_usage(script_name):
  print 'Usage:', script_name, 'infile1.dot infile2.dot [-o outfile.dot] [-d cumulative_percentage] [-t 5]'
  print 'infile1.dot and infile2.dot are the two input files to be compared'
  print '    -o : output file name. Default is', default_output_filename
  print '    -d : Which attribute to use for coloring nodes. Default', default_diff_attribute
  print '    -t : Diff threshold for full red and full green used for coloring nodes. Default', default_diff_threshold
  sys.exit(1)

def process_cmd_args(argv):
  output_filename = default_output_filename
  diff_attr = default_diff_attribute
  diff_thresh = default_diff_threshold
  if len(argv) < 3:
    print_usage(argv[0])
  myopts, args = getopt.getopt(argv[3:], "o:d:t")
  for o, a in myopts:
    if o == '-o':
      output_filename = a
    elif o == '-d':
      diff_attr = a
    elif o == '-t':
      diff_threshold = a
    else:
      print_usage(argv[0])
  return argv[1], argv[2], output_filename, diff_attr, diff_thresh

def main():
  infile1, infile2, outfile, diff_attr, thresh =  process_cmd_args(sys.argv)
  parser = DotFileParser()
  dot1 = parser.get_parsed_dot_file(infile1)
  dot2 = parser.get_parsed_dot_file(infile2)

  combiner = DotFileCombiner(outfile)
  dot = combiner.get_combined_dot(dot1, dot2)
  
  writer = CombinedDotFileWriter(dot, diff_attr, thresh)
  writer.print_dot_file()

if __name__ == "__main__":
  main()



