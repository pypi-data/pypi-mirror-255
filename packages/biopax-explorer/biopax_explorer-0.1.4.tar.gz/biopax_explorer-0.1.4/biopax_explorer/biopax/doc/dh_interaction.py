
from biopax.utils import gen_utils
 

class interaction_DocHelper():
  """
  Class interaction_DocHelper

  documentation helper for interaction
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='Interaction'
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
    # class Interaction
    dmap['Interaction']=dict()
    dmap['Interaction']['class']="""
Definition: A biological relationship between two or more entities. 

Rationale: In BioPAX, interactions are atomic from a database modeling perspective, i.e. interactions can not be decomposed into sub-interactions. When representing non-atomic continuants with explicit subevents the pathway class should be used instead. Interactions are not necessarily  temporally atomic, for example genetic interactions cover a large span of time. Interactions as a formal concept is a continuant, it retains its identitiy regardless of time, or any differences in specific states or properties.

Usage: Interaction is a highly abstract class and in almost all cases it is more appropriate to use one of the subclasses of interaction. 
It is partially possible to define generic reactions by using generic participants. A more comprehensive method is planned for BioPAX L4 for covering all generic cases like oxidization of a generic alcohol.   

Synonyms: Process, relationship, event.

Examples: protein-protein interaction, biochemical reaction, enzyme catalysis
    """
    dmap['Interaction']['attribute']=dict()
  
    dmap['Interaction']['attribute']['cofactor']="""
Any cofactor(s) or coenzyme(s) required for catalysis of the conversion by the enzyme. This is a suproperty of participants.
    """
    dmap['Interaction']['attribute']['controlled']="""
The entity that is controlled, e.g., in a biochemical reaction, the reaction is controlled by an enzyme. Controlled is a sub-property of participants.
    """
    dmap['Interaction']['attribute']['controller']="""
The controlling entity, e.g., in a biochemical reaction, an enzyme is the controlling entity of the reaction. CONTROLLER is a sub-property of PARTICIPANTS.
    """
    dmap['Interaction']['attribute']['interactionType']="""
Controlled vocabulary annotating the interaction type for example, "phosphorylation reaction". This annotation is meant to be human readable and may not be suitable for computing tasks, like reasoning, that require formal vocabulary systems. For instance, this information would be useful for display on a web page or for querying a database. The PSI-MI interaction type controlled vocabulary should be used. This is browsable at: 
http://www.ebi.ac.uk/ontology-lookup/browse.do?ontName=MI&termId=MI%3A0190&termName=interaction%20type
    """
    dmap['Interaction']['attribute']['left']="""
The participants on the left side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the left property may be either reactants or products. left is a sub-property of participants.
    """
    dmap['Interaction']['attribute']['participant']="""
This property lists the entities that participate in this interaction. For example, in a biochemical reaction, the participants are the union of the reactants and the products of the reaction. This property has a number of sub-properties, such as LEFT and RIGHT used in the biochemicalInteraction class. Any participant listed in a sub-property will automatically be assumed to also be in PARTICIPANTS by a number of software systems, including Protege, so this property should not contain any instances if there are instances contained in a sub-property.
    """
    dmap['Interaction']['attribute']['product']="""
The product of a template reaction.
    """
    dmap['Interaction']['attribute']['right']="""
The participants on the right side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the RIGHT property may be either reactants or products. RIGHT is a sub-property of PARTICIPANTS.
    """
    dmap['Interaction']['attribute']['template']="""
The template molecule that is used in this template reaction.
    """
    dmap['Interaction']['attribute']['dataSource']="""
A free text description of the source of this data, e.g. a database or person name. This property should be used to describe the source of the data. This is meant to be used by databases that export their data to the BioPAX format or by systems that are integrating data from multiple sources. The granularity of use (specifying the data source in many or few instances) is up to the user. It is intended that this property report the last data source, not all data sources that the data has passed through from creation.
    """
    dmap['Interaction']['attribute']['evidence']="""
Scientific evidence supporting the existence of the entity as described.
    """
    dmap['Interaction']['attribute']['xref']="""
Values of this property define external cross-references from this entity to entities in external databases.
    """
    dmap['Interaction']['attribute']['availability']="""
Describes the availability of this data (e.g. a copyright statement).
    """
    dmap['Interaction']['attribute']['comment']="""
Comment on the data in the container class. This property should be used instead of the OWL documentation elements (rdfs:comment) for instances because information in 'comment' is data to be exchanged, whereas the rdfs:comment field is used for metadata about the structure of the BioPAX ontology.
    """
    dmap['Interaction']['attribute']['displayName']="""
An abbreviated name for this entity, preferably a name that is short enough to be used in a visualization application to label a graphical element that represents this entity. If no short name is available, an xref may be used for this purpose by the visualization application.

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
    dmap['Interaction']['attribute']['name']="""
Synonyms for this entity.  standardName and shortName are subproperties of this property and if declared they are automatically considered as names. 

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
    dmap['Interaction']['attribute']['standardName']="""
The preferred full name for this entity, if exists assigned by a standard nomenclature organization such as HUGO Gene Nomenclature Committee.

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class Interaction
    dmap['Interaction']=dict()
    dmap['Interaction']['attribute']=dict()
    dmap['Interaction']['attribute']['cofactor']="PhysicalEntity"
    dmap['Interaction']['attribute']['controlled']="Entity"
    dmap['Interaction']['attribute']['controller']="Entity"
    dmap['Interaction']['attribute']['interactionType']="InteractionVocabulary"
    dmap['Interaction']['attribute']['left']="PhysicalEntity"
    dmap['Interaction']['attribute']['participant']="Entity"
    dmap['Interaction']['attribute']['product']="Entity"
    dmap['Interaction']['attribute']['right']="PhysicalEntity"
    dmap['Interaction']['attribute']['template']="Entity"
    dmap['Interaction']['attribute']['dataSource']="Provenance"
    dmap['Interaction']['attribute']['evidence']="Evidence"
    dmap['Interaction']['attribute']['xref']="Xref"
    dmap['Interaction']['attribute']['availability']="str"
    dmap['Interaction']['attribute']['comment']="str"
    dmap['Interaction']['attribute']['displayName']="str"
    dmap['Interaction']['attribute']['name']="str"
    dmap['Interaction']['attribute']['standardName']="str"
  
    return dmap    