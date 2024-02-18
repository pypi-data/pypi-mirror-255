from VizzerClasses import N2ModelContent
from VizzerClasses import N2LoadCase
from VizzerClasses.Classes import N2AdjacencyFunctions
from VizzerClasses.Classes import N2FreeEdges
from NaxToPy.Core.Classes.N2PLoadCase import N2PLoadCase
from NaxToPy.Core.Classes.N2PIncrement import N2PIncrement
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Core.Classes.N2PConnector import N2PConnector
from NaxToPy.Core.Classes.N2PNode import N2PNode
from NaxToPy.Core.Classes.N2PCoord import N2PCoord
from NaxToPy.Core.Classes.N2PConnector import N2PConnector
from NaxToPy.Core.Classes.N2PFreeBody import N2PFreeBody
from NaxToPy.Core.Errors.N2PLog import N2PLog
from NaxToPy.Core.Classes.N2PMaterial import N2PMaterial, N2PMatE, N2PMatMisc, N2PMatI
from NaxToPy.Core.Classes.N2PProperty import N2PProperty, N2PComp, N2PShell, N2PSolid
from NaxToPy.Core.Classes.N2PSet import N2PSet
from NaxToPy.Core.Classes.N2PModelInputData import *
from NaxToPy.Core.Constants.Constants import BINARY_EXTENSIONS
from NaxToPy.Core.Classes.N2PReport import N2PReport
import time
import sys
import numpy as np
import os
import array
import System
from collections import OrderedDict
from typing import Union, overload


