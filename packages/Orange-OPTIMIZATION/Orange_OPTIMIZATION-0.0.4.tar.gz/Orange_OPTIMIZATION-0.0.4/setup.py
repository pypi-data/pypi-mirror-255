from setuptools import setup, find_packages

# Nom du package PyPI ('pip install HKH-Bot')
NAME = "Orange_OPTIMIZATION"

# Version du package PyPI
VERSION = "0.0.4" # la version doit être supérieure à la précédente sinon la publication sera refusée

# Facultatif / Adaptable à souhait
AUTHOR = ""
AUTHOR_EMAIL = ""
URL = ""
DESCRIPTION = "Let's Optimize !"
LICENSE = ""

# 'orange3 add-on' permet de rendre l'addon téléchargeable via l'interface addons d'Orange 
KEYWORDS = ("orange3 add-on",)

# Tous les packages python existants dans le projet
PACKAGES = find_packages()

# Fichiers additionnels aux fichiers .py (comme les icons ou des .ows)
PACKAGE_DATA = {
	"orangecontrib.optimization.widgets": ["icons/*","widget_designer/*"], # contenu du dossier 'icons' situé dans 'orangecontrib/optimization/widgets'
}
# /!\ les noms de fichier 'orangecontrib.OPTIMIZATION.widgets' doivent correspondre à l'arborescence

# Dépendances
INSTALL_REQUIRES = []

# Spécifie le dossier contenant les widgets et le nom de section qu'aura l'addon sur Orange
ENTRY_POINTS = {
	"orange.widgets": (
		"OPTIMIZATION = orangecontrib.optimization.widgets", # 'OPTIMIZATION' sera le nom de la section Orange contenant les widgets
	)
}
# /!\ les noms de fichier 'orangecontrib.OPTIMIZATION.widgets' doivent correspondre à l'arborescence

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







