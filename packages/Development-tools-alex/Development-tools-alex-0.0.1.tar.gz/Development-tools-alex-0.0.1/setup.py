from setuptools import setup, find_packages

# Nom du package PyPI ('pip install development-tools')
NAME = "Development-tools-alex"

# Version du package PyPI
VERSION = "0.0.1" # la version doit être supérieure à la précédente sinon la publication sera refusée

# Facultatif / Adaptable à souhait
AUTHOR = "HKH"
AUTHOR_EMAIL = ""
URL = ""
DESCRIPTION = "A package to built-in widgets (Input data, output data, subworkflow widgets). Also goto widget and others"
LICENSE = ""

# 'orange3 add-on' permet de rendre l'addon téléchargeable via l'interface addons d'Orange 
KEYWORDS = ("orange3 add-on",)

# Tous les packages python existants dans le projet
PACKAGES = find_packages()

# Fichiers additionnels aux fichiers .py (comme les icons ou des .ows)
PACKAGE_DATA = {
	"orangecontrib.development_tools.widgets": ["icons/*", "widget_designer/*", "kernel_function/*"], # contenu du dossier 'icons' situé dans 'orangecontrib/development_tools/widgets'
}
# /!\ les noms de fichier 'orangecontrib.development_tools.widgets' doivent correspondre à l'arborescence

# Dépendances
INSTALL_REQUIRES = []

# Spécifie le dossier contenant les widgets et le nom de section qu'aura l'addon sur Orange
ENTRY_POINTS = {
	"orange.widgets": (
		"Development-tools = orangecontrib.development_tools.widgets", # 'Development-tools' sera le nom de la section Orange contenant les widgets
	)
}
# /!\ les noms de fichier 'orangecontrib.development_tools.widgets' doivent correspondre à l'arborescence

NAMESPACE_PACKAGES = ["orangecontrib"]

setup(name=NAME,
	  version=VERSION,
	  author=AUTHOR,
	  author_email=AUTHOR_EMAIL,
	  url=URL,
	  description=DESCRIPTION,
	  license=LICENSE,
	  keywords=KEYWORDS,
	  packages=PACKAGES,
	  package_data=PACKAGE_DATA,
	  install_requires=INSTALL_REQUIRES,
	  entry_points=ENTRY_POINTS,
	  namespace_packages=NAMESPACE_PACKAGES,
)







