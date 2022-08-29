Using ``lingtreemaps``
-----------------------
To create maps, you can either use `lingtreemaps plot <#lingtreemaps-plot>`_ in the command line or call the :py:meth:`lingtreemaps.plot` function from your own python code.
The available parameters for both approaches are documented `below <#configuring-lingtreemaps>`_.
There are also commands to `download newick trees <#lingtreemaps-download-tree>`_ from `glottolog <glottolog.org/>`_ and `get language coordinates <#lingtreemaps-get-language-data>`_ from `cldfbench <https://cldfbench.readthedocs.io/en/latest/index.html>`_.

The command line interface
***************************
.. click:: lingtreemaps.cli:main
   :prog: lingtreemaps
   :nested: full
