
from biopax.utils import gen_utils
 

class complexassembly_DocHelper():
  """
  Class complexassembly_DocHelper

  documentation helper for complexassembly
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='ComplexAssembly'
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
    # class ComplexAssembly
    dmap['ComplexAssembly']=dict()
    dmap['ComplexAssembly']['class']="""
Definition: A conversion interaction in which a set of physical entities, at least one being a macromolecule (e.g. protein, RNA, DNA), aggregate to from a complex physicalEntity. One of the participants of a complexAssembly must be an instance of the class Complex. The modification of the physicalentities involved in the ComplexAssembly is captured via BindingFeature class.

Usage: This class is also used to represent complex disassembly. The assembly or disassembly of a complex is often a spontaneous process, in which case the direction of the complexAssembly (toward either assembly or disassembly) should be specified via the SPONTANEOUS property. Conversions in which participants obtain or lose CovalentBindingFeatures ( e.g. glycolysation of proteins) should be modeled with BiochemicalReaction.

Synonyms: aggregation, complex formation

Examples: Assembly of the TFB2 and TFB3 proteins into the TFIIH complex, and assembly of the ribosome through aggregation of its subunits.
    """
    dmap['ComplexAssembly']['attribute']=dict()
  
    dmap['ComplexAssembly']['attribute']['left']="""
The participants on the left side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the left property may be either reactants or products. left is a sub-property of participants.
    """
    dmap['ComplexAssembly']['attribute']['participantStoichiometry']="""
Stoichiometry of the left and right participants.
    """
    dmap['ComplexAssembly']['attribute']['right']="""
The participants on the right side of the conversion interaction. Since conversion interactions may proceed in either the left-to-right or right-to-left direction, occupants of the RIGHT property may be either reactants or products. RIGHT is a sub-property of PARTICIPANTS.
    """
    dmap['ComplexAssembly']['attribute']['conversionDirection']="""
This property represents the direction of the reaction. If a reaction will run in a single direction under all biological contexts then it is considered irreversible and has a direction. Otherwise it is reversible.
    """
    dmap['ComplexAssembly']['attribute']['spontaneous']="""
Specifies whether a conversion occurs spontaneously or not. If the spontaneity is not known, the SPONTANEOUS property should be left empty.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class ComplexAssembly
    dmap['ComplexAssembly']=dict()
    dmap['ComplexAssembly']['attribute']=dict()
    dmap['ComplexAssembly']['attribute']['left']="PhysicalEntity"
    dmap['ComplexAssembly']['attribute']['participantStoichiometry']="Stoichiometry"
    dmap['ComplexAssembly']['attribute']['right']="PhysicalEntity"
    dmap['ComplexAssembly']['attribute']['conversionDirection']="str"
    dmap['ComplexAssembly']['attribute']['spontaneous']="bool"
  
    return dmap    