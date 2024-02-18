from setuptools import setup, find_packages

setup(
    name="Mensajes-coropeza",
    version="5.0",
    description="Un paquete pasa saludas y despedir",
    long_description=open('README.md').read(),
    long_description_content_type = "text/markdown",
    author="Carlos Andres Oropeza Velasquez",
    author_email="carlosoropezavelasquez@gmail.com",
    url="https://www.google.com",
    license_files = ['LICENSE'],
    packages= find_packages(), # Encontrar los paquetes automáticamente
    scripts=[],
    test_suite = 'tests',
    install_requires = [paquete.strip() for paquete in open("requirements.txt").readlines()],
    classifiers= [
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ]
)