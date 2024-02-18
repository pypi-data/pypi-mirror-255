
from biopax.utils import gen_utils
 

class experimentalform_DocHelper():
  """
  Class experimentalform_DocHelper

  documentation helper for experimentalform
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='ExperimentalForm'
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
    # class ExperimentalForm
    dmap['ExperimentalForm']=dict()
    dmap['ExperimentalForm']['class']="""
Definition: The form of a physical entity in a particular experiment, as it may be modified for purposes of experimental design.
Examples: A His-tagged protein in a binding assay. A protein can be tagged by multiple tags, so can have more than 1 experimental form type terms
    """
    dmap['ExperimentalForm']['attribute']=dict()
  
    dmap['ExperimentalForm']['attribute']['experimentalFeature']="""
A feature of the experimental form of the participant of the interaction, such as a protein tag. It is not expected to occur in vivo or be necessary for the interaction.
    """
    dmap['ExperimentalForm']['attribute']['experimentalFormDescription']="""
Descriptor of this experimental form from a controlled vocabulary.
    """
    dmap['ExperimentalForm']['attribute']['experimentalFormEntity']="""
The gene or physical entity that this experimental form describes.
    """
    dmap['ExperimentalForm']['attribute']['comment']="""
Comment on the data in the container class. This property should be used instead of the OWL documentation elements (rdfs:comment) for instances because information in 'comment' is data to be exchanged, whereas the rdfs:comment field is used for metadata about the structure of the BioPAX ontology.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class ExperimentalForm
    dmap['ExperimentalForm']=dict()
    dmap['ExperimentalForm']['attribute']=dict()
    dmap['ExperimentalForm']['attribute']['experimentalFeature']="EntityFeature"
    dmap['ExperimentalForm']['attribute']['experimentalFormDescription']="ExperimentalFormVocabulary"
    dmap['ExperimentalForm']['attribute']['experimentalFormEntity']="Gene"
    dmap['ExperimentalForm']['attribute']['comment']="str"
  
    return dmap    