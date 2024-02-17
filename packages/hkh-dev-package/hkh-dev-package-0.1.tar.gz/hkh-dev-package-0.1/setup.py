from setuptools import setup, find_packages

# Nom du package PyPI ('pip install HKH-Bot')
NAME = "hkh-dev-package"

# Version du package PyPI
VERSION = "0.1" # la version doit être supérieure à la précédente sinon la publication sera refusée

# Facultatif / Adaptable à souhait
AUTHOR = "HKH"
AUTHOR_EMAIL = ""
URL = ""
DESCRIPTION = "A package to use our built-in widgets"
LICENSE = ""

# 'orange3 add-on' permet de rendre l'addon téléchargeable via l'interface addons d'Orange 
KEYWORDS = ("orange3 add-on",)

# Tous les packages python existants dans le projet
PACKAGES = find_packages()

# Fichiers additionnels aux fichiers .py (comme les icons ou des .ows)
PACKAGE_DATA = {
	"orangecontrib.dev.widgets": ["icons/*", "kernel_function/*"], # contenu du dossier 'icons' situé dans 'orangecontrib/dev/widgets'
}
# /!\ les noms de fichier 'orangecontrib.dev.widgets' doivent correspondre à l'arborescence

# Dépendances
INSTALL_REQUIRES = ["faiss-cpu==1.7.4", "langchain==0.0.244", "sentence-transformers==2.2.2", "gpt4all==2.0.2", "PyMuPDF==1.22.5"]

# Spécifie le dossier contenant les widgets et le nom de section qu'aura l'addon sur Orange
ENTRY_POINTS = {
	"orange.widgets": (
		"Dev-Package = orangecontrib.dev.widgets", # 'Dev-package' sera le nom de la section Orange contenant les widgets
	)
}
# /!\ les noms de fichier 'orangecontrib.dev.widgets' doivent correspondre à l'arborescence

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







