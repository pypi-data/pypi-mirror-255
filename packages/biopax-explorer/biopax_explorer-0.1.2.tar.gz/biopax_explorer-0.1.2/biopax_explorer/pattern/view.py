import graphviz
import pathlib
import pydot
import networkx as nx
 
from biopax_explorer.pattern.pattern import PatternExecutor,Pattern
 
 


def dottext2png(dot_string,gimagepath):
  """Converts DOT string to PNG image."""
  
  dotgraphs = pydot.graph_from_dot_data(dot_string)
  dotgraph = dotgraphs[0]
  
  dotgraph.write_png(gimagepath)

def dottext2svg(dot_string,gimagepath):
  """Converts DOT string to SVG image."""
  dotgraphs = pydot.graph_from_dot_data(dot_string)
  dotgraph = dotgraphs[0]

  dotgraph.write_svg(gimagepath)

def dot2png(dotfile,gimagepath):
  """Converts DOT file to PNG image."""
  dot_string=pathlib.Path("%s" %(dotfile)).read_text()
  dottext2png(dot_string,gimagepath)

def dot2svg(dotfile,gimagepath):
  """Converts DOT file to SVG image."""
  dot_string=pathlib.Path("%s" %(dotfile)).read_text()
  dottext2svg(dot_string,gimagepath)



def writePatternGraphView(p1:Pattern,gimagepath:str, format="png"):
  
  """
    Generates a graph view of a given Pattern and writes it to an image file.

    Args:
        p1 (Pattern): The Pattern object to generate the graph view from.
        gimagepath (str): The path where the generated image file will be saved.
        format (str, optional): The format of the image file. Defaults to "png".
            Can be "png" or "svg".

    Returns:
        str: The DOT string representing the generated graph.
  """

  pe=PatternExecutor()         
  querylist=pe.queries(p1)
  dstr="digraph  {"
 

  i=0
  glist=pe.glist
   
  for sg in glist:
    i+=1
    nodes=sg.nodes()
    cls_a = nx.get_node_attributes(sg, "cls_info")  
    lbl_a = nx.get_node_attributes(sg, "label") 
    for nd in nodes:
        ndn="%ss%s"%(nd,i)
        info="\""+cls_a[nd]+" "+lbl_a[nd]+"\""
        dstr+="""%s [label=%s];\n""" %(ndn,info)
    edges=sg.edges()
    al = nx.get_edge_attributes(sg, "asso_info")  
    for ed in edges:
           info="\""+al[ed]+"\""
           ndn0="%ss%s"%(ed[0],i)
           ndn1="%ss%s"%(ed[1],i)
           dstr+="""%s -- %s  [label=%s];\n""" %(ndn0,ndn1,info)
    #print( al  )
  dstr+="}"
  dot_string=dstr
 
  dot_string=dot_string.replace('\n', '')
  if format is None or format=="png":
     dottext2png(dot_string,gimagepath)
  elif format=="svg":
     dottext2svg(dot_string,gimagepath) 

  return dot_string  


