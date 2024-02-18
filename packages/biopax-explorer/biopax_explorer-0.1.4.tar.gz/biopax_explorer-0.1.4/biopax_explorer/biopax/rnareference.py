 
from biopax.entityreference import EntityReference
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class RnaReference(EntityReference) :


    """
    Class RnaReference 
    
              Defintion: A RNA  reference is a grouping of several RNA entities that are
      either encoded by the same gene or replicates of the same genome.  Members can
      differ in celular location, sequence features and bound partners. Currently
      conformational states (such as hairpin) are not covered.

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#RnaReference"
        self._organism=kwargs.get('organism',None)  
        self._subRegion=kwargs.get('subRegion',None)  
        self._sequence=kwargs.get('sequence',None)  
  

##########getter
     
    def get_organism(self):
        """
        Attribute _organism  getter
                      An organism, e.g. 'Homo sapiens'. This is the organism that the entity is found
      in. Pathways may not have an organism associated with them, for instance,
      reference pathways from KEGG. Sequence-based entities (DNA, protein, RNA) may
      contain an xref to a sequence database that contains organism information, in
      which case the information should be consistent with the value for ORGANISM.

                """
        return self._organism  
     
    def get_subRegion(self):
        """
        Attribute _subRegion  getter
                      The sub region of a region or nucleic acid molecule. The sub region must be
      wholly part of the region, not outside of it.

                """
        return self._subRegion  
     
    def get_sequence(self):
        """
        Attribute _sequence  getter
                      Polymer sequence in uppercase letters. For DNA, usually A,C,G,T letters
      representing the nucleosides of adenine, cytosine, guanine and thymine,
      respectively; for RNA, usually A, C, U, G; for protein, usually the letters
      corresponding to the 20 letter IUPAC amino acid code.

                """
        return self._sequence  
  
##########setter
    
    @validator(value='biopax.BioSource')  
 
    def set_organism(self,value):
        self._organism=value  
    
    @validator(value='biopax.DnaRegionReference')  
 
    def set_subRegion(self,value):
        self._subRegion=value  
    
    @validator(value=str)  
 
    def set_sequence(self,value):
        self._sequence=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      satt=['organism', 'subRegion']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['sequence']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['organism']='BioSource'  
      ma['subRegion']='DnaRegionReference'  
      ma['sequence']='str'  
      return ma



    def to_json(self):
        return tojson(self)
        

