from setuptools import setup, find_packages




VERSION = '0.0.1'
DESCRIPTION = 'A package that allows to build and handle simple NN model for MNIST-numbers dataset.'
LONG_DESCRIPTION = 'A package that allows to build and handle simple NN model for MNIST-numbers dataset. It also allows to use a piple to output predictions.'



setup (
    name='moduls_ai',
    version=VERSION,
    author="Maks Kucher",
    author_email="maxim.kucher2005@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    license='MIT',
    packages=find_packages(),

    install_requires=[
        'numpy',
        'matplotlib',
        'tensorflow',
        'keras'
    ],
    
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)