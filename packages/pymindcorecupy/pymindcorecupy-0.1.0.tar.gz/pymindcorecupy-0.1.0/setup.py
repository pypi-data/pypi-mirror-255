from setuptools import setup, find_packages

setup(
    name='pymindcorecupy',
    version='0.1.0',
    packages=find_packages(),
    description='A Python library for AI, easy to use, freely available for any use',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Dogz-R-Godz/Pymind-Cupy',
    author='Dogz R Godz',
    author_email='doggocam01@gmail.com',
    license='CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
    install_requires=[
        'numpy',
        'Pillow',
	    'idx2numpy',
        'cupy'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
    ],
)