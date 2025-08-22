Welcome to PairCoder Documentation
===================================

.. toctree::
   :maxdepth: 2
   :caption: Getting Started
   :hidden:

   quickstart
   installation
   philosophy

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   :hidden:

   commands
   workflow
   configuration
   templates

.. toctree::
   :maxdepth: 2
   :caption: Reference
   :hidden:

   cli_reference
   api_reference
   changelog

.. toctree::
   :maxdepth: 1
   :caption: Development
   :hidden:

   contributing
   architecture

PairCoder: AI-Augmented Pair Programming Framework
===================================================

PairCoder gives teams a **drop-in, repo-native toolkit** for pairing with AI coding agents. 
It standardizes governance, persists project memory, and provides a CLI to orchestrate the workflow.

Quick Links
-----------

* :doc:`quickstart` - Get started in 5 minutes
* :doc:`commands` - CLI command reference  
* :doc:`workflow` - The PairCoder workflow
* :doc:`philosophy` - Why PairCoder exists

Features
--------

✨ **Context as Memory** 
   Canonical state in ``/context/*.md`` (roadmap, agents guide, project tree)

🔄 **Disciplined Loop** 
   Agents update Overall/Last/Next/Blockers on every action

🛡️ **Governance** 
   CONTRIBUTING, PR template, CODEOWNERS, SECURITY

🎯 **Quality Gates** 
   Pre-commit hooks, secret scanning, CI workflows

🚀 **CLI (bpsai-pair)** 
   ``init``, ``feature``, ``pack``, ``context-sync``

📦 **Cookiecutter Template** 
   Bootstrap new repos with PairCoder structure

Installation
------------

.. code-block:: bash

   pip install bpsai-pair
   bpsai-pair --version

Quick Start
-----------

.. code-block:: bash

   # Initialize your repository
   bpsai-pair-init

   # Create a feature branch
   bpsai-pair feature auth-system \
     --type feature \
     --primary "Implement authentication" \
     --phase "Design auth architecture"

   # Package context for AI
   bpsai-pair pack --out agent_pack.tgz

   # Update context after changes
   bpsai-pair context-sync \
     --last "Designed auth flow" \
     --next "Implement login endpoint" \
     --blockers "None"

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
