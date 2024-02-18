
from biopax.utils import gen_utils
 

class conversion_DocHelper():
  """
  Class conversion_DocHelper

  documentation helper for conversion
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='Conversion'
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
    # class Conversion
    dmap['Conversion']=dict()
    dmap['Conversion']['class']="""
Definition: An interaction in which molecules of one or more PhysicalEntity pools are physically transformed and become a member of one or more other PhysicalEntity pools.
Rationale: Conversion is Comments: Conversions in BioPAX are stoichiometric and closed world, i.e. it is assumed that all of the participants are listed. Both properties are due to the law of mass conservation.
Usage: Subclasses of conversion represent different types of transformation reflected by the properties of different physicalEntity. BiochemicalReactions will change the ModificationFeatures on a PhysicalEntity, Transport will change the Cellular Location and ComplexAssembly will change BindingFeatures. Generic Conversion class should only be used when the modification does not fit into a any of these classes.
Example: Opening of a voltage gated channel.
    """
    dmap['Conversion']['attribute']=dict()
  
    dmap['Conversion']['attribute']['left']="""
The participants on the left side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the left property may be either reactants or products. left is a sub-property of participants.
    """
    dmap['Conversion']['attribute']['participantStoichiometry']="""
Stoichiometry of the left and right participants.
    """
    dmap['Conversion']['attribute']['right']="""
The participants on the right side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the RIGHT property may be either reactants or products. RIGHT is a sub-property of PARTICIPANTS.
    """
    dmap['Conversion']['attribute']['conversionDirection']="""
This property represents the direction of the reaction. If a reaction will run in a single direction under all biological contexts then it is considered irreversible and has a direction. Otherwise it is reversible.
    """
    dmap['Conversion']['attribute']['spontaneous']="""
Specifies whether a conversion occurs spontaneously or not. If the spontaneity is not known, the SPONTANEOUS property should be left empty.
    """
    dmap['Conversion']['attribute']['cofactor']="""
Any cofactor(s) or coenzyme(s) required for catalysis of the conversion by the enzyme. This is a suproperty of participants.
    """
    dmap['Conversion']['attribute']['controlled']="""
The entity that is controlled, e.g., in a biochemical reaction, the reaction is controlled by an enzyme. Controlled is a sub-property of participants.
    """
    dmap['Conversion']['attribute']['controller']="""
The controlling entity, e.g., in a biochemical reaction, an enzyme is the controlling entity of the reaction. CONTROLLER is a sub-property of PARTICIPANTS.
    """
    dmap['Conversion']['attribute']['interactionType']="""
Controlled vocabulary annotating the interaction type for example, "phosphorylation reaction". This annotation is meant to be human readable and may not be suitable for computing tasks, like reasoning, that require formal vocabulary systems. For instance, this information would be useful for display on a web page or for querying a database. The PSI-MI interaction type controlled vocabulary should be used. This is browsable at: 
http://www.ebi.ac.uk/ontology-lookup/browse.do?ontName=MI&termId=MI%3A0190&termName=interaction%20type
    """
    dmap['Conversion']['attribute']['left']="""
The participants on the left side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the left property may be either reactants or products. left is a sub-property of participants.
    """
    dmap['Conversion']['attribute']['participant']="""
This property lists the entities that participate in this interaction. For example, in a biochemical reaction, the participants are the union of the reactants and the products of the reaction. This property has a number of sub-properties, such as LEFT and RIGHT used in the biochemicalInteraction class. Any participant listed in a sub-property will automatically be assumed to also be in PARTICIPANTS by a number of software systems, including Protege, so this property should not contain any instances if there are instances contained in a sub-property.
    """
    dmap['Conversion']['attribute']['product']="""
The product of a template reaction.
    """
    dmap['Conversion']['attribute']['right']="""
The participants on the right side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the RIGHT property may be either reactants or products. RIGHT is a sub-property of PARTICIPANTS.
    """
    dmap['Conversion']['attribute']['template']="""
The template molecule that is used in this template reaction.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class Conversion
    dmap['Conversion']=dict()
    dmap['Conversion']['attribute']=dict()
    dmap['Conversion']['attribute']['left']="PhysicalEntity"
    dmap['Conversion']['attribute']['participantStoichiometry']="Stoichiometry"
    dmap['Conversion']['attribute']['right']="PhysicalEntity"
    dmap['Conversion']['attribute']['conversionDirection']="str"
    dmap['Conversion']['attribute']['spontaneous']="bool"
    dmap['Conversion']['attribute']['cofactor']="PhysicalEntity"
    dmap['Conversion']['attribute']['controlled']="Entity"
    dmap['Conversion']['attribute']['controller']="Entity"
    dmap['Conversion']['attribute']['interactionType']="InteractionVocabulary"
    dmap['Conversion']['attribute']['left']="PhysicalEntity"
    dmap['Conversion']['attribute']['participant']="Entity"
    dmap['Conversion']['attribute']['product']="Entity"
    dmap['Conversion']['attribute']['right']="PhysicalEntity"
    dmap['Conversion']['attribute']['template']="Entity"
  
    return dmap    