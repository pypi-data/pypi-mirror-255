ironik
======

|PyPI| |Python Version| |Read the Docs| |pre-commit| |Black|

.. |PyPI| image:: https://img.shields.io/pypi/v/ironik.svg
   :target: https://pypi.org/project/ironik/
   :alt: PyPI
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/ironik
   :target: https://pypi.org/project/ironik
   :alt: Python Version
.. |Read the Docs| image:: https://img.shields.io/readthedocs/ironik/latest.svg?label=Read%20the%20Docs
   :target: https://ironik.readthedocs.io/
   :alt: Read the documentation at https://ironik.readthedocs.io/
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Black

.. Warning:: THIS PROJECT HAS BEEN MOVED TO https://gitlab-ce.gwdg.de/jdecker/ironik

.. Warning:: This tool is still in early development and only the core features are available.

Features
--------

- Utilize OpenStack and Rancher APIs to automatically deploy Kubernetes cluster
- Customize the configuration using templates
- Install new Kubernetes versions including deploying the external cloud controller manager for OpenStack

Installation
------------

You can install *ironik* via pip_ from PyPI_:

.. code:: console

   $ pip install ironik

Alternatively, *ironik* can also be used as a container to avoid installing it:

.. code:: console

   $ docker run --rm -ti -v $(pwd):/app/tmp docker.gitlab-ce.gwdg.de/jdecker/ironik/cli:latest ironik --help

This can be abbreviated using an alias:

.. code:: console

   $ alias dironik='docker run --rm -ti -v $(pwd):/app/tmp docker.gitlab-ce.gwdg.de/jdecker/ironik/cli:latest ironik'
   $ dironik --help

Usage
-----

Please see the `Usage Instructions <https://ironik.readthedocs.io/en/latest/cli_usage.html>`_ for details.

Kubernetes can also be deployed manually on OpenStack and Rancher.
See the `Manual Deployment Instructions <https://ironik.readthedocs.io/en/latest/manual_kubernetes_deployment.html>`_ for a full guide.

TODOs
-----

- Update Code documentation to use Google code doc style
- Improve print messages during execution
- Implement a template validator
- Implement cluster validation
- Set up test suite
- Implement automatic config fetching
- Add functionality for undoing deployments and other helpful commands

Contributing
------------

Contributions are very welcome. To learn more, see the `Contributor Guide`_.

Setup Development Environment
-----------------------------
We tested the developing environment with Ubuntu 22.04.

1. Fork project
2. Clone forked project on your working machine
3. Install dependencies (needed to build wheel of netifaces in Step 4.)

.. code:: console

    sudo apt-get install build-essential libssl-dev libffi-dev python3-dev

4. Install python packages

.. code:: console

    poetry install


Credits
-------

This package was created with cookietemple_ using Cookiecutter_ based on Hypermodern_Python_Cookiecutter_.

.. _cookietemple: https://cookietemple.com
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _MIT: http://opensource.org/licenses/MIT
.. _PyPI: https://pypi.org/
.. _Hypermodern_Python_Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python
.. _pip: https://pip.pypa.io/
.. _Contributor Guide: CONTRIBUTING.rst
.. _Usage: https://ironik.readthedocs.io/en/latest/usage.html
