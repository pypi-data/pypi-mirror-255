
from biopax.utils import gen_utils
 

class biochemicalpathwaystep_DocHelper():
  """
  Class biochemicalpathwaystep_DocHelper

  documentation helper for biochemicalpathwaystep
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='BiochemicalPathwayStep'
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
    # class BiochemicalPathwayStep
    dmap['BiochemicalPathwayStep']=dict()
    dmap['BiochemicalPathwayStep']['class']="""
Definition: Imposes ordering on a step in a biochemical pathway. 
Retionale: A biochemical reaction can be reversible by itself, but can be physiologically directed in the context of a pathway, for instance due to flux of reactants and products. 
Usage: Only one conversion interaction can be ordered at a time, but multiple catalysis or modulation instances can be part of one step.
    """
    dmap['BiochemicalPathwayStep']['attribute']=dict()
  
    dmap['BiochemicalPathwayStep']['attribute']['stepConversion']="""
The central process that take place at this step of the biochemical pathway.
    """
    dmap['BiochemicalPathwayStep']['attribute']['stepDirection']="""
Direction of the conversion in this particular pathway context. 
This property can be used for annotating direction of enzymatic activity. Even if an enzyme catalyzes a reaction reversibly, the flow of matter through the pathway will force the equilibrium in a given direction for that particular pathway.
    """
    dmap['BiochemicalPathwayStep']['attribute']['evidence']="""
Scientific evidence supporting the existence of the entity as described.
    """
    dmap['BiochemicalPathwayStep']['attribute']['nextStep']="""
The next step(s) of the pathway.  Contains zero or more pathwayStep instances.  If there is no next step, this property is empty. Multiple pathwayStep instances indicate pathway branching.
    """
    dmap['BiochemicalPathwayStep']['attribute']['stepConversion']="""
The central process that take place at this step of the biochemical pathway.
    """
    dmap['BiochemicalPathwayStep']['attribute']['stepProcess']="""
An interaction or a pathway that are a part of this pathway step.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class BiochemicalPathwayStep
    dmap['BiochemicalPathwayStep']=dict()
    dmap['BiochemicalPathwayStep']['attribute']=dict()
    dmap['BiochemicalPathwayStep']['attribute']['stepConversion']="Conversion"
    dmap['BiochemicalPathwayStep']['attribute']['stepDirection']="str"
    dmap['BiochemicalPathwayStep']['attribute']['evidence']="Evidence"
    dmap['BiochemicalPathwayStep']['attribute']['nextStep']="PathwayStep"
    dmap['BiochemicalPathwayStep']['attribute']['stepConversion']="Conversion"
    dmap['BiochemicalPathwayStep']['attribute']['stepProcess']="Interaction"
  
    return dmap    