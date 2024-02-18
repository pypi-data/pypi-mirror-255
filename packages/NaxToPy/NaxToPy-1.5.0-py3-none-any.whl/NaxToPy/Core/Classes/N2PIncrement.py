# Clase Increment de Python --------------------------------------------------------------------------------------------
class N2PIncrement:
    '''Class which contains the information associated to an increment/frame of a N2PLoadCase instance.

    Attributes:
        Name: str.
        ImaginaryEigenvalue: float.
        RealEigenvalue: float.
        ID: int.
        Time: double.
    '''

    # Constructor de N2PIncrement --------------------------------------------------------------------------------------
    def __init__(self, name, eigi, eigr, number, time):
        '''Python Increment Constructor
            Input:
                name: str -> name of the increment
                eigi: double -> value of the imaginary eigenvalue
                eigr: double -> value of the real eigenvalue
                number: int -> number of the increment within the sequence of increments in the load case
                time: double -> value of the increment
            ----------
            Returns:
                N2PIncrement: object
        '''
        self.__name__ = name
        self.__eigi__ = eigi
        self.__eigr__ = eigr
        self.__number__ = number
        self.__time__ = time
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el nombre del incremento ---------------------------------------------------------------------
    @property
    def Name(self) -> str:
        return(str(self.__name__))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el valor del autovalor real ------------------------------------------------------------------
    @property
    def RealEigenvalue(self) -> float:
        return(float(self.__eigr__))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el valor del autovalor imaginario ------------------------------------------------------------
    @property
    def ImaginaryEigenvalue(self) -> float:
        return(float(self.__eigi__))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el ID del incremento en el caso de carga -----------------------------------------------------
    @property
    def ID(self) -> int:
        return(int(self.__number__))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el valor del incremento ----------------------------------------------------------------------
    @property
    def Time(self) -> float:
        ''' Returns the value of the increment/frame'''
        return(float(self.__time__))
    # ------------------------------------------------------------------------------------------------------------------

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        return f"N2PIncrement({self.ID}: \"{self.Name}\")"
    # ------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------


