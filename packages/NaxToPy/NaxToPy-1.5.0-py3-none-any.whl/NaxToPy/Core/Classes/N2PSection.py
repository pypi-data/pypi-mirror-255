# Clase Section de Python ----------------------------------------------------------------------------------------------
class N2PSection:
    '''Class which contains the information associated to a section of a N2PComponent instance
    '''
    
    # Constructor de N2PSection ----------------------------------------------------------------------------------------
    def __init__(self, name, number):
        """Python Section Constructor.

        Args:
            name: str -> name of the section.
            number: int -> number associated to the section.

        Returns:
            section: N2PSection

        """
        self.__name__ = name
        self.__number__ = number
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el nombre de la seccion ----------------------------------------------------------------------
    @property
    def Name(self) -> str:
        """Returns the name of the section"""
        return(str(self.__name__))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el numero asociado a la seccion --------------------------------------------------------------
    @property
    def InternalNumber(self) -> int:
        """Returns the number associated to the section"""
        return(int(self.__number__))
    # ------------------------------------------------------------------------------------------------------------------

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        return f"N2PSection(\'{self.Name}\')"
    # ------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
