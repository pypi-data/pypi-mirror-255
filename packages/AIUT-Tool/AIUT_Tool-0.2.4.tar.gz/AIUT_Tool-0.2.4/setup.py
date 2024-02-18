
from setuptools import setup, find_packages

setup(
    name='AIUT_Tool',
    version='0.2.4',
    packages=find_packages(),
    install_requires=[
        'Pillow',
    ],
    entry_points={
        'console_scripts': [
            'AIUT_Tool=AIUT_Tool.AIUT:__main__',  
        ],
    },
    
    description='AIUT Tool - Automated Integration and Unit Testing',
   
    keywords='testing automation aiut',
  
   
)
