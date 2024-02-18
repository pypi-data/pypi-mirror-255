from setuptools import setup, find_packages
import pkg_resources
import codecs
import os
#python setup.py sdist bdist_wheel

here = os.path.abspath(os.path.dirname(__file__))

with open('LICENSE.txt') as f:
    license = f.read()
with open('README.md') as f:
    readme = f.read()
VERSION = '0.0.5'
DESCRIPTION = 'growingnn is a cutting-edge Python package that introduces a dynamic neural network architecture learning algorithm. This innovative approach allows the neural network to adapt its structure during training, optimizing both weights and architecture. Leveraging a Stochastic Gradient Descent-based optimizer and guided Monte Carlo tree search, the package provides a powerful tool for enhancing model performance.'


# Setting up
setup(
    name="growingnn",
    version=VERSION,
    author="Szymon Świderski",
    author_email="<pjuralszymqn@gmail.com>",
    description=DESCRIPTION,
    license=license,
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires = ["numpy", "matplotlib", "opencv-python", "scipy", "imgaug", "scikit-learn", "pyvis"],
    keywords=['python', 'neural network', 'growing neural network', 'growing'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows"])
