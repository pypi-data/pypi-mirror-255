from NaxToPy.Core.Classes.N2PNode import N2PNode


class N2PConnector:
    """Class of Connectors for NaxToPy. In the module, elements and connectors are separate classes

    Attributes:
        ID: int.
        PartID: str.
        TypeConnector: str.
        FreeNodes: list[N2PNode].
        SlaveNodes: list[N2PNode].
        Grids: list[N2PNode].
        InternalID: int.
        RefGrid: N2PNode.
    """

    def __init__(self, info, model_father):
        """Python Connector constructor"""
        self.__info__ = info
        self.__model__ = model_father

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el ID conector -------------------------------------------------------------------------------
    @property
    def ID(self) -> int:
        return(int(self.__info__.ID))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el ID de la parte del conector ---------------------------------------------------------------
    @property
    def PartID(self) -> str:
        return(self.__model__._N2PModelContent__partIDtoStr.get(self.__info__.Part, -1))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el tipo de conector conector -----------------------------------------------------------------
    @property
    def TypeConnector(self) -> str:
        return str(self.__info__.tipo)
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener los nodos (N2PNode) libres/independientes conector -------------------------------------------
    @property
    def FreeNodes(self) -> list[N2PNode]:
        # Devuelve el ID interno (el de VTK) de los nodos, no el solver. Entro con ese id en el diccionario de VTK a
        # Solver(ID, partID). Con la tupla entro en el diccionario de nodos para sacar el objeto N2PNode.
        # Todo dentro de una comprension de lista.
        listaobjetos = [ list(self.__model__._N2PModelContent__node_dict)[node]
                        for node in list(self.__info__.pointsIndep) ]
        return listaobjetos
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener los nodos (N2PNode) esclavos/dependientes del conector ---------------------------------------
    @property
    def SlaveNodes(self) -> list[N2PNode]:
        listaobjetos = [list(self.__model__._N2PModelContent__node_dict)[node]
                        for node in list(self.__info__.pointsDep)]
        return listaobjetos
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener los nodos (N2PNode) del conector en caso de ser del tipo MPC o RSPLINE -----------------------
    @property
    def GridIDs(self) -> list[N2PNode]:
        listaobjetos = [ list(self.__model__._N2PModelContent__node_dict)[node]
                        for node in list(self.__info__.gridIDs) ]
        return listaobjetos
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el id interno (o VTK) del conector -----------------------------------------------------------
    @property
    def InternalID(self) -> int:
        return (int(self.__info__.VTKindice))
    # ------------------------------------------------------------------------------------------------------------------
    
    # Metodo para obtener el id del nodo de referencia en caso de que el conector sea RBE3 o COUPLING
    @property
    def RefGrid(self) -> N2PNode:
        return list(self.__model__._N2PModelContent__node_dict)[int(self.__info__.refGrid)]
    # ------------------------------------------------------------------------------------------------------------------

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        return f"N2PConnector({self.ID}, \'{self.PartID}\', \'{self.TypeConnector}\')"
    # ------------------------------------------------------------------------------------------------------------------
