Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_,
and this project adheres to `Semantic Versioning`_.

`2.0.2`_ - 2024-02-10
---------------------

Fixed
~~~~~

* Users didn't have to confirm their passwords a second time. 

`2.0.1`_ - 2023-12-17
---------------------

Fixed
~~~~~

* Submitting evaluation with empty values in optional part failed.
* Showing evaluation results with empty values failed.

`2.0`_ - 2ß23-11-05
-------------------

Added
~~~~~

* Support custom evaluation items on a per-group base.

Changed
~~~~~~~

* Allow parts to be optional.
* Add 'Partially true' as answer choice.
* Completely restructure results page and PDF to include
  evaluation items in their original order.
* Make colors in charts more visible.

Removed
~~~~~~~

* There are no separate result phases anymore, teachers can finish the evaluation phase on their owns.

`1.0`_ - 2023-05-15
-------------------

Nothing changed.

`1.0b1`_ - 2022-04-21
---------------------

Fixed
~~~~~

* Many views were not compatible with new SPA.

`1.0b0`_ – 2022-03-03
---------------------

This version requires AlekSIS-Core 3.0. It is incompatible with any previous
version.

Removed
~~~~~~~

* Legacy menu integration for AlekSIS-Core pre-3.0

Added
~~~~~

* Add SPA support for AlekSIS-Core 3.0
* Add Ukrainian and Russian locale (contributed by Sergiy Gorichenko from Fre(i)e Software GmbH).


`0.5.1`_ - 2022-01-23
---------------------

Fixed
~~~~~

* Charts in results page weren't loaded.

`0.5`_ - 2022-12-29
-------------------

Added
~~~~~

* Deletion mechanism for evaluation results.

`0.4.2`_
--------

Fixed
~~~~~

* Results view caused errors when form wasn't valid.

`0.4.1`_
--------

Fixed
~~~~~

* Some views were unintentionally cached.

`0.4`_
------

Added
~~~~~

* Add option to finish evaluation before phase end to view results then.

Fixed
~~~~~

* Rule names used wrong semantic.

`0.3.2`_
--------

Fixed
~~~~~

* Fix raising of integrity errors when finishing evaluation.

`0.3.1`_
--------

Fixed
~~~~~

* When registration and registration had overlapping time periods, evaluation was not possible.

`0.3`_
------

Added
~~~~~

* [Dev] Add some automatic tests.

Fixed
~~~~~

* [BREAKING CHANGE] Use hybrid encryption for evaluation results to make it possible to properly encrypt longer results.

**Warning:** This change is not compatible with evaluation results from older versions of this app.
If you have evaluation results from older versions of this app, you will need to delete them.

`0.2`_
-------

Changed
~~~~~~~

* Allow overlapping of registration and evaluation period.

`0.1.5`_
--------

Fixed
~~~~~

* Results page failed with zero division error when no results were found.

`0.1.4`_
--------

Fixed
~~~~~

* Use only groups in matching school term for evaluation.

`0.1.3`_
--------

Fixed
~~~~~

* Migrations depended on too new migrations from Core.

`0.1.2`_
--------


Fixed
~~~~~

* Migrations didn't work due to a race condition.


`0.1.1`_
--------

Fixed
~~~~~

* Migrations didn't work due to a race condition.

`0.1`_
------

Added
~~~~~

* Initial release.


.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html


.. _0.1: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/0.1
.. _0.1.1: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/0.1.1
.. _0.1.2: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/0.1.2
.. _0.1.3: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/0.1.3
.. _0.1.4: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/0.1.4
.. _0.1.5: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/0.1.5
.. _0.2: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/0.2
.. _0.3: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/0.3
.. _0.3.1: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/0.3.1
.. _0.3.2: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/0.3.2
.. _0.4: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/0.4
.. _0.4.1: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/0.4.1
.. _0.4.2: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/0.4.2
.. _0.5: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/0.5
.. _0.5.1: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/0.5.1
.. _1.0b0: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/1.0b0
.. _1.0b1: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/1.0b1
.. _1.0: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/1.0
.. _2.0: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/2.0
.. _2.0.1: https://edugit.org/katharineum/AlekSIS-App-EvaLU/-/tags/2.0.1
