from setuptools import setup, find_packages

setup(
    name='strategytrees',
    version='0.1',
    packages=find_packages(),
    description='Evolving trading strategies trees using genetic algorithm',
    author='Oliver Hitchcock',
    author_email='',
    license='MIT',
    install_requires=[
        'pandas',
        'numpy'
    ],
    classifiers=[
        # Package classifiers (https://pypi.org/classifiers/)
          'Programming Language :: ML'
    ],
)
