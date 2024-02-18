from setuptools import setup, find_packages
from setuptools.command.install import install
import requests
import os

class CustomInstallCommand(install):
    """Customized setuptools install command."""
    def run(self):
        file_path = 'StockUniteLegaleHistorique_utf8.zip'
        
        # Vérifie si le fichier existe déjà
        if os.path.exists(file_path):
            # Si le fichier existe, le supprime
            os.remove(file_path)

        url = "https://files.data.gouv.fr/insee-sirene/StockUniteLegaleHistorique_utf8.zip"
        response = requests.get(url, stream=True)

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        install.run(self)

setup(
    name='ddldata',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    cmdclass={
        'install': CustomInstallCommand,
    },
)
