 
from biopax.sequencelocation import SequenceLocation
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class SequenceSite(SequenceLocation) :


    """
    Class SequenceSite 
    
              Definition: Describes a site on a sequence, i.e. the position of a single
      nucleotide or amino acid. Usage: A sequence site is always defined based on the
      reference sequence of the owning entity. For DNARegion and RNARegion it is
      relative to the region itself not the genome or full RNA molecule.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#SequenceSite"
        self._positionStatus=kwargs.get('positionStatus',None)  
        self._sequencePosition=kwargs.get('sequencePosition',None)  
  

##########getter
     
    def get_positionStatus(self):
        """
        Attribute _positionStatus  getter
                      The confidence status of the sequence position. This could be: EQUAL: The
      SEQUENCE-POSITION is known to be at the SEQUENCE-POSITION. GREATER-THAN: The
      site is greater than the SEQUENCE-POSITION. LESS-THAN: The site is less than the
      SEQUENCE-POSITION.

                """
        return self._positionStatus  
     
    def get_sequencePosition(self):
        """
        Attribute _sequencePosition  getter
                      The integer listed gives the position. The first base or amino acid is position
      1. In combination with the numeric value, the property 'POSITION-STATUS' allows
      to express fuzzy positions, e.g. 'less than 4'.

                """
        return self._sequencePosition  
  
##########setter
    
    @validator(value=str)  
 
    def set_positionStatus(self,value):
        self._positionStatus=value  
    
    @validator(value=int)  
 
    def set_sequencePosition(self,value):
        self._sequencePosition=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['positionStatus', 'sequencePosition']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['positionStatus']='str'  
      ma['sequencePosition']='int'  
      return ma



    def to_json(self):
        return tojson(self)
        

