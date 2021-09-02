Clinical guideline recommendation compliance monitor
====================================================

.. image:: docs/img/logo_ceosys.jpg
  :height: 100
  :alt: CEOsys

.. image:: docs/img/logo_num.jpg
  :height: 100
  :alt: Netzwerk Universitätsmedizin


Introduction
------------
Development of a software-based automated evaluation of the adherence to clinical guidelines in the context of the
`CEO-sys - COVID-19 Evidenz-Ökosystems zur Verbesserung von Wissensmanagement und -translation <https://covid-evidenz.de/>`_.

Requirements
------------
Docker and docker-compose needs to be installed, e.g. under linux via:

.. code-block:: shell

   sudo apt install docker docker-compose


Quickstart
----------

1. Clone repository

   .. code-block:: shell

      git clone https://github.com/glichtner/ceosys.git


2. Generate secrets, user database and patient sample data

   .. code-block:: shell

      ./generate.py


3. Build docker containers

   .. code-block:: shell

      docker-compose build --parallel


4. Run containers

   .. code-block:: shell

      docker-compose up


5. Visit the dashboard at http://localhost:5000/