from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()


setup(
    name='pycmdmovie',
    version='1.1.3',
    packages=find_packages(),
    install_requires=[
        'pillow',
        'opencv-python',
        'colorama'
    ],
    long_description=description,
    long_description_content_type='text/markdown'
)