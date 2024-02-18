import Oasys.gRPC


# Metaclass for static properties and constants
class ConstantType(type):
    _consts = {'ALL', 'BASIC', 'BOTTOM', 'CONST_X', 'CONST_Y', 'CONST_Z', 'CURRENT_VAL', 'CUT_SECTION', 'CYLINDRICAL', 'DEFORMED', 'DELETE', 'FAMILY', 'GLOBAL', 'GT', 'GTEQ', 'INCLUDE', 'INTERSECTION', 'LEAVE', 'LOCAL', 'LS_DYNA', 'LT', 'LTEQ', 'MAGNITUDE', 'MATERIAL', 'MAX', 'MIDDLE', 'MIN', 'MODEL', 'N3', 'NEIPH', 'NEIPS', 'NEIPT', 'NIP_B', 'NIP_H', 'NIP_S', 'NIP_T', 'NORMAL', 'N_ON_PLAN', 'N_UBMS', 'N_UBMV', 'N_UNOS', 'N_UNOV', 'N_USSS', 'N_USST', 'OFF', 'OMIT', 'ON', 'OR_AND_V', 'OUTLINE', 'SCREEN', 'STATE', 'TOP', 'TRANSPARENT', 'UNION', 'USER', 'USER_DEFINED', 'X', 'XX', 'XY', 'Y', 'YY', 'YZ', 'Z', 'ZX', 'ZZ'}

    def __getattr__(cls, name):
        if name in ConstantType._consts:
            return Oasys.D3PLOT._connection.classGetter(cls.__name__, name)

        raise AttributeError


class Constant(Oasys.gRPC.OasysItem, metaclass=ConstantType):


    def __del__(self):
        if not Oasys.D3PLOT._connection:
            return

        Oasys.D3PLOT._connection.destructor(self.__class__.__name__, self._handle)


    def __getattr__(self, name):
        raise AttributeError


    def __setattr__(self, name, value):
# Set the property locally
        self.__dict__[name] = value
