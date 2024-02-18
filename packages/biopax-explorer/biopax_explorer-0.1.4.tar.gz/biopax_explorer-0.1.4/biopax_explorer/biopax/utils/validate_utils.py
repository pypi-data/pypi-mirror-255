import importlib, builtins
from functools import wraps
from typepy import  String,Integer,Bool,DateTime,RealNumber, TypeConversionError


def log_error(msg, func_name, logger):
    logger.log.error('error in %s: %s' % (func_name, msg))
    raise Exception('error in %s: %s' % (func_name, msg))

def raise_error(msg, func_name, logger):
    raise Exception('error in %s: %s' % (func_name, msg))

def ignore_error(msg, func_name, logger):
    pass


class BaseDecorator():
    _error_function = None
    _validation_function = None
    _logger = None

    def __init__(self, validation_function, error_function, logger=None):

        self._validation_function = validation_function
        self._error_function = error_function
        self._logger = logger

    __init__.__doc__ = __doc__



class ValidationDecorator(BaseDecorator):
    def __call__(self, **arg_to_check):
        return self._arg_validate(**arg_to_check)

    def _arg_validate(self, validate_func=None, error_func=None, **arg_to_check):
        """
        takes any number of args and kwargs coupled with a validator and passes
        them to the passed validation function.
        example for ValidateArgType:
            a=int, bool, str
            any value that does not have the same type as stated in the decorator will
            result in the error function being called
        """

        def on_decorator_call(func):
            all_args = list(func.__code__.co_varnames)

            @wraps(func)
            def on_call(*args, **kwargs):
                positional_args = all_args[:len(args)]

                msg = ''
                for (arg_name, validators) in arg_to_check.items():
                    if arg_name in kwargs:
                        msg, _ = self._validation_function(kwargs[arg_name], validators)
                    elif arg_name in positional_args:
                        msg, _ = self._validation_function(args[positional_args.index(arg_name)], validators)

                    if msg != '':
                        self._error_function(msg, func.__name__, self._logger)

                return func(*args, **kwargs)
            return on_call
        return on_decorator_call

 




class CValidateArgType(ValidationDecorator):
 
    def __init__(self, error_function, logger=None,allowNone=True):
        self.allowNone=allowNone
        super().__init__(self._check_arg_type, error_function, logger)
        self.cmodule=self. init_caster("typepy")

    def init_caster(self,mod):
      cmodule = importlib.import_module(mod)
      globals()[cmodule] = cmodule
      return cmodule

 

    def split_mod(self,a):
      sep="."
      cc=a.count(sep)
      if cc == 1:
        return a.split(sep)
    
      sp=a.split(sep, cc)
      #print(sp)
      a= sep.join(sp[:cc])
      sb=  sp[len(sp)-1:len(sp)]
      b= sep.join(sb)
      return a,b


    def class_for_name(self,module_name, class_name):
       m = importlib.import_module(module_name)
       c = getattr(m, class_name)
       return c

    def _check_arg_type(self, param_name, clsn):
        
        types=list()
 
        if isinstance(clsn, str):
           module_name, class_name=self.split_mod(clsn)
           cn=self.class_for_name(module_name, class_name)
           types.append(cn)
        else:
           types.append(clsn)


        return self._check_arg_type_from_class( param_name, tuple(types))
 

    def conversionClassMapping(self,cl):
          switch={
           'bool': "Bool",
           'datetime': "DateTime",
           'dict': "Dictionary",
           'list': "List",
           'str': "String",
           'float': "RealNumber",            
           'int': "Integer",            
          }
          clr= switch.get(cl.__name__,None)
          #print("||== == == %s %s" %(cl,clr))
          return clr

    def cast(self,value,conversionClsName,tp):

          class_ = getattr(self.cmodule, conversionClsName)
          instance = class_(value)
          val=instance.force_convert()

          #print("   >>>== == == %s %s %s" %(val,tp,conversionClsName))
          #type_ = getattr(builtins,tp)
          value=tp(val)
          return value


    def _check_arg_type_from_class(self, arg, types):
        msg, value = '', arg
        tp=types[0]
        if value is None and self.allowNone==True:
            return msg, value
 
        conversionClsName=self.conversionClassMapping(tp)
        #print("==conversionClsName=== === === %s %s %s  %s" %(value,type(value) ,tp,conversionClsName))
        if conversionClsName is not None:
          value=self.cast( value, conversionClsName,tp)
          
          #print("==cast=== === === %s %s %s  %s" %(value,type(value) ,tp,conversionClsName))

        if not isinstance(value, tp):
            msg = '%s has the type %s, not %s' %(value, type(value), tp)


        return msg, value






