odinprocservcontrol
===================

|code_ci| |docs_ci| |coverage| |pypi_version| |license|

A pythonSoftIOC to restart Odin procServ processes in a logical way. The IOC provides
START, STOP and RESTART PVs and pokes the corresponding PVs of the procServControl
instances for the given Odin processes, in the correct order and with appropriate
delays.

============== ==============================================================
PyPI           ``pip install odinprocservcontrol``
Source code    https://github.com/dls-controls/odinprocservcontrol
Documentation  https://dls-controls.github.io/odinprocservcontrol
============== ==============================================================

.. |code_ci| image:: https://github.com/dls-controls/odinprocservcontrol/workflows/Code%20CI/badge.svg?branch=master
    :target: https://github.com/dls-controls/odinprocservcontrol/actions?query=workflow%3A%22Code+CI%22
    :alt: Code CI

.. |docs_ci| image:: https://github.com/dls-controls/odinprocservcontrol/workflows/Docs%20CI/badge.svg?branch=master
    :target: https://github.com/dls-controls/odinprocservcontrol/actions?query=workflow%3A%22Docs+CI%22
    :alt: Docs CI

.. |coverage| image:: https://codecov.io/gh/dls-controls/odinprocservcontrol/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/dls-controls/odinprocservcontrol
    :alt: Test Coverage

.. |pypi_version| image:: https://img.shields.io/pypi/v/odinprocservcontrol.svg
    :target: https://pypi.org/project/odinprocservcontrol
    :alt: Latest PyPI version

.. |license| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
    :target: https://opensource.org/licenses/Apache-2.0
    :alt: Apache License

..
    Anything below this line is used when viewing README.rst and will be replaced
    when included in index.rst

See https://dls-controls.github.io/odinprocservcontrol for more detailed documentation.
