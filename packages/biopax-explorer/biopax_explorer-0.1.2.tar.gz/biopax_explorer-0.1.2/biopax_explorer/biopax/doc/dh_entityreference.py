
from biopax.utils import gen_utils
 

class entityreference_DocHelper():
  """
  Class entityreference_DocHelper

  documentation helper for entityreference
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='EntityReference'
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
    # class EntityReference
    dmap['EntityReference']=dict()
    dmap['EntityReference']['class']="""
Definition: An entity reference is a grouping of several physical entities across different contexts and molecular states, that share common physical properties and often named and treated as a single entity with multiple states by biologists. 

Rationale:   Many protein, small molecule and gene databases share this point of view, and such a grouping is an important prerequisite for interoperability with those databases. Biologists would often group different pools of molecules in different contexts under the same name. For example cytoplasmic and extracellular calcium have different effects on the cell's behavior, but they are still called calcium. For DNA, RNA and Proteins the grouping is defined based on a wildtype sequence, for small molecules it is defined by the chemical structure.

Usage: Entity references store the information common to a set of molecules in various states described in the BioPAX document, including database cross-references. For instance, the P53 protein can be phosphorylated in multiple different ways. Each separate P53 protein (pool) in a phosphorylation state would be represented as a different protein (child of physicalEntity) and all things common to all P53 proteins, including all possible phosphorylation sites, the sequence common to all of them and common references to protein databases containing more information about P53 would be stored in a Entity Reference.  

Comments: This grouping has three semantic implications:

1.  Members of different pools share many physical and biochemical properties. This includes their chemical structure, sequence, organism and set of molecules they react with. They will also share a lot of secondary information such as their names, functional groupings, annotation terms and database identifiers.

2. A small number of transitions seperates these pools. In other words it is relatively easy and frequent for a molecule to transform from one physical entity to another that belong to the same reference entity. For example an extracellular calcium can become cytoplasmic, and p53 can become phosphorylated. However no calcium virtually becomes sodium, or no p53 becomes mdm2. In the former it is the sheer energy barrier of a nuclear reaction, in the latter sheer statistical improbability of synthesizing the same sequence without a template. If one thinks about the biochemical network as molecules transforming into each other, and remove edges that respond to transcription, translation, degradation and covalent modification of small molecules, each remaining component is a reference entity.

3. Some of the pools in the same group can overlap. p53-p@ser15 can overlap with p53-p@thr18. Most of the experiments in molecular biology will only check for one state variable, rarely multiple, and never for the all possible combinations. So almost all statements that refer to the state of the molecule talk about a pool that can overlap with other pools. However no overlaps is possible between molecules of different groups.
    """
    dmap['EntityReference']['attribute']=dict()
  
    dmap['EntityReference']['attribute']['entityFeature']="""
Variable features that are observed for the entities of this entityReference - such as known PTM or methylation sites and non-covalent bonds. Note that this is an aggregate list of all known features and it does not represent a state itself.
    """
    dmap['EntityReference']['attribute']['entityReferenceType']="""
A controlled vocabulary term that is used to describe the type of grouping such as homology or functional group.
    """
    dmap['EntityReference']['attribute']['evidence']="""
Scientific evidence supporting the existence of the entity as described.
    """
    dmap['EntityReference']['attribute']['memberEntityReference']="""
An entity reference that qualifies for the definition of this group. For example a member of a PFAM protein family.
    """
    dmap['EntityReference']['attribute']['xref']="""
Values of this property define external cross-references from this entity to entities in external databases.
    """
    dmap['EntityReference']['attribute']['displayName']="""
An abbreviated name for this entity, preferably a name that is short enough to be used in a visualization application to label a graphical element that represents this entity. If no short name is available, an xref may be used for this purpose by the visualization application.

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
    dmap['EntityReference']['attribute']['name']="""
Synonyms for this entity.  standardName and shortName are subproperties of this property and if declared they are automatically considered as names. 

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
    dmap['EntityReference']['attribute']['standardName']="""
The preferred full name for this entity, if exists assigned by a standard nomenclature organization such as HUGO Gene Nomenclature Committee.

Warning:  Subproperties of name are functional, that is we expect to have only one standardName and shortName for a given entity. If a user decides to assign a different name to standardName or shortName, they have to remove the old triplet from the model too. If the old name should be retained as a synonym a regular "name" property should also be introduced with the old name.
    """
    dmap['EntityReference']['attribute']['comment']="""
Comment on the data in the container class. This property should be used instead of the OWL documentation elements (rdfs:comment) for instances because information in 'comment' is data to be exchanged, whereas the rdfs:comment field is used for metadata about the structure of the BioPAX ontology.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class EntityReference
    dmap['EntityReference']=dict()
    dmap['EntityReference']['attribute']=dict()
    dmap['EntityReference']['attribute']['entityFeature']="EntityFeature"
    dmap['EntityReference']['attribute']['entityReferenceType']="EntityReferenceTypeVocabulary"
    dmap['EntityReference']['attribute']['evidence']="Evidence"
    dmap['EntityReference']['attribute']['memberEntityReference']="EntityReference"
    dmap['EntityReference']['attribute']['xref']="Xref"
    dmap['EntityReference']['attribute']['displayName']="str"
    dmap['EntityReference']['attribute']['name']="str"
    dmap['EntityReference']['attribute']['standardName']="str"
    dmap['EntityReference']['attribute']['comment']="str"
  
    return dmap    