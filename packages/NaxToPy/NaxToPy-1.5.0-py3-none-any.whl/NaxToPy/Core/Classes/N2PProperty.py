"""Module with the class N2PProperty and all its derivated class"""

from abc import ABC
import math
from NaxToPy.Core.Errors.N2PLog import N2PLog
import numpy as np


failuredict = {0: "UNKNOWN",
               1: "HILL",
               2: "HOFF",
               3: "TASI",
               4: "STRN",
               5: "HASH",
               6: "PUCK",
               7: "STRS"}


# Clase base para el resto de propiedades ------------------------------------------------------------------------------
class N2PProperty(ABC):
    """Main abstract class for properties. The rest of the properties derive from it"""

    def __init__(self, information, model_father):
        """
        Constructor of the class N2PProperty. As Abaqus don't have ids for the props
        """

        self.__info__ = information
        self.__model__ = model_father

    @property
    def ID(self) -> int:
        if self.__info__.ID is None or self.__info__.ID == 0:
            N2PLog.Error.E209(self.Name)
        return self.__info__.ID

    @property
    def PartID(self) -> int:
        if self.__info__.PartID is None:
            N2PLog.Error.E210(self.Name)
        return self.__info__.PartID

    @property
    def InternalID(self) -> int:
        return self.__info__.InternalID

    @property
    def Name(self) -> str:
        return self.__info__.Name

    @property
    def PropertyType(self) -> str:
        return self.__info__.PropertyType.ToString()



    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        if self.__model__.Solver == "Abaqus":
            reprs = f"N2PProperty(\'{self.Name}\', \'{self.PropertyType}\')"
        else:
            reprs = f"N2PProperty({self.ID}, \'{self.PropertyType}\')"
        return reprs
    # ------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


