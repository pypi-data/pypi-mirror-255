
from biopax.utils import gen_utils
 

class molecularinteraction_DocHelper():
  """
  Class molecularinteraction_DocHelper

  documentation helper for molecularinteraction
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='MolecularInteraction'
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
    # class MolecularInteraction
    dmap['MolecularInteraction']=dict()
    dmap['MolecularInteraction']['class']="""
Definition: An interaction in which participants bind physically to each other, directly or indirectly through intermediary molecules.

Rationale: There is a large body of interaction data, mostly produced by high throughput systems, that does not satisfy the level of detail required to model them with ComplexAssembly class. Specifically, what is lacking is the stoichiometric information and completeness (closed-world) of participants required to model them as chemical processes. Nevertheless interaction data is extremely useful and can be captured in BioPAX using this class. 
 
Usage: This class should be used by default for representing molecular interactions such as those defined by PSI-MI level 2.5. The participants in a molecular interaction should be listed in the PARTICIPANT slot. Note that this is one of the few cases in which the PARTICPANT slot should be directly populated with instances (see comments on the PARTICPANTS property in the interaction class description). If all participants are known with exact stoichiometry, ComplexAssembly class should be used instead.

Example: Two proteins observed to interact in a yeast-two-hybrid experiment where there is not enough experimental evidence to suggest that the proteins are forming a complex by themselves without any indirect involvement of other proteins. This is the case for most large-scale yeast two-hybrid screens.
    """
    dmap['MolecularInteraction']['attribute']=dict()
  
    dmap['MolecularInteraction']['attribute']['cofactor']="""
Any cofactor(s) or coenzyme(s) required for catalysis of the conversion by the enzyme. This is a suproperty of participants.
    """
    dmap['MolecularInteraction']['attribute']['controlled']="""
The entity that is controlled, e.g., in a biochemical reaction, the reaction is controlled by an enzyme. Controlled is a sub-property of participants.
    """
    dmap['MolecularInteraction']['attribute']['controller']="""
The controlling entity, e.g., in a biochemical reaction, an enzyme is the controlling entity of the reaction. CONTROLLER is a sub-property of PARTICIPANTS.
    """
    dmap['MolecularInteraction']['attribute']['interactionType']="""
Controlled vocabulary annotating the interaction type for example, "phosphorylation reaction". This annotation is meant to be human readable and may not be suitable for computing tasks, like reasoning, that require formal vocabulary systems. For instance, this information would be useful for display on a web page or for querying a database. The PSI-MI interaction type controlled vocabulary should be used. This is browsable at: 
http://www.ebi.ac.uk/ontology-lookup/browse.do?ontName=MI&termId=MI%3A0190&termName=interaction%20type
    """
    dmap['MolecularInteraction']['attribute']['left']="""
The participants on the left side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the left property may be either reactants or products. left is a sub-property of participants.
    """
    dmap['MolecularInteraction']['attribute']['participant']="""
This property lists the entities that participate in this interaction. For example, in a biochemical reaction, the participants are the union of the reactants and the products of the reaction. This property has a number of sub-properties, such as LEFT and RIGHT used in the biochemicalInteraction class. Any participant listed in a sub-property will automatically be assumed to also be in PARTICIPANTS by a number of software systems, including Protege, so this property should not contain any instances if there are instances contained in a sub-property.
    """
    dmap['MolecularInteraction']['attribute']['product']="""
The product of a template reaction.
    """
    dmap['MolecularInteraction']['attribute']['right']="""
The participants on the right side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the RIGHT property may be either reactants or products. RIGHT is a sub-property of PARTICIPANTS.
    """
    dmap['MolecularInteraction']['attribute']['template']="""
The template molecule that is used in this template reaction.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class MolecularInteraction
    dmap['MolecularInteraction']=dict()
    dmap['MolecularInteraction']['attribute']=dict()
    dmap['MolecularInteraction']['attribute']['cofactor']="PhysicalEntity"
    dmap['MolecularInteraction']['attribute']['controlled']="Entity"
    dmap['MolecularInteraction']['attribute']['controller']="Entity"
    dmap['MolecularInteraction']['attribute']['interactionType']="InteractionVocabulary"
    dmap['MolecularInteraction']['attribute']['left']="PhysicalEntity"
    dmap['MolecularInteraction']['attribute']['participant']="Entity"
    dmap['MolecularInteraction']['attribute']['product']="Entity"
    dmap['MolecularInteraction']['attribute']['right']="PhysicalEntity"
    dmap['MolecularInteraction']['attribute']['template']="Entity"
  
    return dmap    