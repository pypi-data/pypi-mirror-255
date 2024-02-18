from NaxToPy.Core.Classes.N2PComponent import N2PComponent
from NaxToPy.Core.Errors.N2PLog import N2PLog


# Clase Result de Python --------------------------------------------------------------------------
class N2PResult:
    """Class which contains the information associated to a result of a N2PLoadCase"""

    __Components_by_Name__ = dict()
    
    # Constructor de N2PResult --------------------------------------------------------------------
    def __init__(self, components, position, derivedComps, description, elemTypes, fcode, name, loadCase_father):
        """Python Result Constructor.

        Args:
            components: list[N2Component] -> list with instances of N2Components.
            position: str -> postion of the results.
            derivedComps: list[N2Component] -> list with instances of N2Components (derived).
            description: str -> description of the result.
            elemTypes: list[str] -> list with the types of elements where results have been obtained.
            fcode: str
            name: str -> name of the result.
        """

        self.__components__ = {components[i].Name: N2PComponent(components[i].Name, components[i].Sections, self)
                               for i in range(0, len(components))}
        self.__position__ = position
        self.__derived_comps__ = {derivedComps[i].Name: N2PComponent(derivedComps[i].Name, derivedComps[i].Sections, self)
                                  for i in range(0,len(derivedComps))}
        self.__description__ = description
        self.__elem_types__ = elemTypes
        self.__fcode__ = fcode
        self.__name__ = name
        self.__loadCase_father__ = loadCase_father
    # ---------------------------------------------------------------------------------------------

    # Metodo como propiedad para obtener todas las componentes. Es igual al metodo get_components.
    @property
    def Components(self) -> dict[str, N2PComponent]:
        return self.__components__
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener la posicion donde se han obtenido resultados ----------------------------
    @property
    def Position(self) -> str:
        """Returns the position where the results have been obatined within the load case"""
        return str(self.__position__)
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener la componentes derivadas disponibles en el resultado --------------------
    @property
    def DerivedComponents(self) -> dict[str, N2PComponent]:
        """Returns a list of N2Component with all the derived components available within the result"""
        return self.__derived_comps__
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener la descripcion del resultado --------------------------------------------
    @property
    def Description(self) -> str:
        return(self.__description__)
    # ----------------------------------------------------------------------------------------------

    # Metodo para obtener los tipos de elemento en los cuales se han obtenido resultados -----------
    @property
    def TypesElements(self) -> list[str]:
        """Returns a list with the element types where results are available.
        """
        return(list(self.__elem_types__))
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener el format code del resultado -> PREGUNTAR A ROBERTO OP2??? --------------
    @property
    def FormatCode(self) -> str:
        return(str(self.__fcode__))
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener el nombre del resultado -------------------------------------------------
    @property
    def Name(self) -> str:
        return(str(self.__name__))
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener las componentes disponibles en el resultado -----------------------------
    def get_component(self, name: str) -> N2PComponent:
        """Returns a N2Component as component with name specified

        Args:
            name: str

        Returns:
            component: N2PComponent
        """

        if isinstance(name, str):
            component = self.Components.get(name, None)
            if component is None:
                N2PLog.Error.E215(name)
            return component

        # Devolver todos los resultados
        else:
            N2PLog.Error.E216()
    # ---------------------------------------------------------------------------------------------

    # Metodo para obtener las componentes disponibles en el resultado -----------------------------
    def get_derived_component(self, name: str) -> N2PComponent:
        """Returns a N2Component as derived component with name specified,

        Args:
            name: str

        Returns:
            derived component: N2PComponent
        """

        if isinstance(name, str):
            result = self.DerivedComponents.get(name, None)
            if result is None:
                N2PLog.Error.E217(name)
            return result

        # Devolver todos los resultados
        else:
            N2PLog.Error.E216()
    # ---------------------------------------------------------------------------------------------

    # # Metodo para obtener los resultados de todas las componentes del resultado como DataFrame ----
    # def get_results_dataframe(self, sections=None, aveSections=-1, cornerData=False, aveNodes=-1,
    #                           variation=100, realPolar=0) -> DataFrame:
    #     """
    #     Returns a DataFrame of pandas with the results array of echa component of a LoadCase for
    #     the active increment.
    #     Input (Parameters)
    #
    #     + sections: list of sections (string) which operations are done
    #         · None (Default) = All Sections
    #
    #     + aveSections: Operation Among Sections
    #         · -1 : Maximum (Default)
    #         · -2 : Minimum
    #         · -3 : Average
    #         · -4 : Extreme
    #         · -6 : Difference
    #
    #     + cornerData : flag to get results in element nodal
    #         · True : Results in Element-Nodal
    #         · False : Results in centroid (Default)
    #
    #     + aveNodes: Operation among nodes when cornerData is selected
    #         ·  0 : None
    #         · -1 : Maximum (Default)
    #         · -2 : Minimum
    #         · -3 : Average
    #         · -5 : Average with variation parameter
    #         · -6 : Difference
    #
    #     + variation: Integer between 0 & 100 to select
    #         · 0 : No average between nodes
    #         · 100 : Total average between nodes (Default)
    #
    #     + realPolar: data type when complex result
    #         · 1 : Real / Imaginary
    #         · 2 : Magnitude / Phase
    #
    #     ----------
    #     Returns:
    #         DataFrame:
    #             - data: float64 -> results array
    #             - index: int | tuple -> id of the element/node or tuple (id, part)
    #                                     it could be a tuple (nodo_id, element_id, part) for cornerData
    #             - column: str -> component.Name
    #     ----------
    #     """
    #     first = True
    #     for component in self.Components.values():
    #         data = component.get_result_dataframe(sections, aveSections, cornerData, aveNodes,
    #                                               variation, realPolar)
    #         if first:
    #             resultdataframe = data
    #             first = False
    #         else:
    #             resultdataframe = resultdataframe.join(data)
    #
    #     return resultdataframe
    # # ------------------------------------------------------------------------------------------------------------------

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        loadcasestr = f"N2PResult(\'{self.Name}\')"
        return loadcasestr
    # ------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