# Clase para definir propiedades de compuestos -------------------------------------------------------------------------
class N2PComp(N2PProperty):
    """
    Class for defining compound properties. It derives from N2PProperty.
    """

    def __init__(self, information, model_father):
        """
        Constructor of the class N2PComp. It has base in N2PProperty
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father

    @property
    def NumPiles(self) -> int:
        return self.__info__.NumPiles

    @property
    def IsSymetric(self) -> bool:
        return self.__info__.IsSymetric

    @property
    def NSM(self) -> float:
        return self.__info__.NSM

    @property
    def AllowShear(self) -> float:
        return self.__info__.AllowShear

    @property
    def FailTh(self) -> str:
        return self.__info__.FailTh.ToString()

    @property
    def DampCoef(self) -> float:
        return self.__info__.DampCoef

    @property
    def MatID(self) -> tuple[int]:
        return tuple(self.__info__.Mat)

    @property
    def Thickness(self) -> tuple[float]:
        return tuple(self.__info__.Thickness)

    @property
    def Theta(self) -> tuple[float]:
        return tuple(self.__info__.Theta)

    @property
    def SOut(self) -> tuple[bool]:
        return tuple(self.__info__.SOut)

    @property
    def Plies(self) -> list[tuple]:
        """
        It returns a list of tuple. A tuple for a ply. Plies have four data: (MatID, Thickness, Theta, SOut)
        """
        return [(self.MatID[i], self.Thickness[i], self.Theta[i]) for i in range(self.NumPiles)]

    @property
    def EqQMatrix(self) -> list:
       """
       Returns the lamina stiffness matrix (Q-Bar)
       """
        
       q11_t = 0
       q12_t = 0
       q22_t = 0
       q16_t = 0
       q26_t = 0
       q66_t = 0

       t_thick = sum(self.Thickness) #! is self.Thickness a numpy array?

       for i in range(self.NumPiles):
           c = math.cos(math.radians(self.Theta[i]))
           s = math.sin(math.radians(self.Theta[i]))

           thick = self.Thickness[i]
           rel_thick = thick/t_thick

           mat = self.__model__._N2PModelContent__material_dict[self.MatID[i]]

           s11 = 1 / mat.YoungX
           s22 = 1 / mat.YoungY
           s12 = (-1) * mat.PoissonXY / mat.YoungX
           s66 = 1 / mat.ShearXY if mat.ShearXY != 0.0 else mat.YoungX/(2*(1+mat.PoissonXY))

           # Calculate the terms of the reduced stiffness matrix Q in the laminae coordinate system
           q11 = s22 / (s11 * s22 - s12 ** 2)
           q12 = (-1) * s12 / (s11 * s22 - s12 ** 2)
           q22 = s11 / (s11 * s22 - s12 ** 2)
           q66 = 1 / s66

           # Calculate the terms of the reduced stiffness matrix Q' in the laminate coordinate system
           q11_t += (q11 * c ** 4 + 2 * (q12 + 2 * q66) * s ** 2 * c ** 2 + q22 * s ** 4) * rel_thick #! why multiply by the thickness
           q12_t += ((q11 + q22 - 4 * q66) * s ** 2 * c ** 2 + q12 * (s ** 4 + c ** 4)) * rel_thick
           q22_t += (q11 * s ** 4 + 2 * (q12 + 2 * q66) * s ** 2 * c ** 2 + q22 * c ** 4) * rel_thick
           q16_t += ((q11 - q12 - 2 * q66) * s * c ** 3 + (q12 - q22 + 2 * q66) * s ** 3 * c) * rel_thick
           q26_t += ((q11 - q12 - 2 * q66) * s ** 3 * c + (q12 - q22 + 2 * q66) * s * c ** 3) * rel_thick
           q66_t += ((q11 + q22 - 2 * q12 - 2 * q66) * s ** 2 * c ** 2 + q66 * (s ** 4 + c ** 4)) * rel_thick

       Q = [[q11_t, q12_t, q16_t],
            [q12_t, q22_t, q26_t],
            [q16_t, q26_t, q66_t]]

       return Q
# ----------------------------------------------------------------------------------------------------------------------

    
    def QMatrix(self,i) -> np.ndarray:
        """
        Returns the lamina stiffness matrix (Q-Bar) as a numpy 2D array
        
        """                

        c = np.cos(np.radians(self.Theta[i]))   
        s = np.sin(np.radians(self.Theta[i]))   

        mat = self.__model__.MaterialDict[self.MatID[i]]

        s11 = 1 / mat.YoungX
        s22 = 1 / mat.YoungY
        s12 = (-1) * mat.PoissonXY / mat.YoungX
        shear = mat.ShearXY if mat.ShearXY != 0.0 else mat.YoungX/(2*(1+mat.PoissonXY))
        s66 = 1 / shear

        # Calculate the terms of the reduced stiffness matrix Q in the lamina, principal axis, coordinate system
        q11 = s22 / (s11 * s22 - s12 ** 2)
        q12 = (-1) * s12 / (s11 * s22 - s12 ** 2)
        q22 = s11 / (s11 * s22 - s12 ** 2)
        q66 = 1 / s66

        Q = np.array([[q11, q12, 0],[q12,q22,0],[0,0,q66]])

        # Calculate the terms of the reduced stiffness matrix Q' in the laminate, general, coordinate system
       
        # Calculate matrix of rotation, [T]

        T = np.array([[c**2, s**2,2*s*c],
                      [s**2,c**2,-2*s*c],
                      [-s*c,s*c,c**2-s**2]])

        try:
            T_inv = np.linalg.inv(T)
        except:
            print("ERROR: npQmatrix>>Inversion of rotation matrix failed.") # should not happen                       

        # From Jones pg50-51: [sigma] = [T]**(-1)*[Q]*[T]**(-1) [eps] = [Q_bar]*[eps]

        Q_bar = T_inv @ Q @ np.transpose(T_inv)

        return Q_bar


    @property
    def ABDMatrix(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]: 
        """
        Calculate extensional (A), coupling (B), and bending (D) stiffness matrices

        Returns A, B, C (numpy 2D arrays) of the laminate
        """

        # Nótese que las unidades de las matrices de rigidez ABD deben ser consistentes: A [N/m], B [N] y D [N·m].

        A = np.zeros([3,3],float)
        B = np.zeros([3,3],float)
        D = np.zeros([3,3],float)

        if self.NumPiles < 0:               # SYMMETRIC LAMINATE 
            Nply = abs(self.NumPiles)       # in this case Nply = half the real number of plies     
            t_thick = sum(self.Thickness)*2
            low_reference = - sum(self.Thickness)
            iterplies = np.pad(np.arange(0,Nply),(0,Nply),'symmetric') # e.g.: transforms [0,1,2] in [0,1,2,2,1,0]
        else:                               # NON-SYMMETRIC LAMINATE
            Nply = self.NumPiles            # in this case Nply 0 real number of plies
            t_thick = sum(self.Thickness)
            low_reference = - sum(self.Thickness) / 2
            iterplies = np.arange(0,Nply)
        
        for i in iterplies:
            
            thick = self.Thickness[i] # tener en cuenta caso simetrico
            centroid = low_reference + thick/2            

            Q_bar = self.QMatrix(i) # get Q_bar of the lamina in the laminate coordinate system

            # Calculate A, B, C matrices in the laminate coordinate system
            A += Q_bar*thick # extensional_matrix
            B += Q_bar * centroid * thick # bending_matrix
            D += Q_bar * ((centroid)**2 * thick + (thick**3)/12) # coupling_matrix

            low_reference += thick

        return A, B, D

# Clase para definir propiedades de tipo placa -------------------------------------------------------------------------
class N2PShell(N2PProperty):
    """
    Class for defining shell properties. It derives from N2PProperty.
    """

    def __init__(self, information, model_father):
        """
        Constructor of the class N2PShell. It has base in N2PProperty
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father

    @property
    def MatMemID(self) -> int:
        return self.__info__.MatMemID

    @property
    def MatBenID(self) -> int:
        return self.__info__.MatBenID

    @property
    def MatSheID(self) -> int:
        return self.__info__.MatSheID

    @property
    def Thickness(self) -> float:
        return self.__info__.Thickness

    @property
    def BenMR(self) -> float:
        return self.__info__.BenMR

    @property
    def TrShThickness(self) -> float:
        return self.__info__.TrShThickness

    @property
    def NSM(self) -> float:
        return self.__info__.NSM

    @property
    def FiberDist(self) -> tuple[float, float]:
        """Fiber distances for stress calculations. The positive direction is determined by the right-hand rule, and the
        order in which the grid points are listed on the connection entry"""
        return tuple(self.__info__.FiberDist)
# ----------------------------------------------------------------------------------------------------------------------


# Clase para definir propiedades de tipo solido -------------------------------------------------------------------------
class N2PSolid(N2PProperty):
    """
    Class for defining solid properties. It derives from N2PProperty.
    """

    def __init__(self, information, model_father):
        """
        Constructor of the class N2PSolid. It has base in N2PProperty
        """
        super().__init__(information, model_father)
        self.__info__ = information
        self.__model__ = model_father

    @property
    def MatID(self) -> int:
        return self.__info__.MatID

    @property
    def Cordm(self) -> int:
        return self.__info__.Cordm

    @property
    def IntNet(self) -> str:
        return self.__info__.IntNet.strip()

    @property
    def LocStrssOut(self) -> str:
        return self.__info__.LocStrssOut.strip()

    @property
    def IntSch(self) -> str:
        return self.__info__.IntSch.strip()

    @property
    def Fluid(self) -> str:
        return self.__info__.Fluid
