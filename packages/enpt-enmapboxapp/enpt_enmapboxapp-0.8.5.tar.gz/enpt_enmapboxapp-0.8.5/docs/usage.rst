=====
Usage
=====

The enpt_enmapboxapp GUI can be found in
:menuselection:`QGIS 3.xx --> EnMAP-Box --> Processing Toolbox --> Pre-Processing --> EnPT - EnMAP Processing Tool`


.. image:: ./images/screenshot_how_to_start.png
    :scale: 75 %

Use the GUI to parameterize EnPT_ according to your input dataset and the desired processing settings.
The input parameters are explained
`here <https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/EnPT/doc/usage.html#enpt-cli-py>`__.

.. hint::

    If your QGIS is not installed into a Conda Python environment but installed as a standalone software, make sure,
    that the Conda root directory is correctly set before you start the processing chain. It should
    point to the Conda installation containing the previously installed `enpt` Python environment.

The status of computation can be watched in the log tab and the QGIS Python console.


.. _EnPT: https://git.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/EnPT
