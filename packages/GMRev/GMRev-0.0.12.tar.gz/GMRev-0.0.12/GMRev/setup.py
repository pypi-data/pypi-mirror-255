import pathlib
from setuptools import find_packages, setup

with open('GMRev/README.md', 'r', encoding='utf-8-sig') as fh:
    LONG_DESCRIPTION = fh.read()

VERSION = '0.0.12' #Muy importante, hay que ir cambiando la versión según vayamos mejorando la librería
PACKAGE_NAME = 'GMRev' #Debe coincidir con el nombre de la carpeta 
AUTHOR = 'Pablo Ascorbe Fernández'
AUTHOR_EMAIL = 'paascorb@unirioja.es'
URL = 'https://github.com/PrevenIA/GMRev'

LICENSE = 'GPL-3.0' #Tipo de licencia
DESCRIPTION = 'Librería para evaluar sistemas de generación mejorada por recuperación'
LONG_DESC_TYPE = "text/markdown"


#Paquetes necesarios para que funcione la libreía. Se instalarán a la vez si no lo tuvieras ya instalado
INSTALL_REQUIRES = [
        'numpy'
      ]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    license=LICENSE,
    packages=find_packages(where='GMRev'),
    include_package_data=True
)