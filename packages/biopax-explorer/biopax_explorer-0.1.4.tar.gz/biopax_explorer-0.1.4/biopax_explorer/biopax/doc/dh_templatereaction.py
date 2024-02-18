
from biopax.utils import gen_utils
 

class templatereaction_DocHelper():
  """
  Class templatereaction_DocHelper

  documentation helper for templatereaction
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='TemplateReaction'
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
    # class TemplateReaction
    dmap['TemplateReaction']=dict()
    dmap['TemplateReaction']['class']="""
Definiton: An interaction where a macromolecule is polymerized from a 
    template macromolecule. 

Rationale: This is an abstraction over multiple (not explicitly stated) biochemical 
    reactions. The ubiquitous molecules (NTP and amino acids) consumed are also usually
    omitted. Template reaction is non-stoichiometric, does not obey law of 
    mass conservation and temporally non-atomic. It, however, provides a 
    mechanism to capture processes that are central to all living organisms.  

Usage: Regulation of TemplateReaction, e.g. via a transcription factor can be 
    captured using TemplateReactionRegulation. TemplateReaction can also be 
    indirect  for example, it is not necessary to represent intermediary mRNA 
    for describing expression of a protein. It was decided to not subclass 
    TemplateReaction to subtypes such as transcription of translation for the 
    sake of  simplicity. If needed these subclasses can be added in the 
    future. 

Examples: Transcription, translation, replication, reverse transcription. E.g. 
    DNA to RNA is transcription, RNA to protein is translation and DNA to 
    protein is protein expression from DNA.
    """
    dmap['TemplateReaction']['attribute']=dict()
  
    dmap['TemplateReaction']['attribute']['product']="""
The product of a template reaction.
    """
    dmap['TemplateReaction']['attribute']['template']="""
The template molecule that is used in this template reaction.
    """
    dmap['TemplateReaction']['attribute']['templateDirection']="""
The direction of the template reaction on the template.
    """
    dmap['TemplateReaction']['attribute']['cofactor']="""
Any cofactor(s) or coenzyme(s) required for catalysis of the conversion by the enzyme. This is a suproperty of participants.
    """
    dmap['TemplateReaction']['attribute']['controlled']="""
The entity that is controlled, e.g., in a biochemical reaction, the reaction is controlled by an enzyme. Controlled is a sub-property of participants.
    """
    dmap['TemplateReaction']['attribute']['controller']="""
The controlling entity, e.g., in a biochemical reaction, an enzyme is the controlling entity of the reaction. CONTROLLER is a sub-property of PARTICIPANTS.
    """
    dmap['TemplateReaction']['attribute']['interactionType']="""
Controlled vocabulary annotating the interaction type for example, "phosphorylation reaction". This annotation is meant to be human readable and may not be suitable for computing tasks, like reasoning, that require formal vocabulary systems. For instance, this information would be useful for display on a web page or for querying a database. The PSI-MI interaction type controlled vocabulary should be used. This is browsable at: 
http://www.ebi.ac.uk/ontology-lookup/browse.do?ontName=MI&termId=MI%3A0190&termName=interaction%20type
    """
    dmap['TemplateReaction']['attribute']['left']="""
The participants on the left side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the left property may be either reactants or products. left is a sub-property of participants.
    """
    dmap['TemplateReaction']['attribute']['participant']="""
This property lists the entities that participate in this interaction. For example, in a biochemical reaction, the participants are the union of the reactants and the products of the reaction. This property has a number of sub-properties, such as LEFT and RIGHT used in the biochemicalInteraction class. Any participant listed in a sub-property will automatically be assumed to also be in PARTICIPANTS by a number of software systems, including Protege, so this property should not contain any instances if there are instances contained in a sub-property.
    """
    dmap['TemplateReaction']['attribute']['product']="""
The product of a template reaction.
    """
    dmap['TemplateReaction']['attribute']['right']="""
The participants on the right side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the RIGHT property may be either reactants or products. RIGHT is a sub-property of PARTICIPANTS.
    """
    dmap['TemplateReaction']['attribute']['template']="""
The template molecule that is used in this template reaction.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class TemplateReaction
    dmap['TemplateReaction']=dict()
    dmap['TemplateReaction']['attribute']=dict()
    dmap['TemplateReaction']['attribute']['product']="Entity"
    dmap['TemplateReaction']['attribute']['template']="Entity"
    dmap['TemplateReaction']['attribute']['templateDirection']="str"
    dmap['TemplateReaction']['attribute']['cofactor']="PhysicalEntity"
    dmap['TemplateReaction']['attribute']['controlled']="Entity"
    dmap['TemplateReaction']['attribute']['controller']="Entity"
    dmap['TemplateReaction']['attribute']['interactionType']="InteractionVocabulary"
    dmap['TemplateReaction']['attribute']['left']="PhysicalEntity"
    dmap['TemplateReaction']['attribute']['participant']="Entity"
    dmap['TemplateReaction']['attribute']['product']="Entity"
    dmap['TemplateReaction']['attribute']['right']="PhysicalEntity"
    dmap['TemplateReaction']['attribute']['template']="Entity"
  
    return dmap    