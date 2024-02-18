class N2PCoord(object):
    """Class with the information of a coordinate system

    Attributes:

        ID: int.
        PartID: str.
        TypeSys: str.
        IsGlobal: bool.
        Description: str.
        IsUserDefined: bool.
        Origin: tuple.
        Xaxis: tuple.
        Yaxis: tuple.
        Zaxis: tuple.
    """

    def __init__(self, info, model_father):
        """Constructor of the class N2PCoord"""

        self.__info = info
        self.__model__ = model_father

    # Metodos para obtener los atributos de la clase N2PCoord

    @property
    def ID(self) -> int:
        return int(self.__info.ID)

    # @property
    # def PartID(self) -> str:
    #     try:
    #         partid = int(self.__info.partID)
    #     except:
    #         partid = 0
    #     return self.__model__._N2PModelContent__partIDtoStr.get(self.__info.Part, -1)
    
    @property
    def TypeSys(self) -> str:
        return str(self.__info.type)

    @property
    def Origin(self) -> tuple:
        return tuple(self.__info.origen)
    
    @property
    def Xaxis(self) -> tuple:
        return tuple(self.__info.xAxis)

    @property
    def Yaxis(self) -> tuple:
        return tuple(self.__info.yAxis)

    @property
    def Zaxis(self) -> tuple:
        return tuple(self.__info.zAxis)

    @property
    def Description(self) -> str:
        return str(self.__info.description)

    @property
    def IsGlobal(self) -> bool:
        return bool(self.__info.is_global)

    @property
    def IsUserDefined(self) -> bool:
        return bool(self.__info.is_user_defined)

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        return f"N2PCoord({self.ID}, \'{self.PartID}\', \'{self.TypeSys}\')"
    # ------------------------------------------------------------------------------------------------------------------
