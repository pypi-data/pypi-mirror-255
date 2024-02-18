#  """
#    Copyright (c) 2016- 2023, Wiliot Ltd. All rights reserved.
#
#    Redistribution and use of the Software in source and binary forms, with or without modification,
#     are permitted provided that the following conditions are met:
#
#       1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#       2. Redistributions in binary form, except as used in conjunction with
#       Wiliot's Pixel in a product or a Software update for such product, must reproduce
#       the above copyright notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the distribution.
#
#       3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
#       may be used to endorse or promote products or services derived from this Software,
#       without specific prior written permission.
#
#       4. This Software, with or without modification, must only be used in conjunction
#       with Wiliot's Pixel or with Wiliot's cloud service.
#
#       5. If any Software is provided in binary form under this license, you must not
#       do any of the following:
#       (a) modify, adapt, translate, or create a derivative work of the Software; or
#       (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
#       discover the source code or non-literal aspects (such as the underlying structure,
#       sequence, organization, ideas, or algorithms) of the Software.
#
#       6. If you create a derivative work and/or improvement of any Software, you hereby
#       irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
#       royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
#       right and license to reproduce, use, make, have made, import, distribute, sell,
#       offer for sale, create derivative works of, modify, translate, publicly perform
#       and display, and otherwise commercially exploit such derivative works and improvements
#       (as applicable) in conjunction with Wiliot's products and services.
#
#       7. You represent and warrant that you are not a resident of (and will not use the
#       Software in) a country that the U.S. government has embargoed for use of the Software,
#       nor are you named on the U.S. Treasury Department’s list of Specially Designated
#       Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
#       You must not transfer, export, re-export, import, re-import or divert the Software
#       in violation of any export or re-export control laws and regulations (such as the
#       United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
#       and use restrictions, all as then in effect
#
#     THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
#     OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
#     WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
#     QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
#     IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
#     ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
#     OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
#     FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
#     (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
#     (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
#     CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
#     (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
#     (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
#  """
import json
import logging
import tkinter
from tkinter.font import Font

import numpy
from os import remove
from os import makedirs, mkdir
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pygubu
from threading import Thread, Lock
from time import sleep
import time
import csv
import datetime
from wiliot_testers.sample.configs_gui import ConfigsGui, OUTPUT_DIR, CONFIGS_DIR
from wiliot_testers.sample.com_connect import ComConnect, GO, CONTINUE, CONNECT_HW, READ, SEND
from traceback import print_exc
from json import load, dump
import argparse
import sys
from os.path import isfile, abspath, dirname, join, isdir, exists
from wiliot_testers.utils.get_version import get_version
from wiliot_testers.tester_utils \
    import setLogger, changeFileHandler, removeFileHandler, CsvLog, HeaderType, TesterName, StreamToLogger
from wiliot_core import TagCollection, PacketList
from wiliot_core import check_user_config_is_ok, InlayTypes, WiliotDir
from wiliot_api import ManufacturingClient
from wiliot_testers.config.unusable_inlays import UnusableInlayTypes
from wiliot_testers.utils.upload_to_cloud_api import *
from wiliot_testers.utils.wiliot_external_ids import is_external_id_valid
from enum import Enum
from wiliot_testers.wiliot_tester_tag_result import FailBinSample

addToDictMutex = Lock()
calibMutex = Lock()
recvDataMutex = Lock()
timerMutex = Lock()
mutex = Lock()

STOP = 'Stop'
FINISH = 'Finish'

RAW = 'raw'
TIME = 'time'

DEF_NUM_OF_TAGS = 2

CLOUD_TIMEOUT_POST = 10
CLOUD_TIMEOUT_RESOLVE = 2

SGTIN_PREFIX_DEFAULT = '(01)00850027865010(21)'

RSSI_THR_DEFAULT = 80


class SettingModeOptions(Enum):
    SEND = 'Send to Cloud'
    SEND_TEST = 'Send to Cloud [TEST]'
    OFFLINE = 'Offline Mode'
    CALIB = 'Test Calibration'
    CALIB_OFFLINE = 'Test Calibration [OFFLINE]'


class SampleException(Exception):
    pass


class FailureCodeSampleTest(Enum):
    NONE = 0
    PASS = 1  # Pass
    NO_RESPONSE = 3
    NO_TBP = 5
    HIGH_TBP_AVG = 7
    NOT_COMPLETED = 9


