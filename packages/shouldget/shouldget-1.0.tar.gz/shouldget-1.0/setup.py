import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='shouldget',  
     version='1.0',
     scripts=['should'] ,
     author="Mathieu Giraud; Mikaël Salson",
     author_email="support@vidjil.org",
     description="A testing pipeline using should-get format",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://gitlab.inria.fr/vidjil/should",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
         "Operating System :: OS Independent",
     ],
     python_requires = ">=3.4"
 )