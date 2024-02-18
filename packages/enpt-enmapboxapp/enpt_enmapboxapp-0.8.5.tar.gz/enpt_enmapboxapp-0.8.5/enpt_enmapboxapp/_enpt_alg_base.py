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

"""This module provides the base class for EnPTAlgorithm and ExternalEnPTAlgorithm."""

import os
from os.path import expanduser
import psutil
from importlib.util import find_spec
from datetime import date
from multiprocessing import cpu_count
from threading import Thread
from queue import Queue
from subprocess import Popen, PIPE
from glob import glob
from warnings import warn

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFile,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterEnum,
    NULL
)

from .version import __version__


class _EnPTBaseAlgorithm(QgsProcessingAlgorithm):
    # NOTE: The parameter assignments made here follow the parameter names in enpt/options/options_schema.py

    # Input parameters
    P_json_config = 'json_config'
    P_CPUs = 'CPUs'
    P_path_l1b_enmap_image = 'path_l1b_enmap_image'
    P_path_l1b_enmap_image_gapfill = 'path_l1b_enmap_image_gapfill'
    P_path_dem = 'path_dem'
    P_average_elevation = 'average_elevation'
    P_output_dir = 'output_dir'
    P_working_dir = 'working_dir'
    P_n_lines_to_append = 'n_lines_to_append'
    P_drop_bad_bands = 'drop_bad_bands'
    P_disable_progress_bars = 'disable_progress_bars'
    P_output_format = 'output_format'
    P_output_interleave = 'output_interleave'
    P_output_nodata_value = 'output_nodata_value'
    P_path_earthSunDist = 'path_earthSunDist'
    P_path_solar_irr = 'path_solar_irr'
    P_scale_factor_toa_ref = 'scale_factor_toa_ref'
    P_enable_keystone_correction = 'enable_keystone_correction'
    P_enable_vnir_swir_coreg = 'enable_vnir_swir_coreg'
    P_path_reference_image = 'path_reference_image'
    P_enable_ac = 'enable_ac'
    P_mode_ac = 'mode_ac'
    P_polymer_additional_results = 'polymer_additional_results'
    P_polymer_root = 'polymer_root'
    P_threads = 'threads'
    P_blocksize = 'blocksize'
    P_auto_download_ecmwf = 'auto_download_ecmwf'
    P_scale_factor_boa_ref = 'scale_factor_boa_ref'
    P_run_smile_P = 'run_smile_P'
    P_run_deadpix_P = 'run_deadpix_P'
    P_deadpix_P_algorithm = 'deadpix_P_algorithm'
    P_deadpix_P_interp_spectral = 'deadpix_P_interp_spectral'
    P_deadpix_P_interp_spatial = 'deadpix_P_interp_spatial'
    P_ortho_resampAlg = 'ortho_resampAlg'
    P_vswir_overlap_algorithm = 'vswir_overlap_algorithm'
    P_target_projection_type = 'target_projection_type'
    P_target_epsg = 'target_epsg'

    # # Output parameters
    P_OUTPUT_RASTER = 'outraster'
    # P_OUTPUT_VECTOR = 'outvector'
    # P_OUTPUT_FILE = 'outfile'
    P_OUTPUT_FOLDER = 'outfolder'

    def group(self):
        return 'Pre-Processing'

    def groupId(self):
        return 'PreProcessing'

    def name(self):
        return 'EnPTAlgorithm'

    def displayName(self):
        return f'EnPT - EnMAP Processing Tool (v{__version__})'

    def createInstance(self, *args, **kwargs):
        return type(self)()

    @staticmethod
    def _get_default_polymer_root():
        if not find_spec('polymer'):
            return ''
        elif not find_spec('polymer').origin:
            # this, e.g., happens when installing POLYMER with 'pip install' instead of 'pip install -e'
            print('POLYMER package found, but it is not correctly installed.')
            warn('POLYMER does not seem to be correctly installed. Find the installation instructions here: '
                 'https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/EnPT/doc/'
                 'installation.html#optional-install-polymer-for-advanced-atmospheric-correction-over-water-surfaces')
            return ''
        else:
            return os.path.abspath(os.path.join(os.path.dirname(find_spec('polymer').origin), os.pardir))

    @staticmethod
    def _get_default_output_dir():
        userhomedir = expanduser('~')

        default_enpt_dir = \
            os.path.join(userhomedir, 'Documents', 'EnPT', 'Output') if os.name == 'nt' else\
            os.path.join(userhomedir, 'EnPT', 'Output')

        outdir_nocounter = os.path.join(default_enpt_dir, date.today().strftime('%Y%m%d'))

        counter = 1
        while os.path.isdir('%s__%s' % (outdir_nocounter, counter)):
            counter += 1

        return '%s__%s' % (outdir_nocounter, counter)

    def addParameter(self, param, *args, advanced=False, **kwargs):
        """Add a parameter to the QgsProcessingAlgorithm.

        This overrides the parent method to make it accept an 'advanced' parameter.

        :param param:       the parameter to be added
        :param args:        arguments to be passed to the parent method
        :param advanced:    whether the parameter should be flagged as 'advanced'
        :param kwargs:      keyword arguments to be passed to the parent method
        """
        if advanced:
            param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)

        super(_EnPTBaseAlgorithm, self).addParameter(param, *args, **kwargs)

    def initAlgorithm(self, configuration=None):
        self.addParameter(
            QgsProcessingParameterFile(
                name=self.P_json_config,
                description='Configuration JSON template file',
                behavior=QgsProcessingParameterFile.File,
                extension='json',
                defaultValue=None,
                optional=True))

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.P_CPUs,
                description='Number of CPU cores to be used for processing',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=cpu_count(), minValue=0, maxValue=cpu_count()),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterFile(
                name=self.P_path_l1b_enmap_image,
                description='EnMAP Level-1B image (zip-archive or root directory)'))

        self.addParameter(
            QgsProcessingParameterFile(
                name=self.P_path_l1b_enmap_image_gapfill,
                description='Adjacent EnMAP Level-1B image to be used for gap-filling (zip-archive or root directory)',
                optional=True),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name=self.P_path_dem,
                description='Input path of digital elevation model in map or sensor geometry; GDAL compatible file '
                            'format \n(must cover the EnMAP L1B data completely if given in map geometry or must have '
                            'the same \npixel dimensions like the EnMAP L1B data if given in sensor geometry)',
                optional=True))

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.P_average_elevation,
                description='Average elevation in meters above sea level \n'
                            '(may be provided if no DEM is available and ignored if DEM is given)',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=0),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                name=self.P_output_dir,
                description='Output directory where processed data and log files are saved',
                defaultValue=self._get_default_output_dir(),
                optional=True))

        self.addParameter(
            QgsProcessingParameterFile(
                name=self.P_working_dir,
                description='Directory to be used for temporary files',
                behavior=QgsProcessingParameterFile.Folder,
                defaultValue=None,
                optional=True))

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.P_n_lines_to_append,
                description='Number of lines to be added to the main image [if not given, use the whole imgap]',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=None,
                optional=True),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.P_drop_bad_bands,
                description='Do not include bad bands (water absorption bands 1358-1453 nm / 1814-1961 nm) '
                            'in the L2A product',
                defaultValue=True),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.P_disable_progress_bars,
                description='Disable all progress bars during processing',
                defaultValue=True),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.P_output_format,
                description="Output format (file format of all raster output files)",
                options=['GTiff', 'ENVI'],
                defaultValue=0),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.P_output_interleave,
                description="Output raster data interleaving type",
                options=['band (BSQ)', 'line (BIL)', 'pixel (BIP)'],
                defaultValue=2),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.P_output_nodata_value,
                description="Output no-data/background value (should be within the signed integer 16-bit range)",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=-32768,
                optional=True),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterFile(
                name=self.P_path_earthSunDist,
                description='Input path of the earth sun distance model',
                defaultValue=None,
                optional=True),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterFile(
                name=self.P_path_solar_irr,
                description='Input path of the solar irradiance model',
                defaultValue=None,
                optional=True),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.P_scale_factor_toa_ref,
                description='Scale factor to be applied to TOA reflectance result',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=10000, minValue=0),
            advanced=True)

        # self.addParameter(
        #     QgsProcessingParameterBoolean(
        #         name=self.P_enable_keystone_correction,
        #         description='Keystone correction',
        #         defaultValue=False))

        # self.addParameter(
        #     QgsProcessingParameterBoolean(
        #         name=self.P_enable_vnir_swir_coreg,
        #         description='VNIR/SWIR co-registration',
        #         defaultValue=False))

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                name=self.P_path_reference_image,
                description='Reference image for absolute co-registration.',
                defaultValue=None,
                optional=True))

        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.P_enable_ac,
                description='Enable atmospheric correction',
                defaultValue=True))

        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.P_mode_ac,
                description="Atmospheric correction mode",
                options=['land - SICOR is applied to land AND water',
                         'water - POLYMER is applied to water only; land is cleared ',
                         'combined - SICOR is applied to land and POLYMER to water'],
                defaultValue=2))

        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.P_polymer_additional_results,
                description="Enable generation of additional results from ACwater/POLYMER (if executed)",
                defaultValue=True))

        self.addParameter(
            QgsProcessingParameterFile(
                name=self.P_polymer_root,
                description='Polymer root directory (that contains the subdirectory for ancillary data)',
                behavior=QgsProcessingParameterFile.Folder,
                defaultValue=self._get_default_polymer_root(),
                optional=True),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.P_threads,
                description='Number of threads for multiprocessing when running ACwater/Polymer \n'
                            "('0: no threads', '-1: automatic', '>0: number of threads')",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=-1, minValue=-1, maxValue=cpu_count()),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.P_blocksize,
                description='Block size for multiprocessing when running ACwater/Polymer',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=100, minValue=1),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.P_auto_download_ecmwf,
                description='Automatically download ECMWF data for atmospheric correction '
                            'of water surfaces in ACwater/Polymer',
                defaultValue=True),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.P_scale_factor_boa_ref,
                description='Scale factor to be applied to BOA reflectance result',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=10000, minValue=0),
            advanced=True)

        # self.addParameter(
        #     QgsProcessingParameterBoolean(
        #         name=self.P_run_smile_P,
        #         description='Smile detection and correction (provider smile coefficients are ignored)',
        #         defaultValue=False))

        self.addParameter(
            QgsProcessingParameterBoolean(
                name=self.P_run_deadpix_P,
                description='Dead pixel correction (based on L1B dead pixel map)',
                defaultValue=False))

        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.P_deadpix_P_algorithm,
                description="Algorithm for dead pixel correction",
                options=['spectral', 'spatial'],
                defaultValue=1),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.P_deadpix_P_interp_spectral,
                description="Spectral interpolation algorithm to be used during dead pixel correction ",
                options=['linear', 'bilinear', 'cubic', 'spline'],
                defaultValue=0),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.P_deadpix_P_interp_spatial,
                description="Spatial interpolation algorithm to be used during dead pixel correction",
                options=['linear', 'bilinear', 'cubic', 'spline'],
                defaultValue=0),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.P_ortho_resampAlg,
                description="Ortho-rectification resampling algorithm",
                options=['nearest', 'bilinear', 'gauss', 'cubic', 'cubic_spline', 'lanczos', 'average'],
                defaultValue=1),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.P_vswir_overlap_algorithm,
                description="Algorithm specifying how to deal with the spectral bands "
                            "in the VNIR/SWIR spectral overlap region",
                options=['VNIR and SWIR bands, order by wavelength', 'average VNIR and SWIR bands',
                         'VNIR bands only', 'SWIR bands only'],
                defaultValue=3),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P_target_projection_type,
                description='Projection type of the raster output files',
                options=['UTM', 'Geographic'],
                defaultValue=0),
            advanced=True)

        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.P_target_epsg,
                description='Custom EPSG code of the target projection (overrides target_projection_type)',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=None,
                optional=True),
            advanced=True)

    # TODO:
    #   "target_coord_grid": "None"  /*custom target coordinate grid to which the output is resampled
    #                        ([x0, x1, y0, y1], e.g., [0, 30, 0, 30])*/

    @staticmethod
    def shortHelpString(*args, **kwargs):
        """Display help string.

        Example:
        '<p>Here comes the HTML documentation.</p>' \
        '<h3>With Headers...</h3>' \
        '<p>and Hyperlinks: <a href="www.google.de">Google</a></p>'

        :param args:
        :param kwargs:
        """
        text = \
            '<p>General information about this EnMAP box app can be found ' \
            '<a href="https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/enpt_enmapboxapp/doc/">here</a>. ' \
            'For details, e.g., about all the algorithms implemented in EnPT, take a look at the ' \
            '<a href="https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/EnPT/doc/index.html">EnPT backend ' \
            'documentation</a>.</p>' \
            '<p>Type <i>enpt -h</i> into a shell to get further information about individual parameters or check out ' \
            'the <a href="https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/EnPT/doc/usage.html#' \
            'command-line-utilities">documentation</a>.</p>'

        return text

    def helpString(self):
        return self.shortHelpString()

    @staticmethod
    def helpUrl(*args, **kwargs):
        return 'https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/enpt_enmapboxapp/doc/'

    @staticmethod
    def _get_preprocessed_parameters(parameters):
        # replace Enum parameters with corresponding strings (not needed in case of unittest)
        for n, opts in [
            ('output_format', {0: 'GTiff', 1: 'ENVI'}),
            ('output_interleave', {0: 'band', 1: 'line', 2: 'pixel'}),
            ('mode_ac', {0: 'land', 1: 'water', 2: 'combined'}),
            ('deadpix_P_algorithm', {0: 'spectral', 1: 'spatial'}),
            ('deadpix_P_interp_spectral', {0: 'linear', 1: 'bilinear', 2: 'cubic', 3: 'spline'}),
            ('deadpix_P_interp_spatial', {0: 'linear', 1: 'bilinear', 2: 'cubic', 3: 'spline'}),
            ('ortho_resampAlg', {0: 'nearest', 1: 'bilinear', 2: 'gauss', 3: 'cubic',
                                 4: 'cubic_spline', 5: 'lanczos', 6: 'average'}),
            ('vswir_overlap_algorithm', {0: 'order_by_wvl', 1: 'average', 2: 'vnir_only', 3: 'swir_only'}),
            ('target_projection_type', {0: 'UTM', 1: 'Geographic'}),
        ]:
            if isinstance(parameters[n], int):
                parameters[n] = opts[parameters[n]]

        # remove all parameters not to be forwarded to the EnPT CLI
        parameters = {k: v for k, v in parameters.items()
                      if k not in ['conda_root']
                      and v not in [None, NULL, 'NULL', '']}

        return parameters

    @staticmethod
    def _run_cmd(cmd, qgis_feedback=None, **kwargs):
        """Execute external command and get its stdout, exitcode and stderr.

        Code based on: https://stackoverflow.com/a/31867499

        :param cmd: a normal shell command including parameters
        """
        def reader(pipe, queue):
            try:
                with pipe:
                    for line in iter(pipe.readline, b''):
                        queue.put((pipe, line))
            finally:
                queue.put(None)

        process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, **kwargs)
        q = Queue()
        Thread(target=reader, args=[process.stdout, q]).start()
        Thread(target=reader, args=[process.stderr, q]).start()

        stdout_qname = None
        stderr_qname = None

        # for _ in range(2):
        for source, line in iter(q.get, None):
            if qgis_feedback.isCanceled():
                # qgis_feedback.reportError('CANCELED')

                proc2kill = psutil.Process(process.pid)
                for proc in proc2kill.children(recursive=True):
                    proc.kill()
                proc2kill.kill()

                raise KeyboardInterrupt

            linestr = line.decode('latin-1').rstrip()
            # print("%s: %s" % (source, linestr))

            # source name seems to be platfor/environment specific, so grab it from dummy STDOUT/STDERR messages.
            if linestr == 'Connecting to EnPT STDOUT stream.':
                stdout_qname = source.name
                continue
            if linestr == 'Connecting to EnPT STDERR stream.':
                stderr_qname = source.name
                continue

            if source.name == stdout_qname:
                qgis_feedback.pushInfo(linestr)
            elif source.name == stderr_qname:
                qgis_feedback.reportError(linestr)
            else:
                qgis_feedback.reportError(linestr)

        exitcode = process.poll()

        return exitcode

    def _handle_results(self, parameters: dict, feedback, exitcode: int) -> dict:
        success = False

        if exitcode:
            feedback.reportError("\n" +
                                 "=" * 60 +
                                 "\n" +
                                 "An exception occurred. Processing failed.")

        # list output dir
        if 'output_dir' in parameters:
            outdir = parameters['output_dir']
            outraster_matches = \
                glob(os.path.join(outdir, '*', '*SPECTRAL_IMAGE.TIF')) or \
                glob(os.path.join(outdir, '*', '*SPECTRAL_IMAGE.bsq')) or \
                glob(os.path.join(outdir, '*', '*SPECTRAL_IMAGE.bil')) or \
                glob(os.path.join(outdir, '*', '*SPECTRAL_IMAGE.bip'))
            outraster = outraster_matches[0] if len(outraster_matches) > 0 else None

            if os.path.isdir(outdir):
                if os.listdir(outdir):
                    feedback.pushInfo("The output folder '%s' contains:\n" % outdir)
                    feedback.pushCommandInfo('\n'.join([os.path.basename(f) for f in os.listdir(outdir)]) + '\n')

                    if outraster:
                        subdir = os.path.dirname(outraster_matches[0])
                        feedback.pushInfo(subdir)
                        feedback.pushInfo("...where the folder '%s' contains:\n" % os.path.split(subdir)[-1])
                        feedback.pushCommandInfo('\n'.join(sorted([os.path.basename(f)
                                                                   for f in os.listdir(subdir)])) + '\n')
                        success = True
                    else:
                        feedback.reportError("No output raster was written.")

                else:
                    feedback.reportError("The output folder is empty.")

            else:
                feedback.reportError("No output folder created.")

            # return outputs
            if success:
                return {
                    'success': True,
                    self.P_OUTPUT_RASTER: outraster,
                    # self.P_OUTPUT_VECTOR: parameters[self.P_OUTPUT_RASTER],
                    # self.P_OUTPUT_FILE: parameters[self.P_OUTPUT_RASTER],
                    self.P_OUTPUT_FOLDER: outdir
                }
            else:
                return {'success': False}

        else:
            feedback.pushInfo('The output was skipped according to user setting.')
            return {'success': True}
