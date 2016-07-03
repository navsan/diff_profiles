from ParsedDotFile import ParsedDotFile
import re

class DotFileParser:
  patterns = {
    'node_name'   : r'(N[0-9]+)',                  #'N1' or 'N25'
    'fn_name'     : r'([\w\\_+*\-/%\(\)\[\]~]+)',  #'_ZN9quickstep24Worker\nexecute'
    'percentage'  : r'\(([0-9]+[\.]?[0-9]+)\%\)',  #'(0.0%)' or '(38.7%)'
    'num_samples' : r'([0-9]+)',                   #'0' or '1392'
    'file_path'   : r'([\w\-\./]+)',               #'/home/nav/file12_3.txt
  }
 
  def __init__(self):
    pass
  
  def get_parsed_dot_file(self, filename):
    self.dot = ParsedDotFile(filename)
    self.parse_dot_file(filename)
    return self.dot

  '''Parse the Dot file. File format is assumed to be the following.
  digraph line
  node header line
  Legend line
  node lines ...
  edge lines ...
  end line'''
  def parse_dot_file(self, filename):
    lines = self.open_file(filename)
    line = lines.next()
    assert self.parse_digraph_line(line), 'Parse failed at: ' + line
    line = lines.next()
    assert self.parse_node_header_line(line), 'Parse failed at: ' + line
    line = lines.next()
    assert self.parse_legend_line(line), 'Parse failed at: ' + line
    line = lines.next()
    while self.parse_node_line(line):
      line = lines.next()
    while self.parse_edge_line(line):
      line = lines.next()
    assert self.parse_end_line(line), 'Parse failed at: ' + line

  def open_file(self, filename):
    with open(filename,'r') as f:
      for line in f:
        yield line

  def parse_digraph_line(self, line):
    # eg: digraph "/users/navsan/quickstep/build-master-profile/quickstep_cli_shell; 1094 samples" {
    matches = DotFileParser.regex_match('^digraph[.]*', line)
    if matches:
      self.dot.digraph = {
        'line': line,
      }
      return True
    return False

  def parse_node_header_line(self, line):
    #eg: node [width=0.375,height=0.25];
    matches = DotFileParser.regex_match('^node', line)
    if matches:
      self.dot.node_header = {
        'line': line,
      }
      return True
    return False

  def parse_legend_line(self, line):
    #eg: Legend [shape=box,fontsize=24,shape=plaintext,label="/users/navsan/quickstep/build-master-profile/quickstep_cli_shell\lTotal samples: 1094\lFocusing on: 1094\lDropped nodes with <= 5 abs(samples)\lDropped edges with <= 1 samples\l"]; 
    matches = DotFileParser.regex_match(
      r'^Legend \[([\w=,]*),label="{file_path}\\l'
      r'Total samples: {num_samples}\\l([^"\];]*)"];', line)
    if matches:
      groups = matches.groups()
      self.dot.legend = {
        'stuff_before': groups[0],
        'executable' : groups[1],
        'total_samples' : int(groups[2]),
        'stuff_after': groups[3],
        'line' : line,
      }
      return True
    return False

  def parse_node_line(self, line):
    # eg: N5 [label="quickstep\nWorker\nrun\n0 (0.0%)\rof 1058 (96.7%)\r",shape=box,fontsize=8.0];
    matches = DotFileParser.regex_match(
      r'{node_name} \[label="{fn_name}\\n{num_samples} '
      r'{percentage}\\rof {num_samples} {percentage}\\r",([^\];]*)];', line)
    if matches:
      groups = matches.groups()
      node_id = groups[0]
      fn_name = groups[1]
      self.dot.nodes[fn_name] = {
        'node_id' : node_id,
        'local_samples' : int(groups[2]),
        'local_percentage' : float(groups[3]),
        'cumulative_samples': int(groups[4]),
        'cumulative_percentage' : float(groups[5]),
        'stuff_after': groups[6],
        'line': line,
      }
      # Reverse mapping. Useful for handling edges.
      self.dot.fn_names[node_id] = fn_name
      return True
    # If the local time is the same as the cumulative time, it's not printed:  
    # eg: N18 [label="envz_strip\n155 (14.2%)\r",shape=box,fontsize=26.8];
    matches = DotFileParser.regex_match(
      r'{node_name} \[label="{fn_name}\\n{num_samples} '
      r'{percentage}\\r",([^\];]*)];', line)
    if matches:
      groups = matches.groups()
      node_id = groups[0]
      fn_name = groups[1]
      self.dot.nodes[fn_name] = {
        'fn_name' : fn_name,
        'node_id' : node_id,
        'local_samples' : int(groups[2]),
        'local_percentage' : float(groups[3]),
        'cumulative_samples': int(groups[2]),
        'cumulative_percentage' : float(groups[3]),
        'stuff_after': groups[4],
        'line': line,
      }
      self.dot.fn_names[node_id] = fn_name
      return True
    return False

  def parse_edge_line(self, line):
    #eg: N17 -> N6 [label=308, weight=55, style="setlinewidth(1.689214),dashed"];
    matches = DotFileParser.regex_match(
      r'{node_name} -> {node_name} \[label={num_samples},([^\];]*)];', line)
    if matches: 
      groups = matches.groups()
      from_fn = self.dot.fn_names[groups[0]]
      to_fn = self.dot.fn_names[groups[1]]
      edge_key = ParsedDotFile.make_edge_key(from_fn, to_fn)      
      self.dot.edges[edge_key] = {
        'from_fn' : from_fn,
        'to_fn' : to_fn,
        'num_samples' : groups[2],
        'stuff_after' : groups[3],
      }
      return True
    return False
  
  def parse_end_line(self, line):
    matches = DotFileParser.regex_match(r'}}', line)
    return matches is not None

  @staticmethod
  def regex_match(template, line):
    r = re.compile(template.format(**DotFileParser.patterns))
    matches = re.match(r, line)
    return matches



