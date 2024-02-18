import setuptools




with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='fieldops',
     version="0.0.5",
     author="Jason Berger",
     author_email="berge472@gmail.com",
     description="CLI and library for interacting with FieldOps api",
     long_description=long_description,
     long_description_content_type="text/x-rst",
     scripts=['fieldops/fieldops'],
     url="https://fieldops.readthedocs.io/en/latest/",
     packages=setuptools.find_packages(),
     install_requires=[
        'update_notipy'
     ],
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
