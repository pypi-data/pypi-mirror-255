from NaxToPy.Core.Classes.N2PSection import N2PSection
from NaxToPy.Core.Errors.N2PLog import N2PLog
from VizzerClasses import N2ParamInputResults
from VizzerClasses import N2TensorTransformation
from array import array
import numpy as np
from NaxToPy.Core._AuxFunc._NetToPython import _numpytonet
from typing import Union


# Clase Component de Python
# -----------------------------------------------------------------------
class N2PComponent:
    '''Class which contains the information associated to a component of a N2PResult instance.

    Attributes:
        Name: str.
        Sections: list[N2PSection].
        IsTransformable: bool.
    '''

    # Constructor de N2PComponent
    # -----------------------------------------------------------------
    def __init__(self, name, sections, result_father):
        """ Python Component Constructor

            Args:
                name: str -> name of the component
                sections: list[N2Sections] -> list with instances of N2Sections
                result_father: N2PResult
        """
        self.__name__ = name
        self.__sections__ = [N2PSection(sections[i].Name,
                                        sections[i].number) for i in range(0, len(sections))]
        self.__result_father__ = result_father
    # ---------------------------------------------------------------------------------------------

    # Metodo para Obtener el Nombre de la Componente
    # ----------------------------------------------
    @property
    def Name(self) -> str:
        return(str(self.__name__))
    # ---------------------------------------------------------------------------------------------

    # Metodo para Obtener una lista con las secciones de la componente ----------------------------
    @property
    def Sections(self) -> list[N2PSection, ...]:
        """ Returns a list of N2PSection objects with all the sections contained in the component
        """
        return(self.__sections__)
    # ---------------------------------------------------------------------------------------------

    @property
    def IsTransformable(self) -> bool:
        """Property that keeps if the component of a result is transformable in other coordinate system.
        """
        # No se guarda como atributo privado durante la instanciacion de un objeto porque algunas variables
        # aun no se han construido. Por eso el metodo de la propiedad es la que busca los argumentos y llama
        # al metodo dentro de Vizzer classes.
        solver = self.__result_father__.__loadCase_father__.__solver__
        result = self.__result_father__.Name
        component = self.Name
        return bool(N2TensorTransformation.IsResultSupported(solver, result, component))

    # Metodo para llamar a la funcion de VizzerClasses que devueleve el array de resultados-----------------------------
    def get_result_array(self, sections=None, aveSections=-1, cornerData=False, aveNodes=-1, variation=100,
                         realPolar=0, coordsys: int = -1000,
                         v1: tuple = (1, 0, 0), v2: tuple = (0, 1, 0)) -> tuple[list, str]:
        """Deprecated method. Please, use get_result_list instead for asking the results as a list. If a numpy array is
        preferred, use get_result_ndarray"""
        return self.get_result_list(sections, aveSections, cornerData, aveNodes, variation,
                                    realPolar, coordsys, v1, v2)
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para llamar a la funcion de VizzerClasses que devueleve el array de resultados como lista------------------
    def get_result_list(self, sections=None, aveSections=-1, cornerData=False, aveNodes=-1, variation=100,
                         realPolar=0, coordsys: int = -1000,
                         v1: Union[tuple, np.ndarray] = (1,0,0), v2: Union[tuple, np.ndarray] = (0,1,0)) -> tuple[list, str]:
        """ Returns a tuple with the list of floats with the result array asked and a str with the position of the
        results

        Args:
        
            sections: list[str] | list[N2PSection] -> Optional. Sections which operations are done.
                None (Default) = All Sections

            aveSections: int -> Optional. Operation Among Sections.

                -1 : Maximum (Default),
                -2 : Minimum,
                -3 : Average,
                -4 : Extreme,
                -6 : Difference.

            cornerData: bool -> Optional. Flag to get results in element nodal.

                True : Results in Element-Nodal,
                False : Results in centroid (Default).

            aveNodes: int -> Optional. Operation among nodes when cornerData is selected.

                0 : None,
                -1 : Maximum (Default),
                -2 : Minimum,
                -3 : Average,
                -5 : Average with variation parameter,
                -6 : Difference.

            variation: int -> Optional. Integer between 0 & 100 to select.

                0 : No average between nodes,
                100 : Total average between nodes (Default).

            realPolar: int -> Optional. Data type when complex result.

                1 : Real / Imaginary,
                2 : Magnitude / Phase.

            coordsys: int -> Optional. Coordinate System where the result_array will be represented. By default,
                the output is in element system:

                0   : Global,
                -1  : Material Coordinate System,
                -10 : User defined,
                >0  : Solver ID of the Predefined Coordinate System.

            v1: tuple -> Optional.

            v2: tuple -> Optional. Directions vectors that generate the coordinate system axis:

                x=v1,
                z=v1^v2,
                y=z^x.

        Returns: 
            results: tuple(list[float], str)

        """
        # Aquí se prepara la llamada a la funcion de VizzerClasses.N2PModelContent.getArraytoPlot(). Esta usa como
        # argumento un objeto de la clase N2ParamImputResults. Por se instancia y se modifican sus propiedades antes
        # de hacer la llamada a la funcion.

        # Aqui se mete el sistema de coordenadas en el que queremos que nos saque la informacion.
        # Para ello primero comprobamos que es viable hacer la tansformacion (puede que aun no este implementada o que
        # la componente simplemente no la admita al ser un escalar a secas)

        #resultsParameters.coordSys = -10
        #orientationcoordinatesystem = algo

        resultsParameters = self._create_n2paraminputresult(sections, aveSections, cornerData, aveNodes, variation,
                                                            realPolar, coordsys, v1, v2)
        results = list(
            self.__result_father__.__loadCase_father__.__modelFather__._N2PModelContent__vzmodel.CalculateArrayLastResult(
                resultsParameters, 0))

        if results[1] == 1:
            return(list(results[0]),'NODES')
        elif results[1] == 2:
            return(list(results[0]), 'ELEMENTS')
        elif results[1] == 3:
            return(list(results[0]), 'ELEMENT NODAL')
        else:
            N2PLog.Error.E206(self.Name)
            return(-1, 'NO RESULTS')
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para llamar a la funcion de VizzerClasses que devuelve el array de resultados como array de numpy----------
    def get_result_ndarray(self, sections=None, aveSections=-1, cornerData=False, aveNodes=-1, variation=100,
                         realPolar=0, coordsys: int = -1000,
                         v1: Union[tuple, np.ndarray ] = (1,0,0), v2: Union[tuple, np.ndarray ] = (0,1,0)) -> tuple[np.array, str]:
        """ Returns a tuple with the numpy array of floats with the result array asked and a str with the position of
        the results

        Args:

            sections: list[str] | list[N2PSection] -> Optional. Sections which operations are done.
                None (Default) = All Sections

            aveSections: int -> Optional. Operation Among Sections.

                -1 : Maximum (Default),
                -2 : Minimum,
                -3 : Average,
                -4 : Extreme,
                -6 : Difference.

            cornerData: bool -> Optional. Flag to get results in element nodal.

                True : Results in Element-Nodal,
                False : Results in centroid (Default).

            aveNodes: int -> Optional. Operation among nodes when cornerData is selected.

                0 : None,
                -1 : Maximum (Default),
                -2 : Minimum,
                -3 : Average,
                -5 : Average with variation parameter,
                -6 : Difference.

            variation: int -> Optional. Integer between 0 & 100 to select.

                0 : No average between nodes,
                100 : Total average between nodes (Default).

            realPolar: int -> Optional. Data type when complex result.

                1 : Real / Imaginary,
                2 : Magnitude / Phase.

            coordsys: int -> Optional. Coordinate System where the result_array will be represented. By default,
                the output is in element system:

                0   : Global,
                -1  : Material Coordinate System,
                -10 : User defined,
                >0  : Solver ID of the Predefined Coordinate System.

            v1: tuple -> Optional.

            v2: tuple -> Optional. Directions vectors that generate the coordinate system axis:

                x=v1,
                z=v1^v2,
                y=z^x.

        Returns:
            results: tuple(np.array, str)
        """
        resultsParameters = self._create_n2paraminputresult(sections, aveSections, cornerData, aveNodes, variation,
                                                            realPolar, coordsys, v1, v2)

        results = \
            self.__result_father__.__loadCase_father__.__modelFather__._N2PModelContent__vzmodel.CalculateArrayLastResult(
            resultsParameters, 0)

        if results[1] == 1:
            return(np.array(results[0], np.float64),'NODES')
        elif results[1] == 2:
            return(np.array(results[0], np.float64), 'ELEMENTS')
        elif results[1] == 3:
            return(np.array(results[0], np.float64), 'ELEMENT NODAL')
        else:
            N2PLog.Error.E206(self.Name)
            return(-1, 'NO RESULTS')
    # ------------------------------------------------------------------------------------------------------------------

    # # Metodo que devulve un dataframe con los resulados tras llamar a la funcion de VizzerClasses--
    # def get_result_dataframe(self, sections=None, aveSections=-1, cornerData=False, aveNodes=-1,
    #                          variation=100, realPolar=0, coordsys: int = -1000,
    #                          v1: tuple = (1,0,0), v2: tuple = (0,1,0)) -> DataFrame:
    #     """Returns a DataFrame of pandas with the results array of a component as data for the active increment.
    #
    #     Args:
    #
    #         sections: list[str] | list[N2PSection] -> Sections which operations are done.
    #             None (Default) = All Sections
    #
    #         aveSections: int -> Operation Among Sections.
    #             -1 : Maximum (Default),
    #             -2 : Minimum,
    #             -3 : Average,
    #             -4 : Extreme,
    #             -6 : Difference.
    #
    #         cornerData: bool -> flag to get results in element nodal.
    #             True : Results in Element-Nodal,
    #             False : Results in centroid (Default).
    #
    #         aveNodes: int -> Operation among nodes when cornerData is selected.
    #             0 : None,
    #             -1 : Maximum (Default),
    #             -2 : Minimum,
    #             -3 : Average,
    #             -5 : Average with variation parameter,
    #             -6 : Difference.
    #
    #         variation: int -> Integer between 0 & 100 to select.
    #             0 : No average between nodes,
    #             100 : Total average between nodes (Default).
    #
    #         realPolar: int -> data type when complex result.
    #             1 : Real / Imaginary,
    #             2 : Magnitude / Phase.
    #
    #         coordsys: int -> Coordinate System where the result_array will be represented.
    #             0   : Global,
    #             -1  : Material Coordinate System,
    #             -10 : User defined,
    #             >0  : Solver ID of the Predefined Coordinate System.
    #
    #         v1: tuple
    #
    #         v2: tuple -> Directions vectors that generate the coordinate system axis:
    #             x=v1,
    #             z=v1^v2,
    #             y=z^x.
    #
    #     Returns:
    #         DataFrame:
    #             data: float64: results array
    #             index: int | tuple: id of the element/node or tuple (id, part)
    #                                     it could be a tuple (nodo_id, element_id, part) for cornerData
    #             column: str: component.Name
    #     ----------
    #     """
    #     ids = list()
    #     indexname = list()
    #
    #     resultlist = self.get_result_array(sections, aveSections, cornerData, aveNodes, variation, realPolar, coordsys,
    #                                        v1, v2)
    #
    #     if resultlist[0] == -1:
    #         N2PLog.Error.E208()
    #         return DataFrame()
    #     if len(self.__result_father__.__loadCase_father__.__modelFather__._N2PModelContent__StrPartToID) == 1:
    #         noparts = True
    #     else:
    #         noparts = False
    #
    #     if resultlist[1] == "NODES":
    #         nodos = self.__result_father__.__loadCase_father__.__modelFather__.get_nodes()
    #         if noparts:
    #             ids = [nodo.ID for nodo in nodos]
    #             indexname = ["Grid"]
    #         else:
    #             ids = [(nodo.PartID, nodo.ID) for nodo in nodos]
    #             indexname = ["Part", "Grid"]
    #         del nodos
    #     elif resultlist[1] == "ELEMENTS":
    #         elements = self.__result_father__.__loadCase_father__.__modelFather__.get_elements()
    #         connectors = self.__result_father__.__loadCase_father__.__modelFather__.get_connectors()
    #         if noparts:
    #             # La lista de connectores puede contener N2PConnector o lista de N2PConector. Esto es porque
    #             # los MPC puden tener ids iguales en Nastran. Por eso en la comprension de la lista de conectores
    #             # itero sobre la lista de conetores con igual id dentro de la lista de conectores general y si no
    #             # resulta ser una lista lo transformo en lista e itero.
    #             ids = [element.ID for element in elements] + \
    #                   [c.ID for con in connectors for c in (con if isinstance(con, list) else [con])]
    #             indexname = ["Element"]
    #         else:
    #             ids = [(element.PartID, element.ID) for element in elements] +\
    #                   [(c.PartID, c.ID) for con in connectors for c in (con if isinstance(con, list) else [con])]
    #             indexname = ["Part", "Element"]
    #         del elements, connectors
    #     elif resultlist[1] == "ELEMENT NODAL":
    #         ids = list(self.__result_father__.__loadCase_father__.__modelFather__._elementnodal().values())
    #         indexname = ["Part", "Grid", "Element"]
    #
    #     # Se revisa que la lista de malla y la lista de resultados sean del mismo tamaño
    #     if not len(ids) == len(resultlist[0]):
    #         N2PLog.Warning.W202()
    #         length = min(len(ids), len(resultlist[0]))
    #         ids = ids[:length]
    #         resultlist = (resultlist[0][:length], resultlist[1])
    #
    #     data = {self.Name: resultlist[0]}
    #     if isinstance(ids[0], tuple):
    #         index = MultiIndex.from_tuples(ids, names=indexname)
    #     else:
    #         index = ids
    #
    #     df = DataFrame(data=data, index=index, columns=[self.Name])
    #
    #     if not isinstance(ids[0], tuple):
    #         df = df.rename_axis(indexname, axis='index')
    #
    #     return df
    # # ------------------------------------------------------------------------------------------------------------------

    # Método que devuelve un diccionario con la tupla (LC, Incr) como clave y una lista de resultados como valor -------
    def _get_result_by_LCs_Incr(self, list_lc_incr: list[tuple["N2PLoadCase", "N2PIncrement"],...],
                               sections=None, aveSections=-1, cornerData=False, aveNodes=-1, variation=100,
                               realPolar=0, coordsys: int = -1000,
                               v1: tuple = (1,0,0), v2: tuple = (0,1,0)) -> dict[tuple: list[float,...]]:

        formula = self._create_formula(list_lc_incr)

        if not formula:
            return None

        resultsParameters = self._create_n2paraminputresult(sections, aveSections, cornerData, aveNodes, variation,
                                                            realPolar, coordsys, v1, v2)

        cs_dict = self.__result_father__.__loadCase_father__.__modelFather__._N2PModelContent__vzmodel.CalculateArrayLastResult(
                formula, resultsParameters, 0)

        py_dict = {(int(key.split(":")[0].replace("DoF_LCD", "-").replace("DoF_LC", "")),
                    int(key.split(":")[1][2:])): np.array(value, np.float64)
                   for key, value in dict(cs_dict[0]).items()}

        return py_dict
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo que crea la formula que necesita la funcion de VizzerClasses ----------------------------------------------
    def _create_formula(self, list_lc_incr: list[tuple["N2PLoadCase", "N2PIncrement"],...]) -> str:

        if isinstance(list_lc_incr, tuple):
            list_lc_incr = [list_lc_incr]

        N2PLoadCase = type(self.__result_father__.__loadCase_father__)
        N2PIncrement = type(self.__result_father__.__loadCase_father__.Increments[0])

        if isinstance(list_lc_incr[0][0], N2PLoadCase) and isinstance(list_lc_incr[0][1], N2PIncrement):
            return ",".join(f"<LC{lc[0].ID}:FR{lc[1].ID}>" for lc in list_lc_incr)

        elif isinstance(list_lc_incr[0][0], int) and isinstance(list_lc_incr[0][1], int):
            return ",".join(f"<LC{lc[0]}:FR{lc[1]}>" for lc in list_lc_incr)

        else:
            N2PLog.Error.E310()
            return None
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo que crea el N2ParamInputResult ----------------------------------------------------------------------------
    def _create_n2paraminputresult(self, sections, aveSections, cornerData, aveNodes, variation,
                                   realPolar, coordsys, v1, v2) -> N2ParamInputResults:

        # Aqui comprobamos que si queremos hacer una transformacion y si esta es posible:
        if self.IsTransformable and (coordsys != -1000 or (v1 != (1, 0, 0) or v2 != (0, 1, 0))):
            # si es un sistema definido por el usuarios es -10 y se busca el GlobalID. Si es positivo es de solver.
            # si es material es -1.
            if coordsys > 0:
                resultsParameters = N2ParamInputResults.structResults(0)  # , x_array, y_array, z_array)
                resultsParameters.coordSys = coordsys

            elif coordsys < 0 and (v1 != (1, 0, 0) or v2 != (0, 1, 0)):
                # Esto es una array de doubles. Si se quiere hacer una transformacion tanto en sistemas ya definidos en
                # el solver como por el usuario hay que pasarlo como argumento de N2ParamInputResult
                new_sys = _get_axis(v1, v2)
                new_sys = _numpytonet(new_sys)

                resultsParameters = N2ParamInputResults.structResults(0)
                resultsParameters.coordSys = -10
                resultsParameters.orientationcoordinatesystem = new_sys

            elif coordsys == -1:
                resultsParameters = N2ParamInputResults.structResults(0)
                resultsParameters.coordSys = coordsys

            elif coordsys == 0:
                resultsParameters = N2ParamInputResults.structResults(0)
                resultsParameters.coordSys = coordsys

            else:
                N2PLog.Error.E220()
                return (-1, 'NO RESULTS')

        elif not self.IsTransformable and (coordsys != -1000 or (v1 != (1, 0, 0) or v2 != (0, 1, 0))):
            N2PLog.Error.E219()
            return (-1, 'NO RESULTS')

        else:
            # Initializer if it is no transformable
            resultsParameters = N2ParamInputResults.structResults(0)

        # Component Selected
        resultsParameters.Component = str(self.Name)

        # Entity Selection (So Far 'ALL')
        resultsParameters.IdsEntities = ''

        # Active Increment
        resultsParameters.IncrementID = str(self.__result_father__.__loadCase_father__.__activeIncrement__)

        # Load Case Selected
        resultsParameters.LoadCaseID = str(self.__result_father__.__loadCase_father__.ID)

        # Parts Selected (So Far 'ALL')
        resultsParameters.Part = 'all'

        # Results Selected
        resultsParameters.Result = str(self.__result_father__.Name)

        resultsParameters.Sets = ''
        resultsParameters.TypeElement = ''

        # Sections Selected (By Default 'ALL') & Section Average
        sectionParam = ''

        if sections is None:
            for section in self.__sections__:
                sectionParam += str(section.Name) + '#'
        else:
            if not isinstance(sections, list):
                N2PLog.Error.E218()
            for section in sections:
                if type(section) is N2PSection:
                    sectionParam += str(section.Name) + '#'
                else:
                    sectionParam += str(section) + '#'

        resultsParameters.sectPoint = sectionParam

        resultsParameters.aveSection = aveSections

        # CornerData Selection, Average & Variation
        resultsParameters.cornerData = cornerData

        __aveIntraSupported__ = (0, -1, -2, -3, -6)
        if (aveNodes not in __aveIntraSupported__):
            return (-1)
        else:
            resultsParameters.aveIntra = aveNodes

        variation = variation
        if variation > 100:
            variation = 100
        elif variation < 0:
            variation = 0

        resultsParameters.variation = variation

        # Real/Imaginary or Magnitude/Phase
        __complexSupported__ = (0, 1, 2)
        if (realPolar not in __complexSupported__):
            return (-1)
        else:
            resultsParameters.real_cartesian_polar = realPolar

        return resultsParameters
    # ------------------------------------------------------------------------------------------------------------------


    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        loadcasestr = f"N2PComponent(\'{self.Name}\')"
        return loadcasestr
    # ------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------


def _get_axis(v1: Union[tuple, np.ndarray], v2: Union[tuple, np.ndarray]) -> np.ndarray:
    """Function that returns the components of the three vectors of a rectangular coordinate system

    Args:
        v1: tuple|ndarray
        v2: tuple|ndarray

    Returns:
        ndarray
    """
    v1 = np.array(v1)
    v1 = v1/np.linalg.norm(v1)

    v2 = np.array(v2)
    v2 = v2/np.linalg.norm(v2)

    z = np.cross(v1, v2)
    y = np.cross(z, v1)

    return np.vstack((v1, y, z))
