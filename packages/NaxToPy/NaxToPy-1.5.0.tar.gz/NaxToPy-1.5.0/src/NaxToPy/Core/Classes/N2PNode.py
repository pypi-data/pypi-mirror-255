import array
import time
from VizzerClasses.Classes import N2AdjacencyFunctions


class N2PNode:
    """Class with the information of a node/grid.

    Attributes:
        ID: int.
        PartID: str.
        AnalysisCoordSys: int.
        PositionCoordSys: int.
        GlobalCoords: tuple.
        LocalCoords: tuple.
        X: float.
        Y: float.
        Z: float.
        Term1: float.
        Term2: float.
        Term3: float.
        SPCNode: int.
    """

    # Constructor de N2PNode ------------------------------------------------------------------
    def __init__(self, info, model_father):

        self.__info__ = info
        self.__model__ = model_father

        ## NOTA: En Python, un atributo de una tupla de tres posiciones de floats ocupa menos memoria que tres atributos de floats
        ##       Posibilidad de cambiar las coordenas de floats a una tupla

    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener el indice interno de Vizzer del nodo ------------------------------------
    @property
    def InternalID(self) -> int:
        """Returns the VTKindice of the node/grid."""
        return(int(self.__info__.VTKindice))
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener el id del nodo ----------------------------------------------------------
    @property
    def ID(self) -> int:
        """Returns the id (which the solver uses) of the node/grid."""
        return(int(self.__info__.ID))
    # ---------------------------------------------------------------------------------------------
    
    # Metodo para obtener el del nodo ------------------------------------------------------
    @property
    def PartID(self) -> str:
        """Returns the partID of the node/grid."""
        return(self.__model__._N2PModelContent__partIDtoStr.get(self.__info__.PartID, -1))
    # --------------------------------------------------------------------------------------------- 

    # Metodo para obtener el id del sistema de coordenadas de salida del nodo ---------------------
    @property
    def AnalysisCoordSys(self) -> int:
        """Returns the out_coord_sys of the node/grid."""
        return(int(self.__info__.OutCoordSys))
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener el id del sistema de coordenadas de entrada del nodo del nodo -----------
    @property
    def PositionCoordSys(self) -> int:
        """Returns the in_coord_sys of the node/grid."""
        return(int(self.__info__.InCoordSys))
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener el id del constraint flag del nodo --------------------------------------
    @property
    def SPCNode(self) -> int:
        """Returns the constr_flag of the node/grid."""
        return(int(self.__info__.ConstFlag))
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener las coordenadas en el sistema global  -----------------------------------
    @property
    def GlobalCoords(self) -> tuple[float]:
        """Returns the global coordinates of the node/grid."""
        return(tuple(self.__info__.GCoords))
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener las coordenadas en el sistema local del nodo ----------------------------
    @property
    def LocalCoords(self) -> tuple[float]:
        """Returns the local coordinates of the node/grid."""
        return(tuple(self.__info__.LCoords))
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener la coordenada x en el sistema global del nodo ---------------------------
    @property
    def X(self) -> float:
        """Returns the x coordinate of the node/grid."""
        return(float(self.__info__.GCoords[0]))
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener la coordenada y en el sistema global del nodo ---------------------------
    @property
    def Y(self) -> float:
        """Returns the y coordinate of the node/grid."""
        return(float(self.__info__.GCoords[1]))
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener la coordenada z en el sistema global del nodo ---------------------------
    @property
    def Z(self) -> float:
        """Returns the z coordinate of the node/grid."""
        return(float(self.__info__.GCoords[2]))
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener la coordenada x en el sistema local de entrada del nodo -----------------
    @property
    def Term1(self) -> float:
        """ Returns the first cordinate of the local system of the node/grid."""
        return(float(self.__info__.LCoords[0]))
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener la coordenada y en el sistema local de entrada del nodo -----------------
    @property
    def Term2(self) -> float:
        """Returns the second cordinate of the local system of the node/grid."""
        return(float(self.__info__.LCoords[1]))
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener la coordenada z en el sistema local de entrada del nodo -----------------
    @property
    def Term3(self) -> float:
        """Returns the third cordinate of the local system of the node/grid."""
        return(float(self.__info__.LCoords[2]))
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener la coordenada z en el sistema local de entrada del nodo -----------------
    @property
    def Connectivity(self) -> list["N2PElement", "N2PConnector", ...]:
        """Returns the N2PElements and N2PConnector that the node is connected to
        """

        malla = self.__model__._N2PModelContent__vzmodel.UMesh
        celllist = self.__model__._N2PModelContent__cells_list

        if not self.__model__._N2PModelContent__connectivity_dict:
            self.__model__._N2PModelContent__connectivity_dict = dict(N2AdjacencyFunctions.connectivityDict(malla))

        cs_list = self.__model__._N2PModelContent__connectivity_dict[self.InternalID]

        return [celllist[cell_iid] for cell_iid in cs_list]
    # ---------------------------------------------------------------------------------------------

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        return f"N2PNode({self.ID}, \'{self.PartID}\')"
    # ------------------------------------------------------------------------------------------------------------------
