
from rdfobj.mapper import PK
from biopax import *


class ProcessingCollection():
    """
    A class representing a processing collection.
    """

    def __init__(self ):
      self.localProcessingCollection=self.defineLocalProcessingCollection()

    def defineLocalProcessingCollection(self):
      """
        Define the local processing collection.

        Returns:
            dict: A dictionary containing the local processing collection.
      """
      c=dict()
      #c['voidOuput']=voidOuput
      c['blacklistFilter']=blacklistFilter
      c['usedToProduceProcessing'] = usedToProduceProcessing
      return c
    

################ProcessingCollection filters############
class BlackListFilter():
  """
    A class representing a Black List Filter.
  """
  def __init__(self, blacklist):
    self.blacklist=blacklist

  #remove all uris  nodes in blacklist
  def filter(self,sequence):
    """
        Remove all URIs in the blacklist from the given sequence.

        Args:
            sequence (list): The input sequence to be filtered.

        Returns:
            list: The filtered sequence.
    """
    filtered = filter(self.funcf, sequence) 
    return filtered

  def funcf(self,el):
    """
        Function to check if an element is in the blacklist.

        Args:
            el: The element to check.

        Returns:
            bool: True if the element is not in the blacklist, False otherwise.
    """
    if self.blacklist is None:
       blacklist=[]
    else:
       blacklist=self.blacklist

    if (el.pk in  blacklist):
        return False
    else:
        return True    

 

def blacklistFilter(param):
    """
    Filter the collection using a blacklist.

    Args:
        param (dict): A dictionary containing parameters.

    Returns:
        list: The filtered collection.
    """
    blacklist=param['blacklist']
    collection=param['collection']
    bl= BlackListFilter(blacklist)
    filtered=bl.filter(collection)     
    return list(filtered)

def usedToProduceProcessing(param):
  """
    Eliminate the matches where the small molecule at the left and at the right is the same.

    Args:
        param (dict): A dictionary containing parameters.

    Returns:
        list: The processed collection after elimination of matches.
  """

  collection: list[list[PK]] = param['collection']
  list_not_allowed:list[tuple] = []
  collection_res = []
  for pk_list in collection:
    sm_list = [o for o in pk_list if o.cls == 'SmallMolecule']
    if sm_list[0].pk == sm_list[1].pk:
      list_not_allowed.append((str(pk_list[0].pk), sm_list[0].pk))
  
  for pk_list in collection:
    sm_list = [o for o in pk_list if o.cls == 'SmallMolecule']
    smr_list = [o for o in pk_list if o.cls == 'SmallMoleculeReference']
    if not(smr_list[0] == smr_list[1]) and not((str(pk_list[0].pk), sm_list[0].pk) in list_not_allowed or (str(pk_list[0].pk), sm_list[1].pk) in list_not_allowed):
       collection_res.append(pk_list)
  return collection_res
