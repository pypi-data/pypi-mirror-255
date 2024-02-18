from numbers import Number
from enum import IntEnum
from typing import Callable
from fractions import Fraction
from math import sqrt, prod, ceil, floor, trunc

def prime_factorization_int(n: int) -> list[tuple[int, int]]:
    if n == 1:
        return []
    elif n == 0:
        return []

    fac = []
    powers = []
    count = 0
    while n % 2 == 0:
        count += 1
        n = n // 2
    fac.append(2) if count > 0 else 0
    powers.append(count) if count > 0 else 0
    # n must be odd at this point
    # so a skip of 2 ( i = i + 2) can be used
    for i in range(3,int(sqrt(n))+1,2):
        # while i divides n , add i to the list
        count = 0
        while n % i== 0:
            count += 1
            n = n // i
        fac.append(i) if count > 0 else 0
        powers.append(count) if count > 0 else 0
    # Condition if n is a prime
    # number greater than 2
    if n > 2:
        fac.append(n)
        powers.append(1) 
    return [(factor, power) for factor, power in zip(fac, powers)]


def prime_factorization(n: float) -> list[tuple[int, int]]:
    positive_factors = []
    negative_factors = []

    top, bottom = Fraction(n).limit_denominator().as_integer_ratio()
    positive_factors = prime_factorization_int(top)
    negative_factors = [(factor, -power) for factor, power in prime_factorization_int(bottom)]
    final = positive_factors + negative_factors
    final.sort()
    return final

