from setuptools import setup, find_packages


setup(
    name='pycmdmovie',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'pillow',
        'opencv-python',
        'colorama'
    ]
)