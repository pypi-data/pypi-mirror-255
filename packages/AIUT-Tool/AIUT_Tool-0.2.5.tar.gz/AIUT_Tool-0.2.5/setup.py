
from setuptools import setup, find_packages

setup(
    name='AIUT_Tool',
    version='0.2.5',
    packages=find_packages(),
    install_requires=[
        'Pillow',
    ],
    entry_points={
        'console_scripts': [
            'AIUT_Tool=AIUT_Tool.AIUT:main',  
        ],
    },
    
    description='AIUT Tool - Automated Integration and Unit Testing',
   
    keywords='testing automation aiut',
  
   
)
