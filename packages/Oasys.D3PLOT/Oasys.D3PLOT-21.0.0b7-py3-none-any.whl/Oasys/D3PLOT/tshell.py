import Oasys.gRPC


# Metaclass for static properties and constants
class TshellType(type):

    def __getattr__(cls, name):

        raise AttributeError


class Tshell(Oasys.gRPC.OasysItem, metaclass=TshellType):
    _props = {'data', 'include', 'index', 'integrationPoints', 'label', 'material', 'model', 'onPlanIntegrationPoints', 'part', 'type'}


    def __del__(self):
        if not Oasys.D3PLOT._connection:
            return

        Oasys.D3PLOT._connection.destructor(self.__class__.__name__, self._handle)


    def __getattr__(self, name):
# If one of the properties we define then get it
        if name in Tshell._props:
            return Oasys.D3PLOT._connection.instanceGetter(self.__class__.__name__, self._handle, name)

        raise AttributeError


    def __setattr__(self, name, value):
# If one of the properties we define then set it
        if name in Tshell._props:
            Oasys.D3PLOT._connection.instanceSetter(self.__class__.__name__, self._handle, name, value)
            return

# Set the property locally
        self.__dict__[name] = value


# Static methods
    def BlankAll(window, model):
        """
        Blanks all of the tshells in the model

        Parameters
        ----------
        window : GraphicsWindow
            GraphicsWindow) to blank the tshells in
        model : Model
            Model that all the tshells will be blanked in

        Returns
        -------
        None
            No return value
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "BlankAll", window, model)

    def BlankFlagged(window, model, flag):
        """
        Blanks all of the tshells in the model flagged with a defined flag

        Parameters
        ----------
        window : GraphicsWindow
            GraphicsWindow) to blank the tshells in
        model : Model
            Model that the flagged tshells will be blanked in
        flag : Flag
            Flag (see AllocateFlag) set on the tshells to blank

        Returns
        -------
        None
            No return value
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "BlankFlagged", window, model, flag)

    def First(model):
        """
        Returns the first tshell in the model (or None if there are no tshells in the model)

        Parameters
        ----------
        model : Model
            Model to get first tshell in

        Returns
        -------
        Tshell
            Tshell object
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "First", model)

    def FlagAll(model, flag):
        """
        Flags all of the tshells in the model with a defined flag

        Parameters
        ----------
        model : Model
            Model that all the tshells will be flagged in
        flag : Flag
            Flag (see AllocateFlag) to set on the tshells

        Returns
        -------
        None
            No return value
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "FlagAll", model, flag)

    def GetAll(model):
        """
        Gets all of the tshells in the model

        Parameters
        ----------
        model : Model
            Model that all the tshells are in

        Returns
        -------
        array
            Array of :py:class:`Tshell<Tshell>` objects
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "GetAll", model)

    def GetFlagged(model, flag):
        """
        Gets all of the tshells in the model flagged with a defined flag

        Parameters
        ----------
        model : Model
            Model that the flagged tshells are in
        flag : Flag
            Flag (see AllocateFlag) set on the tshells to get

        Returns
        -------
        array
            Array of :py:class:`Tshell<Tshell>` objects
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "GetFlagged", model, flag)

    def GetFromID(model, label):
        """
        Returns the Tshell object for tshell in model with label (or None if it does not exist)

        Parameters
        ----------
        model : Model
            Model to get tshell in
        label : integer
            The LS-DYNA label for the tshell in the model

        Returns
        -------
        Tshell
            Tshell object
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "GetFromID", model, label)

    def GetFromIndex(model, index):
        """
        Returns the Tshell object for tshell in model with index (or None if it does not exist)

        Parameters
        ----------
        model : Model
            Model to get tshell in
        index : integer
            The D3PLOT internal index in the model for tshell

        Returns
        -------
        Tshell
            Tshell object
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "GetFromIndex", model, index)

    def GetMultipleData(component, items, options=Oasys.gRPC.defaultArg):
        """
        Returns the value for a data component for multiple tshells. For each tshell a local property called data will be created
        containing a number if a scalar component, or a list if a vector or tensor component (or None if the value cannot be calculated).
        The data is also returned as an object.
        Also see GetData

        Parameters
        ----------
        component : constant
            :ref:`Component constant ` to get data for
        items : list
            List of Tshell objects to get the data for.
            All of the tshells must be in the same model
        options : dict
            Optional. Dictionary containing options for getting data. Can be any of:

        Returns
        -------
        $object
            Dict containing the data. A property is created in the object for each tshell with the label. The value of the property is a number if a scalar component or an array if a vector or tensor component (or None if the value cannot be calculated)
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "GetMultipleData", component, items, options)

    def Last(model):
        """
        Returns the last tshell in the model (or None if there are no tshells in the model)

        Parameters
        ----------
        model : Model
            Model to get last tshell in

        Returns
        -------
        Tshell
            Tshell object
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "Last", model)

    def Pick():
        """
        Allows the user to pick a tshell from the screen

        Returns
        -------
        Tshell
            Tshell object or None if cancelled
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "Pick")

    def Select(flag):
        """
        Selects tshells using an object menu

        Parameters
        ----------
        flag : Flag
            Flag (see AllocateFlag) to use when selecting tshells

        Returns
        -------
        integer
            The number of tshells selected or None if menu cancelled
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "Select", flag)

    def Total(model):
        """
        Returns the total number of tshells in the model

        Parameters
        ----------
        model : Model
            Model to get total in

        Returns
        -------
        integer
            The number of tshells
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "Total", model)

    def TotalDeleted(model):
        """
        Returns the total number of thick shells that have been deleted in a model

        Parameters
        ----------
        model : Model
            Model to get total in

        Returns
        -------
        integer
            The number of thick shells that have been deleted
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "TotalDeleted", model)

    def UnblankAll(window, model):
        """
        Unblanks all of the tshells in the model

        Parameters
        ----------
        window : GraphicsWindow
            GraphicsWindow) to unblank the tshells in
        model : Model
            Model that all the tshells will be unblanked in

        Returns
        -------
        None
            No return value
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "UnblankAll", window, model)

    def UnblankFlagged(window, model, flag):
        """
        Unblanks all of the tshells in the model flagged with a defined flag

        Parameters
        ----------
        window : GraphicsWindow
            GraphicsWindow) to unblank the tshells in
        model : Model
            Model that the flagged tshells will be unblanked in
        flag : Flag
            Flag (see AllocateFlag) set on the tshells to unblank

        Returns
        -------
        None
            No return value
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "UnblankFlagged", window, model, flag)

    def UnflagAll(model, flag):
        """
        Unsets a defined flag on all of the tshells in the model

        Parameters
        ----------
        model : Model
            Model that the defined flag for all tshells will be unset in
        flag : Flag
            Flag (see AllocateFlag) to unset on the tshells

        Returns
        -------
        None
            No return value
        """
        return Oasys.D3PLOT._connection.classMethod(__class__.__name__, "UnflagAll", model, flag)



