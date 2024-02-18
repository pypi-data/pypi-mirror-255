from setuptools import setup, find_packages

setup(
    name='ver13',
    version='0.4',
    packages=find_packages(),
    install_requires=[
        # Add any dependencies your project needs
        'Pillow',  # Example dependency
         # Example dependency
    ],
    entry_points={
        'console_scripts': [
            'ver13=ver13.AIUT:main',  
        ],
    },
    
)
