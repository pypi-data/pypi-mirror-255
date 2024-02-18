
import  rdfobj.serializer as se
from biopax_explorer.biopax.utils import gen_utils as gu



def bp_template():
   """
    Generates a BioPAX RDF template.

    Returns:
        str: The BioPAX RDF template.
   """

   return """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
 xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:owl="http://www.w3.org/2002/07/owl#"
 xmlns:bp="http://www.biopax.org/release/biopax-level3.owl#">
<owl:Ontology rdf:about="">
 <owl:imports rdf:resource="http://www.biopax.org/release/biopax-level3.owl#" />
</owl:Ontology>
</rdf:RDF>
     """


class BPSerializer(se.Visitor):
  def __init__(self,userns,collec):
         super().__init__(userns,gu)
         self.template=bp_template()
         self.set(collec)
  def set(self,collec):
    """
        Sets the collection for the serializer.

        Args:
            collec: The collection to set.
    """
    self.populate(collec)
    self.traverse() 







