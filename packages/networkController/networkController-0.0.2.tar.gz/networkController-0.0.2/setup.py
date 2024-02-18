from setuptools import setup, find_packages

VERSION = '0.0.2' 
DESCRIPTION = 'NAS-Network-Controller'
LONG_DESCRIPTION = 'Ejemplo de un network controller creado por NAS para curso de ILP'

# Configurando
setup(
        name="networkController", 
        version=VERSION,
        author="Emiliano Rosico",
        author_email="<emiliano19@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=["netmiko==2.4.2"], # añade cualquier paquete adicional que debe ser
        #instalado junto con tu paquete. Ej: 'caer'
        
        keywords=['python', 'networController', 'MAT', 'IQUALL'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)