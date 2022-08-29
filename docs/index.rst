.. lingtreemaps documentation master file, created by
   sphinx-quickstart on Sat Apr  2 22:11:17 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to lingtreemaps's documentation!
==============================================

The primary use case for ``lingtreemaps`` is this:
You have some sort of data point for a group of related languages the distribution of which you want to visualize on both a genealogical tree and on a map.
``lingtreemaps`` allows you to do both at once, in a single, customizable map + tree image.
All you need is a language table, a tree, and a feature table.

Tables are either stored in CSV files, or provided as `pandas <pandas.org>`_ dataframes.
Trees are either stored in ``.nwk``/``.newick`` files, or provided as `Bio.Phylo.BaseTree <https://biopython.org/docs/1.75/api/Bio.Phylo.BaseTree.html>`_ objects.
The minimal requirements for the input are:

1. The language table must have a ``Latitude`` and a ``Longitude`` colum.
2. It must also have an ``ID`` colum, which will be used to connect to connect the coordinates to the labels on the tree.
3. The tree must be in newick format, and have leaf labels corresponding to the contents of the ``ID`` colum in the language table.
4. Your feature table must have the columns ``Clade`` (corresponding to the values of the ``ID`` columns in the language table) and ``Value``

.. toctree::
   :maxdepth: 2
   
   usage
   config
   examples


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
