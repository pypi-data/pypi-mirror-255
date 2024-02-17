from setuptools import setup, find_packages

f = open("./version.txt", 'r')
versions = f.read()
f.close()

# Setup the package
setup(
    name="gmpykit",
    version=versions,
    author='Gaétan Muck',
    author_email='gaetan.muck@gmail.com',
    description='Package with various python tools',
    long_description='Package with various python tools',
    packages=find_packages(),
    install_requires=[
        "pandas==2.0.3", 
        "numpy==1.26.2",
        "pyyaml==6.0.1", 
        "jdcal==1.4.1", 
        "lxml==4.9.3",
        "plotly==5.18.0"
    ],
    keywords=['python', 'toolkit', 'utilities', 'utils', 'tools']
)
