==================================
Sphinx CSV Filter (JM-Version)
==================================

A Sphinx_ plugin that extends the csv-table_ reStructuredText_ directive to add
row filtering options.

This is an adapted version of the original sphinx-csv-filter which can be found here: sphinx-csv-filter_

**Do not use this version if you expect support. It will most likely contain bugs as it is not tested as professionally as the original version**


Prerequisites
=============

You need to be using Sphinx and reStructuredText.

Installation
============

Add to your requirements.txt:

.. code::
    
    -e git://github.com/Nefti-sama/sphinx_csv_filter-jm.git#egg=sphinx-csv-filter-jm

Set Up
======

To include the extension, add this line to ``config.py`` in
your Sphinx project::

    extensions = ['jm.sphinx.csv']

If you're using other extensions, edit the existing list, or add this::

    extensions.append('jm.sphinx.csv')

Use
===

This plugin adds the following options to the csv-table_ directive:

``:included_cols:``
    This is a comma-separated list of column indexes to include in the output.

``:include:``
    This option takes a Python dict specifying the column index (starting at
    zero) and a regular expression. Rows are included if the columnar value
    matches the supplied regular expression.

``:exclude:``
    This option takes a Python dict specifying the column index (starting at
    zero) and a regular expression. Rows are excluded if the columnar value
    matches the supplied regular expression.

If a row matches an ``:include:`` as well as an ``:exclude:`` filter, the row
with be excluded.

``:include:`` as well as ``:exclude:`` can contain a list of regexes instead of a single regex

Here's an example::

    .. csv-filter:: Example Table
       :header: Company,Contact,Country,Attend?
       :file: example.csv
       :exclude: {3: '(?i)Y\w*'}

In this example, rows from ``example.csv`` will be omitted from the output if the regular expression ``(?i)Y\w*`` matches value of the ``Attend?`` column.

List example::

    .. csv-filter:: Server-List
        :header: IP, Hostname, Type
        :included_cols: 2,5,1
        :include: { 1: ['SRV', 'VM'] }
        :exclude: { 5: ['ESX', 'CIMC'], 2: "254$" }

This will include all Servers and VM's (Type-Column) except those with *ESX* or *CIMC* in the Hostname. Also, if the IP-Address ends with *254* the row will be excluded.


.. _Crate.io: http://crate.io/
.. _csv-table: http://docutils.sourceforge.net/docs/ref/rst/directives.html#csv-table
.. _reStructuredText: http://www.sphinx-doc.org/en/stable/rest.html
.. _Sphinx: http://www.sphinx-doc.org/en/stable/
.. _support channels: https://crate.io/support/
.. _sphinx-csv-filter: https://github.com/crate/sphinx_csv_filter