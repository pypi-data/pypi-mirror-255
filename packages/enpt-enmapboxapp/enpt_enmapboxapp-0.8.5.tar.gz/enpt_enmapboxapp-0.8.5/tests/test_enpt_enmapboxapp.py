#!/usr/bin/env python
# -*- coding: utf-8 -*-

# enpt_enmapboxapp, A QGIS EnMAPBox plugin providing a GUI for the EnMAP processing tools (EnPT)
#
# Copyright (C) 2018-2024 Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
#
# This software was developed within the context of the EnMAP project supported
# by the DLR Space Administration with funds of the German Federal Ministry of
# Economic Affairs and Energy (on the basis of a decision by the German Bundestag:
# 50 EE 1529) and contributions from DLR, GFZ and OHB System AG.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.

"""Tests for `enpt_enmapboxapp` package."""

import os
from tempfile import TemporaryDirectory
import pickle
from typing import Union, Type
from time import sleep

import pytest
from qgis.core import QgsProcessingAlgorithm, QgsProcessingContext, QgsProcessingFeedback, QgsProcessingProvider, NULL

from enmapbox.testing import start_app
from enmapbox import registerEnMAPBoxProcessingProvider
from enmapbox.gui.enmapboxgui import EnMAPBox
from enmapbox.gui.applications import EnMAPBoxApplication as _EnMAPBoxApplication
from enpt_enmapboxapp.enpt_algorithm import EnPTAlgorithm
from enpt_enmapboxapp.enpt_enmapboxapp import EnPTEnMAPBoxApp
from enpt_enmapboxapp.enpt_external_algorithm import ExternalEnPTAlgorithm
# from enpt_enmapboxapp import ExampleAppGUI

# initialize the QGIS API + several background states
APP = start_app()

# initialize the EnMAPBoxProcessingProvider
registerEnMAPBoxProcessingProvider()

# set on True to show widgets and wait until a user closes them.
SHOW_GUI = True

IS_CI_ENV = os.getenv('IS_CI_ENV') == "1"

# os.environ['QT_X11_NO_MITSHM'] = "1"

# FIXME replace hardcoded paths
enpt_test_parameters = dict(
    conda_root='',
    CPUs=12,
    auto_download_ecmwf=True,
    deadpix_P_algorithm='spectral',
    deadpix_P_interp_spectral='linear',
    deadpix_P_interp_spatial='linear',
    drop_bad_bands=True,
    disable_progress_bars=False,
    output_format='GTiff',
    output_interleave='band',
    output_nodata_value=-9999,  # not the default
    enable_keystone_correction=False,
    enable_vnir_swir_coreg=False,
    json_config=None,
    n_lines_to_append=NULL,
    mode_ac='combined',
    polymer_additional_results=True,
    ortho_resampAlg='bilinear',
    vswir_overlap_algorithm='vnir_only',
    output_dir='TEMPORARY_OUTPUT',
    path_earthSunDist=None,
    path_l1b_enmap_image='D:\\Daten\\Code\\python\\EnPT\\tests\\data\\EnMAP_Level_1B\\'
                         'ENMAP01-____L1B-DT000000987_20130205T105307Z_001_V000101_20190426T143700Z__rows0-99.zip',
    path_l1b_enmap_image_gapfill=None,
    path_dem='D:\\Daten\\Code\\python\\EnPT\\tests\\data\\DLR_L2A_DEM_UTM32.bsq',
    path_reference_image=None,
    path_solar_irr=None,
    run_deadpix_P=True,
    run_smile_P=False,
    scale_factor_boa_ref=10000,
    scale_factor_toa_ref=10000,
    sicor_cache_dir=None,
    target_projection_type='UTM',
    working_dir=None)


# def test_algorithms():
#     """
#     Test your core algorithms, which might not require any GUI or QGIS.
#     """
#
#     args, kwds = exampleAlgorithm()
#
#     assert args == ()
#     assert kwds == dict()
#
#     args, kwds = exampleAlgorithm(42, foo='bar')
#     assert args[0] == 42
#     assert kwds['foo'] == 'bar'