# Instance methods
    def Blank(self, window):
        """
        Blanks the tshell in a graphics window

        Parameters
        ----------
        window : GraphicsWindow
            GraphicsWindow) to blank the tshell in

        Returns
        -------
        None
            No return value
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "Blank", window)

    def Blanked(self, window):
        """
        Checks if the tshell is blanked in a graphics window or not

        Parameters
        ----------
        window : GraphicsWindow
            GraphicsWindow) in which to check if the tshell is blanked

        Returns
        -------
        boolean
            True if blanked, False if not
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "Blanked", window)

    def ClearFlag(self, flag):
        """
        Clears a flag on a tshell

        Parameters
        ----------
        flag : Flag
            Flag (see AllocateFlag) to clear on the tshell

        Returns
        -------
        None
            No return value
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "ClearFlag", flag)

    def Deleted(self):
        """
        Checks if the thick shell has been deleted or not

        Returns
        -------
        boolean
            True if deleted, False if not
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "Deleted")

    def Flagged(self, flag):
        """
        Checks if the tshell is flagged or not

        Parameters
        ----------
        flag : Flag
            Flag (see AllocateFlag) to test on the tshell

        Returns
        -------
        boolean
            True if flagged, False if not
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "Flagged", flag)

    def GetData(self, component, options=Oasys.gRPC.defaultArg):
        """
        Returns the value for a data component.
        Also see GetMultipleData

        Parameters
        ----------
        component : constant
            :ref:`Component constant ` to get data for
        options : dict
            Optional. Dictionary containing options for getting data. Can be any of:

        Returns
        -------
        float|array
            Number if a scalar component, array if a vector or tensor component (or None if the value cannot be calculated)
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "GetData", component, options)

    def LocalAxes(self):
        """
        Returns the local axes of the element in model space, expressed as direction cosines in a 2D list.
        Beam elements must have 3 nodes to be able to return local axes

        Returns
        -------
        list
            list of lists
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "LocalAxes")

    def Next(self):
        """
        Returns the next tshell in the model (or None if there is not one)

        Returns
        -------
        Tshell
            Tshell object
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "Next")

    def PlasticStrain(self, options=Oasys.gRPC.defaultArg):
        """
        Returns the effective plastic strain for the thick shell (or None if the value cannot be calculated)

        Parameters
        ----------
        options : dict
            Optional. Dictionary containing options for getting data. Can be any of:

        Returns
        -------
        float
            Plastic strain
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "PlasticStrain", options)

    def Previous(self):
        """
        Returns the previous tshell in the model (or None if there is not one)

        Returns
        -------
        Tshell
            Tshell object
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "Previous")

    def SetFlag(self, flag):
        """
        Sets a flag on a tshell

        Parameters
        ----------
        flag : Flag
            Flag (see AllocateFlag) to set on the tshell

        Returns
        -------
        None
            No return value
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "SetFlag", flag)

    def StrainTensor(self, options=Oasys.gRPC.defaultArg):
        """
        Returns the strain tensor for the thick shell

        Parameters
        ----------
        options : dict
            Optional. Dictionary containing options for getting data. Can be any of:

        Returns
        -------
        array
            Array containing the strain tensor [Exx, Eyy, Ezz, Exy, Eyz, Ezx] (or None if the value cannot be calculated)
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "StrainTensor", options)

    def StressTensor(self, options=Oasys.gRPC.defaultArg):
        """
        Returns the stress tensor for the thick shell

        Parameters
        ----------
        options : dict
            Optional. Dictionary containing options for getting data. Can be any of:

        Returns
        -------
        array
            Array containing the stress tensor [Exx, Eyy, Ezz, Exy, Eyz, Ezx] (or None if the value cannot be calculated)
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "StressTensor", options)

    def Topology(self):
        """
        Returns the topology for the tshell in the model

        Returns
        -------
        list
            list of Node objects
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "Topology")

    def Unblank(self, window):
        """
        Unblanks the tshell in a graphics window

        Parameters
        ----------
        window : GraphicsWindow
            GraphicsWindow) to unblank the tshell in

        Returns
        -------
        None
            No return value
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "Unblank", window)

    def VonMisesStress(self, options=Oasys.gRPC.defaultArg):
        """
        Returns the von Mises stress for the thick shell (or None if the value cannot be calculated)

        Parameters
        ----------
        options : dict
            Optional. Dictionary containing options for getting data. Can be any of:

        Returns
        -------
        float
            von Mises stress
        """
        return Oasys.D3PLOT._connection.instanceMethod(self.__class__.__name__, self._handle, "VonMisesStress", options)

