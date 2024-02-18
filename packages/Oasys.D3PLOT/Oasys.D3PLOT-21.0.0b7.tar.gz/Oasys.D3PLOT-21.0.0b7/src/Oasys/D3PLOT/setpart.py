import Oasys.gRPC


# Metaclass for static properties and constants
class SetPartType(type):

    def __getattr__(cls, name):

        raise AttributeError


class SetPart(Oasys.gRPC.OasysItem, metaclass=SetPartType):
    _props = {'include', 'index', 'label', 'model', 'title', 'total', 'type'}


    def __del__(self):
        if not Oasys.D3PLOT._connection:
            return

        Oasys.D3PLOT._connection.destructor(self.__class__.__name__, self._handle)


    def __getattr__(self, name):
# If one of the properties we define then get it
        if name in SetPart._props:
            return Oasys.D3PLOT._connection.instanceGetter(self.__class__.__name__, self._handle, name)

        raise AttributeError


    def __setattr__(self, name, value):
# If one of the properties we define then set it
        if name in SetPart._props:
            Oasys.D3PLOT._connection.instanceSetter(self.__class__.__name__, self._handle, name, value)
            return

# Set the property locally
        self.__dict__[name] = value


# Static methods
    def First(model):
        """
        Returns the first part set in the model (or None if there are no part sets in the model)

        Parameters
        ----------
        model : Model
            Model to get first part set in

        Returns
        -------
        SetPart
            SetPart object
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "First", model)

    def FlagAll(model, flag):
        """
        Flags all of the part sets in the model with a defined flag

        Parameters
        ----------
        model : Model
            Model that all the part sets will be flagged in
        flag : Flag
            Flag (see AllocateFlag) to set on the part sets

        Returns
        -------
        None
            No return value
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "FlagAll", model, flag)

    def GetAll(model):
        """
        Gets all of the part sets in the model

        Parameters
        ----------
        model : Model
            Model that all the part sets are in

        Returns
        -------
        array
            Array of :py:class:`SetPart<SetPart>` objects
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "GetAll", model)

    def GetFlagged(model, flag):
        """
        Gets all of the part sets in the model flagged with a defined flag

        Parameters
        ----------
        model : Model
            Model that the flagged part sets are in
        flag : Flag
            Flag (see AllocateFlag) set on the part sets to get

        Returns
        -------
        array
            Array of :py:class:`SetPart<SetPart>` objects
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "GetFlagged", model, flag)

    def GetFromID(model, label):
        """
        Returns the SetPart object for part set in model with label (or None if it does not exist)

        Parameters
        ----------
        model : Model
            Model to get part set in
        label : integer
            The LS-DYNA label for the part set in the model

        Returns
        -------
        SetPart
            SetPart object
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "GetFromID", model, label)

    def GetFromIndex(model, index):
        """
        Returns the SetPart object for part set in model with index (or None if it does not exist)

        Parameters
        ----------
        model : Model
            Model to get part set in
        index : integer
            The D3PLOT internal index in the model for part set

        Returns
        -------
        SetPart
            SetPart object
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "GetFromIndex", model, index)

    def Last(model):
        """
        Returns the last part set in the model (or None if there are no part sets in the model)

        Parameters
        ----------
        model : Model
            Model to get last part set in

        Returns
        -------
        SetPart
            SetPart object
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "Last", model)

    def Total(model):
        """
        Returns the total number of part sets in the model

        Parameters
        ----------
        model : Model
            Model to get total in

        Returns
        -------
        integer
            The number of part sets
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "Total", model)

    def UnflagAll(model, flag):
        """
        Unsets a defined flag on all of the part sets in the model

        Parameters
        ----------
        model : Model
            Model that the defined flag for all part sets will be unset in
        flag : Flag
            Flag (see AllocateFlag) to unset on the part sets

        Returns
        -------
        None
            No return value
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "UnflagAll", model, flag)



# Instance methods
    def AllItems(self):
        """
        Returns all of the part items for the part set in the model

        Returns
        -------
        list
            list of Part objects
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "AllItems")

    def ClearFlag(self, flag):
        """
        Clears a flag on a part set

        Parameters
        ----------
        flag : Flag
            Flag (see AllocateFlag) to clear on the part set

        Returns
        -------
        None
            No return value
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "ClearFlag", flag)

    def Flagged(self, flag):
        """
        Checks if the part set is flagged or not

        Parameters
        ----------
        flag : Flag
            Flag (see AllocateFlag) to test on the part set

        Returns
        -------
        boolean
            True if flagged, False if not
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "Flagged", flag)

    def Item(self, index):
        """
        Returns a part item from the part set in the model

        Parameters
        ----------
        index : integer
            The index in the part set to get the part from (0 <= index < total)

        Returns
        -------
        Part
            Part object
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "Item", index)

    def Next(self):
        """
        Returns the next part set in the model (or None if there is not one)

        Returns
        -------
        SetPart
            SetPart object
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "Next")

    def Previous(self):
        """
        Returns the previous part set in the model (or None if there is not one)

        Returns
        -------
        SetPart
            SetPart object
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "Previous")

    def SetFlag(self, flag):
        """
        Sets a flag on a part set

        Parameters
        ----------
        flag : Flag
            Flag (see AllocateFlag) to set on the part set

        Returns
        -------
        None
            No return value
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "SetFlag", flag)