class SampleTest(object):
    goButtonState = CONNECT_HW
    stopButtonState = STOP
    client = None
    comConnect = None
    configsGui = None
    comTtk = None
    configsTtk = None
    testBarcodesThread = None
    finishThread = None
    finishTestThread = None
    closeChambersThread = None
    gatewayDataThread = None
    timerThread = None
    testFinished = True
    post_data = True
    wiliotTags = False
    forceCloseRequested = False
    closeRequested = False
    testGo = False
    stopTimer = False
    closeListener = False
    is_test_pass = False
    testConfig = ''
    reel_id = ''
    gtin = ''
    testDir = ''
    owner = ''
    station_name = ''
    pywiliot_version = ''
    testTime = 0
    # tagsCount = 0
    testStartTime = 0
    sleep = 0
    cur_atten = 0
    test_num = 0
    defaultDict = {}
    dataBaseDict = {}
    runDataDict = {}
    params = {}
    test_barcodes = {}
    barcodes_read = {}
    tagsFinished = {}
    packets_dict = {}
    bad_advas = []
    advas_dict = {}
    total_bad_advas = []
    add_to_dict_threads = []
    unknown_packets = PacketList()
    antenna = ''
    low = 0
    high = 0
    step = 1
    n_repetitions = 1
    logger = logging.getLogger('sample')

    # numOfTags = ''
    multiTag = TagCollection()

    def __init__(self, calib=None, environment='prod', post_data=True, offline=False):

        self.test_is_running = False
        self.set_logger()
        self.calib = calib
        self.offline = offline
        self.offline_tag_index = 0
        self.environment = environment
        self.post_data = post_data
        if self.offline:
            self.post_data = False

        self.pywiliot_version = get_version()
        self.logger.info(f'PyWiliot version: {self.pywiliot_version}')

        if isfile(abspath(join(CONFIGS_DIR, '.defaults.json'))):
            with open(abspath(join(CONFIGS_DIR, '.defaults.json')), 'r') as defaultComs:
                self.defaultDict = load(defaultComs)

        self.popup_login()

        self.builder = builder = pygubu.Builder()

        self.comConnect = ComConnect(top_builder=builder, new_tag_func=self.add_tag_to_test,
                                     update_go=self.update_go_state, default_dict=self.defaultDict, logger=self.logger)
        self.update_data()
        if not self.offline:
            _, api_key, is_success = check_user_config_is_ok(env='prod', owner_id=self.owner)
            if not is_success:
                self.logger.warning('invalid User credential')
                return
            self.client = ManufacturingClient(api_key=api_key, logger_='root', env='prod')
        self.configsGui = ConfigsGui(top_builder=builder)
        self.logger.info(f'Sample test is up and running')
        self.ttk = Tk()
        self.var_option = tkinter.IntVar(0)

    def set_logger(self):
        formatter = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)
        wiliot_dir = WiliotDir()
        logger_path = abspath(join(wiliot_dir.get_wiliot_root_app_dir(), 'sample_test'))
        if not isdir(logger_path):
            os.mkdir(logger_path)
        logger_path = abspath(join(logger_path, 'logs'))
        if not isdir(logger_path):
            os.mkdir(logger_path)
        logger_name = 'sample_test_{}.log'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        self.logger_path = abspath(join(logger_path, logger_name))
        file_handler = logging.FileHandler(self.logger_path, mode='a')
        file_formatter = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', '%H:%M:%S')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)
        self.logger.setLevel(logging.INFO)

    def gui(self):
        self.logger.info(f'Sample test setting the GUI')
        self.set_gui()
        self.logger.info(f'Sample test GUI is running')
        self.ttk.mainloop()

    def set_gui(self):
        uifile = abspath(join(abspath(dirname(__file__)), 'utils', 'sample_test.ui'))
        self.builder.add_from_file(uifile)

        img_path = abspath(join(abspath(dirname(__file__)), ''))
        self.builder.add_resource_path(img_path)
        img_path = abspath(join(abspath(dirname(__file__)), 'utils'))
        self.builder.add_resource_path(img_path)

        self.ttk.title("Wiliot Sample Test")
        self.mainWindow = self.builder.get_object('mainwindow', self.ttk)
        self.ttk.protocol("WM_DELETE_WINDOW", self.close)
        self.builder.connect_callbacks(self)

        self.builder.get_object('reelId').bind("<Key>", self.get_reel_id)
        list_box = self.builder.get_object('scanned')
        scrollbar = self.builder.get_object('scrollbar1')
        list_box.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=list_box.yview)
        self.builder.get_object('scrollbar1').set(self.builder.get_object('scanned').index(ACTIVE),
                                                  self.builder.get_object('scanned').index(END))
        self.logger.info(f'checking available serial connection')
        self.comConnect.choose_com_ports()
        self.logger.info(f'setting up gui defaults')
        self.set_gui_defaults()

        self.builder.connect_callbacks(self)

        self.settings_combobox = self.builder.get_object('settings_combobox', self.ttk)
        self.settings_combobox.configure(values=[v.value for v in SettingModeOptions])
        self.settings_combobox.set(SettingModeOptions.SEND.value)
        self.settings_combobox.bind('<<ComboboxSelected>>', self.on_dropdown_change)

    def on_dropdown_change(self, event=None):

        selected_label = self.settings_combobox.get()

        self.post_data = False
        self.calib = False
        self.offline = False

        if selected_label in [SettingModeOptions.SEND.value, SettingModeOptions.SEND_TEST.value]:  # Send to Cloud
            self.post_data = True
            self.logger.info('Send to cloud was changed to True')
        elif selected_label == SettingModeOptions.CALIB.value:  # Test Calibration
            self.calib = True
            self.logger.info('Calibration mode was changed to True')
        elif selected_label == SettingModeOptions.OFFLINE.value:  # Offline Mode
            self.offline = True
            self.logger.info('Offline mode was changed to True')
        elif selected_label == SettingModeOptions.CALIB_OFFLINE.value:  # Offline Mode
            self.offline = True
            self.calib = True
            self.logger.info('Calibration + Offline mode were changed to True')

        # Update the environment
        self.environment = 'prod' if selected_label != SettingModeOptions.SEND_TEST.value else 'test'
        self.logger.info(f'Environment set to {self.environment}')

    def choose_param(self, *args):
        var = args[0].widget['style'].split('.')[0]
        if self.builder.tkvariables.get(var) is not None:
            value = self.builder.get_object(var).get()
            if var not in self.defaultDict.keys():
                self.defaultDict[var] = []
            if value in self.defaultDict[var]:
                self.defaultDict[var].pop(self.defaultDict[var].index(value))
            self.defaultDict[var].insert(0, value)

    def go(self):
        if self.finishThread is not None and self.finishThread.is_alive():
            self.finishThread.join()
        self.goButtonState = goButtonState = self.builder.tkvariables.get('go').get()
        self.builder.get_object('stop')['state'] = 'disabled'
        self.builder.get_object('settings_combobox')['state'] = 'disabled'
        self.update_params_state(state='disabled', group=GO)
        self.builder.get_variable('forceGo').set('0')
        recvDataMutex.acquire()
        self.forceCloseRequested = False
        recvDataMutex.release()
        if goButtonState == CONNECT_HW:
            self.connectThread = Thread(target=self.connect_all, args=([False]))
            self.connectThread.start()
        elif goButtonState == READ:
            self.builder.get_object('settings_combobox')['state'] = 'disabled'
            if self.stopButtonState == SEND:
                self.remove_barcodes()
                self.stopButtonState = FINISH
                self.builder.tkvariables.get('stop').set(FINISH)
            indexes = self.get_missing_ids_chambers()
            if self.offline:
                self.update_go_state()
            else:
                self.testBarcodesThread = Thread(target=self.read_scanners_barcodes, args=([indexes]))
                self.testBarcodesThread.start()
        elif goButtonState == GO:
            self.numOfPackets = 0
            self.offline_tag_index = 0
            self.multiTag = TagCollection()
            self.total_bad_advas = []
            self.bad_advas = []
            self.advas_dict = {}
            self.builder.tkvariables.get('stop').set(STOP)
            self.stopButtonState = STOP
            # self.numOfTags = int(self.builder.tkvariables.get('numTags').get())
            self.testId = testId = time.time()
            self.testName = testName = self.builder.get_object('testName').get()
            # self.operator = operator = self.builder.get_object('operator').get()
            if not isdir(abspath(join(OUTPUT_DIR, testName))):
                makedirs(abspath(join(OUTPUT_DIR, testName)))
            self.testDir = testDir = datetime.datetime.fromtimestamp(testId).strftime('%d%m%y_%H%M%S')
            mkdir(abspath(join(OUTPUT_DIR, testName, testDir)))
            self.common_run_name = common_run_name = self.reel_id + '_' + testDir
            self.test_log_file = abspath(join(OUTPUT_DIR, testName, testDir, f'{common_run_name}.log'))
            changeFileHandler(self.logger, self.test_log_file, append_handler=True)
            self.logger.info(f'Starts new test: {common_run_name}')
            removeFileHandler(self.logger, self.logger_path)
            self.update_params()
            self.testStartTime = time.time()
            self.comConnect.read_temperature_sensor()  # read temperature
            if self.calib:
                self.calibModeThread = Thread(target=self.calib_thread, args=())
                self.calibModeThread.start()
                self.calibModeThread.join()
                self.calibModeThread = Thread(target=self.calib_mode, args=())
                self.calibModeThread.start()
            else:
                self.sendCommandThread = Thread(target=self.send_gw_commands, args=())
                self.sendCommandThread.start()

        elif goButtonState == CONTINUE:
            self.builder.tkvariables.get('stop').set(STOP)
            self.stopButtonState = STOP
            self.total_bad_advas.append(x for x in self.bad_advas if x not in self.total_bad_advas)
            self.bad_advas = []
            self.advas_dict = {}
            self.sendCommandThread = Thread(target=self.send_gw_commands, args=())
            self.sendCommandThread.start()

    def calib_thread(self):
        self.popup_calib()

    def read_scanners_barcodes(self, indexes):
        self.comConnect.read_scanners_barcodes(indexes)
        # self.update_params_state(state='normal', group=CONTINUE)

    def connect_all(self, gui=True):
        self.comConnect.connect_all(gui=gui)
        self.builder.tkvariables.get('go').set(READ)
        # self.update_params_state(state='normal', group=READ)
        self.builder.get_object('read_qr')['state'] = 'normal'
        self.builder.get_object('reelId')['state'] = 'normal'
        self.builder.get_object('connect')['state'] = 'normal'

    def add_tag_to_test(self, cur_id, reel_id, scanner_index=0, add_to_test=False):
        mutex.acquire()
        if cur_id not in self.test_barcodes.keys() and cur_id not in self.barcodes_read.keys() and add_to_test:
            self.barcodes_read[cur_id] = {'chamber': scanner_index,
                                          'packets': [],
                                          'reel': self.reel_id,
                                          'ext ID': cur_id,
                                          'ttfp': -1,
                                          'tbp': -1,
                                          'rssi': -1,
                                          'adv_address': [],
                                          'packetList': PacketList()}
            # self.test_barcodes[cur_id] = scanner_index
            self.builder.get_object('scanned').insert(END, f'{cur_id}, {scanner_index}')
            mutex.release()
        else:
            mutex.release()
            self.comConnect.popup_message(f'Tag {cur_id} in chamber {scanner_index} already read.', title='Warning',
                                          log='warning')
            return False

        if self.reel_id != '' and self.reel_id != reel_id and self.wiliotTags:
            self.comConnect.popup_message('Tag reel different from test reel.', title='Warning', log='error')

        return True

    def update_go_state(self, force_go=False):
        if (self.comConnect.get_num_of_barcode_scanners() == len(self.barcodes_read.keys()) or force_go) and \
                len(self.test_barcodes.keys()) > 0:
            self.builder.tkvariables.get('go').set(CONTINUE)
            self.update_params_state(state='normal', group=CONTINUE)
        elif self.comConnect.get_num_of_barcode_scanners() == len(self.barcodes_read.keys()) or force_go:
            self.builder.tkvariables.get('go').set(GO)
            self.update_params_state(state='normal', group=GO)
        else:
            self.builder.tkvariables.get('go').set(READ)
            self.update_params_state(state='normal', group=READ)
        # self.top_builder.get_object('go')['state'] = 'normal'

    def get_missing_ids_chambers(self):
        indexes = list(range(self.comConnect.get_num_of_barcode_scanners()))
        if len(self.barcodes_read.keys()) > 0:
            used_indexes = [barcode['chamber'] for barcode in self.barcodes_read.values()]
            indexes = [index for index in indexes if index not in used_indexes]
        return indexes

    def force_go(self):
        """
        enable go in the GUI even if some of the chambers are empty
        """
        if self.builder.get_variable('forceGo').get() == '1':
            self.builder.get_object('forceGo')['state'] = 'disabled'
            self.builder.get_object('stop')['state'] = 'disabled'
            self.builder.get_object('go')['state'] = 'disabled'
            self.builder.get_object('add')['state'] = 'disabled'
            self.builder.get_object('remove')['state'] = 'disabled'
            self.builder.get_object('settings_combobox')['state'] = 'disabled'
            if self.closeChambersThread is not None and self.closeChambersThread.is_alive():
                self.closeChambersThread.join()
            self.closeChambersThread = Thread(target=self.force_go_close_chambers, args=())
            self.closeChambersThread.start()
        else:
            self.update_go_state()

    def force_go_close_chambers(self):
        indexes = self.get_missing_ids_chambers()
        self.comConnect.close_chambers(indexes)
        self.update_go_state(force_go=True)
        self.builder.get_object('forceGo')['state'] = 'normal'
        self.builder.get_object('stop')['state'] = 'normal'
        self.builder.get_object('go')['state'] = 'normal'

    def calib_mode(self):
        self.testFinished = False
        attenuations = numpy.arange(float(self.low), float(self.high) + float(self.step), float(self.step))
        n_rep = int(self.n_repetitions)
        for i in attenuations:
            if self.forceCloseRequested:
                break
            for j in range(n_rep):
                calibMutex.acquire()
                self.total_num_of_unique = 0
                self.offline_tag_index = 0
                self.avg_unique = 1
                self.cur_atten = i
                self.test_num = j
                self.advas_dict = {}
                self.tagsFinished = {}
                self.testGo = True
                if self.antenna.lower() == 'ble':
                    self.params['attenBle'] = self.cur_atten
                    self.dataBaseDict['attenBle[db]'] = self.cur_atten
                elif self.antenna.lower() == 'lora':
                    self.dataBaseDict['attenLoRa[db]'] = self.cur_atten
                    self.params['attenLoRa'] = self.cur_atten
                self.dataBaseDict['testNum'] = self.test_num
                self.params['testNum'] = self.test_num

                self.sendCommandThread = Thread(target=self.send_gw_commands, args=())
                self.sendCommandThread.start()
                self.sendCommandThread.join()
                sleep(5)
                if self.forceCloseRequested:
                    break

        calibMutex.acquire()
        self.calib_mode_post_process()
        self.comConnect.open_chambers()
        # self.builder.tkvariables.get('numTags').set(0)
        # self.builder.tkvariables.get('go').set(READ)
        # self.test_barcodes = {}
        # self.builder.get_object('connect')['state'] = 'normal'
        # self.builder.get_object('read_qr')['state'] = 'normal'
        calibMutex.release()
        self.finish_test(post_data=False, reset_tester=True, post_process=False)
        self.comConnect.popup_message('Sample Test - Calib Mode Finished running.', title='Info', log='info')

    def calib_mode_post_process(self):
        common_run_name = self.reel_id + '_' + self.testDir
        unique_valid = []
        full_test_dir = abspath(join(OUTPUT_DIR, self.testName, self.testDir))
        is_first = True
        for atten, runData in self.packets_dict.items():
            for extId, data in runData.items():
                if data['packetList'].size() > 0:
                    packet_df = data['packetList'].get_df(add_sprinkler_info=True)
                    packet_df.insert(loc=len(packet_df.columns), column='status', value='PASSED')
                    packet_df.insert(loc=len(packet_df.columns), column='attenuation', value=float(atten.split('_')[0]))
                    packet_df.insert(loc=len(packet_df.columns), column='test_num', value=int(atten.split('_')[1]))
                    packet_df.insert(loc=len(packet_df.columns), column='external_id', value=extId)
                    packet_df.insert(loc=len(packet_df.columns), column='chamber', value=data['chamber'])
                    data['packetList'].export_packet_df(
                        packet_df=packet_df,
                        path=abspath(join(full_test_dir, f'{common_run_name}@packets_data_calib_mode.csv')),
                        append=not is_first)
                    is_first = False

                unique_valid.append({
                    'adv_address': data['adv_address'],
                    'tbp': data['tbp'],
                    'ttfp': data['ttfp'],
                    'ext ID': data['ext ID'],
                    'reel': data['reel'],
                    'attenuation': float(atten.split('_')[0]),
                    'test_num': int(atten.split('_')[1]),
                    'chamber': data['chamber']
                })

        if len(unique_valid):
            with open(abspath(join(full_test_dir, f'{common_run_name}@unique_data.csv')), 'w+',
                      newline='') as new_tagsCsv:
                writer = csv.DictWriter(new_tagsCsv, fieldnames=list(unique_valid[0].keys()))
                writer.writeheader()
                writer.writerows(unique_valid)

        self.barcodes_read = {}
        self.test_barcodes = {}
        self.builder.get_object('scanned').delete(0, END)

    def calib_mode_clean_barcodes(self):
        old_barcodes = self.barcodes_read.copy()
        self.barcodes_read = {}
        self.test_barcodes = {}
        self.builder.get_object('scanned').delete(0, END)
        for tag in old_barcodes.values():
            self.add_tag_to_test(tag['ext ID'], tag['reel'], tag['chamber'], add_to_test=True)

    def stop(self):
        """
        stop the test and run post process
        """
        if self.stopButtonState == STOP:
            self.forceCloseRequested = True

        elif self.stopButtonState == FINISH:
            # self.numOfTags = len(self.test_barcodes.keys())
            # self.finishThread = Thread(target=self.iteration_finished, args=([True]))
            # self.finishThread.start()
            self.builder.get_object('scanned').delete(0, END)
            self.builder.tkvariables.get('stop').set(SEND)
            self.stopButtonState = SEND
            for barcode in list(self.test_barcodes.keys()):
                self.builder.get_object('scanned').insert(END, barcode)

        elif self.stopButtonState == SEND:
            if not self.is_test_completed() and 'controlLimits' in self.defaultDict.keys():
                control_limits = self.defaultDict['controlLimits'][self.defaultDict['controlLimitsTestNum']]
                self.update_values_for_control_limits(control_limits=control_limits)
                is_pass, fail_str, complete_sub_test, fail_bin = self.check_control_limits()
                self.reset_values_for_control_limits(control_limits=control_limits)
                if not is_pass or not complete_sub_test:
                    send_anyway = popup_yes_no(f'Test was FAILED!! are you sure you want to finish the test and '
                                               f'send data to the cloud?')
                    if not send_anyway:
                        self.logger.info('User decide to keep testing')
                        return
            self.builder.get_object('go')['state'] = 'disabled'
            self.builder.get_object('stop')['state'] = 'disabled'
            self.builder.get_object('forceGo')['state'] = 'disabled'
            self.builder.get_object('add')['state'] = 'disabled'
            self.builder.get_object('remove')['state'] = 'disabled'
            self.finishThread = Thread(target=self.finish, args=())
            self.finishThread.start()

    def add(self):
        """
        add manually tag to the list
        """
        new_tag = self.builder.tkvariables.get('addTag').get()
        if (self.builder.tkvariables.get('stop').get() != SEND or len(new_tag.split(',')) == 2) and not \
                new_tag.split(',')[0].strip() in self.barcodes_read.keys():
            # self.builder.get_object('scanned').insert(END, new_tag)
            # self.barcodes_read[new_tag.split(',')[0].strip()] = new_tag.split(',')[1].strip()
            if self.builder.tkvariables.get('stop').get() == SEND:
                self.builder.get_object('scanned').delete(0, END)
                self.remove_barcodes()
                self.stopButtonState = FINISH
                self.builder.tkvariables.get('stop').set(FINISH)

            if len(new_tag.split(',')) < 2:
                self.comConnect.popup_message(f'Missing chamber index, add chamber index after a comma.', title='Error',
                                              log='error')
                return
            cur_id = new_tag.split(',')[0].strip()
            scan_index = int(new_tag.split(',')[1].strip())
            if 0 < self.comConnect.get_num_of_barcode_scanners() < (scan_index + 1):
                self.comConnect.popup_message(f'Chamber number {scan_index} not exists.', title='Error', log='error')
                return

            barcodes = self.builder.get_object('scanned').get(0, END)
            if any([barcode for barcode in barcodes if int(barcode.split()[1].strip()) == scan_index]):
                self.comConnect.popup_message(f'Chamber {scan_index} tag already scanned.', title='Error', log='error')
                return
            # logger.info(scan_index)

            self.builder.tkvariables.get('addTag').set('')
            popup_thread = Thread(target=self.comConnect.popup_message,
                                  args=('Chambers are closing!!\nWatch your hands!!!',
                                        'Warning', ("Helvetica", 18), 'warning'))
            popup_thread.start()
            popup_thread.join()
            self.add_tag_to_test(cur_id, self.reel_id, scan_index, add_to_test=True)
            chambers = self.comConnect.get_chambers()
            if len(chambers) > scan_index and chambers[scan_index] is not None:
                chambers[scan_index].close_chamber()
            self.update_go_state()
        else:
            self.builder.get_object('scanned').insert(END, new_tag)
            self.builder.tkvariables.get('addTag').set('')

    def remove(self):
        """
        remove tag read from the list
        """
        tag = self.builder.get_object('scanned').get(ACTIVE)
        tags = list(self.builder.get_object('scanned').get(0, END))
        tag_index = tags.index(tag)
        self.builder.get_object('scanned').delete(tag_index, tag_index)
        tags.pop(tag_index)
        self.builder.tkvariables.get('addTag').set(tag)
        if self.stopButtonState != SEND:
            self.barcodes_read.pop(tag.split(',')[0].strip())
            self.comConnect.open_chambers(indexes=[int(tag.split(',')[1].strip())])
            self.update_go_state()

    def update_params_state(self, state='disabled', group=GO):
        if state == 'disabled' or group == READ:
            self.builder.get_object('connect')['state'] = state

            if len(self.test_barcodes.keys()) == 0:
                self.builder.get_object('read_qr')['state'] = state
                self.builder.get_object('reelId')['state'] = state

            if self.reel_id != '':
                self.builder.get_object('go')['state'] = state
                self.builder.get_object('add')['state'] = state
                self.builder.get_object('remove')['state'] = state
                self.builder.get_object('addTag')['state'] = state
                self.builder.get_object('stop')['state'] = state
                self.builder.get_object('forceGo')['state'] = state
            self.builder.get_object('settings_combobox')['state'] = state

        if state == 'disabled' or group == GO:
            self.builder.get_object('configs')['state'] = state
            self.builder.get_object('test_config')['state'] = state
            self.builder.get_object('testName')['state'] = state
            self.builder.get_object('operator')['state'] = state
            self.builder.get_object('inlay')['state'] = state
            self.builder.get_object('surface')['state'] = state
            self.builder.get_object('settings_combobox')['state'] = state

        if state == 'disabled' or group == CONTINUE or group == GO:
            self.builder.get_object('connect')['state'] = state
            self.builder.get_object('go')['state'] = state
            self.builder.get_object('add')['state'] = state
            self.builder.get_object('remove')['state'] = state
            self.builder.get_object('addTag')['state'] = state
            self.builder.get_object('settings_combobox')['state'] = state
            self.builder.get_object('forceGo')['state'] = 'disabled'

            if len(self.test_barcodes.keys()) == 0:
                self.builder.get_object('read_qr')['state'] = state
                self.builder.get_object('reelId')['state'] = state

        if state == 'disabled':
            self.builder.get_object('read_qr')['state'] = state
            self.builder.get_object('reelId')['state'] = state

    def set_gui_defaults(self):
        configs = self.configsGui.get_configs()
        self.builder.get_object('test_config')['values'] = \
            [key for key, item in configs.items() if isinstance(item, dict)]

        if 'testName' in self.defaultDict.keys():
            self.builder.get_object('testName')['values'] = self.defaultDict['testName']
            self.builder.get_object('testName').set(self.defaultDict['testName'][0])

        if 'operator' in self.defaultDict.keys():
            self.builder.get_object('operator')['values'] = self.defaultDict['operator']
            self.builder.get_object('operator').set(self.defaultDict['operator'][0])

        self.builder.get_object('inlay')['values'] = tuple(
            name for name in InlayTypes._member_names_ if name not in UnusableInlayTypes.__members__)
        if 'inlay' in self.defaultDict.keys():
            self.builder.get_object('inlay').set(self.defaultDict['inlay'][0])

        if 'surface' in self.defaultDict.keys():
            self.builder.get_object('surface')['values'] = self.defaultDict['surface']
            self.builder.get_object('surface').set(self.defaultDict['surface'][0])
        if 'tester_hw' in self.defaultDict.keys():
            self.builder.get_object('tester_hw_ver')['state'] = 'enabled'
            self.builder.get_object('tester_hw_ver').delete(0, END)
            self.builder.get_object('tester_hw_ver').insert(0, self.defaultDict['tester_hw']['version'])
            self.builder.get_object('tester_hw_ver')['state'] = 'disabled'
            self.builder.get_object('tester_hw_desc')['state'] = 'enabled'
            self.builder.get_object('tester_hw_desc').delete(0, END)
            self.builder.get_object('tester_hw_desc').insert(0, self.defaultDict['tester_hw']['description'])
            self.builder.get_object('tester_hw_desc')['state'] = 'disabled'
        # if 'numOfTags' in self.defaultDict.keys():
        # self.builder.tkvariables.get('numTags').set(self.defaultDict['numOfTags'])
        # else:
        # self.builder.tkvariables.get('numTags').set(DEF_NUM_OF_TAGS)
        self.builder.tkvariables.get('numTags').set(0)

        if 'config' in self.defaultDict.keys():
            self.testConfig = self.defaultDict['config']
        else:
            self.testConfig = ''
        self.builder.get_object('test_config').set(self.testConfig)
        self.configsGui.set_default_config(self.testConfig)
        self.configsGui.set_params(self.testConfig)

    def open_configs(self):
        """
        open Configs GUI
        """
        if self.configsGui is not None and not self.configsGui.is_gui_opened():
            self.configsTtk = Toplevel(self.ttk)
            self.ttk.eval(f'tk::PlaceWindow {str(self.configsTtk)} center')
            self.configsGui.gui(self.configsTtk)

    def test_config(self, *args):
        """
        update the configs in Configs module according to the main GUI
        """
        self.configsGui.config_set(self.builder.get_object('test_config').get())

    def open_com_ports(self):
        """
        open ComConnect GUI
        """
        if self.comConnect is not None and not self.comConnect.is_gui_opened():
            self.comTtk = Toplevel(self.ttk)
            self.ttk.eval(f'tk::PlaceWindow {str(self.comTtk)} center')
            self.comConnect.gui(self.comTtk)

    def read_qr(self):
        barcode, reel = self.comConnect.read_barcode()
        if barcode is None:
            read_qr_thread = Thread(target=self.comConnect.popup_message, args=(
                [f'Error reading external ID, try repositioning the tag.', 'Error', ("Helvetica", 10), 'error']))
            read_qr_thread.start()
            read_qr_thread.join()
            if not self.calib:
                return

        if reel is not None:
            reel_id = self.builder.tkvariables.get('reelId')
            reel_id.set(reel)
            self.reel_id = reel

        if 'config' in self.defaultDict.keys():
            self.testConfig = self.defaultDict['config']
        else:
            self.testConfig = []

        self.builder.get_object('reelId').unbind("<Key>")
        self.update_params_state(state='normal', group=GO)
        self.builder.get_object('forceGo')['state'] = 'normal'

    def get_reel_id(self, *args):
        reel = self.builder.tkvariables.get('reelId').get()
        if reel.strip() != '' and (str(args[0].type) != 'KeyPress' or args[0].keysym == 'Return'):
            self.reel_id = reel
            self.update_params_state(state='normal', group=GO)
            self.builder.get_object('reelId').unbind("<Key>")
            self.builder.get_object('forceGo')['state'] = 'normal'

    def update_params(self):
        self.runDataDict = {}
        self.dataBaseDict = {}
        self.params = params = self.configsGui.get_params()
        self.testConfig = self.defaultDict['config'] = self.builder.get_object('test_config').get()

        self.dataBaseDict['timestamp'] = datetime.datetime.fromtimestamp(self.testId).strftime('%d/%m/%y %H:%M:%S')
        self.dataBaseDict['tested'] = self.builder.get_object('numTags').get()
        self.dataBaseDict['channel'] = params['channel']
        self.dataBaseDict['externalId'] = self.comConnect.get_reel_external()
        if 'sleep' in params.keys():
            self.sleep = int(params['sleep'])
        else:
            self.sleep = 0
        self.testTime = float(params['testTime'])

        self.runDataDict['runStartTime'] = self.dataBaseDict['runStartTime'] = time.strftime('%d/%m/%y %H:%M:%S')
        self.runDataDict['antennaType'] = self.dataBaseDict['antennaType'] = params['antennaType']
        self.runDataDict['bleAttenuation'] = self.dataBaseDict['attenBle[db]'] = params['attenBle']
        self.runDataDict['loraAttenuation'] = self.dataBaseDict['attenLoRa[db]'] = params['attenLoRa']
        self.runDataDict['energizingPattern'] = self.dataBaseDict['energizing'] = params['pattern']
        self.runDataDict['testTime'] = self.dataBaseDict['testTime[sec]'] = params['testTime']
        self.runDataDict['inlay'] = self.dataBaseDict['inlay'] = self.builder.get_object('inlay').get()
        self.runDataDict['surface'] = self.dataBaseDict['surface'] = self.builder.get_object('surface').get()
        self.runDataDict['testerStationName'] = self.station_name
        self.runDataDict['commonRunName'] = self.common_run_name
        self.runDataDict['testerType'] = 'sample'
        self.runDataDict['gwVersion'] = self.dataBaseDict['gwVersion'] = self.comConnect.get_gw_version()
        self.runDataDict['operator'] = self.dataBaseDict['operator'] = self.builder.get_object('operator').get()
        self.runDataDict['pyWiliotVersion'] = self.dataBaseDict['pyWiliotVersion'] = self.pywiliot_version
        self.runDataDict['testTimeProfilePeriod'] = self.dataBaseDict['testTimeProfilePeriod'] = params['tTotal']
        self.runDataDict['testTimeProfileOnTime'] = self.dataBaseDict['testTimeProfileOnTime'] = params['tOn']
        self.runDataDict['numChambers'] = self.dataBaseDict[
            'numChambers'] = self.comConnect.get_num_of_barcode_scanners()
        self.runDataDict['timeProfile'] = '[{}, {}]'.format(params['tOn'], params['tTotal'])
        self.runDataDict['txPower'] = 'max'

        if 'controlLimits' in self.defaultDict.keys():
            self.logger.info('reset control limits')
            self.runDataDict['controlLimits'] = self.defaultDict['controlLimits'].copy()
            self.defaultDict['controlLimitsTestNum'] = 0
            self.params['tag_tbp_min'] = self.defaultDict['controlLimits'][0]['tag_tbp_min']
            self.params['tag_tbp_max'] = self.defaultDict['controlLimits'][0]['tag_tbp_max']

        if 'rssiThresholdSW' in self.defaultDict.keys():
            try:
                self.params['rssi_threshold'] = int(self.defaultDict['rssiThresholdSW'])
            except Exception as e:
                self.logger.warning(f'could not convert "rssiThresholdSW" field in ,default to number: '
                                    f'{self.defaultDict["rssiThresholdSW"]} due to {e}. '
                                    f'rssi threshold is set to default: {RSSI_THR_DEFAULT}')
        else:
            self.params['rssi_threshold'] = self.defaultDict['rssiThresholdSW'] = RSSI_THR_DEFAULT

        self.runDataDict['hwVersion'] = self.defaultDict['tester_hw']['version'] \
            if 'tester_hw' in self.defaultDict.keys() else ''
        self.runDataDict['sub1gFrequency'] = params['EmulateSurfaceValue']

        self.update_data()

    def send_gw_commands(self):
        """
        send commands to the GW and start the packet listener
        """
        if self.sleep > 0:
            for i in range(self.sleep):
                sleep(1)
                if i % 3 == 0:
                    print('.', end='')
            print()
        self.recv_data_from_gw()
        self.testFinished = False

    def stop_state(self):
        self.builder.get_object('stop')['state'] = 'normal'

    def recv_data_from_gw(self):
        self.tagsFinished = {}
        self.testGo = True
        self.startTime = self.comConnect.get_gw_time()
        self.logger.info(f'Tags in the test: {",".join(list(self.barcodes_read.keys()))}')
        gw_passed = self.comConnect.send_gw_app(self.params)
        if not gw_passed:
            self.comConnect.popup_message(f'Error sending GW commands.', 'Error', ("Helvetica", 10), 'error')
            self.update_params_state(state='normal', group=CONTINUE)
            return
        self.gatewayDataThread = Thread(target=self.stop_state(), args=())
        self.gatewayDataThread.start()
        last_time = time.time()
        self.targetTime = last_time + self.testTime
        if self.timerThread is not None:
            self.timerThread.join()
        self.timerThread = Thread(target=self.timer_count_down, args=([self.targetTime]))
        self.timerThread.start()
        self.sync_thread = Thread(target=self.threads_sync, args=())
        self.sync_thread.start()
        packets_list = PacketList()
        recvDataMutex.acquire()
        while True:
            sleep(0.001)
            try:
                if self.closeListener:
                    self.logger.info("DataHandlerProcess Stop")
                    break

                if self.comConnect.is_gw_data_available():

                    gw_data = self.comConnect.get_data()

                    packets_list.__add__(gw_data)

                    cur_time = time.time()
                    if cur_time - last_time > 2 and len(packets_list) > 0:
                        temp_thread = Thread(target=self.add_to_packet_dict, args=([packets_list]))
                        # temp_thread.start()
                        addToDictMutex.acquire()
                        self.add_to_dict_threads.append(temp_thread)
                        addToDictMutex.release()
                        packets_list = PacketList()
                        last_time = cur_time

            except BaseException:
                print_exc()
                pass
        self.comConnect.read_temperature_sensor()  # read temperature
        self.comConnect.cancel_gw_commands()
        timerMutex.acquire()
        self.stopTimer = True
        timerMutex.release()
        # self.tagsCount += len(self.barcodes_read.keys())
        recvDataMutex.release()
        self.sync_thread.join()
        self.closeListener = False
        if not self.calib:
            self.builder.get_object('stop')['state'] = 'disabled'
            self.finishIterThread = Thread(target=self.iteration_finished, args=())
            self.finishIterThread.start()
        elif self.calib:
            self.handle_unknown_packets()
            self.unknown_packets = PacketList()
            self.post_process_iteration()

            self.packets_dict[f'{self.cur_atten}_{self.test_num}'] = {}
            self.packets_dict[f'{self.cur_atten}_{self.test_num}'].update(self.barcodes_read)
            self.calib_mode_clean_barcodes()
            calibMutex.release()

    def threads_sync(self):
        while not self.closeRequested and not self.forceCloseRequested and time.time() < self.targetTime:
            if len(self.add_to_dict_threads) > 0:
                addToDictMutex.acquire()
                thread = self.add_to_dict_threads.pop()
                addToDictMutex.release()
                thread.start()
                thread.join()
            sleep(0.1)
        self.closeRequested = False
        self.closeListener = True
        self.add_to_dict_threads = []

    def timer_count_down(self, target_time):
        """
        count down the test time
        """
        while True:
            if self.stopTimer:
                timerMutex.acquire()
                self.stopTimer = False
                timerMutex.release()
                break
            timer = int(target_time - time.time())
            update_timer_thread = Thread(target=self.update_timer, args=([timer]))
            update_timer_thread.start()
            update_timer_thread.join()
            sleep(1)
        self.builder.tkvariables.get('testTime').set(str(int(self.testTime)))

    def update_timer(self, timer):
        """
        update timer value in the GUI
        :type timer: int
        :param timer: remaining time to the test
        """
        self.builder.tkvariables.get('testTime').set(str(timer))

    def add_to_packet_dict(self, packets, post_run=False):
        self.process_packets(packets, post_run=post_run)

    def check_rssi_threshold(self, packet_rssi):
        packet_rssi_list = packet_rssi.tolist()
        if not isinstance(packet_rssi_list, list):
            packet_rssi_list = [packet_rssi_list]
        return any([rssi <= self.params['rssi_threshold'] for rssi in packet_rssi_list])

    def process_packets(self, packets, post_run=False):
        for packet in packets:
            ext_id = ''
            adv_address = packet.packet_data['adv_address']
            self.numOfPackets += 1

            if not self.check_rssi_threshold(packet.gw_data['rssi']):
                self.logger.info(f'packet: {packet.get_packet_string()} was ignore due to high rssi')
                continue

            if adv_address in [x['adv_address'] for x in self.bad_advas]:
                continue

            elif adv_address in self.advas_dict.keys() and self.advas_dict[adv_address] is not None:
                ext_id = self.advas_dict[adv_address]

            else:
                print(packet.get_packet_string())
                full_data, success, is_valid = self.get_packet_ext_id(packet)

                if not success:
                    if not post_run:
                        self.unknown_packets.append(packet)
                        if adv_address not in self.advas_dict.keys():
                            self.logger.error(
                                f'Could not get external ID for adv_address {adv_address} '
                                f'from the cloud - saving data for post process')
                        self.advas_dict[adv_address] = None
                    else:
                        self.logger.error(
                            f'Could not get external ID for adv_address {adv_address} '
                            f'from the cloud - dumping packet')
                    continue

                ext_id = full_data['barcode'] if full_data['barcode'] in self.barcodes_read.keys() else full_data[
                    'cur_id']
                if ext_id is not None and ext_id not in self.barcodes_read.keys():
                    self.logger.info(
                        f'Tag with adv_address {adv_address} and external ID {full_data["cur_id"]} '
                        f'detected but not belong to the test.')
                    self.bad_advas.append({'adv_address': adv_address, 'external_id': full_data["cur_id"],
                                           'is_valid': is_valid})
                    continue

                self.advas_dict[adv_address] = ext_id

                if adv_address not in self.barcodes_read[ext_id]['adv_address']:
                    self.logger.info(
                        f'New Tag detected with adv_address {adv_address} and external ID {full_data["cur_id"]}.')
                    self.barcodes_read[ext_id]['adv_address'].append(adv_address)

            self.barcodes_read[ext_id]['packets'].append(packet.get_packet_string())
            self.barcodes_read[ext_id]['packetList'].append(packet.copy())

            if self.barcodes_read[ext_id]['packetList'].get_statistics()['tbp_min'] > 0 and not post_run:
                self.tagsFinished[ext_id] = True

            if len(self.tagsFinished.keys()) >= len(self.barcodes_read.keys()) and not post_run:
                self.closeRequested = True

    def iteration_finished(self, force_finish=False):
        self.testGo = False
        self.handle_unknown_packets()
        avg_tbp, avg_ttfp = self.post_process_iteration()
        self.test_barcodes = dict(list(self.test_barcodes.items()) + list(self.barcodes_read.items()))
        self.comConnect.open_chambers()

        all_answered = all([False for ext_id in self.barcodes_read.values() if len(ext_id['packets']) == 0])
        dup_adva = [extId for extId, tag in self.barcodes_read.items() if len(tag['adv_address']) > 1]
        adva_warning = len(dup_adva) > 0
        serial_warning = '' if all_answered or len(self.bad_advas) == 0 else 'Serialization warning!\n'
        serial_warning = serial_warning if not adva_warning else serial_warning + f'ADVA warning in tags: {dup_adva}\n'
        bg_color = None if all_answered or len(self.bad_advas) == 0 else 'yellow'
        bg_color = bg_color if not adva_warning else 'yellow'
        stat = ''
        if avg_ttfp != 0:
            stat = f'Average TTFP: {avg_ttfp:.3f} [sec]\n' + \
                   f'Average TBP: {avg_tbp:.3f} [msec]'
        else:
            stat = 'No packets received'

        self.finish_test()

        # read_tags = ''
        # if self.tagsCount < self.numOfTags and not force_finish:
        read_tags = '\nReplace tags and click on "Read"'

        finishThread = Thread(target=self.comConnect.popup_message, args=(f'{serial_warning}'
                                                                          f'{stat}'
                                                                          f'{read_tags}',
                                                                          'info',
                                                                          ("Helvetica", 10),
                                                                          'info',
                                                                          bg_color))
        finishThread.start()
        finishThread.join()

        self.update_params_state(state='normal', group=READ)

        self.builder.tkvariables.get('numTags').set(len(self.test_barcodes.keys()))
        self.builder.tkvariables.get('addTag').set('')
        self.builder.get_object('connect')['state'] = 'normal'
        self.builder.get_object('scanned').delete(0, END)
        self.builder.tkvariables.get('go').set(READ)
        self.builder.tkvariables.get('stop').set(FINISH)
        self.stopButtonState = FINISH

        self.barcodes_read = {}
        self.unknown_packets = PacketList()

    def remove_barcodes(self):
        final_barcodes = self.builder.get_object('scanned').get(0, END)
        self.builder.get_object('scanned').delete(0, END)
        test_barcodes = list(self.test_barcodes.keys()).copy()
        for barcode in test_barcodes:
            if barcode not in final_barcodes:
                self.test_barcodes.pop(barcode)

    def finish(self):
        self.remove_barcodes()
        self.finish_test(True, True)
        # self.finishTestThread = Thread(target=self.finish_test, args=([True, True]))
        # self.finishTestThread.start()

    def handle_unknown_packets(self):
        if self.unknown_packets.size() > 0:
            self.logger.info(f'Start handling unknown packets.')
            self.process_packets(self.unknown_packets, post_run=True)

    def post_process_iteration(self):
        tbp_count = 0
        ttfp_count = 0
        ttfp_avg = 0
        tbp_avg = 0

        for extId, tag in self.barcodes_read.items():
            stat = tag['packetList'].get_statistics()
            if 'ttfp' in stat.keys():
                tbp = stat['tbp_min']
                tbp = tbp if type(tbp).__name__ != 'str' else -1
                if tbp != -1:
                    tbp_avg = ((tbp_avg * tbp_count) + tbp) / (tbp_count + 1)
                    tbp_count += 1

                ttfp = stat['ttfp']
                ttfp_avg = ((ttfp_avg * ttfp_count) + ttfp) / (ttfp_count + 1)
                ttfp_count += 1
                self.barcodes_read[extId]['tbp'] = int(tbp)
                self.barcodes_read[extId]['ttfp'] = ttfp

                self.barcodes_read[extId]['rssi'] = float(stat["rssi_mean"])

        return tbp_avg, ttfp_avg

    def update_values_for_control_limits(self, control_limits):
        self.params['test_tbp_min'] = control_limits['test_tbp_min']
        self.params['test_tbp_max'] = control_limits['test_tbp_max']
        self.params['test_responding_min'] = control_limits['test_responding_min']
        self.params['test_valid_tbp'] = control_limits['test_valid_tbp']

    def reset_values_for_control_limits(self, control_limits):
        self.params['tag_tbp_min'] = control_limits['tag_tbp_min']
        self.params['tag_tbp_max'] = control_limits['tag_tbp_max']
        self.params['test_tbp_min'] = ''
        self.params['test_tbp_max'] = ''
        self.params['test_responding_min'] = ''
        self.params['test_valid_tbp'] = ''

    def update_control_limits(self, reset_test=False):
        next_test = False
        if 'controlLimits' in self.defaultDict.keys():
            self.logger.info(f'Check control limits for pre-defined phased-test:'
                             f'\nnumber of tested:{self.dataBaseDict["tested"]}')
            if reset_test and self.defaultDict['controlLimitsTestNum'] < len(self.defaultDict['controlLimits']) - 1:
                self.defaultDict['controlLimitsTestNum'] += 1
                self.logger.info(f'move to the next test: {self.defaultDict["controlLimitsTestNum"]}')

            control_limits = self.defaultDict['controlLimits'][self.defaultDict['controlLimitsTestNum']]

            if reset_test:
                self.reset_values_for_control_limits(control_limits=control_limits)

            elif self.dataBaseDict['tested'] >= int(control_limits['n_tags']):
                self.update_values_for_control_limits(control_limits=control_limits)
                next_test = True
        return next_test

    def is_test_completed(self):
        completed = True
        if 'controlLimits' in self.defaultDict.keys():
            control_limits = self.defaultDict['controlLimits'][-1]
            if self.dataBaseDict['tested'] < int(control_limits['n_tags']):
                completed = False
        return completed

    def check_control_limits(self):
        complete_sub_test = self.update_control_limits(reset_test=False)
        is_pass = True
        fail_str = ''
        fail_bin = FailureCodeSampleTest.PASS

        if self.params['test_responding_min'] != '':
            if float(self.dataBaseDict['responding[%]'].replace('%', '')) < float(self.params['test_responding_min']):
                is_pass = False
                fail_str += 'Failed % responding test. '
                if fail_bin == FailureCodeSampleTest.PASS:
                    fail_bin = FailureCodeSampleTest.NO_RESPONSE
        if self.params['test_valid_tbp'] != '':
            if float(self.dataBaseDict['validTbp[%]'].replace('%', '')) < float(self.params['test_valid_tbp']):
                is_pass = False
                fail_str += 'Failed % from the responded tags with valid tbp avg test. '
                if fail_bin == FailureCodeSampleTest.PASS:
                    fail_bin = FailureCodeSampleTest.NO_TBP
        if self.params['test_tbp_min'] != '' and self.params['test_tbp_max'] != '':
            if not int(self.params['test_tbp_min']) < float(
                    self.runDataDict['tbpAvg']) < int(self.params['test_tbp_max']):
                is_pass = False
                fail_str += 'Failed tbp avg test. '
                if fail_bin == FailureCodeSampleTest.PASS:
                    fail_bin = FailureCodeSampleTest.HIGH_TBP_AVG

        return is_pass, fail_str, complete_sub_test, fail_bin

    def finish_test(self, post_data=False, reset_tester=False, post_process=True):
        if post_process:
            pass_barcodes = self.post_process()
            pass_fail, fail_str, complete_sub_test, fail_bin = self.check_control_limits()
            if complete_sub_test and not pass_fail:
                self.update_control_limits(reset_test=True)

            dup_adva = [extId for extId, tag in self.test_barcodes.items() if len(tag['adv_address']) > 1]

            all_answered = all([False for ext_id in self.test_barcodes.values() if len(ext_id['packets']) == 0])
            serial_warning = (not all_answered) and len(self.total_bad_advas) != 0
            adva_warning = len(dup_adva) > 0
            serial_warning = '' if not serial_warning else 'Serialization warning!\n'
            serial_warning = serial_warning \
                if not adva_warning else serial_warning + f'ADVA warning in tags: {dup_adva}\n'
            bg_color = 'green'
            if 'controlLimits' not in self.defaultDict.keys():
                bg_color = 'green' if not (serial_warning or adva_warning) else 'yellow'
            bg_color = bg_color if pass_fail else 'red'
            pass_fail_str = 'Passed' if pass_fail else 'Failed'

            if 'controlLimits' in self.defaultDict.keys():
                if reset_tester and not complete_sub_test:
                    # user click on finish but test was not completed:
                    if fail_bin == FailureCodeSampleTest.PASS:
                        fail_bin = FailureCodeSampleTest.NOT_COMPLETED
                        pass_fail = False
                        pass_fail_str = 'Failed'
                        bg_color = 'red'
                if complete_sub_test and not reset_tester:
                    new_test_pass_str = 'SUCCESSFULLY COMPLETED THE TEST! please move to the next reel'
                    last_stage = self.is_test_completed()
                    new_test_fail_str = 'FAILED CURRENT TEST STAGE,' + \
                                        ' failed the reel' if last_stage else ' please continue to test the reel'
                    if not last_stage and not pass_fail:
                        bg_color = 'yellow'
                    self.comConnect.popup_message(f'Test {self.common_run_name} has {pass_fail_str}\n' +
                                                  f'{fail_str}\n' +
                                                  f'{new_test_pass_str if pass_fail else new_test_fail_str}'
                                                  f'\n' +
                                                  f'{serial_warning}'
                                                  f'Fail bin: {fail_bin.value}:{fail_bin.name}', title='Finished test',
                                                  bg=bg_color,
                                                  log='info')
            self.is_test_pass = pass_fail

            if reset_tester:
                self.comConnect.popup_message(f'Test {self.common_run_name} has {pass_fail_str}\n' +
                                              f'{fail_str}\n' +
                                              f'{serial_warning}' +
                                              f'Fail bin: {fail_bin.value}:{fail_bin.name}\n' +
                                              f'Average TTFP: {self.dataBaseDict["ttfpAvg"]} [sec]\n' +
                                              f'Average TBP: {self.dataBaseDict["tbpAvg"]} [msec]\n' +
                                              f'STD TBP: {self.dataBaseDict["tbpStd"]} [msec]\n' +
                                              f'Yield: {self.dataBaseDict["passed[%]"]}', title='Finished test',
                                              bg=bg_color,
                                              log='info')
                self.update_control_limits(reset_test=True)

            # log data:
            self.runDataDict['testStatus'] = pass_fail
            self.runDataDict['failBin'] = str(fail_bin.value) + str(self.defaultDict['controlLimitsTestNum']) \
                if 'controlLimitsTestNum' in self.defaultDict.keys() else ''
            self.runDataDict['failBinStr'] = fail_bin.name

            self.files_and_cloud(post_data)

        if reset_tester:
            # self.tagsCount = 0
            self.builder.get_object('reelId').bind("<Key>", self.get_reel_id)
            self.builder.tkvariables.get('numTags').set(0)
            self.builder.tkvariables.get('go').set(READ)
            self.testFinished = True
            self.packets_dict = {}
            self.test_barcodes = {}
            self.barcodes_read = {}
            self.reel_id = ''
            self.gtin = ''
            self.builder.tkvariables.get('reelId').set('')

            changeFileHandler(self.logger, self.logger_path, file_mode='a+', append_handler=True)
            self.logger.info(f'Test {self.common_run_name} ended.')
            removeFileHandler(self.logger, self.test_log_file)
            self.update_params_state(state='normal', group=READ)
            self.builder.tkvariables.get('stop').set(STOP)
            self.builder.get_object('stop')['state'] = 'disabled'

        if self.offline:
            self.offline_tag_index = 0

    def update_run_data(self, run_data_path):
        if exists(run_data_path):
            remove(run_data_path)

        run_csv = CsvLog(HeaderType.RUN, run_data_path, tester_type=TesterName.SAMPLE)
        run_csv.open_csv()
        run_csv.append_dict_as_row([self.runDataDict])

    def calc_tag_state(self, data):
        if len(data['packetList']):
            if len(data['adv_address']) > 1:
                tag_state = FailBinSample.ADVA_DUPLICATION
            elif data['ttfp'] == -1:
                tag_state = FailBinSample.NO_TTFP
            elif data['tbp'] == -1:
                tag_state = FailBinSample.NO_TBP
            else:
                tag_state = FailBinSample.TBP_EXISTS
        else:
            if len(self.bad_advas) == 0:
                tag_state = FailBinSample.NO_TTFP
            elif any(b['is_valid'] for b in self.bad_advas):
                tag_state = FailBinSample.UNDETERMINED_ERROR
            elif len(self.bad_advas) == sum([len(tag['packetList']) == 0 for tag in self.test_barcodes.values()]):
                tag_state = FailBinSample.NO_SERIALIZATION
            else:
                tag_state = FailBinSample.UNDETERMINED_ERROR

        return tag_state

    def files_and_cloud(self, post_data=False):
        self.runDataDict['runEndTime'] = self.dataBaseDict['runEndTime'] = time.strftime('%d/%m/%y %H:%M:%S')
        self.runDataDict['uploadToCloud'] = post_data and self.post_data
        run_data_path = abspath(join(OUTPUT_DIR, self.testName, self.testDir, f'{self.common_run_name}@run_data.csv'))

        self.update_run_data(run_data_path)

        tags_data_path = abspath(
            join(OUTPUT_DIR, self.testName, self.testDir, f'{self.common_run_name}@packets_data.csv'))
        if exists(tags_data_path):
            remove(tags_data_path)
        packets_csv = CsvLog(header_type=HeaderType.PACKETS, path=tags_data_path, tester_type=TesterName.SAMPLE)
        packets_csv.open_csv()

        for extId, data in self.test_barcodes.items():
            if data['chamber'] < len(self.comConnect.temperature_sensor_readings):
                all_reading_temp = self.comConnect.temperature_sensor_readings[data['chamber']]
            else:
                all_reading_temp = []
            temperature_from_sensor = numpy.mean(all_reading_temp) if len(all_reading_temp) else float('nan')
            tag_state = self.calc_tag_state(data)
            if data['packetList'].packet_list.size > 0:
                for sprinkler in data['packetList'].packet_list:
                    for i in range(sprinkler.gw_data['gw_packet'].size):
                        if sprinkler.gw_data["time_from_start"].size > 1:
                            time_from_start = sprinkler.gw_data["time_from_start"][i]
                        else:
                            time_from_start = sprinkler.gw_data["time_from_start"].item()
                        tag_row = {'commonRunName': self.common_run_name,
                                   'encryptedPacket': sprinkler.get_packet_string(i),
                                   'time': time_from_start,
                                   'externalId': extId,
                                   'reel': data['reel'], 'ttfp': data['ttfp'], 'tbp': data['tbp'],
                                   'adv_address': data['adv_address'],
                                   'state(tbp_exists:0,no_tbp:-1,no_ttfp:-2,dup_adv_address:-3)': tag_state.value,
                                   'fail_bin': tag_state.name,
                                   'status': data['status'], 'chamber': data['chamber'],
                                   'temperature_from_sensor': temperature_from_sensor
                                   }

                        packets_csv.append_dict_as_row([tag_row])
            else:  # add no response tags
                tag_row = {'commonRunName': self.common_run_name,
                           'encryptedPacket': '',
                           'time': float('nan'),
                           'externalId': extId,
                           'reel': self.reel_id, 'ttfp': float('nan'), 'tbp': None,
                           'adv_address': '',
                           'state(tbp_exists:0,no_tbp:-1,no_ttfp:-2,dup_adv_address:-3)': tag_state.value,
                           'fail_bin':tag_state.name,
                           'status': False, 'chamber': None,
                           'temperature_from_sensor': float('nan')
                           }
                packets_csv.append_dict_as_row([tag_row])

        with open(abspath(join(OUTPUT_DIR, self.testName, self.testDir, f'{self.common_run_name}@configs_data.csv')),
                  'w+', newline='') as newCsv:
            writer = csv.DictWriter(newCsv, fieldnames=self.dataBaseDict.keys())
            writer.writeheader()
            writer.writerows([self.dataBaseDict])

        with open(abspath(join(OUTPUT_DIR, self.testName, self.testDir, f'{self.common_run_name}@tags_data.csv')),
                  'w+', newline='') as newCsv:
            ids_dict = self.test_barcodes
            tags = []
            for extId, tag in ids_dict.items():
                tag_state = self.calc_tag_state(tag)
                if tag['chamber'] < len(self.comConnect.temperature_sensor_readings):
                    all_reading_temp = self.comConnect.temperature_sensor_readings[tag['chamber']]
                else:
                    all_reading_temp = []
                temperature_from_sensor = numpy.mean(all_reading_temp) if len(all_reading_temp) else float('nan')
                temp_dict = {}
                temp_dict['chamber'] = tag['chamber']
                temp_dict['reel'] = tag['reel']
                temp_dict['ext_id'] = extId
                temp_dict['ttfp'] = tag['ttfp']
                temp_dict['tbp'] = tag['tbp']
                temp_dict['adv_address'] = tag['adv_address']
                temp_dict['state(tbp_exists:0,no_tbp:-1,no_ttfp:-2,dup_adv_address:-3)'] = tag_state.value
                temp_dict['fail_bin'] = tag_state.name
                temp_dict['status'] = tag['status']
                temp_dict['testName'] = self.testName
                temp_dict['rssi'] = tag['rssi']
                temp_dict['temperature_from_sensor'] = temperature_from_sensor

                tags.append(temp_dict)

            writer = csv.DictWriter(newCsv, fieldnames=tags[0].keys())
            writer.writeheader()
            writer.writerows(tags)

        if post_data and self.post_data:
            post_success = self.post_to_cloud(run_data_path, tags_data_path, environment=self.environment)
            if post_success:
                self.logger.info('files were uploaded!')
            else:
                self.comConnect.popup_message(f'Failed uploading run and/or tags data, Upload manually:\n' +
                                              f'{self.common_run_name}@run_data.csv\n' +
                                              f'{self.common_run_name}@packets_data.csv', log='warning')
                self.runDataDict['uploadToCloud'] = False
                self.update_run_data(run_data_path)

    def get_packet_ext_id(self, packet):
        """
        get external ID of a tag by sending an example packet to the cloud.
        :type packet: Packet
        :param packet: contains the raw and time of the packet.
        :return: external ID of the tag, and the external ID parsed when it's wiliot tag.
        """
        full_data = {'barcode': None, 'cur_id': None, 'reel_id': None, 'gtin': None}
        success = False
        is_valid = False
        if self.offline:
            success = True
            is_valid = True
            if self.offline_tag_index <= len(self.barcodes_read.keys()) and len(self.barcodes_read.keys()) > 0:
                full_data['cur_id'] = list(self.barcodes_read.keys())[self.offline_tag_index - 1]
            else:
                print(f'discard {packet.get_packet_string()} since too many tags detected')
            full_data['reel_id'] = self.reel_id
            if len(self.reel_id) < 4:
                print('reel id smaller than 4 char assuming barcode format')
                full_data['gtin'] = ''
            else:
                print('according to reel id length, assuming sgtin format')
                full_data['gtin'] = SGTIN_PREFIX_DEFAULT
            full_data['barcode'] = full_data['gtin'] + full_data['reel_id'] + 'T' + full_data['cur_id']
            self.offline_tag_index += 1
            return full_data, success, is_valid

        packet_payload = packet.get_payload()

        res = self.client.resolve_payload(payload=packet_payload, owner_id=self.owner, verbose=True)
        if 'externalId' in res.keys():
            if res['externalId'] != 'unknown':
                full_data['barcode'] = res['externalId']
                full_data['cur_id'] = full_data['reel_id'] = full_data['gtin'] = full_data['barcode']
                try:
                    is_valid = is_external_id_valid(full_data['barcode'])
                    if is_valid:
                        if ')' in full_data['barcode']:
                            tag_data = full_data['barcode'].split(')')[2]
                            full_data['gtin'] = ')'.join(full_data['barcode'].split(')')[:2]) + ')'
                        elif len(full_data['barcode']) >= len(SGTIN_PREFIX_DEFAULT):  # gtin without parenthesis
                            full_data['gtin'] = full_data['barcode'][0:18]
                            tag_data = full_data['barcode'][18:]
                        else:  # barcode or an other type with no prefix
                            full_data['gtin'] = ''
                            tag_data = full_data['barcode']

                        full_data['cur_id'] = tag_data.split('T')[1].strip("' ")
                        full_data['reel_id'] = tag_data.split('T')[0].strip("' ")
                    success = True
                except Exception as e:
                    success = False
                    print('got invalid external id: {} with exception: {}'.format(res, e))
        return full_data, success, is_valid

    def post_to_cloud(self, run_data_file_path, packets_data_file_path, environment='test/'):
        """
        post file to the cloud
        :type run_data_file_path: string
        :param run_data_file_path: the path to the uploaded run data file
        :type packets_data_file_path: string
        :param packets_data_file_path: the path to the uploaded packets data file
        :type environment: string
        :param environment: the environment in the cloud (dev, test, prod, etc.)
        :return: bool - True if succeeded, False otherwise
        """
        success = False
        first_iter = True
        while not success:
            if not first_iter:
                try_again = popup_yes_no(f'Could not post data to cloud, try again?')
                if not try_again:
                    return False

            success = upload_to_cloud_api(batch_name=self.reel_id, tester_type='sample-test',
                                          run_data_csv_name=run_data_file_path,
                                          packets_data_csv_name=packets_data_file_path,
                                          is_path=True,
                                          env=environment,
                                          owner_id=self.owner,
                                          logger_='sample')
            first_iter = False

        if not success:
            self.comConnect.popup_message(
                f'Run upload failed. Check exception error at the console and check Internet connection is available and upload logs manually.',
                title='Upload Error',
                log='error')

        return success

    def post_process(self):
        tbp_arr = []
        ttfp_arr = []
        rssi_arr = []
        status_arr = []
        for extId, tag in self.test_barcodes.items():
            status_temp = False
            if tag['tbp'] != -1:
                tbp_arr.append(tag['tbp'])
                if self.params['tag_tbp_min'] != '' and self.params['tag_tbp_max'] != '':
                    if int(self.params['tag_tbp_min']) < tag['tbp'] < int(self.params['tag_tbp_max']):
                        status_temp = True
                    else:
                        status_temp = False
                else:
                    status_temp = True

            if tag['ttfp'] != -1:
                ttfp_arr.append(tag['ttfp'])
            if tag['rssi'] != -1:
                rssi_arr.append(tag['rssi'])
            if len(tag['adv_address']) != 1:
                status_temp = False
            tag['status'] = status_temp
            status_arr.append(status_temp)

        pass_barcodes = [extId for extId, is_pass in zip(self.test_barcodes.keys(), status_arr) if is_pass]
        tested_barcodes = len(self.test_barcodes.keys())
        num_of_answered = len(ttfp_arr)
        num_of_pass = len(pass_barcodes)
        self.dataBaseDict['packets'] = self.numOfPackets
        self.dataBaseDict['tested'] = self.runDataDict['tested'] = tested_barcodes
        self.dataBaseDict['responded'] = self.runDataDict['responded'] = num_of_answered
        self.dataBaseDict['passed'] = self.runDataDict['passed'] = num_of_pass
        self.dataBaseDict['responding[%]'] = self.runDataDict['responding[%]'] = self.runDataDict['yield'] = \
            f'{float((num_of_answered / tested_barcodes) * 100) if tested_barcodes > 0 else 0}%'
        self.dataBaseDict['passed[%]'] = self.runDataDict[
            'passed[%]'] = f'{float((num_of_pass / tested_barcodes) * 100 if tested_barcodes > 0 else 0)}%'
        self.dataBaseDict['validTbp[%]'] = self.runDataDict[
            'validTbp[%]'] = f'{float((num_of_pass / num_of_answered) * 100 if num_of_answered > 0 else 0)}%'
        # calc ttfp
        avg_ttfp = sum(ttfp_arr) / len(ttfp_arr) if len(ttfp_arr) > 0 else -1
        ttfp_arr = ttfp_arr if len(ttfp_arr) > 0 else [-1]

        self.dataBaseDict['ttfpStd'] = f'{numpy.std(ttfp_arr):.3f}'
        self.runDataDict['ttfpAvg'] = self.dataBaseDict['ttfpAvg'] = f'{avg_ttfp:.3f}'
        self.dataBaseDict['ttfpMin'] = f'{min(ttfp_arr):.3f}'
        self.runDataDict['maxTtfp'] = self.dataBaseDict['ttfpMax'] = f'{max(ttfp_arr):.3f}'

        # calc tbp
        avg_tbp = sum(tbp_arr) / len(tbp_arr) if len(tbp_arr) > 0 else -1
        tbp_arr = tbp_arr if len(tbp_arr) > 0 else [-1]

        self.runDataDict['tbpStd'] = self.dataBaseDict['tbpStd'] = f'{numpy.std(tbp_arr):.3f}'
        self.runDataDict['tbpAvg'] = self.dataBaseDict['tbpAvg'] = f'{avg_tbp:.3f}'
        self.dataBaseDict['tbpMin'] = f'{min(tbp_arr):.3f}'
        self.dataBaseDict['tbpMax'] = f'{max(tbp_arr):.3f}'

        avg_rssi = sum(rssi_arr) / len(rssi_arr) if len(rssi_arr) > 0 else -1
        rssi_arr = rssi_arr if len(rssi_arr) > 0 else [-1]

        self.runDataDict['rssiAvg'] = self.dataBaseDict['rssiAvg'] = str(avg_rssi)

        return pass_barcodes

    def reset(self):
        """
        reset the tester (fully available only when running from bat file)
        """
        global RESET
        RESET = False
        self.comConnect.cancel_gw_commands()
        if popup_yes_no(f'Reset Sample test?'):
            try:
                self.comConnect.close()
                self.comConnect.__del__()
                self.remove_barcodes()

                self.ttk.destroy()
                RESET = True
            except Exception as e:
                print(f'could not reset due to: {e}')
                exit(1)
        else:
            pass

    def close(self):
        """
        close the gui and destroy the test
        """
        try:
            self.comConnect.close()
            self.comConnect.gateway.exit_gw_api()
            self.ttk.destroy()
        except Exception as e:
            print(e)
            exit(1)

    def update_data(self):
        """
        update station name and owner in json file, for future usage.
        """
        # temp_coms = {}
        # if isfile(join(CONFIGS_DIR, '.defaults.json')):
        #     with open(join(CONFIGS_DIR, '.defaults.json'), 'r') as defaultComs:
        #         temp_coms = load(defaultComs)
        # temp_coms.update(self.defaultDict)
        temp_coms = self.comConnect.get_default_dict()
        if self.station_name.strip() != '':
            temp_coms['stationName'] = self.station_name
        if self.testConfig != '':
            temp_coms['config'] = self.testConfig
        if self.calib:
            temp_coms[f'{self.antenna}_calib'] = {'low': self.low, 'high': self.high, 'step': self.step}

        with open(abspath(join(CONFIGS_DIR, '.defaults.json')), 'w+') as defaultComs:
            dump(temp_coms, defaultComs, indent=4)

    def popup_login(self):
        """
        popup to insert fusion auth credentials, and choosing owner.
        """
        default_font = ("Helvetica", 10)
        popup = Tk()
        popup.eval('tk::PlaceWindow . center')
        popup.wm_title('Login')

        def quit_tester():
            try:
                popup.destroy()
            except Exception as e:
                print(e)
                exit(1)

        popup.protocol("WM_DELETE_WINDOW", quit_tester)

        def ok():
            self.owner = c1.get()
            self.station_name = e3.get()
            popup.destroy()

        l1 = Label(popup, text='Choose owner and station name:', font=default_font)
        l1.grid(row=2, column=0, padx=10, pady=10, columnspan=3)
        l4 = Label(popup, text='Owner:', font=default_font)
        l4.grid(row=6, column=0, padx=10, pady=10)
        c1 = ttk.Combobox(popup, state='normal')
        c1.grid(row=6, column=1, padx=10, pady=15)
        l5 = Label(popup, text='Station Name:', font=default_font)
        l5.grid(row=7, column=0, padx=10, pady=10)
        e3 = Entry(popup)
        if 'stationName' in self.defaultDict.keys():
            e3.insert(0, self.defaultDict['stationName'])
        e3.grid(row=7, column=1, padx=10, pady=5)
        b3 = Button(popup, text="OK", command=ok, height=1, width=10)
        b3.grid(row=8, column=1, padx=10, pady=10)

        if 'owner' in self.defaultDict.keys():
            owner_id_list = self.defaultDict['owner'] \
                if isinstance(self.defaultDict['owner'], list) else [self.defaultDict['owner']]
        else:
            owner_id_list = ['']
        c1['values'] = owner_id_list
        c1.set(owner_id_list[-1])

        popup.mainloop()

        if self.owner not in owner_id_list:
            owner_id_list.append(self.owner)
            owner_id_list = [o for o in owner_id_list if o != '']
            self.defaultDict['owner'] = owner_id_list
            with open(abspath(join(CONFIGS_DIR, '.defaults.json')), 'w+') as defaultComs:
                dump(self.defaultDict, defaultComs, indent=4)

    def update_default_dict(self, field, value):
        antenna = self.antenna.lower()
        if f'{antenna}_calib' in self.defaultDict.keys():
            self.defaultDict[f'{antenna}_calib'][field] = value

    def popup_calib(self):
        """
        popup to choose calib mode parameters
        """
        default_font = ("Helvetica", 10)
        popup = Tk()
        popup.wm_title('Login')

        def quit_calib():
            popup.destroy()

        popup.protocol("WM_DELETE_WINDOW", quit_calib)

        def ok():
            self.low = e2.get()
            self.high = e3.get()
            self.step = e4.get()
            self.n_repetitions = e5.get()
            # save the dictionary back to the file
            with open(abspath(join(CONFIGS_DIR, '.defaults.json')), 'w') as defaultComs:
                dump(self.defaultDict, defaultComs)
            popup.destroy()

        def update_antenna_params(*args):
            self.antenna = antenna = c2.get().lower()
            if f'{antenna}_calib' in self.defaultDict.keys():
                antennaDict = self.defaultDict[f'{antenna}_calib']
                e2.delete(0, END)
                e3.delete(0, END)
                e4.delete(0, END)
                e5.delete(0, END)
                e2.insert(0, antennaDict['low'])
                e3.insert(0, antennaDict['high'])
                e4.insert(0, antennaDict['step'])
                e5.insert(0, 1)

        l1 = Label(popup, text='Enter calibration parameters:', font=default_font)
        l1.grid(row=1, column=0, padx=10, pady=10, columnspan=3)
        l2 = Label(popup, text='Antenna Type:', font=default_font)
        l2.grid(row=2, column=0, padx=10, pady=10)
        c2 = ttk.Combobox(popup, values=['BLE', 'LoRa'])
        c2.grid(row=2, column=1, padx=10, pady=10)
        c2.bind("<FocusOut>", update_antenna_params)
        c2.bind("<<ComboboxSelected>>", update_antenna_params)
        l3 = Label(popup, text='Low value:', font=default_font)
        l3.grid(row=3, column=0, padx=10, pady=10)
        e2 = Entry(popup)
        e2.grid(row=3, column=1, padx=10, pady=5)
        e2.bind("<FocusOut>", lambda e: self.update_default_dict('low', e2.get()))
        l4 = Label(popup, text='High value:', font=default_font)
        l4.grid(row=4, column=0, padx=10, pady=10)
        e3 = Entry(popup)
        e3.grid(row=4, column=1, padx=10, pady=5)
        e3.bind("<FocusOut>", lambda e: self.update_default_dict('high', e3.get()))
        l5 = Label(popup, text='Step:', font=default_font)
        l5.grid(row=5, column=0, padx=10, pady=10)
        e4 = Entry(popup)
        e4.grid(row=5, column=1, padx=10, pady=5)
        e4.bind("<FocusOut>", lambda e: self.update_default_dict('step', e4.get()))
        l6 = Label(popup, text='Number of Repetitions per step:', font=default_font)
        l6.grid(row=6, column=0, padx=10, pady=10)
        e5 = Entry(popup)
        e5.grid(row=6, column=1, padx=10, pady=5)
        e5.bind("<FocusOut>", lambda e: self.update_default_dict('n_repetitions', e5.get()))
        b1 = Button(popup, text="Quit", command=quit_calib, height=1, width=10)
        b1.grid(row=7, column=0, padx=10, pady=10)
        b2 = Button(popup, text="Ok", command=ok, height=1, width=10)
        b2.grid(row=7, column=1, padx=10, pady=10)

        popup.mainloop()


