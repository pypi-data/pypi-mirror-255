import array

from NaxToPy.Core.Classes.N2PNode import N2PNode
from VizzerClasses import N2ElementsCoordinateSystems

# Clase Element de Python
class N2PElement:
    """Class with the information of an element.

    Attributes:
        ID: int.
        PartID: str.
        NumNodes: int.
        Nodes: tuple[N2PNode].
        Prop: int.
        TypeElement: str.
        NodesIds: tuple[int].
        AngleMat: float.
        InternalID: int.
        InternalElemType: str.
        ElemSystem: list[float].
    """

    def __init__(self, info, model_father):
        """Python Element constructor"""

        self.__info__ = info
        self.__model__ = model_father

    # Metodo para obtener  del elemento --------------------------------------------------------------------------------
    @property
    def InternalID(self) -> int:
        return(int(self.__info__.VTKindice))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el id del elemento ---------------------------------------------------------------------------
    @property
    def ID(self) -> int:
        return(int(self.__info__.ID))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener  del elemento --------------------------------------------------------------------------------
    @property
    def PartID(self) -> str:
        return(self.__model__._N2PModelContent__partIDtoStr.get(self.__info__.partID, -1))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener  del elemento --------------------------------------------------------------------------------
    @property
    def TypeElement(self) -> str:
        return(self.__model__._N2PModelContent__elementTypeIDtoStr.get(self.__info__.typeElementSolver, -1))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener  del elemento --------------------------------------------------------------------------------
    @property
    def Prop(self) -> int:
        return(int(self.__info__.prop))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el material del elemento ---------------------------------------------------------------------
    @property
    def InternalElemType(self) -> int:
        return(int(self.__info__.typeElementVTK))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener nNodes del elemento --------------------------------------------------------------------------
    @property
    def NumNodes(self) -> int:
        return(int(self.__info__.nNodes))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener los nodos del elemento como N2PNode ----------------------------------------------------------
    @property
    def Nodes(self) -> tuple[N2PNode]:
        aux = list(self.__info__.nodeList)
        retornar = tuple()
        for nodo in aux:
            retornar += (self.__model__._N2PModelContent__node_dict.get((nodo, self.__info__.partID), -1) ,)
        return(retornar)
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener los ids de los nodos del elemento ------------------------------------------------------------
    @property
    def NodesIds(self) -> tuple:
        return(tuple(self.__info__.nodeList))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el angulo material del elemento --------------------------------------------------------------
    @property
    def AngleMat(self) -> float:
        return(float(self.__info__.angleMaterial))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para el sistema de coordenadas elemento -------------------------------------------------------------------
    @property
    def ElemSystemArray(self) -> list[float, ...]:  # En el futuro se puede crear una clase N2PElemSys
        """
        Returns an array with the position of the three vectors that define the element system of the element:
        [x1, x2, x3, y1, y2, y3, z1, z2, z3]
        """
        systems = self.__model__._elements_coord_sys()
        return [systems[self.InternalID, i] for i in range(9)]
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para el sistema de material elemento ----------------------------------------------------------------------
    @property
    def MaterialSystemArray(self) -> list[float, ...]:
        """
        Returns list with the position of the three vectors that define the material system of the element:
        [x1, x2, x3, y1, y2, y3, z1, z2, z3]
        """
        mastsys = N2ElementsCoordinateSystems.GetElementMaterialSystem(self.__model__._N2PModelContent__vzmodel,
                                                                       self.InternalID)
        if mastsys is not None:
            return list(mastsys)
        else:
            return None
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para el sistema de material elemento ----------------------------------------------------------------------
    @property
    def Centroid(self) -> list[float, ...]:
        """
        Returns list with the centroid of the element: [x, y, z]
        """
        all_centroids = self.__model__._N2PModelContent__vzmodel.ElementCentroids
        iid = self.InternalID
        return [all_centroids[iid, i] for i in range(3)]
    # ------------------------------------------------------------------------------------------------------------------

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        return f"N2PElement({self.ID}, \'{self.PartID}\')"
    # ------------------------------------------------------------------------------------------------------------------
