from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'Automatically mask sentences from a given input where certain words vary, and fil-mask from given candidates'

# Setting up
setup(
    name="autoFillMaskWithCandy",
    version=VERSION,
    author="Elatot",
    author_email="<elashiishii@gmail.com>",
    license="MIT",
    url="https://github.com/Elashico/autoFillMaskWithCandy.git",
    description=DESCRIPTION,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown', 
    packages=find_packages(),
    install_requires=['torch','transformers'],
    keywords=['python', 'hugging-face', 'fill-mask', 'natural language processing','pretrained langugae model'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)