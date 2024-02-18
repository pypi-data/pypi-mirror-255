from setuptools import setup, find_packages

setup(
    name='azfuncblobclient',
    version='0.0.5',
    author='Your Name',
    author_email='your.email@example.com',
    description='A short description of your package',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'azfuncbindingbase',
        'azure-storage-blob'
    ],
)