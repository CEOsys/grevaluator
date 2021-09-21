Guideline Recommendation Evaluator (GREvaluator)
####################################################
.. start-badges

.. image:: https://readthedocs.org/projects/ceosys/badge/?version=latest
    :target: https://ceosys.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. end-badges

The guideline recommendation evaluator (GREvaluator) is a clinical decision support system based on automated integration of clinical guideline recommendations with real-time clinical data.



Introduction
============
Clinical guideline synthesize the current state of medical knowledge into treatment recommendations and provide thereby a source of decision support for health care professionals. However, the implementation of these guidelines in clinical practice is often hindered by the lack of awareness of individual guideline recommendations existence or applicability for specific patient conditions.

We have therefore designed a system for the automated integration of guideline recommendations with real-time clinical data to provide clinical decision support during individual patient treatments as well as for monitoring of overall guideline implementations.


The is being developed in the context of the `CEOsys: Living evidence synthesis as the basis for decisions in the COVID-19 pandemic <https://covid-evidenz.de/>`_ project.

|logo_ceosys|  |logo_num|

.. |logo_ceosys| image:: docs/img/logo_ceosys.jpg
  :height: 100
  :alt: CEOsys

.. |logo_num| image:: docs/img/logo_num.jpg
  :height: 100
  :alt: Netzwerk Universitätsmedizin






Quickstart
============

Prerequisites
-------------

Docker and docker-compose needs to be installed, e.g. under linux via:

.. code-block:: shell

    sudo apt install docker docker-compose


Run
---

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




Documentation
=============
The `API Reference <http://ceosys.readthedocs.io>`_ provides API-level documentation.
