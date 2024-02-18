FieldOps Py
===========

This is a python library and cli for working with `fieldops <https://fieldops.readthedocs.io/en/latest/>`_. It can be used for creating custom provisioning scripts, or setting up deployment for a CI/CD pipeline 


Installation
------------

.. code:: bash 

    pip3 install fieldops


Using the CLI 
-------------

The CLI can be used to poll the server for information, download packages, and upload new versions of packages. For the most part it just wraps the rest calls and handles authentication, so the api paths are the same as the rest api.

Show the packages 

.. code:: bash 

    fieldops -u <username> -p <password> -s <server> get packages 

.. note:: You can replace 'get' with 'list' to show a simple list instead of the full detailed json response


Show the details of the latest version of a package: 

.. code:: bash 

    fieldops -u <username> -p <password> -s <server> get packages/pa/versions/latest 

Download the latest version of a package:

.. code:: bash 

    fieldops -u <username> -p <password> -s <server> download packages/pa/versions/latest

Upload a new version of a package:

.. code:: bash 

    fieldops -u <username> -p <password> -s <server> upload packages/pa-firmware -f <path to package file> -v <version number> -r <release notes>

.. note:: you can use the -t or --track flag to specify a track to upload to. If you don't specify a track, the package will be uploaded to 'release' by default.



Using as a library
------------------

The library can be used to create custom provisioning scripts, or to integrate with a CI/CD pipeline.
