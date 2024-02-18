 
from biopax.conversion import Conversion
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class ComplexAssembly(Conversion) :


    """
    Class ComplexAssembly 
    
              Definition: A conversion interaction in which a set of physical entities, at
      least one being a macromolecule (e.g. protein, RNA, DNA), aggregate to from a
      complex physicalEntity. One of the participants of a complexAssembly must be an
      instance of the class Complex. The modification of the physicalentities involved
      in the ComplexAssembly is captured via BindingFeature class.  Usage: This class
      is also used to represent complex disassembly. The assembly or disassembly of a
      complex is often a spontaneous process, in which case the direction of the
      complexAssembly (toward either assembly or disassembly) should be specified via
      the SPONTANEOUS property. Conversions in which participants obtain or lose
      CovalentBindingFeatures ( e.g. glycolysation of proteins) should be modeled with
      BiochemicalReaction.  Synonyms: aggregation, complex formation  Examples:
      Assembly of the TFB2 and TFB3 proteins into the TFIIH complex, and assembly of
      the ribosome through aggregation of its subunits.

    
    code generator : rdfobj (author F.Moreews 2023).
    
    """

    ##########constructor

    def __init__(self, *args, **kwargs):
        #args -- tuple of anonymous arguments
        #kwargs -- dictionary of named arguments
        
        self.pk=kwargs.get('pk',None)    
        self.pop_state=kwargs.get('pop_state',None)  
        self.exhausted=kwargs.get('exhausted',None)
        self.meta_label=None  
        
        super().__init__(*args, **kwargs) 
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#ComplexAssembly"
  

##########getter
  
##########setter
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      return ma



    def to_json(self):
        return tojson(self)
        