def popup_yes_no(question, tk_frame=None):
    if tk_frame is None:
        root = Tk()
        root.eval(f'tk::PlaceWindow {str(root)} center')
    else:
        root = tk_frame
    root.wm_withdraw()
    result = messagebox.askquestion("Sample Test", question, icon='warning')
    root.destroy()
    if result == 'yes':
        return True
    else:
        return False


def float_precision(num, prec=2):
    dot_pos = str(num).index('.')
    first_idx = [i for i in range(len(str(num))) if str(num)[i] != '0' and str(num)[i] != '.']
    first_idx = first_idx[0] if first_idx[0] > 0 else first_idx[0] + 1
    after_dot = first_idx - dot_pos + prec
    if after_dot > 0:
        eval_str = '{:.%sf}' % (str(first_idx - dot_pos + prec))
    else:
        eval_str = '{:.0f}'
    return float(eval_str.format(num))


if __name__ == '__main__':
    global RESET
    RESET = False
    parser = argparse.ArgumentParser(description='Run PixieParser')
    parser.add_argument('-c', '--calib', help='Calibration mode', default=False, action='store_true')
    parser.add_argument('-e', '--environment', help='Environment: test or not', default='prod')
    parser.add_argument('-p', '--post_data', help='Post data to the cloud', default=True)
    parser.add_argument('-o', '--offline', help='Offline mode', default=False, action='store_true')
    args = parser.parse_args()
    calib = args.calib
    post_data = args.post_data
    offline = args.offline

    # Run the UI
    # calib = True
    # offline = True
    if calib:
        print(f'Sample Test - calibration mode active.')
    if offline:
        print(f'Sample Test - offline mode active.')
    app_folder = abspath(join(dirname(__file__), '../wiliot_testers'))
    is_first_run = True
    while is_first_run or RESET:
        is_first_run = False
        try:
            RESET = False
            sampleTest = SampleTest(calib=calib, environment=args.environment, post_data=post_data,
                                    offline=offline)
            sampleTest.gui()
        except BaseException:
            print_exc()
            exit(0)
            break
