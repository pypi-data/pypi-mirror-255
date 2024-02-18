from setuptools import setup, find_packages
from src import g2fl

requirements = [
    'torch==2.2.0',
    'torchvision==0.17.0',
    'matplotlib==3.7.4',
    'matplotlib-inline==0.1.6'
]

setup(
    name='g2fl',
    version=g2fl.__version__,
    python_requires='>=3.8',
    author='chenlh',
    author_email='gavnlhchen@gmail.com',
    url='https://github.com/chenlehua/network',
    description="Gavin's Deep Learning functions",
    license='MIT',
    packages=find_packages(),
    zip_safe=True,
    install_requires=requirements,
)
