import os
import sys
import logging
import time
import atexit
from abc import ABC
from NaxToPy.Core.Errors.N2PFileHandler import FileHandler

# Clase que se encarga del registro de NaxToPy -------------------------------------------------------------------------
class N2PLog(ABC):
    """ Class prepared for the control of the program.

    It uses the module logging to register the main instructions and
    data of the NaxToPy Package. It can't be instanced.

    Attributes:
        LevelList
    """

    # Aqui se definen los atributos de la clase, cuyo concepto es ligeramente diferente ald de los de la instancia
    flv = "INFO"
    clv = "WARNING"

    __levellist = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    # Nivel de registro del archivo .log
    if flv == "DEBUG":
        __flevel = logging.DEBUG
    elif flv == "WARNING":
        __flevel = logging.WARNING
    elif flv == "ERROR":
        __flevel = logging.ERROR
    elif flv == "CRITICAL":
        __flevel = logging.CRITICAL
    else:
        __flevel = logging.INFO

    # Nivel de registro de lo que sale por consola
    if clv == "DEBUG":
        __clevel = logging.DEBUG
    elif clv == "WARNING":
        __clevel = logging.WARNING
    elif clv == "ERROR":
        __clevel = logging.ERROR
    elif clv == "CRITICAL":
        __clevel = logging.CRITICAL
    else:
        __clevel = logging.INFO

    __directory = os.path.dirname(os.path.abspath(sys.argv[0]))

    if __directory == "C:\\Users":
        __directory = os.path.expanduser("~") + "\\Documents\\"

    __filename = time.strftime("NaxToPy_%d-%m-%Y.log", time.localtime())
    __path = os.path.join(__directory, __filename)

    __logger = logging.getLogger('Logger')
    __logger.setLevel("DEBUG")

    # Formato en el que se presenta los datos del registro en el archivo .log
    __formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)-5s", "%H:%M:%S")

    # File with the loggin data:
    __fh = FileHandler(__path)
    __fh.setLevel(__flevel)
    __fh.setFormatter(__formatter)
    __logger.addHandler(__fh)

    # Formato en el que se presenta los datos del registro en la consola
    __formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)-5s", "%H:%M:%S")

    # Loggin data shown in the console
    __ch = logging.StreamHandler()
    __ch.setLevel(__clevel)
    __ch.setFormatter(__formatter)
    __logger.addHandler(__ch)

    # Primera instruccion en el logger
    __logger.info("############### NaxToPy Started ###############")

    # Ultima instruccion en el logger
    atexit.register(__logger.info, "############### NaxToPy Finished ###############\n")

    # Tras cualquier error critico, contemplado o no, se ejecuta esta funcion. Se comprueba si el ultimo error
    # almacenado era crtico o no, se escribe el archivo .log y se activa el logger. Si el ultimo error almacenado no
    # era critico o no hay errores almacenados es porque el error que ha causado el fallo no estaba contemplado. En
    # ese caso se llama al error C001 y despues se escribe el log 
    def _my_excepthook(excType, excValue, traceback, logger=__logger, fh=__fh):

        if not fh.buffered_records:
            previous_critical = fh.buffered_records[-1].getMessage().startswith('C')
        else:
            previous_critical = False

        if not previous_critical:
            logger.critical("C001: UNCAUGHT CRITICAL EXCEPTION: ", exc_info=(excType, excValue, traceback))

        fh.write_buffered_records()
        fh.immediate_logging()
    # ----------------------------------------------------------------------------------------------------------------

    sys.excepthook = _my_excepthook

    # ATRIBUTOS COMO CLASES DE LA CLASE N2PLog PARA INTRODUCIR DATOS EN EL REGISTRO -----------------------------------

    ############################################  DEBUG  ###############################################################
    class Debug:
        """ Class with all the debug data.

        The DXXX are methods that keep in the register the information in the
        debuggibg procces about the processes that the package is keeping. Use only in the debug stages.
        """

        @staticmethod
        def user(message: str) -> None:
            """Method prepared to be called by the user for adding debugs data to the loggin

            Anyone who is using NaxToPy can write in the register their
            own debug message. Use the following structure as a standard message (D + four digits + Body).

            Args:
                message: str

            Example:
                "DXXXX: Body of the message"
            """
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D100(instruction, timee) -> None:
            """Method for timing the instructions during debug
            """
            message = f"Time (s) {instruction}: {timee}"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D101(path) -> None:
            """Method that shows the location of the VizzerClasses library found"""
            message = f"VizzerClasses founded at: {path}"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D102() -> None:
            """Method that shows if the property Program_Call of N2ModelContent was changed"""
            message = f"Program_Call of N2ModelContent has been set"
            N2PLog._N2PLog__logger.debug(message)

        @staticmethod
        def D103(parallel) -> None:
            """Method that shows the parallel option set at low level"""
            message = f"The parallel processing has been set to {parallel}"
            N2PLog._N2PLog__logger.debug(message)

    # ------------------------------------------------------------------------------------------------------------------

    ############################################  INFO  ################################################################
    class Info:
        """ Class with all the information data. The IXXX are methods that keep in the register the information
about the processes that the package is keeping.
        """

        @staticmethod
        def user(message) -> None:
            """ Method prepared to be used by the user so anyone who is using NaxToPy can write in the register their
own information message. Use the following structure as a standard message (I + four digits + Body).

                "IXXXX: Body of the message"
            """
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I100() -> None:
            """ Information that show that the NaxToPy Runing Code.
            """
            from IdaeroLicense import LicenseManager
            from System import DateTime

            time_date = DateTime.Now
            licen = LicenseManager()
            code = licen.GetRunCode(time_date)
            message = f"I100: The NaxToPy Running with the code: {code}"
            N2PLog._set_format2(time_date.ToString().split(" ")[1])
            N2PLog._N2PLog__logger.info(message)
            N2PLog._set_format1()

        @staticmethod
        def I101(vizzer_libs) -> None:
            """ Information that show that the NaxTo libraries were correctly found at vizzer_libs.
            """
            message = f"I101: The NaxTo libraries were found successfully at {vizzer_libs}."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I102(value) -> None:
            message = f"I102: The directory of the .log file has been modified to {value} ."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I103(value) -> None:
            message = f"I103: The name of the .log file has been modified to {value} ."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I104() -> None:
            message = f"I104: Numpy installation has been successfully completed."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I105() -> None:
            """ Information given when the register is modified correctly.
            """
            message = f"I105: The windows register was modified with the path of the NaxTo libraries successfully."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I106(register, key_version) -> None:
            """ Information given when the register is modified correctly.
            """
            message = f"I106: Key for {key_version} created successfully in {register}."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I107() -> None:
            """ Information given when the program is called from a .exe file.
            """
            message = "I107: Working with the executable version of NaxToPy."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I108() -> None:
            """ Information given when the program use the develover version of VizzerClasses.
            """
            message = "I108: Working with developer version of VizzerClasses."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I109() -> None:
            """ Information given when the VizzerClasses library is load correctly.
            """
            message = f"I109: The library VizzerClasses.dll was load successfully."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I110(path) -> None:
            """ Information given when the file .N2P is saved correctly.
            """
            message = f"I110: The file {path} has been successfully saved."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I111(path) -> None:
            """ Information given when the result file is initialize correctly.
            """
            message = f"I111: The file {path} has been successfully opened."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I112() -> None:
            """ Information given when the result the mesh is build correctly.
            """
            message = "I112: The mesh has been successfully created."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I200() -> None:
            """ Information given when the NaxToPy.ico is found correctly.
            """
            message = "I200: The NaxToPy icon file has been successfully found."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I201(file) -> None:
            """ Information given when the .exe file built with n2ptoexe() is correctly created.
            """
            message = f"I201: The .exe file has been successfully created at {file}."
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I202(id) -> None:
            """ Information given when the .exe file built with n2ptoexe() is correctly created.
            """
            message = f"I202: The Active Increment has been set to the ID: {id}"
            N2PLog._N2PLog__logger.info(message)

        @staticmethod
        def I203() -> None:
            """ Information given when the module N2PEnvelope is executing.
            """
            message = f"I203: Executing N2PEnvelope..."
            N2PLog._N2PLog__logger.info(message)

    # ------------------------------------------------------------------------------------------------------------------

    ###########################################  WARNING  ##############################################################
    class Warning:
        """ Class with all the warnings. The WXXX are methods that keep in the register the warnings that might be
        revised. They don't affect directly to the correct working of the package.
        """

        @staticmethod
        def user(message) -> None:
            """ Method prepared to be used by the user so anyone who is using NaxToPy can write in the register their
            own warning message. Use the following structure as a standard message (W + four digits + Body).

                "WXXXX: Body of the message"
            """
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W100() -> None:
            """ Warning raised when numpy is not installed and it will be installed using pip
            """
            message = "W100: numpy package is not installed. In order to execute this method, the package is needed. \n" + \
                      "      The installation will start in 10 seconds ."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W101() -> None:
            """ Warning raised when the register level of the .log file is intended to change, as it could make more difficult to track errors
            """
            message = "W101: Register level of the .log has changed to a higher filter. This can make more difficult to track errors."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W102(path) -> None:
            """ Warning raised when the Windows Register is modified by NaxToPy
            """
            message = f"W102: The Windows Register has been modified: CURRENT_USER/SOFTWARE/IDAERO -> Path = {path}" + \
                "If NaxTo is installed afterwards, this key must be deleted"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W103() -> None:
            """ Warning raised when the Windows Register is modified by NaxToPy: The Path value is deleted
            """
            message = f"W103: The Path Value in Windows Register has been deleted: Using installed NaxTo libraries"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W200() -> None:
            """ Warning raised when the executable file is build without the icon
            """
            message = "W200: The .exe file will not have the NaxToPy icon. There should have been an error while loading it"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W201() -> None:
            """ Warning raised when the AbaqusVersion is asked but the solver is not Abaqus
            """
            message = "W201: The Abaqus version is None as the solver is not ABAQUS"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W202() -> None:
            """ Warning raised when the number of elements don't match with the size of the results
            """
            message = "W202: The number of elements don't match with the size of the results"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W203(key) -> None:
            """ Warning raised when there are two connectors with the same id. So they are saved in the connector dict
            as a list.
            """
            message = f"W203: there are two or more connectors with the same id. They are saved in the connector" + \
                      f"dict as a list with the same key: {key}."
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W204() -> None:
            """ Warning raised when there is no Model Data from an Input File.
            """
            message = f"W204: There is no data from an input file data supported"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W205() -> None:
            """ Warning raised when there the Deprecated function "Initialize" is called.
            """
            message = f"W205: Initialize is a deprecated function. Please, use load_model instead"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W300() -> None:
            """ Warning raised when there are more dimensions than points in n2p.envelope
            """
            message = f"W300: there are more dimensions than points as arguments in n2p.envelope"
            N2PLog._N2PLog__logger.warning(message)

        @staticmethod
        def W301(name) -> None:
            """ Warning raised when the name for the new derived load case already exist
            """
            message = f"W301: the name for the new load case already exist. It has been rename to '{name}'"
            N2PLog._N2PLog__logger.warning(message)

    # ------------------------------------------------------------------------------------------------------------------

    ############################################  ERROR  ###############################################################
    class Error:
        """ Class with all the errors that can be expected.

        They should be handeled by a try-exception clasule. The errors are method that do not return anything,
        they write in the log file and console the error.
        """

        @staticmethod
        def user(message: str) -> None:
            """ Method prepared to be called by the user for adding errors to the loggin

            This anyone who is using NaxToPy can write in the register their
            own error message. Use the following structure as a standard message (E + four digits + Body).

            Args:
                message: str

            Example:
                "EXXXX: BODY OF THE MESSAGE"
            """
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E101() -> None:
            """ Error raised when the NaxTo libraries couldn't be found.
            """
            message = "E101: THE NAXTO LIBRARIES COULDN'T BE FOUND."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E102() -> None:
            """ Error raised when the value to set the directory where the .log file is not a string.
            """
            message = "E102: THE DIRECTORY OF THE .log MUST BE A STRING."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E103() -> None:
            """ Error raised when the value to set the file name of the .log is not a string.
            """
            message = "E103: THE FILE NAME OF THE .log MUST BE A STRING."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E104() -> None:
            """ Error raised when directory of the .log couldn't be changed.
            """
            message = "E104: THE DIRECTORY OF THE .log COULDN'T BE CHANGED."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E105() -> None:
            """ Error raised when the file name of the .log could'nt be changed.
            """
            message = "E105: THE FILE NAME OF THE .log COULDN'T BE CHANGED."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E106() -> None:
            """ Error raised when there is an error while closing the windows register after modifing.
            """
            message = "E106: THE WINDOWS REGISTER COULDN'T BE CLOSED PROPERLY."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E107(levellist) -> None:
            """ Error raised when the register level is intended to change and the level is not one of the possible choices.
            """
            message = f"E107: THE REGISTER LEVEL IS NOT OF THE POSSIBLE ONES ({levellist})."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E108() -> None:
            """ Error raised when the change of register level of the .log file fails.
            """
            message = f"E108: THE REGISTER LEVEL OF THE .log FILE COULDN'T BE CHANGED."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E109() -> None:
            """ Error raised when the change of register level of the console fails.
            """
            message = f"E109: THE REGISTER LEVEL OF THE CONSOLE COULDN'T BE CHANGED."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E110(path) -> None:
            """ Error raised when the n2ptoexe tries to createa exe from a module that dont use NaxToPy.
            """
            message = f"E110: THE MODULE IN {path} DOESN'T USE NaxToPy"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E111() -> None:
            """ Error raised when a file with an extension of a binary result file is intended to be loaded as
            nastran input text file
            """
            message = f"E111: THE FILE THAT IS INTENDED TO LOAD IS BINARY RESULT FILE, NOT A NASTRAN INPUT TEXT FILE"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E112(er) -> None:
            """ Error raised when the Windows Register couldn't be modified
            """
            message = f"E112: THE WINDOWS REGISTER COULDN'T BE MODIFIED. ERROR: {er}"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E201(*args) -> None:
            ''' Error raised when the id of the node is not in the node dictionary.
            '''
            message = "E201: NODE " + str(*args) + " NOT FOUND."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E202(*args) -> None:
            ''' Error raised when the id of the element is not in the element dictionary.
            '''
            message = "E202: ELEMENT " + str(*args) + " NOT FOUND."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E203(*args) -> None:
            ''' Error raised when the id of the coordinate system is not in the coord dictionary.
            '''
            message = "E203: COORDINATE SYSTEM " + str(*args) + " NOT FOUND."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E204(*args) -> None:
            ''' Error raised when the id of the connector is not in the coord dictionary.
            '''
            message = "E204: CONNECTOR " + str(*args) + " NOT FOUND."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E205(*args) -> None:
            ''' Error raised when the arguments are no recognize by the function.
            '''
            message = "E205: THE INPUT " + str(*args) + " IS NOT RECOGNIZE."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E206(arg) -> None:
            ''' Error raised when the component don't have any results.
            '''
            message = "E206: THE COMPONENT " + str(arg) + " DON'T HAVE ANY RESULTS WITH THE SPECIFIED CONFIG."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E207(arg) -> None:
            ''' Error raised when there is not any Increment with the ID specified.
            '''
            message = "E207: THE INCREMENT WITH THE ID " + str(arg) + " DOESN'T EXIST."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E208() -> None:
            """
            Error raised when there is not any result. Some arguments may be the problem.
            """
            message = "E208: THERE IS NOT ANY RESULT WITH THE SPECIFICATION GIVEN."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E209(name) -> None:
            """
            Error raised when there is not ID for the property (Abaqus don't use ids for properties).
            """
            message = f"E209: THERE IS NOT ID FOR THE PROPERTY {name}"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E210(name) -> None:
            """
            Error raised when there is not PartID for the property (Abaqus don't use ids for properties).
            """
            message = f"E210: THERE IS NOT PartID FOR THE PROPERTY {name}"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E211() -> None:
            """
            Error raised when the increment asked is not an id(int) or a name(str).
            """
            message = f"E211: THE ARGUMENT FOR GET INCREMENT MUST BE A NAME(str) or an ID(int)"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E212(id) -> None:
            """
            Error raised when the increment asked is found.
            """
            message = f"E212: THE INCREMENT {id} WAS NOT FOUND"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E213(name) -> None:
            """
            Error raised when the result asked is found.
            """
            message = f"E213: THE RESULT {name} WAS NOT FOUND"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E214() -> None:
            """
            Error raised when the result asked is not name(str).
            """
            message = f"E214: THE ARGUMENT FOR GET RESULT MUST BE A NAME(str)"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E215(name) -> None:
            """
            Error raised when the component asked is not found.
            """
            message = f"E215: THE COMPONENT {name} WAS NOT FOUND"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E216() -> None:
            """
            Error raised when the component asked is not name(str).
            """
            message = f"E216: THE ARGUMENT FOR GET COMPONENT MUST BE A NAME(str)"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E217(name) -> None:
            """
            Error raised when the derived component asked is not found.
            """
            message = f"E215: THE DERIVED COMPONENT {name} WAS NOT FOUND"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E218() -> None:
            """
            Error raised when the sections asked in the get_array function.
            """
            message = f"E218: THE SECTIONS MUST BE A LIST OF STRINGS IN THE GET ARRAY RESULT"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E219() -> None:
            """
            Error raised when the component selected is not transformable.
            """
            message = f"E219: THE COMPONET SELECTED IS NOT TRANSFORMABLE"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E220() -> None:
            """
            Error raised when there is an error during the processing of the output coord system.
            """
            message = f"E220: ERROR SELECTION THE OUTPUT COORDINATE SYSTEM"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E221(arg) -> None:
            ''' Error raised when the id of the load case is not found.
            '''
            message = F"E221: THE LOAD CASE WITH ID {arg} DOESN'T EXIST IN THE MODEL."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E222(arg) -> None:
            ''' Error raised when the NAME of the load case is not found.
            '''
            message = F"E222: THE LOAD CASE WITH NAME {arg} DOESN'T EXIST IN THE MODEL."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E223() -> None:
            ''' Error raised when the get element need the part and not only the id.
            '''
            message = F"E223: THE PART IS NEEDED AS A INPUT IN get_elements(arg). TRY USING A TUPLE: (id, part)"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E224() -> None:
            ''' Error raised when the get nodes need the part and not only the id.
            '''
            message = F"E224: THE PART IS NEEDED AS A INPUT IN get_nodes(arg). TRY USING A TUPLE: (id, part)"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E225() -> None:
            ''' Error raised when the get connectors need the part and not only the id.
            '''
            message = F"E225: THE PART IS NEEDED AS A INPUT IN get_connectors(arg). TRY USING A TUPLE: (id, part)"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E226() -> None:
            ''' Error raised when ABD matrix is not invertible.
            '''
            message = F"E226: THE ABD MATRIX IS NOT INVERTIBLE"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E227(rep_id) -> None:
            ''' Error raised when there is a repeated ID in the properties
            '''
            message = f"E227: THE PROPERTY ID {-rep_id} IS REPEATED. ONE WILL BE SAVE WITH THE SIGN CHANGE"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E300(args) -> None:
            ''' Error raised when the program fail to save the model (as a N2PModelContent object).
            '''
            prueba = list(locals().keys())
            message = "E300: THE MODEL {prueba} COULDN\'T BE SAVE."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E301(args) -> None:
            ''' Error raised when the extension of the file path that is intended to save is wrong.
            '''
            message = "E301: FILE {args} HAS A WRONG EXTENSION."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E302(args) -> None:
            ''' Error raised when the program faile to load the model (as a N2PModelContent object) from a .N2P file.
            '''
            message = "E302: THE MODEL COULDN'T BE LOAD FROM {args}."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E303(args) -> None:
            ''' Error raised when the extension of the file path that is intended to load is wrong.
            '''
            message = "E303: FILE {args} HAS A WRONG EXTENSION."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E304() -> None:
            ''' Error raised when NaxToPy.ico is not found.
            '''
            message = f"E304: NAXTOPYTHON ICON WAS NOT FOUND IN THE PACKAGE (icon.ico)."
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E305() -> None:
            ''' Error raised when the length of the columns of the cloud of points don't macht in N2PEnvelope.
            '''
            message = f"E305: THE LENGHT OF THE DATA INCLUDED MUST HAVE THE SAME LENGTH"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E306() -> None:
            ''' Error raised when the arguments of envelope are not valid.
            '''
            message = f"E306: THE ARGUMENTS OF 'envelope' MUST BE A DATAFRAME OR LISTS"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E307() -> None:
            ''' Error raised when the dataframe of envelope has NaN values.
            '''
            message = f"E307: THE DATAFRAME ARGUMENT HAS NAN VALUES IN IT. PLEASE CHECK THE INPUTS"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E308() -> None:
            ''' Error raised when qhull library fails (wrong inputs, coplanar points, etc).
            '''
            message = f"E308: THE INNER LIBRARY FAILED (WRONG INPUTS OR COPLANAR POINTS)"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E309() -> None:
            ''' Error raised when qhull library fails (wrong inputs, coplanar points, etc).
            '''
            message = f"E309: THE INNER LIBRARY FAILED (INSUFFICIENT NUMBER OF POINTS)"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E310() -> None:
            ''' Error raised when the inputs list(tuple(LC, Incr)) for getting results for LC and Incr are wrong.
            '''
            message = f"E310: THE LIST OF LOAD CASES AND INCREMENTS MUST BE A A LIST OF TUPLES. THE TUPLE MUST BE " + \
                      f"(N2PLOADCASE, N2PINCREMENT) OR (INT[id_lc], INT[id_incr])"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E311() -> None:
            ''' Error raised when the sortby parameter of the N2PReport is not one of the possible ones.
            '''
            message = f"E311: THE SORTBY PARAMETER FOR A N2PREPORT MUST BE 'LC' OR 'IDS' "
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E312() -> None:
            ''' Error raised when the components asked for the N2PReport are not found in the model
            '''
            message = f"E312: THE COMPONENTS ASKED FOR THE N2PREPORT ARE NOT IN THE MODEL"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E313() -> None:
            ''' Error raised when there is an error in the arguments, probably in the formulas.
            '''
            message = f"E313: THERE IS AN ERROR IN THE ARGUMENTS OF THE METHOD new_report()"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E314() -> None:
            ''' Error raised when there is an error generating the report in VizzerClasses.
            '''
            message = f"E314: INTERNAL ERROR WHILE CALCULATING THE REPORT. PLEASE, CHECK THE ARGUMENTS"
            N2PLog._N2PLog__logger.error(message)

        @staticmethod
        def E400() -> None:
            ''' Error raised when the atttribute of a N2PCard is intended to change and the new value lenght don't match
            with the previous.
            '''
            message = f"E400: THE LENGTH OF THE LIST DONT MATCH WITH THE PREVIOUS LENGTH LIST ATTRIBUTE OF A N2PCARD"
            N2PLog._N2PLog__logger.error(message)
    # ------------------------------------------------------------------------------------------------------------------

    ###########################################  CRITICAL  #############################################################
    class Critical:
        """Class with all the critical errors.

        The critical are methods that do not return anything, they write in the log file and console the error.
        Optionally a raise Exception could be added. Always a sys.exit() should be executed at the end.
        """

        @staticmethod
        def user(message: str) -> None:
            """Method prepared to be called by the user for adding CRITICAL errors to the loggin.

            Anyone who is using NaxToPy can write in the register their own CRITICAL error message.
            Use the following structure as a standard message (C + four digits + Body).

            Args:
                message: str

            Example:
                "CXXXX: BODY OF THE MESSAGE"
            """
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C001(message):
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C100(path, error) -> None:
            """ Critical error raised when the model couldn't be initialized.
            """
            message = f"C100: THE MODEL IN THE FILE {path} COULDN'T BE INITIALIZED. (Vizzer Error: {error})"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C101(error) -> None:
            """ Critical error raised when the mesh couldn't be generated.
            """
            message = f"C101: THE MESH COULDN'T BE GENERATED. (Vizzer Error: {error})"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C102(py_version) -> None:
            """ Critical Error raised when the current python version is not supported.
            """
            message = f"C102: THE CURRENT PYTHON VERSION ({py_version}) IS NOT SUPPORTED."
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C103() -> None:
            """ Critical Error raised when VizzerClasses.dll is not properly load.
            """
            message = f"C103: THE LIBRARY 'VizzerClasses.dll' COULDN'T BE LOADED CORRECTLY"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C104() -> None:
            """ Critical Error raised when the console argument in n2ptoexe is not a bool type.
            """
            message = f"C104: THE ARGUMENT CONSOLE MUST BE A BOOLEAN: True | False"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C105(directions) -> None:
            """ Critical Error raised when the argument abaqus version in n2ptoexe is wrong or not supported.
            """
            message = f"C105: THE ARGUMENT ABAQUSVERSION MUST BE ONE OF THE AVIABLE: {directions}"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C106() -> None:
            """ Critical Error raised when the pyinstaller is not installed and it couldn´t be downloaded.
            """
            message = f"C106: THE PACKAGE PyInstaller COULDN'T BE LOADED. PLEASE INSTALL IT MANUALLY"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C107() -> None:
            """ Error raised when the NaxTo libraries couldn't be found.
            """
            message = "C107: THE NAXTO LIBRARIES COULDN'T BE FOUND. PLEASE, INSTALL NAXTO"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C108(path) -> None:
            """ Error raised when the file couldn't be found.
            """
            message = f"C108: THE FILE {path} DOESN'T EXIST"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C109(ver, comp_ver) -> None:
            """ Error raised when NaxTo is not installed.
            """
            message = f"C109: THIS VERSION OF NAXTOPY ({ver}) IS ONLY COMPATIBLE WITH THIS ASSEMBLY VERSION: {comp_ver}"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C110(ver, comp_ver) -> None:
            """ Error raised when there aren't installed a compatible version of  with minor changes.
            """
            message = f"C110: THIS VERSION OF NAXTOPY({ver}) IS NOT COMPATIBLE WITH THIS NAXTO VERSION: {comp_ver}"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C111(ver) -> None:
            """ Error raised when there version of NaxTo is not found.
            """
            message = f"C111: NAXTO VERSION WAS NOT FOUND. PLEASE, CHECK IF NAXTO{ver} IS INSTALLED"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C112() -> None:
            """ Error raised when there is an Elements safearray error in VizzerClasses (Vizzer Error: -1003). This
            error could happen when the memory of the processor tthat call the low level libraries has a leak (is not
            correctly erased). A solution may be change the initialize method to parallel.
            """
            message = f"C112: ERROR RAISED WHEN THERE IS AN ERROR IN THE SA OF ELEMENTS. THIS MAY BE CAUSED BY A MEMORY" \
                      f"LEAK IN THE LOW LEVEL LIBRERIES. A SOLUTION MAY BE CHANGE THE \"initilaize\" method to parallel:" \
                      f"model = NaxToPy.initialize(path, parallelprocessing=True)"
            N2PLog._N2PLog__logger.critical(message)

        @staticmethod
        def C200() -> None:
            """ Critical error raised when numpy couldn't be installed.
            """
            message = "C200: NUMPY PACKAGE COULDN\'T BE INSTALLED. PLEASE, INSATALL IT MANUALY."
            N2PLog._N2PLog__logger.critical(message)

    # ------------------------------------------------------------------------------------------------------------------

    ####################################################################################################################
    ##################  METODOS GETTER Y SETTER PARA USAR LOS ATRIBUTOS COMO PROPIEDADES  ##############################
    ####################################################################################################################

    # Nota: Estos metodos cambian los atributos del objeto que se ha instanciado como clase N2PLog y que se
    #       ha guardado dentro del atributo _ De ahí que estos metodos no vayan como propiedades.

    # Metodo para obtener la lista de niveles del registro -------------------------------------------------------------
    @classmethod
    @property
    def LevelList(cls) -> list[str]:
        """Property that retuns the list with the message levels in the log"""
        return cls.__levellist

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener directorio donde se guarda el archivo.log ----------------------------------------------------
    @classmethod
    def get_directory(cls) -> str:
        """Method that returns the folder where the .log file is being saved"""
        return cls.__directory

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para declarar directorio donde se guarda el archivo.log ---------------------------------------------------
    @classmethod
    def set_directory(cls, value) -> None:
        """Method that sets the folder where the .log file must be saved

        Args:
            value: str -> Path to the folder where the .log must be saved.

        """
        if isinstance(value, str):
            cls.__directory = value
            cls.__path = os.path.join(cls.__directory, cls.__filename)
            cls.__fh.path = cls.__path
        else:
            cls.Error.E102()

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para cambiar el nivel de registro del fichero .log---------------------------------------------------------
    @classmethod
    def set_file_level(cls, flv) -> None:
        """ Method to set a different level for the file .log of the register. The default level is "INFO". Only The level
register and higher will be printed in the .log file. Higher levels could make more difficult to track errors.
The possible levels are:

    "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
        """
        if flv in cls.LevelList:
            if flv == "DEBUG":
                flevel = logging.DEBUG
            elif flv == "WARNING":
                flevel = logging.WARNING
            elif flv == "ERROR":
                flevel = logging.ERROR
            elif flv == "CRITICAL":
                flevel = logging.CRITICAL
            else:
                flevel = logging.INFO

            try:
                if flv in ["WARNING", "ERROR", "CRITICAL"]:
                    cls.Warning.W101()
                cls.__flevel = flevel
                cls.__fh.setLevel(cls.__flevel)
                #cls._N2PLog__logger.addHandler(cls.__fh)
            except:
                cls.Error.E108()

        else:
            cls.Error.E107(cls.LevelList)

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para cambiar el nivel de registro por consola -------------------------------------------------------------
    @classmethod
    def set_console_level(cls, clv) -> None:
        """ Method to set a different level for console register. The default level is "WARNING". Only The level
register and higher will be printed in the console.
The possible levels are:

    "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
        """
        if clv in cls.LevelList:
            if clv == "DEBUG":
                clevel = logging.DEBUG
            elif clv == "WARNING":
                clevel = logging.WARNING
            elif clv == "ERROR":
                clevel = logging.ERROR
            elif clv == "CRITICAL":
                clevel = logging.CRITICAL
            else:
                clevel = logging.INFO

            try:
                cls.__clevel = clevel
                cls.__ch.setLevel(cls.__clevel)
                cls._N2PLog__logger.addHandler(cls.__ch)
            except:
                cls.Error.E109()

        else:
            cls.Error.E107(cls.LevelList)

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para obtener el nombre del archivo.log --------------------------------------------------------------------
    @classmethod
    def get_file_name(cls) -> str:
        """Method that returns the name of the file of the .log"""
        return cls.__filename

    # ------------------------------------------------------------------------------------------------------------------

    # Metodo para cambiar el nombre del archivo.log --------------------------------------------------------------------
    @classmethod
    def set_file_name(cls, value: str) -> None:
        """Method that sets the name of the file of the .log
        
        Args:
            value: str -> Name of the .log file

        """
        if isinstance(value, str):
            try:
                cls.__filename = value
                cls.__path = os.path.join(cls.__directory, cls.__filename)
                cls.__fh.path = cls.__path
            except:
                cls.Error.E105()

        else:
            cls.Error.E103()

    # ------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------

    # Metodo para cambiar desactivar la generación del archivo .log-----------------------------------------------------
    @classmethod
    def deactivate_log(cls) -> None:
        """Method that deactivates the .log"""
        cls.__fh.active = False

    # ------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------

    # Metodo para cambiar activar la generación del archivo .log-----------------------------------------------------
    @classmethod
    def activate_log(cls) -> None:
        """Method that activates the .log"""
        cls.__fh.active = True
    # ------------------------------------------------------------------------------------------------------------------

    @classmethod
    def _set_format1(cls) -> None:
        cls.__formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)-5s", "%H:%M:%S")
        cls.__fh.setFormatter(cls.__formatter)
        cls.__logger.addHandler(cls.__fh)

    @classmethod
    def _set_format2(cls, time) -> None:
        if len(time) < 8:
            time = "0" + time
        cls.__formatter = logging.Formatter(f"{time} %(levelname)-8s %(message)-5s")
        cls.__fh.setFormatter(cls.__formatter)
        cls.__logger.addHandler(cls.__fh)
# ----------------------------------------------------------------------------------------------------------------------