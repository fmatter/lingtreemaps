Customizing your treemap
-------------------------

By default, ``lingtreemaps`` uses the parameter values shown below.
The values in it can be overridden by passing a YAML file with the ``-c``/``--config`` option for ``lingtreemaps plot``, or by passing arguments to :py:meth:`lingtreemaps.plot`.
In the latter scenario, note that YAML ``null`` corresponds to python ``None``.

.. include:: ../src/lingtreemaps/data/default_config.yaml
   :literal:

A ``text_df`` must have the following columns: ``Latitude``, ``Longitude``, ``Label``.