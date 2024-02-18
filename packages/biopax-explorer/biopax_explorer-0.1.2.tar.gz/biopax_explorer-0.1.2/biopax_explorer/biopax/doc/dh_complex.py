
from biopax.utils import gen_utils
 

class complex_DocHelper():
  """
  Class complex_DocHelper

  documentation helper for complex
  
  """  
  def __init__(self):
    self.dmap=self.definitions()
    self.cln='Complex'
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
    # class Complex
    dmap['Complex']=dict()
    dmap['Complex']['class']="""
Definition: A physical entity whose structure is comprised of other physical entities bound to each other covalently or non-covalently, at least one of which is a macromolecule (e.g. protein, DNA, or RNA) and the Stoichiometry of the components are known. 

Comment: Complexes must be stable enough to function as a biological unit; in general, the temporary association of an enzyme with its substrate(s) should not be considered or represented as a complex. A complex is the physical product of an interaction (complexAssembly) and is not itself considered an interaction.
The boundaries on the size of complexes described by this class are not defined here, although possible, elements of the cell  such a mitochondria would typically not be described using this class (later versions of this ontology may include a cellularComponent class to represent these). The strength of binding cannot be described currently, but may be included in future versions of the ontology, depending on community need.
Examples: Ribosome, RNA polymerase II. Other examples of this class include complexes of multiple protein monomers and complexes of proteins and small molecules.
    """
    dmap['Complex']['attribute']=dict()
  
  
    dmap['Complex']['attribute']['component']=""
    dmap['Complex']['attribute']['componentStoichiometry']="""
The stoichiometry of components in a complex
    """
    dmap['Complex']['attribute']['cellularLocation']="""
A cellular location, e.g. 'cytoplasm'. This should reference a term in the Gene Ontology Cellular Component ontology. The location referred to by this property should be as specific as is known. If an interaction is known to occur in multiple locations, separate interactions (and physicalEntities) must be created for each different location.  If the location of a participant in a complex is unspecified, it may be assumed to be the same location as that of the complex. 

 A molecule in two different cellular locations are considered two different physical entities.
    """
    dmap['Complex']['attribute']['feature']="""
Sequence features of the owner physical entity.
    """
    dmap['Complex']['attribute']['memberPhysicalEntity']="""
This property stores the members of a generic physical entity. 

For representing homology generics a better way is to use generic entity references and generic features. However not all generic logic can be captured by this, such as complex generics or rare cases where feature cardinality is variable. Usages of this property should be limited to such cases.
    """
    dmap['Complex']['attribute']['notFeature']="""
Sequence features where the owner physical entity has a feature. If not specified, other potential features are not known.
    """
  
    return dmap


  def attr_type_def(self):
    dmap=dict()
    ####################################
    # class Complex
    dmap['Complex']=dict()
    dmap['Complex']['attribute']=dict()
    dmap['Complex']['attribute']['component']="PhysicalEntity"
    dmap['Complex']['attribute']['componentStoichiometry']="Stoichiometry"
    dmap['Complex']['attribute']['cellularLocation']="CellularLocationVocabulary"
    dmap['Complex']['attribute']['feature']="EntityFeature"
    dmap['Complex']['attribute']['memberPhysicalEntity']="PhysicalEntity"
    dmap['Complex']['attribute']['notFeature']="EntityFeature"
  
    return dmap    