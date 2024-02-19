Unofficial AlekSIS App EvaLU (Evaluation of teaching and lesson quality)
========================================================================

AlekSIS
-------

This is an unofficial application for use with the `AlekSIS`_ platform.

Features
--------

This app can be used to evaluate teaching and lesson quality of teachers.

Licence
-------

::

  Copyright © 2021, 2022, 2023 Jonathan Weth <dev@jonathanweth.de>

  Licenced under the EUPL, version 1.2 or later

Create graph of models
----------------------

::

  poetry run pip install pygraphviz
  poetry run aleksis-admin graph_models evalu -X Site,ExtensibleModel -x site,extended_data -o

Please see the LICENCE.rst file accompanying this distribution for the
full licence text or on the `European Union Public Licence`_ website
https://joinup.ec.europa.eu/collection/eupl/guidelines-users-and-developers
(including all other official language versions).

.. _AlekSIS: https://edugit.org/AlekSIS/AlekSIS
.. _European Union Public Licence: https://eupl.eu/
