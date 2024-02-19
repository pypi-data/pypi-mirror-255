from setuptools import setup, find_packages

PACKAGE_NAME = 'gaia_cmd_plotter'
PACKAGE_VERSION = '0.1.1'
AUTHOR_NAME = 'Yue Zhao'
AUTHOR_EMAIL = 'Yue.Zhao@soton.ac.uk'

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    python_requires='>=3.8',
    packages=find_packages(),
    install_requires=[
        'matplotlib>=3.3.0',
    ],
    package_data={
        'gaia_cmd_plotter': ['gaia_cmd.mplstyle', 'data/gaia_cmd_background.png'],
    },
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    description='A Python package that provides a matplotlib.pyplot.Axes object that displays a Gaia CMD background.',
    url='https://github.com/coryzh/gaia_cmd_plotter',
)
