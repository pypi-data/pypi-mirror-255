import pathlib
from setuptools import find_packages, setup
import os
with open('README.md', 'r', encoding='utf-8-sig') as fh:
    LONG_DESCRIPTION = fh.read()

VERSION = '0.0.22' #Muy importante, hay que ir cambiand o la versión según vayamos mejorando la librería
PACKAGE_NAME = 'GMRev' #Debe coincidir con el nombre de la carpeta 
AUTHOR = 'Pablo Ascorbe Fernández'
AUTHOR_EMAIL = 'paascorb@unirioja.es'
URL = 'https://github.com/PrevenIA/GMRev'

LICENSE = 'GPL-3.0' #Tipo de licencia
DESCRIPTION = 'Librería para evaluar sistemas de generación mejorada por recuperación'
LONG_DESC_TYPE = "text/markdown"


#Paquetes necesarios para que funcione la librería. Se instalarán a la vez si no lo tuvieras ya instalado
INSTALL_REQUIRES = [
        'transformers',
        'torch',
        'evaluate'
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
    packages=["GMRev"]
)