def custom_factors(n: float, custom_factors: list[float]):
    num_factors = prime_factorization(n)
    factors_check = [prime_factorization(custom) for custom in custom_factors]
    final = []
    for fac, custom in zip(factors_check, custom_factors):
        if all(prime_fac[0] in [e[0] for e in num_factors] for prime_fac in fac):
        #if all(prime_fac[0] == prime_n[0] and abs(prime_fac[1]) <= abs(prime_n[1]) for prime_fac, prime_n in zip(fac, num_factors)):
            matching = [a for a in num_factors if a[0] in [b[0] for b in fac]]
            not_matching = [a for a in num_factors if a not in matching]
            power = min([prime_n[1]//prime_fac[1] for prime_fac, prime_n in zip(fac, matching)], key=abs)
            num_factors = [(prime_n[0], prime_n[1] - prime_fac[1]*power) for prime_fac, prime_n in zip(fac, matching) if prime_n[1] - prime_fac[1]*power != 0] + not_matching
            final.append((custom, power))
    return final + num_factors

class DefaultUnits(IntEnum):
    none = 1
    meter = 2
    second = 3
    kilogram = 5
    kelvin = 7
    ampere = 11
    mol = 13
    candela = 17

    def __str__(self):
        match self:
            case DefaultUnits.none:
                return ""
            case DefaultUnits.meter:
                return "m"
            case DefaultUnits.second:
                return "s"
            case DefaultUnits.kilogram:
                return "kg"
            case DefaultUnits.kelvin:
                return "K"
            case DefaultUnits.ampere:
                return "A"
            case DefaultUnits.mol:
                return "mol"
            case DefaultUnits.candela:
                return "cd"

class Quantity:
    _SI_map: dict[int, str] = {2: "m", 3:"s", 5:"kg", 7:"K", 11:"A", 13:"mol", 17:"cd"}
    def __init__(self, value: Number = 1, units: float = 1, expected_units: list = [], custom_string: str = "", expect_self: bool = False) -> None:
        self.units = units
        self.value = value
        self.expected_units: list[Quantity] = expected_units
        self.unit_map = Quantity._SI_map
        self.custom_string: str = custom_string
        if expect_self:
            self.expected_units = [self]

    def _units_to_strings(self) -> tuple[Number, str]:
        units_vals = self.units
        value = self.value
        custom_map = self.unit_map | {unit.units:unit.custom_string for unit in self.expected_units}
        units = []
        factors = custom_factors(units_vals, [e.units for e in self.expected_units])
        for unit in self.expected_units:
            try:
                power = [e[1] for e in factors if e[0] == unit.units][0]
            except:
                continue
            value /= unit.value**power

        units = [f"{custom_map.get(e[0])}^{e[1]}" if e[1] != 1 else f"{custom_map.get(e[0])}" for e in factors]
        return value, " * ".join(units)

    def _set_custom_string(self, text: str) -> None:
        self.custom_string = text

    def _get_expected_units(self, other, division: bool = False) -> list | None:
        if self.expected_units[0].units == DefaultUnits.none or other.expected_units[0].units == DefaultUnits.none:
            unit1, unit2 = self.expected_units[0], other.expected_units[0]
            newUnit = Quantity(value=unit1.value*unit2.value, units=unit1.units*unit2.units)
            newUnit.custom_string = unit1.custom_string + unit2.custom_string
            return [newUnit]
        final_self = [a for a in self.expected_units if a.units not in [e.units for e in other.expected_units]]
        return final_self + other.expected_units
    
    def to_SI(self):
        self.expected_units = []
        return self
    
    def to_units(self, units):
        if not isinstance(units, list):
            units = [units]
        final = []
        for unit in units:
            final += unit.expected_units
        self.expected_units = final
        return self

    def __str__(self): 
        val, units = self._units_to_strings() 
        return f"{val} {units}"

    def __repr__(self):
        return str(self)

    # Multiplication
    
    def __mul__(self, other):
        if isinstance(other, Number):
            return Quantity(value=self.value*other, units=self.units, expected_units=self.expected_units, custom_string=self.custom_string)
        if isinstance(other, Quantity):
            return Quantity(value=self.value*other.value, units=self.units*other.units, expected_units=self._get_expected_units(other))

    def __rmul__(self, other):
        if isinstance(other, Number):
            return Quantity(value=self.value*other, units=self.units, expected_units=self.expected_units, custom_string=self.custom_string)

    def __truediv__(self, other):
        if isinstance(other, Number):
            return Quantity(value=self.value/other, units=self.units, custom_string=self.custom_string, expected_units=self.expected_units)
        if isinstance(other, Quantity):
            return Quantity(value=self.value/other.value, units=self.units/other.units, expected_units=self._get_expected_units(other))

    def __rtruediv__(self, other):
        if isinstance(other, Number):
            return Quantity(value=other/self.value, units=1/self.units, custom_string=self.custom_string, expected_units=self.expected_units)

    def __pow__(self, other):
        if isinstance(other, int):
            return Quantity(value=self.value**other, units=self.units**other, expected_units=self.expected_units)
    
    # Addition
    def __neg__(self):
        return Quantity(value=-self.value, units=self.units, custom_string=self.custom_string, expected_units=self.expected_units)
    def __add__(self, other):
        if isinstance(other, Quantity):
            if self.units != other.units:
                raise ValueError("Units do not match!")
            return Quantity(value=self.value+other.value, units=self.units, expected_units=self._get_expected_units(other))
        else:
            raise ValueError("Quantities can only be added with other quantities")
    def __radd__(self, other):
        if not isinstance(other, Quantity):
            raise ValueError("Quantities can only be added with other quantities")
    def __sub__(self, other):
        return self.__add__(-other)

    def __float__(self):
        return self.value
    
    # Rounding

    def __round_general__(self, method: Callable, decimals: int | None = None):
        value = self.value
        value /= prod([e.value for e in self.expected_units])
        rounded = method(value, decimals) if decimals is not None else method(value)
        value = rounded * prod([e.value for e in self.expected_units])
        return Quantity(value=value, units=self.units, custom_string=self.custom_string, expected_units=self.expected_units)
    def __round__(self, decimals = 0): return self.__round_general__(round, decimals)
    def __ceil__(self): return self.__round_general__(ceil)
    def __floor__(self): return self.__round_general__(floor)
    def __trunc__(self): return self.__round_general__(trunc)

    # For numpy support -> 

    def sqrt(self): return sqrt(self.value)
    def rint(self): return self.__round__()
    
# ------------ DEFINITIONS ---------------

def __define_unit(unit, symbol) -> None:
    unit._set_custom_string(symbol)
    unit.expected_units = [unit]

meter = Quantity(1, DefaultUnits.meter, custom_string="m", expect_self=True)
second = Quantity(1, DefaultUnits.second, custom_string="s", expect_self=True)
kilogram = Quantity(1, DefaultUnits.kilogram, custom_string="kg", expect_self=True)
gram = Quantity(1e-3, DefaultUnits.kilogram, custom_string="g", expect_self=True)
kelvin = Quantity(1, DefaultUnits.kelvin, custom_string="K", expect_self=True)
ampere = Quantity(1, DefaultUnits.ampere, custom_string="A", expect_self=True)
mol = Quantity(1, DefaultUnits.mol, custom_string="mol", expect_self= True)
candela = Quantity(1, DefaultUnits.candela,custom_string="cd", expect_self=True)

quetta = Quantity(1e30, units=DefaultUnits.none, custom_string="Q", expect_self=True)
ronna  = Quantity(1e27, units=DefaultUnits.none, custom_string="R", expect_self=True)
yotta  = Quantity(1e24, units=DefaultUnits.none, custom_string="Y", expect_self=True)
zetta  = Quantity(1e21, units=DefaultUnits.none, custom_string="Z", expect_self=True)
exa    = Quantity(1e18, units=DefaultUnits.none, custom_string="E", expect_self=True)
peta   = Quantity(1e15, units=DefaultUnits.none, custom_string="P", expect_self=True)
tera   = Quantity(1e12, units=DefaultUnits.none, custom_string="T", expect_self=True)
giga   = Quantity(1e9, units=DefaultUnits.none, custom_string="G", expect_self=True)
mega   = Quantity(1e6, units=DefaultUnits.none, custom_string="M", expect_self=True)
kilo   = Quantity(1e3, units=DefaultUnits.none, custom_string="k", expect_self=True)
hecto  = Quantity(1e2, units=DefaultUnits.none, custom_string="h", expect_self=True)
deca   = Quantity(1e1, units=DefaultUnits.none, custom_string="da", expect_self=True)
deci   = Quantity(1e-1, units=DefaultUnits.none, custom_string="d", expect_self=True)
centi  = Quantity(1e-2, units=DefaultUnits.none, custom_string="c", expect_self=True)
mili   = Quantity(1e-3, units=DefaultUnits.none, custom_string="m", expect_self=True)
micro  = Quantity(1e-6, units=DefaultUnits.none, custom_string="µ", expect_self=True)
nano   = Quantity(1e-9, units=DefaultUnits.none, custom_string="n", expect_self=True)
pico   = Quantity(1e-12, units=DefaultUnits.none, custom_string="p", expect_self=True)
femto  = Quantity(1e-15, units=DefaultUnits.none, custom_string="f", expect_self=True)
atto   = Quantity(1e-18, units=DefaultUnits.none, custom_string="a", expect_self=True)
zepto  = Quantity(1e-21, units=DefaultUnits.none, custom_string="z", expect_self=True)
yocto  = Quantity(1e-24, units=DefaultUnits.none, custom_string="y", expect_self=True)
ronto  = Quantity(1e-27, units=DefaultUnits.none, custom_string="r", expect_self=True)
quecto = Quantity(1e-30, units=DefaultUnits.none, custom_string="q", expect_self=True)

hertz = second**-1
__define_unit(hertz, "Hz")
newton = kilogram*meter*second**-2
__define_unit(newton, "N")
pascal = newton/meter**2
__define_unit(pascal, "Pa")
joule = newton*meter
__define_unit(joule, "J")
watt = joule/second
__define_unit(watt, "W")
coulomb = ampere*second
__define_unit(coulomb, "C")
volt = joule/coulomb
__define_unit(volt, "V")
electronvolt = 1.6e-19*joule
__define_unit(electronvolt, "eV")
farad = coulomb/volt
__define_unit(farad, "F")
ohm = volt/ampere
__define_unit(ohm, "Ω")
siemens = ohm**-1
__define_unit(siemens, "S")
weber = volt*second
__define_unit(weber, "Wb")
tesla = weber/meter**2
__define_unit(tesla, "T")
henry = weber/ampere
__define_unit(henry, "H")
# TODO: ºC

lumen = 1*candela
__define_unit(lumen, "lm")
lux = lumen/meter**2
__define_unit(lux, "lx")
becquerel = second**-1
__define_unit(becquerel, "Bq")
gray = joule/kilogram
__define_unit(gray, "Gy")
sievert = joule/kilogram
__define_unit(sievert, "Sv")
katal = mol*second**-1
__define_unit(katal, "kat")