# Clase Model Content de Python ----------------------------------------------------------------------------------------
class N2PModelContent:
    '''Main Class of the NaxToPy package. Keeps almost all the information contained in the output result.

    Attributes:
        FilePath: str
        Solver: str
        AbaqusVersion: str
        LoadCases: list[N2PLoadCases]
        NumberLoadCases: int
        Parts: list[str]
    '''

    def __init__(self, path, parallelprocessing, solver=None):
        """ Python ModelContent Constructor.

            Args:
                path: str
                parallelprocessing: bool
        """
        # 0 ) Genera el archivo .log y añade los logs de la importación ------------------------------------------------
        # Configura el logger para que escriba automaticamente los logs ------------------------------------------------
        N2PLog._N2PLog__fh.write_buffered_records()
        N2PLog._N2PLog__fh.immediate_logging()


        # 1) Extraer Toda la Informacion Principal de NaxTo ------------------------------------------------------------
        # Inicializador del modelo
        self.__vzmodel = N2ModelContent()

        self.__LCs_by_ID__: dict[int: N2PLoadCase] = dict()
        self.__LCs_by_Name__: dict[str: N2PLoadCase] = dict()
        self.__load_cases__ = None

        self.__number_of_load_cases = None
        self.__material_dict = dict()
        self.__property_dict: dict[tuple[int, int]] = dict()
        self.__elements_coord_sys = None
        self.__material_coord_sys = None
        self.__cells_list = None  # Lista con N2PElement y N2PConnector
        self.__connectivity_dict = {}

        if (solver is None) and (solver != "InputFileNastran") and (solver != "Binary"):
            t1 = time.time()
            solver = _is_binary(path)
            t2 = time.time()-t1

        if solver == 'InputFileNastran':
            self.__vzmodel.Solver = self.__vzmodel.Solver.InputFileNastran

        error = self.__vzmodel.Initialize(path)
        self.__solver = self.__vzmodel.Solver.ToString()
        self.__elementnodal_dict = None
        self.__elemIdInternalToId = dict()

        # Si NaxTo devuelve un numero por debajo de 0 en el inicializador del modelo -> Error al inicializar modelo
        if(error < 0):
            if not os.path.exists(path):
                N2PLog.Critical.C108(path)
                # sys.exit(error)
            else:
                N2PLog.Critical.C100(path, error)
                # sys.exit(error)
        else:
            N2PLog.Info.I111(path)

        # Activar banderas de NaxToPy en dll de Naxto
        # Es imprescindible hacer esta llamada para que se carguen los datos necesarios para que
        # el modulo funcione
        self.__vzmodel.Program_Call = self.__vzmodel.Program_Call.NaxToPy

        N2PLog.Debug.D102()

        # Opcion que indica que la lectura de la malla dentro de vizzer se haga en paralelo
        self.__vzmodel.LoadModelInParallel = parallelprocessing  # No siempre es mas rapido

        N2PLog.Debug.D103(parallelprocessing)

        error = self.__vzmodel.BuildMesh2()
        # Si NaxTo devuelve un numero por debajo de 0 en el generador de malla -> Error al generar malla
        if error == -1003:
            N2PLog.Critical.C112()
            # sys.exit(error)
        elif(error < 0):
            N2PLog.Critical.C101(error)
            # sys.exit(error)
        else:
            N2PLog.Info.I112()

        # Generar Informacion Disponible (LCs, Result-Types ...)
        if self.__solver != "InputFileNastran":
            t1 = time.time()
            self.__vzmodel.LoadInfoResults()
            t2 = time.time()
            N2PLog.Debug.D100("LoadInfoResults()", t2-t1)
        # --------------------------------------------------------------------------------------------------------------

        ################################################################################################################
        ###########################################    N2PLoadCase    ##################################################
        ################################################################################################################
        # 2) Obtener los casos de carga del modelo ---------------------------------------------------------------------
        t1 = time.time()

        self._import_load_cases()

        t2 = time.time()
        N2PLog.Debug.D100("LoadCases", t2-t1)
        # --------------------------------------------------------------------------------------------------------------

        ################################################################################################################
        ##########################################    GENERAL DICTS     ################################################
        ################################################################################################################
        # Diccionarios obtenidos directamente de Vizzer ---------------
        t1 = time.time()

        self.__elementTypeStrtoID = dict(self.__vzmodel.elementTypeID)
        self.__propertiesID = dict(self.__vzmodel.propertiesID)
        self.__StrPartToID = dict(self.__vzmodel.partID)
        self.__materialsID = dict(self.__vzmodel.materialsID)
        self.__ConnectorsID = dict(self.__vzmodel.ConnectorsID)
        # --------------------------------------------------------------------------------------------------------------

        # Diccionario de en el que entras con un ID de elemento dado por Vizzer y sacas
        # un string con el tipo de elemento de solver
        self.__elementTypeIDtoStr = {v: k for k, v in self.__elementTypeStrtoID.items()}

        # Diccionario en el que entras con el ID de la parte y te devuelve el nombre.
        self.__partIDtoStr = {v: k for k, v in self.__StrPartToID.items()}

        # Diccionario en el que entras con un Id de propiedad y te devuelve el string.
        self.__propertyIDtoStr = {v: k for k, v in self.__propertiesID.items()}

        # Diccionario en el que entras con un Id de tipo de conector y te devuelve un string con su nombre.
        self.__connectorTypeIDtoStr = {v: k for k, v in self.__ConnectorsID.items()}

        # Diccionario de en el que entras con un material y devuelve una lista de propiedades en las que está incluido
        # Al ser una lista no vale el metodo dict() tal cual. Hay que sacar sus claves y valores y construirlo nosotros
        aux = dict(self.__vzmodel.DictMaterialsProperties)
        self.__DictMaterialsProperties = {key: list(aux[key]) for key in aux}
        del aux
        # --------------------------------------------------------------------------------------------------------------

        # Diccionario de en el que entras con una propiedad y devuelve una lista de materiales que tiene incluido
        # Se construye igual que el diccionario anterior
        aux = dict(self.__vzmodel.DictPropertiesMaterials)
        self.__DictPropertiesMaterials = {key: list(aux[key]) for key in aux}
        del aux

        t2 = time.time()
        N2PLog.Debug.D100("Direct Dictionaries", t2-t1)
        # --------------------------------------------------------------------------------------------------------------

        ################################################################################################################
        #############################################    N2PCoord    ###################################################
        ################################################################################################################
        t1 = time.time()
        
        listadecoords = list(self.__vzmodel.coordList.Values)

        if len(listadecoords) == 0:
            self.__vzmodel.LoadCoords()
            listadecoords = list(self.__vzmodel.coordList.Values)

        # Revisar porque es posible los sistemas de coordenadas nunca tengan partes
        self.__coord_dict = {((coord.ID, coord.PartID) if hasattr(coord, 'PartID') else (coord.ID, 0)):
                             N2PCoord(coord, self) for coord in listadecoords}

        # Se elimina la variable coord para liberar memoria
        del listadecoords

        t2 = time.time()
        N2PLog.Debug.D100("N2PCoord Dictionary", t2-t1)
        # --------------------------------------------------------------------------------------------------------------

        ################################################################################################################
        #############################################    N2PNode     ###################################################
        ################################################################################################################
        t1 = time.time()

        def __n2pnode_func(listadenodos):
            node_dict = OrderedDict(((nodo.ID, nodo.PartID), N2PNode(nodo, self)) for nodo in listadenodos)
            return node_dict

        listadenodos = list(self.__vzmodel.N2PNodeList)
        self.__node_dict = __n2pnode_func(listadenodos)
        del listadenodos


        t2 = time.time()
        N2PLog.Debug.D100("N2PNode Dictionary", t2-t1)
        # --------------------------------------------------------------------------------------------------------------

        ################################################################################################################
        ############################################    N2PElement     #################################################
        ################################################################################################################
        t1 = time.time()

        def __n2pelement_func(listadeelementos):
            elem_dict = OrderedDict(((elem.ID, elem.partID), N2PElement(elem, self)) for elem in listadeelementos)
            return elem_dict

        listadeelementos = list(self.__vzmodel.N2PElementList)
        self.__element_dict = __n2pelement_func(listadeelementos)
        self.__cells_list = list(self.__element_dict.values())
        del listadeelementos

        t2 = time.time()
        N2PLog.Debug.D100("N2PElement Dictionary", t2-t1)
        # --------------------------------------------------------------------------------------------------------------

        ################################################################################################################
        ###########################################    N2PConnector     ################################################
        ################################################################################################################
        t1 = time.time()

        listadeconectores = list(self.__vzmodel.connectorList)

        self.__connector_dict = OrderedDict()
        for con in listadeconectores:
            if not (con.ID, con.Part) in self.__connector_dict:
                self.__connector_dict[(con.ID, con.Part)] = N2PConnector(con, self)
            elif isinstance(self.__connector_dict.get((con.ID, con.Part)), list):
                self.__connector_dict[(con.ID, con.Part)].append(N2PConnector(con, self))
            else:
                self.__connector_dict[(con.ID, con.Part)] = \
                    [self.__connector_dict.get((con.ID, con.Part)), (N2PConnector(con, self))]
                N2PLog.Warning.W203((con.ID, con.Part))
        del listadeconectores
        # OJO. EN NASTRAN SE PUEDEN TENER VARIOS MPC CON EL MISMO ID, POR TANTO SE GUARDARAN COMO UNA LISTA DE
        # N2PConnectors
        self.__cells_list += [conn for conn_list in self.__connector_dict.values()
                              for conn in (conn_list if isinstance(conn_list, list) else [conn_list])]
        t2 = time.time()
        N2PLog.Debug.D100("N2PConnector Dictionary", t2-t1)
        # --------------------------------------------------------------------------------------------------------------

        ################################################################################################################
        ########################################    N2PModelInputData     ##############################################
        ################################################################################################################
        t1 = time.time()
        if self.__vzmodel.InfoInputFileData is not None:
            n2pmodelimpudata = self.__vzmodel.InfoInputFileData.ListBulkDataCards

            #lista_cards = zeros(len(n2pmodelimpudata), object)
            #diccionario
            #llamar por separado a las tarjetas (props, elems, mat, ...)
            #lista_cards = [construct_dict[card.CardType.ToString()](card) for card in n2pmodelimpudata]
            lista_cards = list(CONSTRUCTDICT[card.CardType.ToString()](card) for card in n2pmodelimpudata)
            self.__modelinputdata = N2PModelInputData(lista_cards, self.__vzmodel.InfoInputFileData)

        else:
            self.__modelinputdata = None
        t2 = time.time()-t1
        N2PLog.Debug.D100("N2PModelInputData", t2)
        # --------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    ############################################### PROPIEDADES ########################################################
    # Metodo para Obtener la Ruta del Modelo ---------------------------------------------------------------------------
    @property
    def FilePath(self) -> str:
        return(str(self.__vzmodel.FilePath))
    # ------------------------------------------------------------------------------------------------------------------
     
    # Metodo para Obtener el Solver del Modelo -------------------------------------------------------------------------
    @property
    def Solver(self) -> str:
        return self.__solver
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para Obtener la Version de Abaqus del Modelo --------------------------------------------------------------
    @property
    def AbaqusVersion(self) -> str:
        """ Returns the Abaqus version used in the output result file if the solver is Abaqus
        """
        if(self.__solver == 'Abaqus'):
            return(str(self.__vzmodel.version_abqs_model.ToString()))
        else:
            return None
    # ------------------------------------------------------------------------------------------------------------------


    # Metodo para obtener el numero de casos de carga en el modelo -----------------------------------------------------
    @property
    def LoadCases(self) -> list[N2PLoadCase, ...]:
        """ Returns a list with all the of N2PLoadCase
        """
        return self.__load_cases__
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el numero de casos de carga en el modelo -----------------------------------------------------
    @property
    def NumberLoadCases(self) -> int:

        if(self.__number_of_load_cases is None):
            self.__number_of_load_cases = int(self.__vzmodel.LoadCases.Count)
            return(int(self.__vzmodel.LoadCases.Count))
        else:
            return(int(self.__number_of_load_cases))
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Parts(self) -> list[str]:
        """Returns the list of parts/superelements of the model"""
        return list(self.__partIDtoStr.values())

    @property
    def ElementsDict(self) -> OrderedDict[tuple[int, int], N2PElement]:
        """Returns a dictionary with the N2PElement of the model as values. The key is the tuple (id, partid)"""
        return self.__element_dict

    @property
    def NodesDict(self) -> OrderedDict[tuple[int, int], N2PNode]:
        """Returns a dictionary with the N2PNode of the model as values. The key is the tuple (id, partid)"""
        return self.__node_dict

    @property
    def ConnectorsDict(self) -> OrderedDict[tuple[int, int], N2PConnector]:
        """Returns a dictionary with the N2PConnector of the model as values. The key is the tuple (id, partid)"""
        return self.__connector_dict

    @property
    def SetList(self) -> list[N2PSet, ...]:
        """Returns a list of N2PSet kept in the model"""
        return [N2PSet(_) for _ in list(self.__vzmodel.SetList)]

    @property
    def ModelInputData(self) -> N2PModelInputData:
        """Returns a N2PModelInputData with the information of the input data file"""
        if self.__modelinputdata is None:
            N2PLog.Warning.W204()
        return self.__modelinputdata

    ####################################################################################################################
    ###########################################    N2PMaterial     #####################################################
    ####################################################################################################################
    @property
    def MaterialDict(self) -> dict[int, N2PMaterial]:
        """
        Property of the N2PModelContent class that returns the dictionary of materials. This is an attribute of the class,
        but it is not initialize at first, only when it is needed.

        Returns:
            dict[tuple[ID]] = N2PMaterial
        """

        t1 = time.time()

        if not self.__material_dict:

            dictmateriales = dict(self.__vzmodel.N2MatDict)

            for key, value in dictmateriales.items():
                if self.Solver == "Nastran" or self.Solver == "Optistruct" or self.Solver == "InputFileNastran":
                    key = int(key)

                if value.GetType().ToString() == 'VizzerClasses.N2MatE':
                    self.__material_dict[key] = N2PMatE(value, self)
                elif value.GetType().ToString() == 'VizzerClasses.N2MatI':
                    self.__material_dict[key] = N2PMatI(value, self)
                elif value.GetType().ToString() == 'VizzerClasses.N2MatMisc':
                    self.__material_dict[key] = N2PMatMisc(value, self)

        t2 = time.time()
        N2PLog.Debug.D100("N2PMaterial Dictionary", t2-t1)
        return self.__material_dict
    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    ###########################################    N2PProperty     #####################################################
    ####################################################################################################################
    @property
    def PropertyDict(self) -> dict[tuple, N2PProperty]:
        """
        Property of the N2PModelContent class that returns the dictionary of properties. This is an attribute of the class,
        but it is not initialize at first, only when it is needed

        Returns:
            dict[tuple[ID, PartID]] = N2PProperty
        """

        t1 = time.time()

        if not self.__property_dict:

            dictprop = dict(self.__vzmodel.N2PropDict)

            for key, value in dictprop.items():

                if self.Solver == "Nastran" or self.Solver == "Optistruct" or self.Solver == "InputFileNastran":
                    key = int(key)
                    if key < 0:
                        N2PLog.Error.E227(key)

                if value.GetType().ToString() == 'VizzerClasses.N2Shell':
                    self.__property_dict[key] = N2PShell(value, self)

                elif value.GetType().ToString() == 'VizzerClasses.N2Comp':
                    self.__property_dict[key] = N2PComp(value, self)

                elif value.GetType().ToString() == 'VizzerClasses.N2Solid':
                    self.__property_dict[key] = N2PSolid(value, self)

        t2 = time.time()
        N2PLog.Debug.D100("N2PProperty Dictionary", t2 - t1)
        return self.__property_dict
    # ------------------------------------------------------------------------------------------------------------------

    ################################################# METODOS ##########################################################

    # Metodo para obtener los casos de carga del modelo ----------------------------------------------------------------
    @overload
    def get_load_case(self, id: int) -> Union[list[N2PLoadCase], N2PLoadCase, None]:
        ...

    @overload
    def get_load_case(self, name: str) -> Union[list[N2PLoadCase], N2PLoadCase, None]:
        ...

    def get_load_case(self,
                      id: Union[int, None] = None,
                      name: Union[str, None] = None) -> Union[list[N2PLoadCase], N2PLoadCase, None]:
        """Returns a list of N2PLoadCase objects with all the load cases contained in the output result file.

        Args:
            id (int, optional): ID of the load case. Defaults to None.
            name (str, optional): Name of the load case. Defaults to None.

        Returns:
                N2PLoadCase: load_case
        """
        # Check if the input ID is a string
        if isinstance(id, str):
            name = id
            id = None

        # Check the value of ID
        if id is not None:
            if not self.__LCs_by_ID__:
                self.__LCs_by_ID__ = {loadcase.ID: loadcase for loadcase in self.LoadCases}
                aux = self.__LCs_by_ID__.get(id, None)
            else:
                aux = self.__LCs_by_ID__.get(id, None)

            if aux is None:
                N2PLog.Error.E221(id)
            return aux

        # Check the value of Name
        elif name is not None:
            if not self.__LCs_by_Name__:
                self.__LCs_by_Name__ = {loadcase.Name: loadcase for loadcase in self.LoadCases}
            aux = self.__LCs_by_Name__.get(name, None)

            if aux is None:
                N2PLog.Error.E222(name)
            return aux

        # Return all load cases
        else:
            return self.LoadCases
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo general para elementos ------------------------------------------------------------------------------------
    def get_elements(self, ids: Union[tuple[int, str], list, int] = 0) -> Union[N2PElement, list[N2PElement]]:
        """ General method for obtain elements.

        If it has no argument or is 0: returns all the elements
        If it has one id as argument: returns one N2PElement 
        If it has a list as argument it returns a list of N2PElement 
        The ids should be a tuple (id, part_id). If not, part_id = 0 by default

        Args:
            ids: int | list[int] | tuple[int, str] | list[tuple[int, str]]

        Returns:
            object: N2PElement | list[N2PElement]
        """
        try:
            if ids == 0:
                elements = list(self.__element_dict.values())
                return elements

            if ids != 0 and isinstance(ids, int):
                if self.Solver == "Nastran" or self.Solver == "Optistruct" or self.Solver == "Ansys" or self.Solver == "InputFileNastran":
                    if len(self.__partIDtoStr) > 1:
                        N2PLog.Error.E223()
                        elements = -2
                    else:
                        elements = self.__element_dict.get((ids, 0), -1)
                elif self.Solver == "Abaqus":
                    if len(self.__partIDtoStr) > 2:
                        N2PLog.Error.E223()
                        elements = -2
                    else:
                        elements = self.__element_dict.get((ids, 1), -1)
                if elements == -1:
                    N2PLog.Error.E202(ids)
                return elements

            if isinstance(ids, tuple) and len(ids) == 2:
                if isinstance(ids[1], str):
                    aux = self.__StrPartToID.get(ids[1])
                    elements = self.__element_dict.get((ids[0], aux), -1)
                else:
                    elements = self.__element_dict.get(ids, -1)
                if elements == -1: N2PLog.Error.E202(ids)
                return elements

            if (isinstance(ids, tuple) and len(ids) > 2) or isinstance(ids, list):
                elements = list()
                if isinstance(ids[0], tuple):
                    for id in ids:
                        if isinstance(id[1], str):
                            aux = self.__StrPartToID.get(id[1])
                            elemento = self.__element_dict.get((id[0], aux), -1)
                        else:
                            elemento = self.__element_dict.get(id, -1)
                        if elemento == -1: N2PLog.Error.E202(id)
                        elements.append( elemento )
                    return elements

                if isinstance(ids[0], int):
                    for id in ids:
                        if self.Solver == "Nastran" or self.Solver == "Optistruct" or self.Solver == "Ansys" or self.Solver == "InputFileNastran":
                            if len(self.__partIDtoStr) > 1:
                                N2PLog.Error.E223()
                                elemento = -2
                            else:
                                elemento = self.__element_dict.get((id, 0), -1)
                        elif self.Solver == "Abaqus":
                            if len(self.__partIDtoStr) > 2:
                                N2PLog.Error.E223()
                                elements = -2
                            else:
                                elemento = self.__element_dict.get((id, 1), -1)
                        if elemento == -1:
                            N2PLog.Error.E202(id)
                        elements.append( elemento )
                    return elements
            return elements

        except:
            elements = -1
            N2PLog.Error.E205(ids)
            return elements
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo general para nodos ----------------------------------------------------------------------------------------
    def get_nodes(self, ids=0) -> Union[N2PNode, list[N2PNode]]:
        """ General method for obtain nodes.

        If it has no argument or is 0: returns all the nodes.
        If it has one id as argument: returns one N2PNode.
        If it has a list as argument it returns a list of N2PNode.
        The ids should be a tuple (id, part_id). If not, part_id = 0 by default.

        Args:
            ids: int | list[int] | tuple[int, str] | list[tuple[int, str]]

        Returns:
            object: N2PNode | list[N2PNode]
        """
        try:
            if ids == 0:
                nodes = list(self.__node_dict.values())
                return nodes

            if ids != 0 and isinstance(ids, int):
                if self.Solver == "Nastran" or self.Solver == "Optistruct" or self.Solver == "Ansys" or self.Solver == "InputFileNastran":
                    if len(self.__partIDtoStr) > 1:
                        N2PLog.Error.E224()
                        nodes = -2
                    else:
                        nodes = self.__node_dict.get((ids, 0), -1)

                elif self.Solver == "Abaqus":
                    if len(self.__partIDtoStr) > 2:
                        N2PLog.Error.E224()
                        nodes = -2
                    else:
                        nodes = self.__node_dict.get((ids, 1), -1)

                if nodes == -1:
                    N2PLog.Error.E201(ids)
                return nodes

            if isinstance(ids, tuple) and len(ids) == 2:
                if isinstance(ids[1], str):
                    aux = self.__StrPartToID.get(ids[1])
                    nodes = self.__node_dict.get((ids[0], aux), -1)
                else:
                    nodes = self.__node_dict.get(ids, -1)
                if nodes == -1: N2PLog.Error.E201(ids)
                return nodes

            if ( isinstance(ids, tuple) and len(ids) > 2 ) or isinstance(ids, list):
                nodes = list()
                if isinstance(ids[0], tuple):
                    for id in ids:
                        if isinstance(id[1], str):
                            aux = self.__StrPartToID.get(id[1])
                            nodo = self.__node_dict.get((id[0], aux), -1)
                        else:
                            nodo = self.__node_dict.get(id, -1)
                        if nodo == -1: N2PLog.Error.E201(id)
                        nodes.append( nodo )
                    return nodes

                if isinstance(ids[0], int):
                    for id in ids:
                        if self.Solver == "Nastran" or self.Solver == "Optistruct" or self.Solver == "Ansys" or self.Solver == "InputFileNastran":
                            if len(self.__partIDtoStr) > 1:
                                N2PLog.Error.E224()
                                nodo = -2
                            else:
                                nodo = self.__node_dict.get((id, 0), -1)
                        elif self.Solver == "Abaqus":
                            if len(self.__partIDtoStr) > 2:
                                N2PLog.Error.E224()
                                nodes = -2
                            else:
                                nodo = self.__node_dict.get((id, 1), -1)
                        if nodo == -1:
                            N2PLog.Error.E201(id)
                        nodes.append( nodo )
                    return nodes
            return nodes

        except:
            nodes = -1
            N2PLog.Error.E205(ids)
            return nodes
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo general para conectores -----------------------------------------------------------------------------------
    def get_connectors(self, ids=0) -> N2PConnector or list[N2PConnector]:
        """ General method for obtain connectors.

        If it has no argument or is 0: returns all the elements.
        If it has one id as argument: returns one N2PConnector.
        If it has a list as argument it returns a list of N2PConnector.
        The ids should be a tuple (id, part_id). If not, part_id = 0 by default.

        Args:
            ids: int | list[int] | tuple[int, str] | list[tuple[int, str]]

        Returns:
            object: N2PConnector | list[N2PConnector]
        """
        try:
            if ids == 0:
                connectors = list(self.__connector_dict.values())
                return connectors

            if ids != 0 and isinstance(ids, int):
                if self.Solver == "Nastran" or self.Solver == "Optistruct" or self.Solver == "Ansys" or self.Solver == "InputFileNastran":
                    if len(self.__partIDtoStr) > 1:
                        N2PLog.Error.E225()
                        connectors = -2
                    else:
                        connectors = self.__connector_dict.get((ids, 0), -1)

                elif self.Solver == "Abaqus":
                    if len(self.__partIDtoStr) > 2:
                        N2PLog.Error.E225()
                        connectors = -2
                    else:
                        connectors = self.__connector_dict.get((ids, 1), -1)
                if connectors == -1:
                    N2PLog.Error.E204(ids)
                return connectors

            if isinstance(ids, tuple) and len(ids) == 2:
                if isinstance(ids[1], str):
                    aux = self.__StrPartToID.get(ids[1])
                    connectors = self.__connector_dict.get((ids[0], aux), -1)
                else:
                    connectors = self.__connector_dict.get(ids, -1)
                if connectors == -1: N2PLog.Error.E204(ids)
                return connectors

            if ( isinstance(ids, tuple) and len(ids) > 2 ) or isinstance(ids, list):
                connectors = list()
                if isinstance(ids[0], tuple):
                    for id in ids:
                        if isinstance(id[1], str):
                            aux = self.__StrPartToID.get(id[1])
                            conector = self.__connector_dict.get((id[0], aux), -1)
                        else:
                            conector = self.__connector_dict.get(id, -1)
                        if conector == -1: N2PLog.Error.E204(id)
                        connectors.append( conector )
                    return connectors

                if isinstance(ids[0], int):
                    for id in ids:
                        if self.Solver == "Nastran" or self.Solver == "Optistruct" or self.Solver == "Ansys" or self.Solver == "InputFileNastran":
                            if len(self.__partIDtoStr) > 1:
                                N2PLog.Error.E225()
                                conector = -2
                            else:
                                conector = self.__connector_dict.get((id, 0), -1)

                        elif self.Solver == "Abaqus":
                            if len(self.__partIDtoStr) > 2:
                                N2PLog.Error.E225()
                                connectors = -2
                            else:
                                conector = self.__connector_dict.get((id, 1), -1)

                        if conector == -1: N2PLog.Error.E204(id)
                        connectors.append( conector )
                    return connectors
            return connectors

        except:
            connectors = -1
            N2PLog.Error.E205(ids)
            return connectors   
    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener todos los sistemas de coordenadas (como N2Coord)----------------------------------------------
    def get_coords(self, ids=0) -> N2PCoord or list[N2PCoord]:
        """General method for obtain coordinate systems.

        If it has no argument or is 0: returns all the coordinate systems
        If it has one id as argument: returns one N2PCoord
        If it has a list as argument it returns a list of N2PCoord
        The ids should be a tuple (id, part_id). If not, part_id = 0 by default

        Args:
            ids: int | list[int] | tuple[int, str] | list[tuple[int, str]]

        Returns:
            object: N2PCoord | list[N2PCoord]
        """
        try:
            if ids == 0:
                coords = list(self.__coord_dict.values())
                return coords

            if ids != 0 and isinstance(ids, int):
                coords = self.__coord_dict.get((ids, 0), -1)
                if coords == -1: N2PLog.Error.E203(ids)
                return coords

            if isinstance(ids, tuple) and len(ids) == 2:
                if isinstance(ids[1], str):
                    aux = self.__StrPartToID.get(ids[1])
                    coords = self.__coord_dict.get((ids[0], aux), -1)
                else:
                    coords = self.__coord_dict.get(ids, -1)
                if coords == -1: N2PLog.Error.E203(ids)
                return coords

            if ( isinstance(ids, tuple) and len(ids) > 2 ) or isinstance(ids, list):
                coords = list()
                if isinstance(ids[0], tuple):
                    for id in ids:
                        if isinstance(id[1], str):
                            aux = self.__StrPartToID.get(id[1])
                            coord = self.__coord_dict.get((id[0], aux), -1)
                        else:
                            coord = self.__coord_dict.get(id, -1)
                        if coord == -1: N2PLog.Error.E203(id)
                        coords.append( coord )
                    return coords

                if isinstance(ids[0], int):
                    for id in ids:
                        coord = self.__coord_dict.get((id, 0), -1)
                        if coord == -1: N2PLog.Error.E203(id)
                        coords.append( coord )
                    return coords
            return coords

        except:
            coords = -1
            N2PLog.Error.E205(ids)
            return coords   
    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    ########################################    ClearResultStorage     #################################################
    ####################################################################################################################
    def clear_results_memory(self) -> None:
        """Method that delete the results data store at low level. It is useful when a lot of results are asked and
        kept in Python memory"""
        self.__vzmodel.ClearResultsStorage()
    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    ##########################################    Element-Nodal     ####################################################
    ####################################################################################################################
    # Metodo oculto para generar el array de nodos descosidos-----------------------------------------------------------
    def elementnodal(self) -> dict[int, tuple]:
        """ Method that generate the dictionary for the element-nodal mesh.

        Use the internal id for unsew nodes as key and a tuple (ID_Part_Solver, ID_Node_Solver, ID_Element_Solver) as a
        value. If the dictionary has already created it is pointed instead.

        Returns:
            dict[internal_node_unsew] = (Part_Solver, ID_Node_Solver, ID_Element_Solver)
        """
        # Si ya se ha creado no se vuelve a crear, directamente devuelve el valor
        if self.__elementnodal_dict is not None:
            return self.__elementnodal_dict
        else:

            aux = self.__vzmodel.GetNodosDescosidos()
            aux2 = np.array(aux, dtype=np.int32)

            self.__elementnodal_dict = {i: (self.__partIDtoStr.get(aux2[i][2], None), aux2[i][0], aux2[i][1])
                                        for i in range(aux2.shape[0])}

            return self.__elementnodal_dict
    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    ##########################################     Free Bodies      ####################################################
    ####################################################################################################################
    def create_free_body(self, name: str, loadcase: N2PLoadCase, increment: N2PIncrement = None, nodes: list[N2PNode] =
                         None, elements: list[N2PElement] = None, outpoint: tuple[float, ...] = None,
                         coordsysout: N2PCoord = None) -> N2PFreeBody:
        """Method that creates a N2PFreeBody object, keeps in N2PModelContent.FreeBodiesDict and returns it.

        A N2PFreeBody contains the information of the cross-section defined by the user and the forces and moments
        calculated by NaxToPy durin the instance of the object.

        Args:
            name: str -> Must be unique. If a new FreeBody is name as an old one, the old FreeBody will be deleted.
            loadcase: N2PLoadCase
            increment: N2PIncrement
            nodes: list[N2PNode]
            elements: list[N2PElement]
            outpoint: tuple[float]
            coordsysout: N2PCoord

        Returns:
            freebody: N2PFreeBody
        """

        if increment is None:
            increment = loadcase.get_increments(loadcase.ActiveIncrement)

        return N2PFreeBody(name, loadcase, increment, nodes, elements, self, coordsysout, outpoint)
    # ------------------------------------------------------------------------------------------------------------------

    def _import_load_cases(self):
        lcs = self.__vzmodel.LoadCases
        __number_of_load_cases = int(lcs.Count)

        self.__load_cases__ = [N2PLoadCase(lc.ID,
                                           lc.IDOriginal,
                                           lc.Increments,
                                           lc.IncrementsNumberList,
                                           lc.IsComplex,
                                           lc.LCType,
                                           lc.Name,
                                           lc.Results,
                                           lc.SolutionType,
                                           lc.Solver,
                                           self,
                                           lc) for lc in lcs]

    ####################################################################################################################
    ########################################     import_results      ###################################################
    ####################################################################################################################
    def import_results_from_files(self, results_files: list[str, ...]) -> None:
        """ Method of N2PModelContent that reads an output result file from Nastran, Abaqus, Optistruct or Ansys and
         add the results to the N2PModelContent Object.

            Supports .op2, .xdb, .odb, .h5, .h3d and .rst file extensions read from a local filesystem or URL.

            Args:
                results_files: list[str, ...]
            """
        if isinstance(results_files, str):
            results_files = [results_files]

        for result_file in results_files:
            self.__vzmodel.ImportResults(str(result_file))
            self._import_load_cases()
    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    ##################################     get_adjacent_from_elements      #############################################
    ####################################################################################################################
    def get_elements_adjacent(self,
                              cells: list[N2PElement, N2PConnector, ...],
                              domain: list[N2PElement, N2PConnector, ...] = None) -> list[N2PElement, N2PConnector, ...]:
        """ Method of N2PModelContent that returns a list of N2PElement and N2PConnector that are adjacent to selected
        ones. If a domain is selected, the adjacent elements only will be searched in that domain.

        Args:
            cells: list[N2PElement, N2PConnector, ...]
            domain: list[N2PElement, N2PConnector, ...] -> Optional. Set the domain where to look for the adjacent elements
            """
        if not isinstance(cells, list):
            cells = [cells]
        inernal_ids = array.array("q", [cell.InternalID for cell in cells])
        if not domain:
            adjacent_ids = N2AdjacencyFunctions.GetAdjacent(self.__vzmodel.UMesh, inernal_ids)
        else:
            csharp_bool_array = System.Array.CreateInstance(System.Boolean,
                                                            len(self.__element_dict)+len(self.__connector_dict))

            for elem in domain:
                csharp_bool_array[elem.InternalID] = True

            adjacent_ids = N2AdjacencyFunctions.GetAdjacent(self.__vzmodel.UMesh, inernal_ids, csharp_bool_array)

        cell_list = self.__cells_list

        return [cell_list[ids] for ids in adjacent_ids]
    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    ##################################     get_adjacent_from_elements      #############################################
    ####################################################################################################################
    def get_elements_attached(self,
                              cells: list[N2PElement, N2PConnector, ...],
                              domain: list[N2PElement, N2PConnector, ...] = None) -> list[N2PElement, N2PConnector, ...]:
        """ Method of N2PModelContent that returns a list of N2PElement and N2PConnector that are attached to selected ones. If a domain
        is selected, the attached elements only will be searched in that domain.

        Args:
            cells: list[N2PElement, N2PConnector, ...]
            domain: list[N2PElement, N2PConnector, ...] -> Optional. Set the domain where to look for the adjacent elements
            """
        if not isinstance(cells, list):
            cells = [cells]
        inernal_ids = array.array("q", [cell.InternalID for cell in cells])
        if not domain:
            adjacent_ids = N2AdjacencyFunctions.GetAttached(self.__vzmodel.UMesh, inernal_ids)
        else:
            csharp_bool_array = System.Array.CreateInstance(System.Boolean,
                                                            len(self.__element_dict)+len(self.__connector_dict))

            for elem in domain:
                csharp_bool_array[elem.InternalID] = True

            adjacent_ids = N2AdjacencyFunctions.GetAttached(self.__vzmodel.UMesh, inernal_ids, csharp_bool_array)

        cell_list = self.__cells_list

        return [cell_list[ids] for ids in adjacent_ids]
    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    #########################################     get_by_face      #####################################################
    ####################################################################################################################
    def get_elements_by_face(self,
                             cells: list[N2PElement, N2PConnector, ...],
                             tolerance_angle: float = 30,
                             one_element_adjacent: bool = True,
                             domain: list[N2PElement, N2PConnector, ...] = None) -> list[N2PElement, N2PConnector, ...]:
        """ Method of N2PModelContent that returns a list of N2PElement and N2PConnector that are in the same face as
        the selected ones. If a domain is selected, the face elements only will be searched in that domain. To be
        considered in the same face, the adjacent element must share an arist and the angle between the elements must be
        lower than the tolerance angle.

        Args:
            cells: list[N2PElement, N2PConnector, ...]
            tolerance_angle: float -> Optional (30º by default). Max angle[º] between two elements to be considered in the same face
            one_element_adjacent: bool -> Optional (True by default). If true, two elements are connected to arist of a selected element they will no be consisidered.
            domain: list[N2PElement, N2PConnector, ...] -> Optional. Set the domain where to look for the adjacent elements
            """
        if not isinstance(cells, list):
            cells = [cells]
        inernal_ids = array.array("q", [cell.InternalID for cell in cells])
        if not domain:
            adjacent_ids = N2AdjacencyFunctions.GetByFace(self.__vzmodel,
                                                          inernal_ids,
                                                          tolerance_angle,
                                                          one_element_adjacent)
        else:
            csharp_bool_array = System.Array.CreateInstance(System.Boolean,
                                                            len(self.__element_dict)+len(self.__connector_dict))

            for elem in domain:
                csharp_bool_array[elem.InternalID] = True

            adjacent_ids = N2AdjacencyFunctions.GetByFace(self.__vzmodel,
                                                          inernal_ids,
                                                          tolerance_angle,
                                                          one_element_adjacent,
                                                          csharp_bool_array)

        cell_list = self.__cells_list

        return [cell_list[ids] for ids in adjacent_ids]



    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    #########################################     get_free_edges      ##################################################
    ####################################################################################################################
    def get_free_edges(self,
                       domain: list[N2PElement, N2PConnector, ...] = None) -> list[tuple[N2PElement, N2PNode, N2PNode], ...]:

        """ Method of N2PModelContent that returns a list of tuples of N2PElement and two N2PNode of that element. 
        The two nodes define the edge of the element that is contained in the free edge of the mesh If a domain is selected, 
        the tuple will only be searched in that domain. Notice that connectors, although they may be given in the domain,
        they are never included in the free edges.

        Args:
            domain: list[N2PElement, N2PConnector, ...] -> Optional. Set the domain where to look for the adjacent elements
            """

        csharp_bool_array = System.Array.CreateInstance(System.Boolean,
                                                        len(self.__element_dict)+len(self.__connector_dict))

        if not domain:
            for i in range(len(self.__element_dict)+len(self.__connector_dict)):
                csharp_bool_array[i] = True
        else:
            for elem in domain:
                csharp_bool_array[elem.InternalID] = True

        free_edges_ids = N2FreeEdges.GetFreeEdgesFromVisibleIDs(self.__vzmodel.UMesh,
                                                                csharp_bool_array)

        cell_list = self.__cells_list
        node_list = list(self.__node_dict.values())
        return [(cell_list[id[0]], node_list[id[1]], node_list[id[2]]) for id in free_edges_ids]
    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    ######################################     Derived Load Case      ##################################################
    ####################################################################################################################
    def new_derived_loadcase(self, name: str, formula: str) -> N2PLoadCase:
        """Method of N2PModelContent that generate a new N2PLoadCase by lineal combination of n loadcases|frames.

        In order to define the combination a string with the load case and frame and the arithmetical commands as strings
        must be passed as arguments. The name of the new derived loadcase must be set, but the id not. The id will be a
        negative integer. The loadcases|frames must have this structure: <LCXX:FRYY>. Examples of formulas:
            - formula = "<LC1:FR1>+2*<LC2:FR1>+0.5*<LC5:FR3>"
            - formula = "0.5*<LC1:FR2>"
            - formula = "5*<LC2:FR3>-2*<LC3:FR3>"

        Args:
            name: str -> String with the name of the load case.
            formula: str -> String that must have the loadcase|frame is intended to use and the arithmetical opreations.

        Returns:
            N2PLoadCase -> Derived load case
        """
        # Comprobamos que el nombre no se repite:
        if name in [lc.Name for lc in self.LoadCases]:
            name += "-1"
            N2PLog.Warning.W301(name)

        # Genera una instancia de un N2LoadCase the VizzerClasses
        cs_lc = N2LoadCase(self.__vzmodel, name, formula)

        # Método de N2LoadCase que pone todoo en su sitio
        cs_lc.RecalculateLCInfo2Formule()

        # Se transforma el caso de carga de VizzerClasses en un N2PLoadCase de python
        py_lc = N2PLoadCase(cs_lc.ID, cs_lc.IDOriginal, cs_lc.Increments, cs_lc.IncrementsNumberList, cs_lc.IsComplex,
                            cs_lc.TypeLoadCase, cs_lc.Name, cs_lc.Results, cs_lc.SolutionType, cs_lc.Solver, self, cs_lc)

        # Se añade el caso de carga de csharp a N2ModelContent de Vizzer
        self.__vzmodel.LoadCases.Add(cs_lc)

        # Se añade el case de carga de python a N2PModelContent
        self.__load_cases__.append(py_lc)

        return py_lc

    def new_envelope_loadcase(self, name: str, formula: str) -> N2PLoadCase:
        """Method of N2PModelContent that generate a new N2PLoadCase that is the envelope of the load cases and increments
        selected.

        The id is automatically generated. It will be negative, starting at -1. If the new load case use a derivated or
        envelope load case use LCD1 in the formula instead of LC-1:

        Args:
            name: str -> Name of the envelope load case. It mustn't be repeated.
            formula: str -> formula that define the loadcases and increments must have this structure: <LCXX:FRYY>
                exmaple: "<LC1:FR1>,<LCD2:FR1>,<LC2:FR10>"

        Returns:
            N2PLoadCase
        """
        # Comprobamos que el nombre no se repite:
        if name in [lc.Name for lc in self.LoadCases]:
            name += "-1"
            N2PLog.Warning.W301(name)

        # Comprobamos que la formula está bien:
        formula = formula.replace("-", "D").replace(" ", "")

        # Genera una instancia de un N2LoadCase the VizzerClasses
        cs_lc = N2LoadCase(self.__vzmodel, name, formula, True)

        # Método de N2LoadCase que pone todoo en su sitio
        cs_lc.RecalculateLCInfo2Formule()

        # Se transforma el caso de carga de VizzerClasses en un N2PLoadCase de python
        py_lc = N2PLoadCase(cs_lc.ID, cs_lc.IDOriginal, cs_lc.Increments, cs_lc.IncrementsNumberList, cs_lc.IsComplex,
                            cs_lc.TypeLoadCase, cs_lc.Name, cs_lc.Results, cs_lc.SolutionType, cs_lc.Solver, self, cs_lc)

        # Se añade el caso de carga de csharp a N2ModelContent de Vizzer
        self.__vzmodel.LoadCases.Add(cs_lc)

        # Se añade el case de carga de python a N2PModelContent
        self.__load_cases__.append(py_lc)

        return py_lc
    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    #####################################     Results by LCs & Incr      ###############################################
    ####################################################################################################################
    def new_report(self, lc_incr: str, allincr: bool, result: str, componentssections: str, ifenvelope: bool,
                 selection: list[N2PNode, N2PElement], sortby: str, aveSections=-1, cornerData=False,
                 aveNodes=-1, variation=100, realPolar=0, coordsys: int = -1000,
                 v1: Union[tuple, np.ndarray] = (1, 0, 0), v2: Union[tuple, np.ndarray] = (0, 1, 0)) -> N2PReport:
        """Method of N2PModelContent that generates a N2PReport. A N2PReport object contains the information of the
        load cases, increments, components and sections for a result in the selection specified (nodes or elements).

        The N2PReport has a method that calculate the array result for the desired parameter and returns two ndarray
        of numpy (dtype = str): the array of headers, and the array of results.

        The N2PReport has also a method to write into a CSV all these data.

        Note:
            Only one result is available per report. Example: DISPLACEMENTS -> All components, for all load cases, but not
            STRESSES at the same time.

        Args:
            lc_incr: str -> Formula of the loadcases-increments desired. Each pair LC-FR must have the following
                structure <LCX:FRY> where X is the id of the load case and Y the id of the increment/frame. Example:
                "<LC1:FR1>,<LC1:FR2>,<LC2:FR1>,<LC2:FR2>".

            allincr: bool -> Parameter for asking all increments for the load cases asked.

            result: str -> Name of the result to ask.

            componentssections: str -> Formula with the components and the section desired. Each component can have
                several sections, and the structure must be: <ComopnentName:X#Y#Z#> where X, Y, Z are the names of the
                section. After each name of section there must be an #, even if there is only one. Example:
                "<VONMISES:Z1#Z2#>,<MAX_SHEAR:Z1#Z2#>"

            ifenvelope: bool -> Parameter to ask only for the results of the envelope of the load cases

            selection: list -> List of N2PElement or N2PNode where the results are desired. The user must take care that
                with displacements the list must be nodes and for stresses must be elements.

            sortby: str -> This parameter have two options: "LC" and "IDS". Specify if the results should be sorted by
                load cases or ids.

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

            coordsys: int -> Optional. Coordinate System where the result_array will be represented.
                0   : Global,
                -1  : Material Coordinate System,
                -10 : User defined,
                >0  : Solver ID of the Predefined Coordinate System.

            v1: tuple -> Optional.

            v2: tuple -> Optional. Directions vectors that generate the coordinate system axis:
                x=v1,
                z=v1^v2,
                y=z^x.

        Examples:
            report1 = model.new_report("<LC1:FR1>,<LC2:FR1>", False, "DISPLACEMNETS", "<X:NONE#>,<Y:NONE#>", False,
            list_n2pnodes, "LC")

            report2 = model.new_report("<LC1:FR1>,<LC1:FR2>,<LC4:FR6>", False, "STRESSES", "<VON_MISES:Z1#Z2#>,<MAX_SHEAR:Z1#Z2#>",
            False, list_n2pelements, "IDS", aveSections=-4, coordsys=-1)
        """
        # Here it is checkd if the components, the loadcases and the result exist and the formula is right
        try:
            lcs = [int(lc.split(":")[0][3:]) for lc in lc_incr.split(",")]
            components = [c.split(":")[0][1:] for c in componentssections.split(",")]
            for lc in lcs:
                A = self.get_load_case(lc).get_result(result).Components.keys()
                if not all(c in self.get_load_case(lc).get_result(result).Components.keys() for c in components):
                    N2PLog.Error.E312()
                    return "ERROR"
        except:
            N2PLog.Error.E313()
            return "ERROR"

        return N2PReport(self.__vzmodel, lc_incr, allincr, result, componentssections, ifenvelope, selection, sortby,
                         aveSections, cornerData, aveNodes, variation, realPolar, coordsys, v1, v2)
    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    #####################################     Results by LCs & Incr      ###############################################
    ####################################################################################################################
    def get_result_by_LCs_Incr(self, list_lc_incr: Union[list[tuple["N2PLoadCase", "N2PIncrement"],...],
                               list[tuple[int, int],...]], result: str,
                               component: str,  sections=None, aveSections=-1, cornerData=False, aveNodes=-1,
                               variation=100, realPolar=0, coordsys: int = -1000, v1: tuple = (1,0,0),
                               v2: tuple = (0,1,0)) -> dict[tuple: "ndarray"]:
        """Method to ask for results of a component in several loadcases and increments. It uses parallel subprocesses
        to speed up the calculus. Returns a dictionary where the keys are tuples with the IDs of LoadCase and Increment
        and the values are numpy arrays.

        Examples:
            vonmises = .get_result_by_LCs_Incr([(1,2),(2,2)], "STRESSES", "VON_MISES")
            XX = .get_result_by_LCs_Incr([(loadcase1, increment2), (loadcase2, increment2), "STRAINS", "XX"])

        Args:

            list_lc_incr: list[tuple] -> list with the tuples of the loadcase|increment asked for the component

            result: str -> String with the result

            component: str -> String with the component

            sections: list[str] | list[N2PSection] -> Sections which operations are done.
                None (Default) = All Sections

            aveSections: int -> Operation Among Sections.
                -1 : Maximum (Default),
                -2 : Minimum,
                -3 : Average,
                -4 : Extreme,
                -6 : Difference.

            cornerData: bool -> flag to get results in element nodal.
                True : Results in Element-Nodal,
                False : Results in centroid (Default).

            aveNodes: int -> Operation among nodes when cornerData is selected.
                0 : None,
                -1 : Maximum (Default),
                -2 : Minimum,
                -3 : Average,
                -5 : Average with variation parameter,
                -6 : Difference.

            variation: int -> Integer between 0 & 100 to select.
                0 : No average between nodes,
                100 : Total average between nodes (Default).

            realPolar: int -> data type when complex result.
                1 : Real / Imaginary,
                2 : Magnitude / Phase.

            coordsys: int -> Coordinate System where the result_array will be represented.
                0   : Global,
                -1  : Material Coordinate System,
                -10 : User defined,
                >0  : Solver ID of the Predefined Coordinate System.

            v1: tuple

            v2: tuple -> Directions vectors that generate the coordinate system axis:
                x=v1,
                z=v1^v2,
                y=z^x.

        Returns:
            dict[tuple: ndarray] -> results for the component ordered in a dictionary

        """

        if isinstance(list_lc_incr[0][0], N2PLoadCase):
            aux_lc = list_lc_incr[0][0]
        elif isinstance(list_lc_incr[0][0], int):
            aux_lc = self.get_load_case(list_lc_incr[0][0])
        else:
            N2PLog.Error.E310()
            return None

        # Aqui se llama la funcion de verdad que es un metodo de N2PComponent. Se llama a ella porque hace uso de otras
        # funciones ya definidas (n2paraminputresult) en la clase y es mejor no repetir codigo.
        return aux_lc.get_result(result).get_component(component)._get_result_by_LCs_Incr(list_lc_incr,
                                                                                          sections,
                                                                                          aveSections,
                                                                                          cornerData,
                                                                                          aveNodes,
                                                                                          variation,
                                                                                          realPolar,
                                                                                          coordsys,
                                                                                          v1,
                                                                                          v2)

    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    #######################################     ElementsCoordSys      ##################################################
    ####################################################################################################################
    def _elements_coord_sys(self):
        if not self.__elements_coord_sys:
            self.__elements_coord_sys = self.__vzmodel.ElementCoordSystem
        return self.__elements_coord_sys
    # ------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


