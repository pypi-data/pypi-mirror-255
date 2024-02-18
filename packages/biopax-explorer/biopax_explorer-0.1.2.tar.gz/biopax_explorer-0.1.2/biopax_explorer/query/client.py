import os,pathlib

from SPARQLWrapper import SPARQLWrapper, JSON, POST, DIGEST
import networkx as nx
 
 

import textwrap

from rdfobj import *
import rdfobj
from biopax_explorer.biopax.utils import gen_utils as gu
from biopax_explorer.biopax  import *
from biopax_explorer.graph  import serializer as se

class BIOPAXStoreClient():
  """
    A class for interacting with a BIOPAX RDF store.

    Attributes:
        db (str): The database URL.
        dataset (str): The dataset name.
        credentials (tuple): A tuple containing username and password for authentication.
        unwanted_subject_uri (str): URI of unwanted subjects.
  """

  def __init__(self,db,dataset,credentials=None,unwanted_subject_uri=None):
     """
        Initializes the BIOPAXStoreClient.

        Args:
            db (str): The database URL.
            dataset (str): The dataset name.
            credentials (tuple, optional): A tuple containing username and password for authentication.
            unwanted_subject_uri (str, optional): URI of unwanted subjects.
     """
     self.prefix=gu.prefix()
     self.domain_schema_uri=gu.domain()
     self.mp=gu.modelPopulator()
     classDict=self.mp.classDict
     self.sc=StoreClient(classDict) 
     self.db=db
     self.dataset=dataset
     self.credentials=credentials 
     urlq=self.dbstr(self.db,self.route_query(self.dataset)) 
     self.wrapper_query=self.defineWrapper(urlq,self.credentials)
     urlu=self.dbstr(self.db,self.route_update(self.dataset)) 
     self.wrapper_update=self.defineWrapper(urlu,self.credentials) 
     self.unwanted_subject_uri=unwanted_subject_uri 
  
  def dbstr(self,pre,sfx):        
    """
        Constructs a database string.

        Args:
            pre (str): The prefix.
            sfx (str): The suffix.

        Returns:
            str: The constructed database string.
    """

    return "%s/%s" %(pre,sfx)


  def route_update(self, path):
      """
        Constructs a route for update.

        Args:
            path (str): The path.

        Returns:
            str: The constructed update route.
      """
      return "%s/%s" %(path,"update")
      
  def route_query(self,path):    
       """
        Constructs a route for query.

        Args:
            path (str): The path.

        Returns:
            str: The constructed query route.
       """      

       return "%s/%s" %(path,"query")
      
  def defineWrapper(self,url,credentials): 
      """
        Defines a SPARQLWrapper instance.

        Args:
            url (str): The URL.
            credentials (tuple): A tuple containing username and password for authentication.

        Returns:
            SPARQLWrapper: The configured SPARQLWrapper instance.
      """      
      wrapper = SPARQLWrapper(url)
      
      wrapper.setMethod('POST')
      wrapper.setReturnFormat(JSON)
      if credentials is not None:
         wrapper.setCredentials(credentials[0], credentials[1])
      
      return wrapper
      

  def executeQuery(self,query): 
       """
       Executes a SPARQL query.

       Args:
           query (str): The SPARQL query string.

       Returns:
           dict: The results of the query.
       """      


       dbstr=self.dbstr(self.db,self.route_query(self.dataset))
       results=self.mp.executeQuery(dbstr, None,query)
       
       return results
      
  def execute(self,query) :
      """
      Executes a SPARQL query and returns the results as a list.

      Args:
          query (str): The SPARQL query string.

      Returns:
          list: A list of query results.
      """      



      lst=[]
       
             
      results=self.executeQuery(query) 
      heads=results["head"]["vars"]
      bindings=results["results"]["bindings"]
    
      if len(bindings)==0:
         return lst
      
      for result in bindings:
        tp=[]
        for v in heads:
           tp.append(result[v]['value'])
        lst.append(tp)  
      return lst

    
  def define_bp_template(self):
   """
      Defines a BioPAX template.

      Returns:
          object: The BioPAX template object.
   """
   return se.bp_template()
  
  def store_to_graph(self,limit=1000):
      
      """
      Stores RDF data into a NetworkX graph.

      Args:
          limit (int, optional): The limit of records to retrieve. Defaults to 1000.

      Returns:
          object: The NetworkX graph object.
      """   


      dbstr=self.dbstr(self.db,self.route_query(self.dataset))
      print(dbstr,self.prefix,self.domain_schema_uri,self.unwanted_subject_uri,limit)
      g=self.sc.store_to_graph(dbstr,self.prefix,self.domain_schema_uri,self.unwanted_subject_uri,limit)
      return g
       
  def save_graph_as_rdf_xml(self,efile, gr=None):   
      """
      Saves a graph as an RDF/XML file.

      Args:
          efile (str): The file path to save the RDF/XML.
          gr (object, optional): The graph object. Defaults to None.

      Returns:
          object: The graph object.
      """      

      g=self.sc.save_graph_as_rdf_xml(efile, gr)   
      return g


  def custom_query_list_append(self,q):
      """
      Appends a custom query to the custom query list.

      Args:
          q (str): The custom query string.
      """      

      return self.sc.custom_query_list.append(q)
       
  def store_custom_query_to_graph(self,extension, labels=None):  
      
      """
      Stores custom query results into a NetworkX graph.

      Args:
          extension (str): The extension for the custom query.
          labels (list, optional): A list of labels. Defaults to None.

      Returns:
          object: The NetworkX graph object.
      """
    
      dbstr=self.dbstr(self.db,self.route_query(self.dataset))
      if labels is None:
        return self.sc.store_custom_query_to_graph(dbstr,extension)
      else:
        return self.sc.store_custom_query_to_graph(dbstr,extension, labels) 
      
  def delete_from_store_by_uri_id(self,uri_id,prefix=None,domain=None):
      """
      Deletes data from the store by URI ID.

      Args:
          uri_id (str): The URI ID.
          prefix (str, optional): The prefix. Defaults to None.
          domain (str, optional): The domain. Defaults to None.

      Returns:
          object: The result of the delete operation.
      """



      if prefix is None:
          prefix=self.prefix
      if domain is None:
          domain=self.domain
          
      return self.sc.delete_from_store_by_uri_id(self.wrapper_update,uri_id, prefix, domain)

  def insert_instance(self,rel):
      """
      Inserts an instance.

      Args:
          rel (object): The instance to insert.

      Returns:
          object: The result of the insert operation.
      """    


      return self.sc.insert_instance(self.wrapper_update,rel)
      
  def update_or_insert_instance(self,rel):
      
      """
      Updates or inserts an instance.

      Args:
          rel (object): The instance to update or insert.

      Returns:
          object: The result of the update or insert operation.
      """     


      return self.sc.update_or_insert_instance(self.wrapper_update,rel)

  def select_all_query(self,limit=1000,offset=0):
      """
      Performs a select all query.

      Args:
          limit (int, optional): The limit of records to retrieve. Defaults to 1000.
          offset (int, optional): The offset. Defaults to 0.

      Returns:
          object: The result of the select all query.
      """      



      return self.sc.select_all_query(self.prefix,self.domain_schema_uri,self.unwanted_subject_uri,limit,offset)

  def file_to_graph(self,file) :
      """
      Converts a file to a NetworkX graph.

      Args:
          file (str): The file path.

      Returns:
          object: The NetworkX graph object.
      """      


      return self.sc.file_to_graph(file)

  def string_to_graph(self,xml) :
    """
      Converts an XML string to a NetworkX graph.

      Args:
          xml (str): The XML string.

      Returns:
          object: The NetworkX graph object.
    """


    return self.sc.string_to_graph(xml)
  
  def rdf_xml_string(self,g=None): 
    """
      Generates an RDF/XML string from a graph.

      Args:
          g (object, optional): The graph object. Defaults to None.

      Returns:
          str: The RDF/XML string.
    """      

    return self.sc.rdf_xml_string(g)

  def nxgraph(self,g=None):
    """
      Converts an RDF graph to a NetworkX graph.

      Args:
          g (object, optional): The RDF graph object. Defaults to None.

      Returns:
          object: The NetworkX graph object.
    """
    nx_graph = nx.Graph()
    if g is None:
      rdf_graph=self.sc.g
    else:
      rdf_graph=g   
    # Iterate through RDF triples and add nodes and edges to NetworkX graph
    for subject, predicate, obj in rdf_graph:
        subject_node = str(subject)
        object_node = str(obj)
        predicate_edge = str(predicate)
        nx_graph.add_node(subject_node)
        nx_graph.add_node(object_node)
        nx_graph.add_edge(subject_node, object_node, predicate=predicate_edge)
    return nx_graph

