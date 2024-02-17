import os
import io
import setuptools

name = "superset-gcp-cloud"
description = 'A Superset gcp cloud plugin'

package_root = os.path.abspath(os.path.dirname(__file__))

readme_filename = os.path.join(package_root, "README.rst")
with io.open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()

packages = [
    package
    for package in setuptools.find_namespace_packages()
    if package.startswith("superset")
]

setuptools.setup(
    name=name,
    version='1.0.0',
    author='Avinash Katariya',
    author_email='akatariya@quotient.com',
    description= description,
    long_description=readme,
    packages=packages,
    license="Apache 2.0",
    classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    ],
    python_requires='>=3.6'
)