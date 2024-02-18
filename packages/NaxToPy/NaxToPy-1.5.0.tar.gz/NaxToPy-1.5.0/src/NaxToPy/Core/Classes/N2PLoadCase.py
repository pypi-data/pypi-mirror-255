from NaxToPy.Core.Classes.N2PIncrement import N2PIncrement
from NaxToPy.Core.Classes.N2PResult import N2PResult
from NaxToPy.Core.Errors.N2PLog import N2PLog
from typing import Union


# Clase Load Case de Python --------------------------------------------------------------------------------------------
class N2PLoadCase:
    '''Class which contains the information associated to a load case instance of N2PLoadCase object

    Attrubutes:
        ID: int.
        Name: str.
        TypeSolution: str.
        Results: dict[str: N2PResult].
        Increments list[N2PIncrement].
        NumIncrements: int.
        ActiveIncrement: N2PIncrement.
        TypeLC: int.
        IsComplex: bool.
        InternalID: int.

    '''

    __increments_by_name__ = dict()
    __increments_by_id__ = dict()

    # Constructor de N2PLoadCase ---------------------------------------------------------------------------------------
    def __init__(self, id, id_original, increments, increments_number_list, is_complex, lc_type, name, results,
                 solution_type, solver, model_father, n2loadcase):
        '''Python Load Case Constructor
        Input:
            ID: int -> Identification Number of the Load Case
            IDOriginal: int -> Original Identification Number of the Load Case
            Increments: list[N2Increment] -> list with instances of N2Increment
            IncrementsNumberList: list[int] -> list with the number associated to each increment
            IsComplex: bool -> boolean value. True if the LC is associated to a complex LC
            LCType: str -> Type of solution applied in the load case
            Name : str -> Name of the load case
            Solver : str -> Solver of the load case
            Results: list[N2Results] -> list with instances of N2Results
        ----------
        Returns:
            N2PLoadCase: object
        '''
        self.__id__ = id
        self.__idoriginal__ = id_original

        self.__increments__ = [N2PIncrement(increments[i].Name,
                                            increments[i].eigi,
                                            increments[i].eigr,
                                            increments[i].number,
                                            increments[i].time) for i in range(0, len(increments))]

        self.__incrementsnumberlist__ = increments_number_list
        self.__iscomplex__ = is_complex
        self.__lctype__ = lc_type
        self.__namelc__ = name
        self.__results__ = {results[i].name: N2PResult(results[i].Components,
                                                       results[i].Position,
                                                       results[i].derivedComps,
                                                       results[i].description,
                                                       results[i].elemTypes,
                                                       results[i].fcode,
                                                       results[i].name,
                                                       self) for i in range(0, len(results))}

        self.__solutiontype__ = solution_type
        self.__activeIncrement__ = list(increments)[-1].number
        self.__solver__ = solver
        self.__modelFather__ = model_father
        self.__n2loadcase = n2loadcase
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el numero de identificacion interno del caso de carga ----------------------------------------
    @property
    def InternalID(self) -> int:
        return(int(self.__id__))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo oara obtener el numero de identificacion original del caso de carga ---------------------------------------
    @property
    def ID(self) -> int:
        return(int(self.__idoriginal__))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el numero de incrementos dentro del caso de carga --------------------------------------------
    @property
    def NumIncrements(self) -> int:
        if self.__increments__ is not None:
            return len(self.__increments__)
        else:
            return 0
    # ------------------------------------------------------------------------------------------------------------------
    
    # Metodo para obtener los incrementos de un caso de carga ----------------------------------------------------------
    @property
    def Increments(self) -> list[N2PIncrement]:
        return self.__increments__
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener si un caso de carga esta asociado a una solucion compleja ------------------------------------
    @property
    def IsComplex(self) -> bool:
        """Returns a boolean indicating whether the load case is associated to a complex solution"""
        return(bool(self.__iscomplex__))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el tipo de caso de Carga ---------------------------------------------------------------------
    @property
    def TypeLC(self) -> str:
        ''' Returns the type of Load Case. RAW -> the load case is extracted from the original file. IMPORTED -> the
        load case has been imported.
        '''
        return(str(self.__lctype__))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el nombre del caso de carga ------------------------------------------------------------------
    @property
    def Name(self) -> str:
        return(str(self.__namelc__))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el incremento activo. Influye en la funcion de llamada a get_result_array
    @property
    def ActiveIncrement(self) -> str:
        ''' Returns the active increment of the load case. By default, is the last one.'''
        return self.__activeIncrement__
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el incremento activo. Influye en la funcion de llamada a get_result_array
    @ActiveIncrement.setter
    def ActiveIncrement(self, id: Union[int, str]) -> None:
        ''' Sets the active increment of the load case. By defult is the last one.

        Args:
            id: int | str -> ID or Name of the N2PIncrement
        '''
        activincrement = self.get_increments(id).ID

        if activincrement is not None:
            self.__activeIncrement__ = activincrement
            N2PLog.Info.I202(id)
        else:
            N2PLog.Error.E207(id)
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo como propiedad que devuelve todos los N2PResult. Es igual que llamar a get_results sin
    # parametros
    @property
    def Results(self) -> dict[str, N2PResult]:
        return self.__results__

    # Metodo para obtener el tipo de solucion del modelo ---------------------------------------------------------------
    @property
    def TypeSolution(self) -> str:
        return(str(self.__solutiontype__))
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el solver del caso de carga ------------------------------------------------------------------
    @property
    def Solver(self) -> str:
        return(str(self.__solver__))
    # ------------------------------------------------------------------------------------------------------------------

    # Propiedad que devuelve la ruta del fichero desde donde se importo el caso de carga -------------------------------
    @property
    def PathFile(self) -> str:
        """Returns the path of the file where the load cases were imported from"""
        return str(self.__n2loadcase.PathFile)
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener los incrementos disponibles en el caso de carga ----------------------------------------------
    def get_increments(self, id: Union[int, str]) -> N2PIncrement:
        ''' Returns the N2PIncrement object with the id=ID or the id=Name of the Increment

        Args:
            id: str|int -> It can be the ID(int) of the increment or the Name(srt) of the increment

        Returns:
            increment: N2PIncrement
        '''

        # Chequear valor de Name
        if isinstance(id, str):
            # Si el diccionario está vacío se llena
            #if len(self.__increments_by_name__) == 0:
            if not self.__increments_by_name__:
                self.__increments_by_name__ = {str(incr.Name).lower(): incr for incr in self.Increments}
            # Devuelvo N2PResult
            increment = self.__increments_by_name__.get(id.lower(), None)
            if increment is not None:
                return increment
            else:
                N2PLog.Error.E212(id)
                return increment

        elif isinstance(id, int):
            # Si el diccionario está vacío se llena
            if not self.__increments_by_id__:
                self.__increments_by_id__ = {incr.ID: incr for incr in self.Increments}
            # Devuelvo N2PResult
            increment = self.__increments_by_id__.get(id, None)
            if increment is not None:
                return increment
            else:
                N2PLog.Error.E212(id)
                return increment

        # Devolver todos los resultados
        else:
            N2PLog.Error.E211()
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener los incrementos disponibles en el caso de carga ----------------------------------------------
    def get_result(self, name: str) -> N2PResult:
        ''' Returns the N2PResult object with the Name of the Result

        Args:
            name: str

        Returns:
            result: N2PResult
        '''

        # Chequear valor de Name
        if isinstance(name, str):
            result = self.Results.get(name, None)
            if result is None:
                N2PLog.Error.E213(name)
            return result

        # Devolver todos los resultados
        else:
            N2PLog.Error.E214()
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener los incrementos disponibles en el caso de carga ----------------------------------------------
    def set_increment(self, id: Union[int, str]) -> 'N2PLoadCase':
        """Method that sets the active increment where the results will be obtained. It is equivalent to use the property
        setter N2PLoadCase.ActiveIncrement = a_increment. If id=-1 the last increment is used as active.

        Args:
            id: int|str -> Number id or name of the increment is intended to set as active increment
        Returns:
            loadcase: 'N2PLoadCase'
        """
        if id == -1:
            self.ActiveIncrement = self.__increments__[-1].ID
        else:
            self.ActiveIncrement = id

        return self
    # ------------------------------------------------------------------------------------------------------------------

    # Special Method for Object Representation -------------------------------------------------------------------------
    def __repr__(self):
        return f"N2PLoadCase({self.ID}: \'{self.Name}\')"
    # ------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
