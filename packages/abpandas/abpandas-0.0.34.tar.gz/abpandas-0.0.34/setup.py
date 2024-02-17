from setuptools import setup, find_packages

VERSION = '0.0.34' 
DESCRIPTION = 'Agent Based Pandas tool (ABPandas)'
LONG_DESCRIPTION = 'An Agent Based Modelling (ABM) package that can generate grid spatial shape files or work with predefined shape files.\nThe package focuses on simplicity by assigning Agents to spatial Polygons instead of assigning x and y locations for each agents.\nThis makes it useful in situations where granual movement of agents in space is not necessary (e.g. residentail location models).\nFor documentation visit https://github.com/YahyaGamal/ABPandas_Documentation'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="abpandas", 
        version=VERSION,
        author="Yahya Gamal",
        author_email="<abpandas.yg@outlook.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['geopandas', 'pandas', 'fiona', 'pyshp', 'shapely'], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'Agent Based Model', 'Spatial', 'Pandas'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Science/Research",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)