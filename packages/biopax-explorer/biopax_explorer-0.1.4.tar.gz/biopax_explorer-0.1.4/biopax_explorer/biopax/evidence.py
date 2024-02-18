##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class Evidence() :


    """
    Class Evidence 
    
              Definition: The support for a particular assertion, such as the existence of an
      interaction or pathway.  Usage: At least one of confidence, evidenceCode, or
      experimentalForm must be instantiated when creating an evidence instance. XREF
      may reference a publication describing the experimental evidence using a
      publicationXref or may store a description of the experiment in an experimental
      description database using a unificationXref (if the referenced experiment is
      the same) or relationshipXref (if it is not identical, but similar in some way
      e.g. similar in protocol). Evidence is meant to provide more information than
      just an xref to the source paper. Examples: A description of a molecular binding
      assay that was used to detect a protein-protein interaction.

    
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
        
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#Evidence"
        self._confidence=kwargs.get('confidence',None)  
        self._evidenceCode=kwargs.get('evidenceCode',None)  
        self._experimentalForm=kwargs.get('experimentalForm',None)  
        self._xref=kwargs.get('xref',None)  
  

##########getter
     
    def get_confidence(self):
        """
        Attribute _confidence  getter
                      Confidence in the containing instance.  Usually a statistical measure.

                """
        return self._confidence  
     
    def get_evidenceCode(self):
        """
        Attribute _evidenceCode  getter
                      A pointer to a term in an external controlled vocabulary, such as the GO, PSI-MI
      or BioCyc evidence codes, that describes the nature of the support, such as
      'traceable author statement' or 'yeast two-hybrid'.

                """
        return self._evidenceCode  
     
    def get_experimentalForm(self):
        """
        Attribute _experimentalForm  getter
                      The experimental forms associated with an evidence instance.

                """
        return self._experimentalForm  
     
    def get_xref(self):
        """
        Attribute _xref  getter
                      Values of this property define external cross-references from this entity to
      entities in external databases.

                """
        return self._xref  
  
##########setter
    
    @validator(value='biopax.Score')  
 
    def set_confidence(self,value):
        self._confidence=value  
    
    @validator(value='biopax.EvidenceCodeVocabulary')  
 
    def set_evidenceCode(self,value):
        self._evidenceCode=value  
    
    @validator(value='biopax.ExperimentalForm')  
 
    def set_experimentalForm(self,value):
        self._experimentalForm=value  
    
    @validator(value='biopax.Xref')  
 
    def set_xref(self,value):
        self._xref=value  
  




    def object_attributes(self):

      object_attribute_list=list()
      satt=['confidence', 'evidenceCode', 'experimentalForm', 'xref']
      for elem in satt:
        object_attribute_list.append(elem)
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=list()
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma['confidence']='Score'  
      ma['evidenceCode']='EvidenceCodeVocabulary'  
      ma['experimentalForm']='ExperimentalForm'  
      ma['xref']='Xref'  
      return ma



    def to_json(self):
        return tojson(self)
        

