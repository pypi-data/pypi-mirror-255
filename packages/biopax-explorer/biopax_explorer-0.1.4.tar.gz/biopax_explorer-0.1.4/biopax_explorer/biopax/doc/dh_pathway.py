
from biopax.utils import gen_utils
 

class pathway_DocHelper():
  """
  Class pathway_DocHelper

  documentation helper for pathway
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='Pathway'
    self.inst=gen_utils.define_model_instance(self.cln)
    self.tmap=self.attr_type_def()


  def classInfo(self):
    cln=self.cln
    if cln in self.dmap.keys():
       m=self.dmap[cln]
       return m['class']
    return None
  
  def attributeNameString(self):
    cln=self.cln
    s=""
    if cln in self.dmap.keys():
       m=self.dmap[cln]
       atm= m['attribute']
       for k in atm.keys():
         s+="%s\n" %(k)    
    return s

  def attributeNames(self):
    cln=self.cln
    al=[]
    if cln in self.dmap.keys():
       m=self.dmap[cln]
       atm= m['attribute']
       for k in atm.keys():
         al.append(k)
    return al  

  def objectAttributeNames(self):
    cln=self.cln
    oa=self.inst.object_attributes()
    al=[]
    if cln in self.dmap.keys():
       m=self.dmap[cln]
       atm= m['attribute']
       for k in atm.keys():
         if k in oa:
           al.append(k)
    return al    

  def typeAttributeNames(self):
    cln=self.cln
    ta=self.inst.type_attributes()
    al=[]
    if cln in self.dmap.keys():
       m=self.dmap[cln]
       atm= m['attribute']
       for k in atm.keys():
         if k in ta:
           al.append(k)
    return al   


  def attributesInfo(self):
    cln=self.cln
    s=""
    if cln in self.dmap.keys():
       m=self.dmap[cln]
       atm= m['attribute']
       for k in atm.keys():
         s+="%s:" %(k)
         s+="\n%s" %(atm[k])
    return s

  def attributeInfo(self,attn):
    cln=self.cln
    if cln in self.dmap.keys():
       m=self.dmap[cln]
       atm= m['attribute']
       if attn in atm.keys():
          return atm[attn]
    return None

  def attributeType(self,attn):
    cln=self.cln
    if cln in self.dmap.keys():
       m=self.tmap[cln]
       atm= m['attribute']
       if attn in atm.keys():
          return atm[attn]
    return None


  def definitions(self):
    dmap=dict()
    ####################################
    # class Pathway
    dmap['Pathway']=dict()
    dmap['Pathway']['class']="""
Definition: A set or series of interactions, often forming a network, which biologists have found useful to group together for organizational, historic, biophysical or other reasons.

Usage: Pathways can be used for demarcating any subnetwork of a BioPAX model. It is also possible to define a pathway without specifying the interactions within the pathway. In this case, the pathway instance could consist simply of a name and could be treated as a 'black box'.  Pathways can also soverlap, i.e. a single interaction might belong to multiple pathways. Pathways can also contain sub-pathways. Pathways are continuants.

Synonyms: network, module, cascade,  
Examples: glycolysis, valine biosynthesis, EGFR signaling
    """
    dmap['Pathway']['attribute']=dict()
  
    dmap['Pathway']['attribute']['organism']="""
An organism, e.g. 'Homo sapiens'. This is the organism that the entity is found in. Pathways may not have an organism associated with them, for instance, reference pathways from KEGG. Sequence-based entities (DNA, protein, RNA) may contain an xref to a sequence database that contains organism information, in which case the information should be consistent with the value for ORGANISM.
    """
    dmap['Pathway']['attribute']['pathwayComponent']="""
The set of interactions and/or pathwaySteps in this pathway/network. Each instance of the pathwayStep class defines: 1) a set of interactions that together define a particular step in the pathway, for example a catalysis instance and the conversion that it catalyzes; 2) an order relationship to one or more other pathway steps (via the NEXT-STEP property). Note: This ordering is not necessarily temporal - the order described may simply represent connectivity between adjacent steps. Temporal ordering information should only be inferred from the direction of each interaction.
    """
    dmap['Pathway']['attribute']['pathwayOrder']="""
The ordering of components (interactions and pathways) in the context of this pathway. This is useful to specific circular or branched pathways or orderings when component biochemical reactions are normally reversible, but are directed in the context of this pathway.
    """
    dmap['Pathway']['attribute']['dataSource']="""
A free text description of the source of this data, e.g. a database or person name. This property should be used to describe the source of the data. This is meant to be used by databases that export their data to the BioPAX format or by systems that are integrating data from multiple sources. The granularity of use (specifying the data source in many or few instances) is up to the user. It is intended that this property report the last data source, not all data sources that the data has passed through from creation.
    """
    dmap['Pathway']['attribute']['evidence']="""
Scientific evidence supporting the existence of the entity as described.
    """
    dmap['Pathway']['attribute']['xref']="""
Values of this property define external cross-references from this entity to entities in external databases.
    """
    dmap['Pathway']['attribute']['availability']="""
Describes the availability of this data (e.g. a copyright statement).
    """
    dmap['Pathway']['attribute']['comment']="""
Comment on the data in the container class. This property should be used instead of the OWL documentation elements (rdfs:comment) for instances because information in 'comment' is data to be exchanged, whereas the rdfs:comment field is used for metadata about the structure of the BioPAX ontology.
    """
    dmap['Pathway']['attribute']['displayName']="""
An abbreviated name for this entity, preferably a name that is short enough to be used in a visualization application to label a graphical element that represents this entity. If no short name is available, an xref may be used for this purpose by the visualization application.

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
    dmap['Pathway']['attribute']['name']="""
Synonyms for this entity.  standardName and shortName are subproperties of this property and if declared they are automatically considered as names. 

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
    dmap['Pathway']['attribute']['standardName']="""
The preferred full name for this entity, if exists assigned by a standard nomenclature organization such as HUGO Gene Nomenclature Committee.

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class Pathway
    dmap['Pathway']=dict()
    dmap['Pathway']['attribute']=dict()
    dmap['Pathway']['attribute']['organism']="BioSource"
    dmap['Pathway']['attribute']['pathwayComponent']="Interaction"
    dmap['Pathway']['attribute']['pathwayOrder']="PathwayStep"
    dmap['Pathway']['attribute']['dataSource']="Provenance"
    dmap['Pathway']['attribute']['evidence']="Evidence"
    dmap['Pathway']['attribute']['xref']="Xref"
    dmap['Pathway']['attribute']['availability']="str"
    dmap['Pathway']['attribute']['comment']="str"
    dmap['Pathway']['attribute']['displayName']="str"
    dmap['Pathway']['attribute']['name']="str"
    dmap['Pathway']['attribute']['standardName']="str"
  
    return dmap    