# def test_dialog():
#     """
#     Test your Qt GUI components, without any EnMAP-Box
#     """
#     g = ExampleAppGUI()
#     g.show()
#
#     assert isinstance(g.numberOfClicks(), int)
#     assert g.numberOfClicks() == 0
#
#     # click the button programmatically
#     g.btn.click()
#     assert g.numberOfClicks() == 1
#
#     if SHOW_GUI:
#         APP.exec_()


def _test_processingAlgorithm(Algorithm: Union[Type[EnPTAlgorithm], Type[ExternalEnPTAlgorithm]]):
    try:
        os.environ['IS_ENPT_GUI_TEST'] = '1'

        alg = Algorithm()
        assert isinstance(alg, QgsProcessingAlgorithm)

        alg2 = alg.createInstance()
        assert isinstance(alg2, QgsProcessingAlgorithm)

        with TemporaryDirectory() as td:
            params = enpt_test_parameters.copy()
            params['output_dir'] = td
            params['path_l1b_enmap_image'] = os.path.join('dummy', 'path', 'to', 'EnMAP_file.zip')
            params['path_dem'] = os.path.join('dummy', 'path', 'to', 'DEM.bsq')

            # call the EnPT_Controller with the above params, it will pickle.dump them to disk
            outputs = alg.processAlgorithm(params,
                                           QgsProcessingContext(),
                                           QgsProcessingFeedback())

            assert isinstance(outputs, dict)

            # unpickle the dumped args/kwargs and validate that EnPT received them correctly
            content = None
            try:
                with open(os.path.join(td, 'received_args_kwargs.pkl'), 'rb') as inF:
                    content = pickle.load(inF)
            except FileNotFoundError:
                pass

            if content is None:
                pytest.fail('The EnPT_Controller did not dump the '
                            'received arguments or did not receive any.')

            none_params = [k for k, v in params.items() if params[k] in [None, NULL]]
            for k, v in params.items():
                if k not in ['conda_root', 'json_config'] + none_params:
                    if k not in content['kwargs']:
                        pytest.fail(f"Missing key '{k}' in received parameters.")
                    assert v == content['kwargs'][k]

    finally:
        del os.environ['IS_ENPT_GUI_TEST']


def test_EnPTAlgorithm():
    _test_processingAlgorithm(EnPTAlgorithm)


def test_ExternalEnPTAlgorithm():
    _test_processingAlgorithm(ExternalEnPTAlgorithm)


def test_with_EnMAPBox():
    """
    Finally, test if your application can be added into the EnMAP-Box
    """
    enmapBox = EnMAPBox.instance()
    if enmapBox is None:
        enmapBox = EnMAPBox()
    assert isinstance(enmapBox, EnMAPBox)
    enmapBox.run()

    myApp = EnPTEnMAPBoxApp(enmapBox)
    assert isinstance(myApp, _EnMAPBoxApplication)
    enmapBox.addApplication(myApp)

    provider = enmapBox.processingProvider()
    assert isinstance(provider, QgsProcessingProvider)
    algorithmNames = [a.name() for a in provider.algorithms()]
    for name in ['EnPTAlgorithm', ]:
        assert name in algorithmNames

    if SHOW_GUI and not IS_CI_ENV:
        myApp.startGUI()
        APP.exec_()
    else:
        sleep(2)
        enmapBox.exit()


def test_EnPTGUI():
    enmapBox = EnMAPBox.instance()
    if enmapBox is None:
        enmapBox = EnMAPBox()
    assert isinstance(enmapBox, EnMAPBox)
    enmapBox.run()

    app = [a for a in enmapBox.applicationRegistry.applications() if isinstance(a, EnPTEnMAPBoxApp)]
    if len(app) != 1:
        pytest.fail('EnPTEnMAPBoxApp was not loaded during EnMAP-Box startup')

    app = app[0]
    assert isinstance(app, EnPTEnMAPBoxApp)

    if SHOW_GUI and not IS_CI_ENV:
        app.startGUI()
        APP.exec_()
    else:
        sleep(2)
        enmapBox.exit()


if __name__ == "__main__":
    SHOW_GUI = False

    # quiet matplotlib
    import logging
    mpl_logger = logging.getLogger('matplotlib')
    mpl_logger.setLevel(logging.WARNING)

    # run tests
    pytest.main()
