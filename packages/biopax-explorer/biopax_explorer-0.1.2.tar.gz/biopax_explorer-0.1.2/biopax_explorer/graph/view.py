import os
import warnings

# Variables to track whether certain packages are installed
has_gt=None
has_cyto=None
silent_warn=True
 
 
gt=None
icyt=None


has_gt=None
has_cyto=None
silent_warn=True

 
from biopax_explorer.biopax.utils import gen_utils as gu
from biopax_explorer.biopax.doc import helper
import  rdfobj  as ro 
import networkx as nx
import matplotlib.colors as mcolors


# Attempt to import required packages
try:
    import ipycytoscape as icyt 
    has_cyto=True    
     
except:
    has_cyto=False
try:
    import  graph_tool.all as gt
    has_gt=True
     
except:
    has_gt=False


# Configuration function to check installed backends     
def config():
   """
    Checks the installed backends and returns a message indicating the available options.

    Returns:
        str: A message indicating the available backends.
    """
   global has_gt
   global has_cyto
   msg=""
   msg+="networkx backend installed\n"
   if has_gt==True:
     msg+="graph.tool backend installed\n" 
   if has_cyto==True: 
       msg+="cytoscape.js jupyter viewer installed\n"
   return msg


class GraphModelLayer(ro.GraphModelLayer):
    """
    GraphModelLayer class.
    """
    def __init__(self):
     
         super().__init__() 
         super().build(gu)


class Factory():
    """
    Factory class for creating graph dataset layers.
    """
    def __init__(self,back="NX"):
        self.glayer=None
        

        if back=="NK":
          self.glayer= GraphDatasetLayerNX()
        elif  back=="GT":   
          
          if has_gt==True:
        
             self.glayer= GraphDatasetLayerGT()
          else:    
            print("WARNING: The package graph-tool is not installed. GraphDatasetLayerGT can not be instancied ")
            self.glayer=None
          
        else:
          self.glayer= GraphDatasetLayerNX()    

    def graphDatasetLayer(self):
        """
        Returns the graph dataset layer.

        Returns:
            GraphDatasetLayerAbs: The graph dataset layer.
        """
        return self.glayer
          

class GraphDatasetLayerNX(ro.GraphDatasetLayerAbs):
    """
    GraphDatasetLayerNX class for NetworkX backend.
    """
    def __init__(self):
      
         super().__init__()          
         self.mpop=gu.modelPopulator()
         self.model_instance_dict={} 

    def populate_dataset(self,db,dataset):
        dburl=db+"/%s/query"
        self.model_instance_dict=self.mpop.populate_domain_instance(dburl,dataset,gu.prefix(),gu.domain()) 


class GraphDatasetLayerGT(ro.GraphDatasetLayerAbsBKGT):
    """
    GraphDatasetLayerGT class for Graph-tool backend.
    """
    def __init__(self):
      
         super().__init__()          
         self.mpop=gu.modelPopulator()
         self.model_instance_dict={} 

    def populate_dataset(self,db,dataset):
        dburl=db+"/%s/query"
        self.model_instance_dict=self.mpop.populate_domain_instance(dburl,dataset,gu.prefix(),gu.domain()) 
       



################

def graphString(g):
        
        """
    Generates a string representation of a graph.

    Args:
        g (nx.Graph): The input graph.

    Returns:
        str: A string representation of the graph.
        """

        output = "Graph:\n"

        # Display nodes with attributes
        output += "Nodes:\n"
        for node, data in g.nodes(data=True):
            output += "%s: %s\n" %(  node, data)

        # Display edges with attributes
        output += "Edges:\n"
        for n1,n2,attv in g.edges(data=True):
        #for edge, data in g.edges(data=True):
            output +=  "{%s -- %s}: %s \n" %(n1,n2,attv)

        return output



