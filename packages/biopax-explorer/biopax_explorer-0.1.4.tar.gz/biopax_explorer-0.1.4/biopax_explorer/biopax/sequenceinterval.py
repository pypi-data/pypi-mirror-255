 
from biopax.sequencelocation import SequenceLocation
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class SequenceInterval(SequenceLocation) :


    """
    Class SequenceInterval 
    
              Definition: An interval on a sequence.  Usage: Interval is defined as an ordered
      pair of SequenceSites. All of the sequence from the begin site to the end site
      (inclusive) is described, not any subset.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#SequenceInterval"
        self._sequenceIntervalBegin=kwargs.get('sequenceIntervalBegin',None)  
        self._sequenceIntervalEnd=kwargs.get('sequenceIntervalEnd',None)  
  

##########getter
     
    def get_sequenceIntervalBegin(self):
        """
        Attribute _sequenceIntervalBegin  getter
                      The begin position of a sequence interval.

                """
        return self._sequenceIntervalBegin  
     
    def get_sequenceIntervalEnd(self):
        """
        Attribute _sequenceIntervalEnd  getter
                      The end position of a sequence interval.

                """
        return self._sequenceIntervalEnd  
  
##########setter
    
    @validator(value='biopax.SequenceSite')  
 
    def set_sequenceIntervalBegin(self,value):
        self._sequenceIntervalBegin=value  
    
    @validator(value='biopax.SequenceSite')  
 
    def set_sequenceIntervalEnd(self,value):
        self._sequenceIntervalEnd=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['sequenceIntervalBegin', 'sequenceIntervalEnd']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['sequenceIntervalBegin']='SequenceSite'  
      ma['sequenceIntervalEnd']='SequenceSite'  
      return ma



    def to_json(self):
        return tojson(self)
        

