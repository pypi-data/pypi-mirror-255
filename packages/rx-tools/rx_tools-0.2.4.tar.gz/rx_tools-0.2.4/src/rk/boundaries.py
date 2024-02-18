import utils_noroot as utnr
import re
import math

#--------------------------------------
class boundaries:
    log=utnr.getLogger('boundaries')
    #--------------------------
    def __init__(self, tp):
        self._bounds      = tp

        self._regex       = '([inf\d\.-]+),\s+([inf\d\.-]+)' 
        self._identifier  = None
        self._sbounds     = None
        self._initialized = False
    #--------------------------
    @property
    def data(self):
        self._initialize()

        return self._bounds
    #--------------------------
    @property
    def identifier(self):
        self._initialize()

        return self._identifier
    #--------------------------
    @property
    def sbounds(self):
        self._initialize()

        return self._sbounds
    #--------------------------
    def _initialize(self):
        if self._initialized:
            return

        if isinstance(self._bounds, str):
            self._str_to_tuple()

        self._check_tuple(self._bounds)
        for elm in self._bounds:
            self._check_tuple(elm)
            try:
                minv, maxv = elm
            except:
                self.log.error(f'Coordinate boundaries is not a tuple of two elements: {elm}')
                raise ValueError

            self._check_numeric(minv)
            self._check_numeric(maxv)

        self._identifier = self._get_identifier()
        self._sbounds    = self._get_sbounds()

        self._initialized = True
    #--------------------------
    def _get_identifier(self):
        l_name = [ f'{minv:.0f}_{maxv:.0f}' for minv, maxv in self._bounds]

        name = '_'.join(l_name)
        name = name.replace('.', 'p')

        return name
    #--------------------------
    def _get_sbounds(self):
        l_name = [ f'[{minv:.0f}, {maxv:.0f}]' for minv, maxv in self._bounds]
        name   = ', '.join(l_name)

        return name
    #--------------------------
    def _str_to_tuple(self):
        l_group = re.findall(self._regex, self._bounds)
        if l_group == []:
            self.log.error(f'Cannot find any bound in {self._bounds} using {self._regex}')
            raise ValueError

        l_coo = []
        for minv, maxv in l_group: 
            minv = self._cast_to_num(minv)
            maxv = self._cast_to_num(maxv)
            l_coo.append((minv, maxv))

        self._bounds = tuple(l_coo)
    #--------------------------
    def has_inf(self):
        self._initialize()

        for minv, maxv in self._bounds:
            if abs(minv) == math.inf or abs(maxv) == math.inf: 
                return True

        return False
    #--------------------------
    def _cast_to_num(self, val):
        if   val == '-inf':
            fval = -math.inf
        elif val ==  'inf':
            fval = +math.inf
        else:
            fval = float(val)

        return fval
    #--------------------------
    def _check_tuple(self, obj):
        if not isinstance(obj, tuple):
            self.log.error(f'Object is not a tuple: {obj}/{type(obj)}')
            raise TypeError
    #--------------------------
    def _check_numeric(self, val):
        if not isinstance(val, (int, float)):
            self.log.error(f'Value not an int or float: {val}')
            raise ValueError
    #--------------------------
    def __str__(self):
        self._initialize()

        axis=1
        val =''
        for minv, maxv in self._bounds:
            val += f'x{axis} in [{minv:<10.3f}, {maxv:<10.3f}]\n'
            axis+=1

        return val
    #--------------------------
    def __lt__(self, other):
        self._initialize()
        other._initialize()

        b1  = reversed( self._bounds)
        b2  = reversed(other._bounds)

        tb1 = tuple(b1)
        tb2 = tuple(b2)

        less_than = tb1 < tb2

        return less_than 
    #--------------------------
    def __eq__(self, other):
        return self.data == other.data
    #--------------------------
    def __hash__(self):
        return hash(self.data)
#--------------------------------------

