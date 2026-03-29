API Reference
=============

This section contains automatically generated documentation for all HireSense modules.

app package
-----------

The main application package containing Flask blueprints, models, and core functionality.

.. automodule:: app
   :members:
   :undoc-members:
   :show-inheritance:

app.models module
-----------------

Database models for users, projects, skills, and related entities.

.. automodule:: app.models
   :members:
   :undoc-members:
   :show-inheritance:

app.auth module
---------------

Authentication routes for login, registration, and logout.

.. automodule:: app.auth
   :members:
   :undoc-members:
   :show-inheritance:

app.views module
----------------

Main routing and dashboard redirects.

.. automodule:: app.views
   :members:
   :undoc-members:
   :show-inheritance:

app.admin module
----------------

Admin blueprint for user management and system administration.

.. automodule:: app.admin
   :members:
   :undoc-members:
   :show-inheritance:

app.employee module
-------------------

Employee blueprint for profile management, skills, and learning paths.

.. automodule:: app.employee
   :members:
   :undoc-members:
   :show-inheritance:

app.manager module
------------------

Manager blueprint for project management and team coordination.

.. automodule:: app.manager
   :members:
   :undoc-members:
   :show-inheritance:

app.services package
====================

Business logic layer providing services for skill matching, resume processing,
project management, and learning path generation.

.. automodule:: app.services
   :members:
   :undoc-members:
   :show-inheritance:

app.services.skill_service module
---------------------------------

Skill matching and gap analysis service.

.. automodule:: app.services.skill_service
   :members:
   :undoc-members:
   :show-inheritance:

app.services.resume_service module
----------------------------------

Resume parsing and skill extraction with NLP.

.. automodule:: app.services.resume_service
   :members:
   :undoc-members:
   :show-inheritance:

app.services.project_service module
-----------------------------------

Project management and employee matching service.

.. automodule:: app.services.project_service
   :members:
   :undoc-members:
   :show-inheritance:

app.services.learning_path_service module
-----------------------------------------

Career path generation and learning recommendations.

.. automodule:: app.services.learning_path_service
   :members:
   :undoc-members:
   :show-inheritance:

app.services.document_parser module
-----------------------------------

Document parsing for PDF, DOCX, and text files.

.. automodule:: app.services.document_parser
   :members:
   :undoc-members:
   :show-inheritance:

app.services.nlp_manager module
-------------------------------

NLP model management for skill extraction.

.. automodule:: app.services.nlp_manager
   :members:
   :undoc-members:
   :show-inheritance:

utility package
===============

CLI utilities for database seeding and management.

.. automodule:: utility
   :members:
   :undoc-members:
   :show-inheritance:

utility.seed_users module
-------------------------

User seeding utilities for development and testing.

.. automodule:: utility.seed_users
   :members:
   :undoc-members:
   :show-inheritance:

utility.seed_projects module
----------------------------

Project seeding utilities.

.. automodule:: utility.seed_projects
   :members:
   :undoc-members:
   :show-inheritance:

utility.clear_db module
-----------------------

Database clearing utility.

.. automodule:: utility.clear_db
   :members:
   :undoc-members:
   :show-inheritance:

testing package
===============

Test fixtures and configuration for the HireSense test suite.

testing.conftest module
-----------------------

Shared pytest fixtures for database, clients, and authenticated sessions.

.. automodule:: testing.conftest
   :members:
   :undoc-members:
   :show-inheritance: