.. highlight:: shell

============
Installation
============

Since enpt_enmapboxapp (the EnPT GUI package) extends the functionality of the EnMAP-Box_, the installation of
enpt_enmapboxapp requires QGIS_ including the EnMAP-Box plugin. If QGIS_ or the EnMAP-Box_ is not yet installed on your
system, follow the installation instructions
`here <https://enmap-box.readthedocs.io/en/latest/usr_section/usr_installation.html>`__. This should also automatically
install the enpt_enmapboxapp package into the QGIS_ Python environment.

However, make sure you have the latest version of the GUI installed by running the following command on a command line
with the QGIS Python environment activated:

.. code-block:: console

    pip install --upgrade enpt_enmapboxapp

.. note::

    On a Windows system and in case your QGIS is NOT installed into a Conda Python environment but, e.g., via the
    OSGeo4W installer, you have to activate the the QGIS environment first. To do so, run the OSGeo4W Shell (listed
    under OSGeo4W in the Windows Start Menu) as administrator and enter :code:`call py3_env.bat`.

To make the enpt_enmapboxapp (GUI code) run together with EnPT_ (backend), the EnPT_ backend code has to be installed.
The easiest way (recommended) is to install QGIS, the EnMAP-Box and EnPT into a single Conda environment. Please
refer to the EnPT_ installation instructions
`here <https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/EnPT/doc/installation.html>`__ to do so. However,
if QGIS is already installed as a standalone-software which does not use a Conda Python environment in the background
(e.g., installed via the OSGeo4W installer on Windows), the EnPT backend code has to be installed into a separate
Conda environment that is called 'enpt' and then linked to the QGIS Python using the EnPT GUI.

.. _EnPT: https://git.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/EnPT
.. _EnMAP-Box: https://www.enmap.org/data_tools/enmapbox/
.. _QGIS: https://www.qgis.org
