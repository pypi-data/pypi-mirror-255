from numbers  import Number


TAB = '  '
MINUS_TAB = '- '
NL = '\n'
SEP = ': '
NaN = 'null'

def infer_repr(value):
    str_value = repr(value).lower()
    if str_value == 'nan' or str_value == 'none':
        return NaN
    if isinstance(value, Number):
        return str(value)
    if isinstance(value, str):
        #return '"{}"'.format(repr(value))
        return repr(value)
    if isinstance(value, list):
        #TODO !!
        return str(value)


class Entry():
    def __init__(self, parent=None, obj=None, ytype=None, is_ylist=None, is_parent_value=None, is_last=False):
        self.is_last = is_last
        self.parent = str(parent)
        self.obj = obj
        self.ytype = ytype
        self.is_ylist = is_ylist
        self.is_parent_value = is_parent_value
        self.is_write_ready = False
        
    @classmethod
    def from_dict(cls, obj, parent, is_ylist=False):
        this = cls()
        this.parent = parent
        this.is_ylist = is_ylist
        this.obj = obj
        this.obj = {str(k): infer_repr(v) for k,v in this.obj.items()}
        this.is_write_ready = True
        return this
        
    @classmethod
    def from_keyval(cls, key, val):
        key = str(key)
        this = cls()
        this.parent= key
        this.is_ylist = False
        this.is_parent_value = True
        this.obj = infer_repr(val)
        this.is_write_ready = True
        return this
        
    @classmethod
    def dict2d_to_list(cls, dict2d):
        return [cls.from_keyval(k,v) if not isinstance(v, dict) else 
                        cls.from_dict(v, parent=k, is_ylist=False)  
                        for k, v in dict2d.items()]
            
