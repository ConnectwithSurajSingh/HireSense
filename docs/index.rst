HireSense Documentation
=======================

**AI-Powered Resume Intelligence & Career Path Recommendation System**

HireSense is a semantic AI-driven resume analysis platform that uses transformer-based
language models to understand resumes, extract skills, and generate personalized
learning paths.

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   content/DOCUMENTATION
   content/UTILITIES

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide

   developer/TESTING
   developer/DEPLOYMENT
   developer/MIGRATIONS
   developer/THEMING
   developer/CI_CD
   developer/GITHUB_PAGES

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   modules

Quick Start
-----------

**Installation**

.. code-block:: bash

   git clone https://github.com/paarthsiloiya/HireSense.git
   cd HireSense
   docker compose up --build

**Access Points**

* Port 5010: http://localhost:5010
* Port 5011: http://localhost:5011
* Port 5012: http://localhost:5012

**Default Admin**: ``admin`` / ``Admin@1234``

Features
--------

* **Semantic Resume Parsing** - AI-powered skill extraction
* **Role-Based Access** - Admin, Manager, Employee roles
* **Project Matching** - Match employees to projects by skills
* **Learning Paths** - Personalized career development
* **Skill Gap Analysis** - Identify and address skill gaps

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`