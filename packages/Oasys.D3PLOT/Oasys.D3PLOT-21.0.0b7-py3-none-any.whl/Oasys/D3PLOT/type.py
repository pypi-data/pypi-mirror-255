import Oasys.gRPC


# Metaclass for static properties and constants
class TypeType(type):
    _consts = {'BEAM', 'BOLT', 'BWLD', 'CONTACT', 'CONX', 'CWLD', 'DES', 'ELEMENT', 'GROUP', 'GWLD', 'HSWA', 'HWLD', 'JOINT', 'MASS', 'MATERIAL', 'MIG', 'MODEL', 'NODE', 'NRB', 'PART', 'PRETENSIONER', 'RBOLT', 'RETRACTOR', 'RIGIDWALL', 'SBENT', 'SEATBELT', 'SECTION', 'SEGMENT', 'SET_BEAM', 'SET_DISCRETE', 'SET_NODE', 'SET_PART', 'SET_SHELL', 'SET_SOLID', 'SET_TSHELL', 'SHELL', 'SLIPRING', 'SOLID', 'SPC', 'SPH', 'SPRING', 'TSHELL', 'WINDOW', 'XSEC'}

    def __getattr__(cls, name):
        if name in TypeType._consts:
            return Oasys.D3PLOT._connection.classGetter(cls.__name__, name)

        raise AttributeError


class Type(Oasys.gRPC.OasysItem, metaclass=TypeType):


    def __del__(self):
        if not Oasys.D3PLOT._connection:
            return

        Oasys.D3PLOT._connection.destructor(self.__class__.__name__, self._handle)


    def __getattr__(self, name):
        raise AttributeError


    def __setattr__(self, name, value):
# Set the property locally
        self.__dict__[name] = value
