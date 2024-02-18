==============
Project Hadron
==============

Introduction
============
Unfortunately, 85% of data science projects fail due to a lack of understanding of the real
business problem. This is usually because of poor communication between data scientists and
business teams, resulting in a disconnect between the two groups. Project Hadron has been built
to bridge the gap between data scientists and data engineers. More specifically between machine
learning business outcomes or use case and a product pipeline. It translates the work of data
scientists into meaningful, production ready solutions that can be easily integrated into a
DevOps, CI/CD pipeline.

Project Hadron addresses data selection, feature engineering and feature transformation as part
of the critical preprocessing of a Machine Learning pipeline or System Data pipeline. At its core
the code uses PyArrow as its canonical combining with Pandas as a directed specialist toolset.
PyArrow complements Pandas by providing a more memory-efficient in-memory representation,
enabling efficient data interchange between different systems, supporting distributed computing,
and enhancing compatibility with other programming languages. When used together, Pandas and
PyArrow form a powerful combination for handling diverse data processing tasks efficiently.

Data Selection and Feature Engineering
======================================
Data selection and feature engineering is the art/science of converting raw data to a form that
optimises the success of the next step in a pipeline. This involves a skilled blend of domain
expertise, intuition and mathematics. Data selection and feature engineering are the most
essential part of building a useable machine learning or data project, constituting an average of
80% of the project's time, even with hundreds of cutting-edge  machine learning algorithms
appearing.

Prof Domingos, the author of 'The Master Algorithm' says::

    "At the end of the day, some machine learning projects succeed and some fail. What makes the
    difference? Easily the most important factor is the features used."

Preprocessing
-------------
The term "data preprocessing" is commonly used in the field of data science and machine learning
to refer ata selection and feature engineering as steps taken to clean, format, and organize raw
data into a suitable format for Model Evaluation & Tunning

.. image:: docs/images/introduction/machine_learning_pipeline_v01.png
  :align: center
  :width: 700









Main features
-------------

* Data Preparation
* Feature Selection
* Feature Engineering
* Feature Cataloguing
* Augmented Knowledge
* Synthetic Feature Build

Feature transformers
--------------------

Project Hadron is a Python library with multiple transformers to engineer and select features to use
across a synthetic build, statistics and machine learning.

* Missing data imputation
* Categorical encoding
* Variable Discretisation
* Outlier capping or removal
* Numerical transformation
* Redundant feature removal
* Synthetic variable creation
* Synthetic multivariate
* Synthetic model distributions
* Datetime features
* Time series

Project Hadron allows one to present optimal parameters associated with each transformer, allowing
different engineering procedures to be applied to different variables and feature subsets.

Background
----------
Born out of the frustration of time constraints and the inability to show business value
within a business expectation, this project aims to provide a set of tools to quickly build production ready
data science disciplines within a component based solution demonstrating coupling and cohesion between each
disipline, providing a separation of concerns between components.

It also aims to improve the communication outputs needed by ML delivery to talk to Pre-Sales, Stakholders,
Business SME's, Data SME's product coders and tooling engineers while still remaining within familiar code
paradigms.

Getting Started
===============

The ``discovery-transition-ds`` package is a set of python components that are focussed on Data Science. They
are a concrete implementation of the Project Hadron abstract core. It is build to be very light weight
in terms of package dependencies requiring nothing beyond what would be found in an basic Data Science environment.
Its designed to be used easily within multiple python based interfaces such as Jupyter, IDE or terminal python.

Package Installation
--------------------

The best way to install the component packages is directly from the Python Package Index repository using pip.

The component package is ``discovery-transition-ds`` and pip installed with:

.. code-block:: bash

    python -m pip install discovery-transition-ds

if you want to upgrade your current version then using pip install upgrade with:

.. code-block:: bash

    python -m pip install -U discovery-transition-ds

This will also install or update dependent third party packages. The dependencies are
limited to python and related Data Science tooling such as pandas, numpy, scipy,
scikit-learn and visual packages matplotlib and seaborn, and thus have a limited
footprint and non-disruptive in a machine learning environment.

Get the Source Code
-------------------

``discovery-transition-ds`` is actively developed on GitHub, where the code is
`always available <https://github.com/project-hadron/discovery-transition-ds>`_.

You can clone the public repository with:

.. code-block:: bash

    $ git clone git@github.com:project-hadron/discovery-transition-ds.git

Once you have a copy of the source, you can embed it in your own Python
package, or install it into your site-packages easily running:

.. code-block:: bash

    $ cd discovery-transition-ds
    $ python -m pip install .

Release Process and Rules
-------------------------

Versions to be released after ``3.5.27``, the following rules will govern
and describe how the ``discovery-transition-ds`` produces a new release.

To find the current version of ``discovery-transition-ds``, from your
terminal run:

.. code-block:: bash

    $ python -c "import ds_discovery; print(ds_discovery.__version__)"

Major Releases
**************

A major release will include breaking changes. When it is versioned, it will
be versioned as ``vX.0.0``. For example, if the previous release was
``v10.2.7`` the next version will be ``v11.0.0``.

Breaking changes are changes that break backwards compatibility with prior
versions. If the project were to change an existing methods signature or
alter a class or method name, that would only happen in a Major release.
The majority of changes to the dependant core abstraction will result in a
major release. Major releases may also include miscellaneous bug fixes that
have significant implications.

Project Hadron is committed to providing a good user experience
and as such, committed to preserving backwards compatibility as much as possible.
Major releases will be infrequent and will need strong justifications before they
are considered.

Minor Releases
**************

A minor release will include addition methods, or noticeable changes to
code in a backward-compatable manner and miscellaneous bug fixes. If the previous
version released was ``v10.2.7`` a minor release would be versioned as
``v10.3.0``.

Minor releases will be backwards compatible with releases that have the same
major version number. In other words, all versions that would start with
``v10.`` should be compatible with each other.

Patch Releases
**************

A patch release include small and encapsulated code changes that do
not directly effect a Major or Minor release, for example changing
``round(...`` to ``np.around(...``, and bug fixes that were missed
when the project released the previous version. If the previous
version released ``v10.2.7`` the hotfix release would be versioned
as ``v10.2.8``.

Reference
=========

Python version
--------------

Python 3.7 or less is not supported. Although it is recommended to install ``discovery-transition-ds`` against the
latest Python version or greater whenever possible.

Pandas version
--------------

Pandas 1.0.x and above are supported but It is highly recommended to use the latest 1.0.x release as the first
major release of Pandas.

GitHub Project
--------------

discovery-transition-ds: `<https://github.com/project-hadron/discovery-transition-ds>`_.

Change log
----------

See `CHANGELOG <https://github.com/project-hadron/discovery-transition-ds/blob/master/CHANGELOG.rst>`_.


License
-------
This project uses the following license:
MIT License: `<https://opensource.org/license/mit/>`_.



Authors
-------

`Gigas64`_  (`@gigas64`_) created discovery-transition-ds.


.. _pip: https://pip.pypa.io/en/stable/installing/
.. _Github API: http://developer.github.com/v3/issues/comments/#create-a-comment
.. _Gigas64: http://opengrass.io
.. _@gigas64: https://twitter.com/gigas64


