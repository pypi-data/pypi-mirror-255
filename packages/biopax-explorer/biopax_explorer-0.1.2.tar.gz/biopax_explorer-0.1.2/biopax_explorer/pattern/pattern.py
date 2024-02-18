import  rdfobj.pattern as pa
import  rdfobj.mapper as ma
from . import   processing    as pr
from biopax_explorer.biopax.utils import gen_utils
# 
class Pattern(pa.Pattern):
    
    """
    This class holds a list of Step objects containing Patterns or LocalProcessings.
    It abstracts a query pattern.
    """
    def __init__(self):
         
         super().__init__()

#
class Step(pa.Step):
    """
    This class holds two kinds of data:
    - a list of EntityNodes used to generate a SPARQL query, or
    - a LocalProcessing that enables local in-memory filter operations on entities.

    Args:
        core (list): A list of EntityNodes used to generate a SPARQL query.
        add_children (bool): Whether to add children nodes (default is True).
        op (str): The operation to apply when combining multiple Step objects (default is "UNION").
    """
    def __init__(self, core, add_children = True, op="UNION"):
         
         super().__init__(core, add_children, op)
#
class LocalProcessing(pa.LocalProcessing):
    """
    This class manages 'in-memory processing' to post-process a SPARQL query.
    """
    def __init__(self):
         
         super().__init__()         


class DataPump(pa.DataPump):
    """
    This class fills the entities with void attributes.
    It is designed to be the core attribute of a Step class instance.

    Args:
        level (int): The level for the data pump (default is 1).
    """
    def __init__(self,level=1):
         
         super().__init__(level)         




#
class ProcessingCollection(pr.ProcessingCollection):
    """
    This class manages a list of referenced 'in-memory processing'.
    """
    def __init__(self):
         
         super().__init__()      

#
          
class PatternExecutor(pa.PatternExecutor):
    """
    This class manages the execution of a 'Pattern' instance.

    Args:
        gen_utils (module): Meta model python module from the target domain module (biopax).
        db (str): Database name for API connection.
        dataset (str): Dataset name for API connection.
        blacklist (list): A list of entities to be excluded.
        doProcess (bool): True to activate (default is True).
    """
    def __init__(self,db=None,dataset=None,blacklist=None,doProcess=True):
         geut=gen_utils
         super().__init__(geut,db,dataset,blacklist ,doProcess ) 
         
#
class PK(ma.PK):
    """
    Utility class to mock model entities with a lower memory footprint.

    Args:
        pk (str): Primary key of the entity (URI).
        cls (str): Simple entity class name.
    """
    def __init__(self,pk,cls=None):
        super().__init__(pk,cls)





