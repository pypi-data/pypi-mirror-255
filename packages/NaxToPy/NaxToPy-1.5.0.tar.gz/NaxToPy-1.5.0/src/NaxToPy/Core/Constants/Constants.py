"""Constants of the NaxToPy package"""

# NaxToPy Version
VERSION = "1.5.0"

# Supported for Naxto:
NAXTO_VERSION = '2024R0'
NAXTO_STEP = "5"

# Assembly version of VizzerClasses.dll
VIZZER_ASSEMBLY = "4.0.0.5"

# PYTHON EXTERNO ----------------------------------------------------------------------------------
# Versiones de Python soportadas:
SUP_PY_VER = (9, 10, 11, 12)

# Librerias Externas de Python
EXTERNAL_LIBS_PYTHON = ['cffi',
                        'clr_loader',
                        'pycparser',
                        'pythonnet',
                        'numpy',
                        'setuptools']
# -------------------------------------------------------------------------------------------------

# Binary extensions supported by NaxToPy ----------------------------------------------------------
BINARY_EXTENSIONS = ["op2", "xdb", "h5", "h3d", "odb", "rst"]

# NAXTO -------------------------------------------------------------------------------------------
# Ruta a las librerias de NaxTo
DEVELOPER_VIZZER = r'C:\GIT_REPOSITORIES\NAXTO\NAXTOVIEW\v.3.0\NAX2VIZZER\VizzerClasses\bin\x64\Debug'

# DLLs de NaxTo
VIZZER_CLASSES_DLL = 'VizzerClasses.dll'
# -------------------------------------------------------------------------------------------------

PEDIGREE_FACTOR = 1000  # Para pasar de id pedigree a id solver: id_solver = id_pedigree // _PEDIGREE_FACTOR_
                        # Para obtener el id part: id_pedigree % _PEDIGREE_FACTOR_


