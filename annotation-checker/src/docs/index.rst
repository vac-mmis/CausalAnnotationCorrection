.. Causal Annotation Correction Documentation documentation master file, created by
   sphinx-quickstart on Sun Aug 27 18:05:36 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

CausalAnnotationCorrection
===========================

Introduction
-------------

This application provides a tool for inspection, validation and correction of behavioral annotations:

With this small example you can try out the tool:

1. Install docker (https://docs.docker.com/engine/install/)
2. Run the image from docker hub:

.. code-block::

    $ docker run -p 9000:9000 -it fgratzkowski/cac

3. Navigate to: ``Examples/Checking_Annotation`` or ``Examples/Creating_Domain``
4. Simply invoke:

.. code-block::

    $ make run

If you need more information about the examples, check out the :ref:`Example` section.

.. warning::

   In general, the Causal Annotation Correction Tool will not work out of the box after having been installed with pip. See the :ref:`Installation` section for more details.

Documentation Index
====================

.. toctree::
   :maxdepth: 1

   installation
   usage
   example
   structure
   acheck