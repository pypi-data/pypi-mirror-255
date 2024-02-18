import Oasys.gRPC


# Metaclass for static properties and constants
class IncludeType(type):
    _consts = {'NATIVE', 'UNIX', 'WINDOWS'}

    def __getattr__(cls, name):
        if name in IncludeType._consts:
            return Oasys.D3PLOT._connection.classGetter(cls.__name__, name)

        raise AttributeError


class Include(Oasys.gRPC.OasysItem, metaclass=IncludeType):
    _props = {'label', 'name', 'parent'}


    def __del__(self):
        if not Oasys.D3PLOT._connection:
            return

        Oasys.D3PLOT._connection.destructor(self.__class__.__name__, self._handle)


    def __getattr__(self, name):
# If one of the properties we define then get it
        if name in Include._props:
            return Oasys.D3PLOT._connection.instanceGetter(self.__class__.__name__, self._handle, name)

        raise AttributeError


    def __setattr__(self, name, value):
# If one of the properties we define then set it
        if name in Include._props:
            Oasys.D3PLOT._connection.instanceSetter(self.__class__.__name__, self._handle, name, value)
            return

# Set the property locally
        self.__dict__[name] = value


# Static methods
    def First(model):
        """
        Returns the first include file in the model (or None if there are no include files in the model)

        Parameters
        ----------
        model : Model
            Model to get first include file in

        Returns
        -------
        Include
            Include object
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "First", model)

    def GetFromID(model, number):
        """
        Returns the include file in the model with number (or None if it does not exist)

        Parameters
        ----------
        model : Model
            Model to get include file in
        number : integer
            The number for the include file in the model. Note that include file numbers start at 1. 0 is the main file

        Returns
        -------
        Include
            Include object
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "GetFromID", model, number)

    def Last(model):
        """
        Returns the last include file in the model (or None if there are no include files in the model)

        Parameters
        ----------
        model : Model
            Model to get last include file in

        Returns
        -------
        Include
            Include object
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "Last", model)

    def Total(model):
        """
        Returns the total number of include files in the model

        Parameters
        ----------
        model : Model
            Model to get total in

        Returns
        -------
        int
            Number of includes
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "Total", model)



# Instance methods
    def Next(self):
        """
        Returns the next include file in the model (or None if there is not one)

        Returns
        -------
        Include
            Include object
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "Next")

    def Previous(self):
        """
        Returns the previous include file in the model (or None if there is not one)

        Returns
        -------
        Include
            Include object
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "Previous")