class CytoViewer():
    """
    A wrapper for the cytoscape.js jupyter widget.
    """

    def __init__(self,graph, gtype="NX"):
        """
        Initializes a CytoViewer instance.

        Args:
            graph: The input graph data.
            gtype (str): The type of graph, either "NX" for NetworkX or "GT" for graph-tool.
        """

        # Define the possible shapes for nodes
        self.shapes=self.defineShapes()
        # Define the viewer for displaying the graph
        self.viewer=self.defineViewer()
        # Initialize default style settings
        self.default_style=None
        self.added_style=None
        self.final_style=None
        # Initialize graph-related attributes
        self.graph=None
        self.gtype=gtype
        self.nlabel=["nlabel",["name"]]
        self.elabel=["elabel",["name"]]
        self.nseparator=" "
        self.eseparator=" "
        # Convert the input graph data to the appropriate format
        if self.gtype=="NX":
            self.graph=self.from_networkx(graph) 
        elif self.gtype=="GT":   
            self.graph=self.from_graphtool(graph)  

        
    def initStyle(self,nodeLabel,edgeLabel):
        """
        Initializes the style settings for the graph nodes and edges.

        Args:
            nodeLabel (str): The label attribute for nodes.
            edgeLabel (str): The label attribute for edges.
        """
        # Set the default style based on provided labels
        self.default_style=self.define_default_style(nodeLabel,edgeLabel)
        # If final style is not set, use default style
        if  self.final_style is None:
            self.final_style=self.default_style
        # If additional styles are provided, extend the final style            
        if self.added_style is not None:    
            self.final_style.extend(self.added_style) 


    def defineViewer(self):
        """
        Defines the viewer for displaying the graph.

        Returns:
            cyto.CytoscapeWidget: The cytoscape.js widget for graph visualization.
        """
        if  has_cyto==True:
            vi = icyt.CytoscapeWidget()
            self.viewer=vi
            return vi
        else:
            print("package ipycytoscape not defined.please install it (pip)")
            return None
        
        
    def defineShapes(self):
        
        """
        Defines the possible shapes for node representation.

        Returns:
            list: List of strings representing node shapes.
        """
        # The following are  the possible values for the node shape property:
        shapes=[
            "rectangle",
            "roundrectangle",
            "ellipse",
            "triangle",
            "pentagon",
            "hexagon",
            "octagon",
            "rhomboid",
            "round-triangle",
            "round-pentagon",
            "round-hexagon",
            "round-octagon",
            "round-rhomboid",
            "barrel",
            "rhombus",
            "diamond",
            "heptagon",
            "star",
            "vee"
        ]
        return shapes
    
    def define_default_style(self,nodeLabel,edgeLabel)    :
        """
        Defines the default style settings for nodes and edges.

        Args:
            nodeLabel (str): The label attribute for nodes.
            edgeLabel (str): The label attribute for edges.

        Returns:
            list: List of dictionaries representing default style settings.
        """

        cstyled=[       
        {'selector': 'node', 'css': {'background-color': '#8d9193', 'background-opacity': 0.6} },
        {'selector': 'node:parent', 'css': {'background-opacity': 0.333}},
        {'selector': 'edge', 'style': {'width': 4, 'line-color': 'lightblue'}  },
        ]
        if nodeLabel!= None:
           cstyled.append({'selector': 'node[ctype]','style': {'label': "data(%s)" %(nodeLabel)}})
        if edgeLabel!= None:
           cstyled.append({'selector': 'edge[name]','style': {'label':  "data(%s)" %(edgeLabel)}})
        cstyled.extend(self.generate_node_selector())
        return cstyled 



    def select_list_alternatively(self,a, b, c, d, e, x):
      
      """
        Selects a list from the provided lists alternately based on the value of x.

        Args:
            a, b, c, d, e (list): Lists to select from.
            x (int): Value used for selection.

        Returns:
            list: The selected list.
      """       

      if x % 2 == 0:
         selected_list = a
      else:
         selected_list = b if x % 4 == 1 else c if x % 4 == 3 else d
 
      if x % 5 == 0:
        selected_list = e     
        
      return selected_list

    def generate_node_selector(self):    
        """
        Generates node selector styles based on defined color schemes.

        Returns:
            list: List of dictionaries representing node selector styles.
        """        

        start_color1 = 'lightblue'
        end_color1 = 'lightgreen'

        start_color2 = 'lightpink'
        end_color2 = 'violet'

        start_color3 = 'midnightblue'
        end_color3 = 'royalblue'


        start_color4 = 'darkseagreen'
        end_color4 = 'aquamarine'

        start_color5 = 'khaki'
        end_color5 = 'tan'

        lentries=len(helper.entries())

        nshapes=[]
        while len(nshapes) < lentries:
          nshapes.extend(self.shapes)

       
        custstyle=[]
        a = self.generate_web_colors(start_color1, end_color1, lentries)
        b = self.generate_web_colors(start_color2, end_color2, lentries)
        c = self.generate_web_colors(start_color3, end_color3, lentries)
        d = self.generate_web_colors(start_color4, end_color4, lentries)
        e = self.generate_web_colors(start_color5, end_color5, lentries)

        ix=-1
        for cls in helper.entries():
          ix+=1   
          web_colors=self.select_list_alternatively(a,b,c,d,e,ix)   
          selector={ 'selector': 'node[ctype="%s"]' %(cls), 'css': { 'background-color': '%s' %(web_colors[ix]), 'shape': '%s' %(nshapes[ix])  } }  
          custstyle.append(selector)   
        return custstyle


    def  from_json(self,data):
         """
        Loads graph data from JSON format.

        Args:
            data (str): JSON data representing the graph.

        Returns:
            None
         """         
         self.viewer.graph.add_graph_from_json(data)    

    def addStyle(self,cstyle):
        """
        Adds additional style to the final style settings.

        Args:
            cstyle (list): List of dictionaries representing additional style settings.

        Returns:
            None
        """        
        if self.added_style is None:
            self.added_style=[]
        self.added_style.extend(cstyle)

    def  style(self,cstyle):
         """
        Sets the final style settings.

        Args:
            cstyle (list): List of dictionaries representing final style settings.

        Returns:
            None
         """         

         self.final_style=cstyle

    def  layout(self,layoutname):
         """
        Sets the layout for graph visualization.

        Args:
            layoutname (str): Name of the layout.

        Returns:
            None
         """         
         self.viewer.set_layout(name=layoutname) 

    def  tooltip(self,tooltip):
         
         """
        Sets the tooltip source for graph elements.

        Args:
            tooltip (str): Tooltip source.

        Returns:
            None
         """
         self.viewer.set_tooltip_source(tooltip)  

    def  display(self,nodeLabel="nlabel",edgeLabel="elabel"):

         """
        Displays the graph with specified node and edge labels.

        Args:
            nodeLabel (str): Label attribute for nodes.
            edgeLabel (str): Label attribute for edges.

        Returns:
            cyto.CytoscapeWidget: The cytoscape.js widget displaying the graph.
         """
         
         self.defineNodeLabelImpl()
         self.defineEdgeLabelImpl()
         self.initViewFromGraph()
         self.initStyle(nodeLabel,edgeLabel)
         self.viewer.set_style(self.final_style)
         
         return self.viewer
    

    def defineNodeLabel(self,attlist=["name"], separator=" ",attName="nlabel"):

        """
        Defines the label attribute for nodes.

        Args:
            attlist (list): List of node attributes to include in the label.
            separator (str): Separator to use between attribute values.
            attName (str): Name of the label attribute.

        Returns:
            None
        """

        self.nlabel=[attName,attlist]
        self.nseparator=separator

    def defineNodeLabelImpl(self):


        """
        Defines the label attribute for nodes based on defined attributes and separator.

        Returns:
            None
        """

        attName=self.nlabel[0]
        attlist=self.nlabel[1]
        sep=self.nseparator
        for n1,attv in self.graph.nodes(data=True):
            v=""
            i=0
            for attn in attlist:
                i=i+1
                if i==len(attlist):
                    sep=""
                v+=str(attv[attn])+sep
            self.graph.nodes[n1][attName]=  v
            
    def defineEdgeLabel(self,attlist=["name"], separator=" ",attName="elabel"):

        """
        Defines the label attribute for edges.

        Args:
            attlist (list): List of edge attributes to include in the label.
            separator (str): Separator to use between attribute values.
            attName (str): Name of the label attribute.

        Returns:
            None
        """
        self.elabel=[attName,attlist]
        self.eseparator=separator

    def defineEdgeLabelImpl(self):
        """
        Defines the label attribute for edges based on defined attributes and separator.

        Returns:
            None
        """
        attName=self.elabel[0]
        attlist=self.elabel[1]
        sep=sep=self.eseparator
        for n1,n2,attv in self.graph.edges(data=True):
            v=""
            i=0
            for attn in attlist:
                i=i+1
                if i==len(attlist):
                    sep=""
                v+=str(attv[attn])+sep
            self.graph.edges[n1, n2][attName]=  v



    def  from_graphtool(self,g):
         """
        Converts a graph-tool graph to a CytoViewer graph.

        Args:
            graph (Graph): The input graph-tool graph.

        Returns:
            cyto.CytoscapeWidget: The CytoViewer graph.
         """

         nxg=self.gf2nx(g)
         
         return nxg
    
    def  gf2nx(self,g):
        ##convert a graph-tool graph to networkx 
         # Create a networkx graph
         nx_graph = nx.Graph()

         # Add nodes with properties
         for v in g.vertices():
             node_id = int(v)
             node_properties = {key: g.vp[key][v] for key in g.vp}
             nx_graph.add_node(node_id, **node_properties)

         # Add edges with properties
         for e in g.edges():
             source_id = int(e.source())
             target_id = int(e.target())
             edge_properties = {key: g.ep[key][e] for key in g.ep}
             nx_graph.add_edge(source_id, target_id, **edge_properties)
         return nx_graph
   
   
    def  from_networkx(self,g):
         """
        Converts a NetworkX graph to a CytoViewer graph.

        Args:
            graph (nx.Graph): The input NetworkX graph.

        Returns:
            cyto.CytoscapeWidget: The CytoViewer graph.
         """
         return g
    
    def initViewFromGraph(self):
        """
        Initializes the viewer from the provided graph.
        """
        self.viewer.graph.add_graph_from_networkx(self.graph)


    def generate_web_colors(self,start_color, end_color, num_colors):
        """
        Generates a list of web colors between two specified colors.

        Args:
            start_color (str): The starting color.
            end_color (str): The ending color.
            steps (int): The number of steps.

        Returns:
            List[str]: A list of web colors.
        """
        # Convert color names to RGB values
        
        start_rgb = mcolors.to_rgba(mcolors.CSS4_COLORS[start_color])
        end_rgb = mcolors.to_rgba(mcolors.CSS4_COLORS[end_color])

        # Generate a smooth transition of colors using linear interpolation
        r = [start_rgb[0] + i * (end_rgb[0] - start_rgb[0]) / (num_colors - 1) for i in range(num_colors)]
        g = [start_rgb[1] + i * (end_rgb[1] - start_rgb[1]) / (num_colors - 1) for i in range(num_colors)]
        b = [start_rgb[2] + i * (end_rgb[2] - start_rgb[2]) / (num_colors - 1) for i in range(num_colors)]

        # Convert RGB values to hex format
        hex_colors = [mcolors.rgb2hex([r[i], g[i], b[i]]) for i in range(num_colors)]

        return hex_colors

    def nodeSelector(self,attribute_key,attribute_value, operator="IN", color="red"):
      
      """
    Selects nodes in the graph based on the specified attribute key and value,
    and applies a custom style to them.

    Args:
        attribute_key (str): The key of the attribute to filter nodes by.
        attribute_value (str): The value of the attribute to filter nodes by.
        operator (str, optional): The comparison operator to use for filtering.
            Defaults to "IN". Can be "IN" for "inclusion" or "EQ" for "equality".
        color (str, optional): The color to apply to the selected nodes. Defaults to "red".

    Returns:
        list: A list of custom styles applied to the selected nodes.
      """
      custstyle=[]
      g=self.graph
      filtered_nodes=[]  
        # Find nodes with the specified attribute value
      if operator=="IN":   
        filtered_nodes = [node for node, data in g.nodes(data=True) if attribute_value in data.get(attribute_key) ]
      elif operator=="EQ":  
       # Find nodes with the specified attribute value
        filtered_nodes = [node for node, data in g.nodes(data=True) if attribute_value == data.get(attribute_key) ]
      
      for id in filtered_nodes:
          selector={ 'selector': 'node[id="%s"]' %(id)  , 'css': { 'background-color': '%s' %(color)  } }  
          custstyle.append(selector)
      self.addStyle(custstyle)     
      return custstyle    
    