# Metodo para cargar un objeto N2PModelContent desde un archivo de resultados ------------------------------------------
def initialize(path: str, parallelprocessing: bool = False) -> N2PModelContent:
    """ Deprecated function. This funtion has been substituted by load_model() """
    N2PLog.Warning.W205()

    return load_model(path, parallelprocessing, "Binary")
# ----------------------------------------------------------------------------------------------------------------------


# Metodo para cargar un objeto N2PModelContent desde un archivo de resultados o desde un archivo de texto --------------
def load_model(path: str, parallelprocessing: bool = False, file_type: str = None) -> N2PModelContent:
    """ Read an output result file in binary format from Nastran, Abaqus, Optistruct or Ansys and transform it into a
    N2PModelContent Object. It also can read models from input files in Nastran format.

        Supports .op2, .xdb, .odb, .h5, .h3d and .rst file extensions read from a local filesystem or URL.

        Supports Nastran input files. (Typically .bdf extension)

        Args:
            path: str
            parallelprocessing: bool -> Optional. If true, the low libraries open the result files in several processes. It is slightly faster.
            file_type: str -> Optional. It specifies if it is Nastran input file ("InputFileNastran") or binary result file ("Binary").

        Returns:
            model: N2PModelContent
        """
    if not os.path.exists(path):
        N2PLog.Critical.C108(path)
        return "ERROR"
        # sys.exit()

    if path.split(".")[-1] in BINARY_EXTENSIONS and file_type == "InputFileNastran":
        N2PLog.Error.E111()

    return N2PModelContent(path, parallelprocessing, file_type)


def _is_binary(path) -> str:
    """Function that returns if the file is a binary or text file"""
    count = 0
    with open(path, 'rb') as f:
        for block in f:
            if b'\x00' in block:
                return "Binary"
            elif any(byte < 9 or (13 < byte < 32) for byte in block):
                return "Binary"
            if count > 100:
                break
            count += 1
    return "InputFileNastran"
