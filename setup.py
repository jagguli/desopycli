from distutils.core import setup


import os

lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = lib_folder + "/requirements.txt"
install_requires = (
    []
)  # Here we'll get: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()
setup(
    name="DeSoPyCLI",
    version="1.0",
    description="Python Deso Command Line Interface",
    author="Steven Joseph",
    author_email="steve@stevenjoseph.in",
    url="https://bitclout.com/desopycli",
    scripts=["bin/deso"],
    packages=["desopycli"],
    provides=["desopycli"],
    install_requires=install_requires,
)
