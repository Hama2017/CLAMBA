from setuptools import setup, find_packages

setup(
    name="clamba",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pdfplumber",
        "requests"
    ],
    include_package_data=True,
    description="CLAMBA: Générateur de Smart Legal Contract Automaton (.slca) à partir de PDF.",
    author="Hamadou Ba",
)
