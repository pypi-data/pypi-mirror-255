 
from biopax.xref import Xref
##############################
 


 
from biopax.utils.class_utils import tostring,tojson
from biopax.utils.validate_utils import CValidateArgType,raise_error





validator = CValidateArgType(raise_error, logger=None)

@tostring
class PublicationXref(Xref) :


    """
    Class PublicationXref 
    
              Definition: An xref that defines a reference to a publication such as a book,
      journal article, web page, or software manual. Usage:  The reference may or may
      not be in a database, although references to PubMed are preferred when possible.
      The publication should make a direct reference to the instance it is attached
      to. Publication xrefs should make use of PubMed IDs wherever possible. The DB
      property of an xref to an entry in PubMed should use the string "PubMed" and not
      "MEDLINE". Examples: PubMed:10234245

    
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
        self.rdf_type="http://www.biopax.org/release/biopax-level3.owl#PublicationXref"
        self._author=kwargs.get('author',None)  
        self._source=kwargs.get('source',None)  
        self._title=kwargs.get('title',None)  
        self._url=kwargs.get('url',None)  
        self._year=kwargs.get('year',None)  
  

##########getter
     
    def get_author(self):
        """
        Attribute _author  getter
                      The authors of this publication, one per property value.

                """
        return self._author  
     
    def get_source(self):
        """
        Attribute _source  getter
                      The source  in which the reference was published, such as: a book title, or a
      journal title and volume and pages.

                """
        return self._source  
     
    def get_title(self):
        """
        Attribute _title  getter
                      The title of the publication.

                """
        return self._title  
     
    def get_url(self):
        """
        Attribute _url  getter
                      The URL at which the publication can be found, if it is available through the
      Web.

                """
        return self._url  
     
    def get_year(self):
        """
        Attribute _year  getter
                      The year in which this publication was published.

                """
        return self._year  
  
##########setter
    
    @validator(value=str)  
 
    def set_author(self,value):
        self._author=value  
    
    @validator(value=str)  
 
    def set_source(self,value):
        self._source=value  
    
    @validator(value=str)  
 
    def set_title(self,value):
        self._title=value  
    
    @validator(value=str)  
 
    def set_url(self,value):
        self._url=value  
    
    @validator(value=int)  
 
    def set_year(self,value):
        self._year=value  
  




    def object_attributes(self):

      object_attribute_list=super().object_attributes() 
      return object_attribute_list
 

    def type_attributes(self):
 
      type_attribute_list=super().type_attributes() 
      satt=['author', 'source', 'title', 'url', 'year']
      for elem in satt:
        type_attribute_list.append(elem)
      return type_attribute_list
 
#####get attributes types 
    def attribute_type_by_name(self):
      ma=dict()
      ma=super().attribute_type_by_name() 
      ma['author']='str'  
      ma['source']='str'  
      ma['title']='str'  
      ma['url']='str'  
      ma['year']='int'  
      return ma



    def to_json(self):
        return tojson(self)
        

