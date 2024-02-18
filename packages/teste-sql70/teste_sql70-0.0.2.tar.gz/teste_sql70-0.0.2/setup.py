from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'Mi primer paquete de Python'
LONG_DESCRIPTION = 'Mi primer paquete de Python con una descripción ligeramente más larga'

# Configurando
setup(
    # el nombre debe coincidir con el nombre de la carpeta
    name="teste_sql70",
    version=VERSION,
    author="Sql 70",
    author_email="<sql70@outlook.es>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],  # añade cualquier paquete adicional que debe ser
    # instalado junto con tu paquete.

    keywords=['python', 'prueba', 'paquete', 'teste'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)