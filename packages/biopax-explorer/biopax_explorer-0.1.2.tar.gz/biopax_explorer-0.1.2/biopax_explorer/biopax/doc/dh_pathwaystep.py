
from biopax.utils import gen_utils
 

class pathwaystep_DocHelper():
  """
  Class pathwaystep_DocHelper

  documentation helper for pathwaystep
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='PathwayStep'
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
    # class PathwayStep
    dmap['PathwayStep']=dict()
    dmap['PathwayStep']['class']="""
Definition: A step in an ordered pathway.
Rationale: Some pathways can have a temporal order. For example,  if the pathway boundaries are based on a perturbation phenotype link, the pathway might start with the perturbing agent and end at gene expression leading to the observed changes. Pathway steps can represent directed compound graphs.
Usage: Multiple interactions may occur in a pathway step, each should be listed in the stepProcess property. Order relationships between pathway steps may be established with the nextStep slot. If the reaction contained in the step is a reversible biochemical reaction but physiologically has a direction in the context of this pathway, use the subclass BiochemicalPathwayStep.

Example: A metabolic pathway may contain a pathway step composed of one biochemical reaction (BR1) and one catalysis (CAT1) instance, where CAT1 describes the catalysis of BR1. The M phase of the cell cycle, defined as a pathway, precedes the G1 phase, also defined as a pathway.
    """
    dmap['PathwayStep']['attribute']=dict()
  
    dmap['PathwayStep']['attribute']['evidence']="""
Scientific evidence supporting the existence of the entity as described.
    """
    dmap['PathwayStep']['attribute']['nextStep']="""
The next step(s) of the pathway.  Contains zero or more pathwayStep instances.  If there is no next step, this property is empty. Multiple pathwayStep instances indicate pathway branching.
    """
    dmap['PathwayStep']['attribute']['stepConversion']="""
The central process that take place at this step of the biochemical pathway.
    """
    dmap['PathwayStep']['attribute']['stepProcess']="""
An interaction or a pathway that are a part of this pathway step.
    """
    dmap['PathwayStep']['attribute']['comment']="""
Comment on the data in the container class. This property should be used instead of the OWL documentation elements (rdfs:comment) for instances because information in 'comment' is data to be exchanged, whereas the rdfs:comment field is used for metadata about the structure of the BioPAX ontology.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class PathwayStep
    dmap['PathwayStep']=dict()
    dmap['PathwayStep']['attribute']=dict()
    dmap['PathwayStep']['attribute']['evidence']="Evidence"
    dmap['PathwayStep']['attribute']['nextStep']="PathwayStep"
    dmap['PathwayStep']['attribute']['stepConversion']="Conversion"
    dmap['PathwayStep']['attribute']['stepProcess']="Interaction"
    dmap['PathwayStep']['attribute']['comment']="str"
  
    return dmap    