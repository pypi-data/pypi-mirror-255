import winreg
import sys
import os
import clr
from NaxToPy.Core.Constants.Constants import *
from NaxToPy.Core.Errors.N2PLog import N2PLog
from System.Diagnostics import FileVersionInfo


# Comprueba que la Version que el Usuario esta usando de Python esta dentro de las soportadas
def py_ver_comp() -> None:
    """ Funcion que devuelve True si la version de python esta soportada
    """
    py_version = sys.version.split(".")

    if int(py_version[0]) == 3 and int(py_version[1]) in SUP_PY_VER:
        return
    else:
        N2PLog.Critical.C102(py_version)
        # sys.exit(f"C102: THE CURRENT PYTHON VERSION IS NOT SUPPORTED.")


# Funcion que devuelve la ruta donde se encuentran las librerias de NaxTo----------------------
def vizzer_libs() -> list[str, ...]:
    """Funcion que devuelve las rutas donde se encuentran las librerias de VizzerClasses. Si hay varias versiones
    puede haber varias rutas.
    ----------
    Returns: 
        vizzer_libs: str
            Ruta a las librerias de NaxTo
    ----------
    """
    vizzer_libs = []

    # Miro en LOCAL MACHINE, donde está instalado el NAXTOVIEW. Ahí se busca la libreria de VizzerClasses.
    key_id = winreg.HKEY_LOCAL_MACHINE

    try:
        sub_key_id = winreg.OpenKeyEx(key_id, os.path.join("SOFTWARE", "IDAERO"))
        naxto_ver = winreg.QueryInfoKey(sub_key_id)
        naxto_ver2 = list()

        for i in range(naxto_ver[0]):

            # De todas las claves de Registro en la carpeta de IDAERO busca solo las de NAXTOVIEW
            if winreg.EnumKey(sub_key_id, i).split("_")[0] == "NAXTOVIEW":
                naxto_ver2.append(winreg.EnumKey(sub_key_id, i))

        # Se busca en la version mas nueva. Si no en la anterior.
        naxto_ver2.sort()

        if len(naxto_ver2) == 0:
            N2PLog.Critical.C107()
            # sys.exit()

        for i in range(len(naxto_ver2)):
            vizzer_key = winreg.OpenKeyEx(key_id, os.path.join("SOFTWARE", "IDAERO", naxto_ver2[i]))
            vizzer_libs.append(winreg.QueryValueEx(vizzer_key, "Path")[0])

        vizzer_libs2 = [os.path.join(lib, "bin") for lib in vizzer_libs]

    except:
        N2PLog.Critical.C107()

    return vizzer_libs2


# ---------------------------------------------------------------------------------------------
def open_idaero_key() -> winreg.HKEYType:
    """Returns the Windows Register Key for the IDAERO software (NAXTOVIEW)

    Returns:
        naxto_key: winreg.HKEYType

    """
    reg_path = r"SOFTWARE\IDAERO"

    # Se crea o se abre la clave CURRENT_USER\SOFTWARE\IDAERO
    idaero_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)

    # Se crea o se abre la clave CURRENT_USER\SOFTWARE\IDAERO\NAXTOVIEW_202XRY donde X e Y serán los que corresponda
    naxto_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path + r"\NAXTOVIEW_" + NAXTO_VERSION)

    # Se devuelve la clave de NAXTOVIEW que es donde se modifica el valor Path
    return naxto_key


# ---------------------------------------------------------------------------------------------
def change_register() -> None:
    """Function that changes or create a path variable in the register.

    By default, NaxToPy uses the NaxTo that is installed. If NaxToPy from .exe or from developer is used, the register
    don't have the path variable, it must be created at Software/Idaero/NaxToView

    Returns:
        None.
    """
    try:
        naxto_key = open_idaero_key()

        # La ruta que vamos a meter es la de la carpeta en la que esta una carpeta llamada bin. En ella
        # estan las bibliotecas de NaxTo. Debe funcionar esta carpeta para los ejecutables y para las
        # versiones de desarrollo. En las salidas normales este path no debe estar.
        naxtopy_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

        winreg.SetValueEx(naxto_key, "Path", 0, winreg.REG_SZ, naxtopy_path + "\\")

        N2PLog.Warning.W102(naxtopy_path)

    except Exception as e:

        N2PLog.Error.E112(e)
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
def destroy_register() -> None:
    """Function that destroy the register path for developers or .exe files of NaxToPy.

    Returns:
        None
    """
    naxto_key = open_idaero_key()
    try:
        winreg.QueryValueEx(naxto_key, "Path")
        winreg.DeleteValue(naxto_key, "Path")
        N2PLog.Warning.W103()
    except FileNotFoundError:
        pass
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
def compatible_vizzer(vizzer_libs: list) -> str:
    """Returns the path of the VizzerClasses this NaxToPy version is compatible with"""

    for lib in vizzer_libs:
        lib_path = lib + "\\" + VIZZER_CLASSES_DLL
        versionInfo = FileVersionInfo.GetVersionInfo(lib_path)
        assemblyVersion = versionInfo.FileVersion

        if assemblyVersion == VIZZER_ASSEMBLY:
            return lib_path

    N2PLog.Critical.C109(VERSION, VIZZER_ASSEMBLY)
    # sys.exit()
# ---------------------------------------------------------------------------------------------


# Inicializador para encontrar la libreria de VizzerClasses
def __reference_finder():
    # La ruta cambia si se tiene el repositorio de NaxToView
    developer_vizzer = DEVELOPER_VIZZER + "\\" + VIZZER_CLASSES_DLL

    # Si se crea un .exe queremos que encuentre unas nuevas librerias distribuibles, que estarán en la carpeta temporal que se
    # crea cuando se ejecuta el .exe. Tampoco se ejecutan los modulos del reference finder
    if getattr(sys, 'frozen', False):
        change_register()
        exe_dir = sys._MEIPASS
        vizzer_path = exe_dir + "\\libraries\\VizzerClasses.dll"
        N2PLog.Info.I107()

    elif os.path.isfile(developer_vizzer):
        if VERSION.split(".")[-1][0:3] == "dev":
            change_register()
        vizzer_path = developer_vizzer
        N2PLog.Info.I108()

    else:
        destroy_register()
        # Compruebo que la version de python es compatible
        py_ver_comp()
        # Busco todas las vizzerclasses
        list_libs = vizzer_libs()
        # Devuelvo el path de la vizzerclasses que es compatible con NaxToPy
        vizzer_path = compatible_vizzer(list_libs)

    # Llamada a las librerias
    try:
        clr.AddReference(vizzer_path)
        N2PLog.Info.I109()
        N2PLog.Debug.D101(vizzer_path)
    except:
        N2PLog.Critical.C103()
        # sys.exit("C103: THE LIBRARY 'VizzerClasses.dll' COULDN'T BE LOADED CORRECTLY")
# ---------------------------------------------------------------------------------------------
