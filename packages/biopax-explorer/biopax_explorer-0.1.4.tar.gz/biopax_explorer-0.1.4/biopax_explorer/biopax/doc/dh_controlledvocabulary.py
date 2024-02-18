
from biopax.utils import gen_utils
 

class controlledvocabulary_DocHelper():
  """
  Class controlledvocabulary_DocHelper

  documentation helper for controlledvocabulary
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='ControlledVocabulary'
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
    # class ControlledVocabulary
    dmap['ControlledVocabulary']=dict()
    dmap['ControlledVocabulary']['class']="""
Definition: This class represents a term from an external controlled vocabulary (CV).
Rationale: Controlled Vocabularies mark cases where BioPAX delegates the representation of a complex biological phenomena to an external controlled vocabulary development effort such as Gene Ontology. Each subclass of this class represents one such case and often has an associated "Best-Practice" external resource to use. See the documentation of each subclass for more specific information. Correct usage of controlled vocabularies are critical to data exchange and integration.
Usage: The individuals belonging to this class must unambiguously refer to the source controlled vocabulary. This can be achieved in two manners:
The xref property of this class is restricted to the unification xref class. It must point to the source controlled vocabulary.
Alternatively the rdf-id of the member individuals can be set to the designated MIRIAM URN.
It is a best practice to do both whenever possible.
Although it is possible to use multiple unification xrefs to identify semantically identical terms across alternative controlled vocabularies, this is not a recommended practice as it might lead to maintenance issues as the controlled vocabularies change.
There is no recommended use-case for directly instantiating this class. Please use its subclasses instead.
    """
    dmap['ControlledVocabulary']['attribute']=dict()
  
    dmap['ControlledVocabulary']['attribute']['xref']="""
Values of this property define external cross-references from this entity to entities in external databases.
    """
    dmap['ControlledVocabulary']['attribute']['term']="""
The external controlled vocabulary term.
    """
    dmap['ControlledVocabulary']['attribute']['comment']="""
Comment on the data in the container class. This property should be used instead of the OWL documentation elements (rdfs:comment) for instances because information in 'comment' is data to be exchanged, whereas the rdfs:comment field is used for metadata about the structure of the BioPAX ontology.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class ControlledVocabulary
    dmap['ControlledVocabulary']=dict()
    dmap['ControlledVocabulary']['attribute']=dict()
    dmap['ControlledVocabulary']['attribute']['xref']="Xref"
    dmap['ControlledVocabulary']['attribute']['term']="str"
    dmap['ControlledVocabulary']['attribute']['comment']="str"
  
    return dmap    