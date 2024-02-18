
from biopax.utils import gen_utils
 

class transport_DocHelper():
  """
  Class transport_DocHelper

  documentation helper for transport
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='Transport'
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
    # class Transport
    dmap['Transport']=dict()
    dmap['Transport']['class']="""
Definition: An conversion in which molecules of one or more physicalEntity pools change their subcellular location and become a member of one or more other physicalEntity pools. A transport interaction does not include the transporter entity, even if one is required in order for the transport to occur. Instead, transporters are linked to transport interactions via the catalysis class.

Usage: If there is a simultaneous chemical modification of the participant(s), use transportWithBiochemicalReaction class.

Synonyms: translocation.

Examples: The movement of Na+ into the cell through an open voltage-gated channel.
    """
    dmap['Transport']['attribute']=dict()
  
    dmap['Transport']['attribute']['left']="""
The participants on the left side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the left property may be either reactants or products. left is a sub-property of participants.
    """
    dmap['Transport']['attribute']['participantStoichiometry']="""
Stoichiometry of the left and right participants.
    """
    dmap['Transport']['attribute']['right']="""
The participants on the right side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the RIGHT property may be either reactants or products. RIGHT is a sub-property of PARTICIPANTS.
    """
    dmap['Transport']['attribute']['conversionDirection']="""
This property represents the direction of the reaction. If a reaction will run in a single direction under all biological contexts then it is considered irreversible and has a direction. Otherwise it is reversible.
    """
    dmap['Transport']['attribute']['spontaneous']="""
Specifies whether a conversion occurs spontaneously or not. If the spontaneity is not known, the SPONTANEOUS property should be left empty.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class Transport
    dmap['Transport']=dict()
    dmap['Transport']['attribute']=dict()
    dmap['Transport']['attribute']['left']="PhysicalEntity"
    dmap['Transport']['attribute']['participantStoichiometry']="Stoichiometry"
    dmap['Transport']['attribute']['right']="PhysicalEntity"
    dmap['Transport']['attribute']['conversionDirection']="str"
    dmap['Transport']['attribute']['spontaneous']="bool"
  
    return dmap    