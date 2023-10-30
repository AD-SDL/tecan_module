import os
from setuptools import setup, find_packages
from glob import glob

package_name = 'tecan_module_client'

setup(
    name='tecan_module_client',
    version='0.0.1',
    packages=find_packages(),
    data_files=[],
    install_requires=[],
    zip_safe=True,
    python_requires=">=3.8",
    maintainer='',
    maintainer_email='dozgulbas@anl.gov',
    description='',
    url='', 
    license='MIT License',
    entry_points={ 
        'console_scripts': [
            'tecan_client = tecan_module_client.tecan_client:main',
        ]
    },
)
