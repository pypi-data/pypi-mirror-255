"""
  Copyright (c) 2016- 2023, Wiliot Ltd. All rights reserved.

  Redistribution and use of the Software in source and binary forms, with or without modification,
   are permitted provided that the following conditions are met:

     1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     2. Redistributions in binary form, except as used in conjunction with
     Wiliot's Pixel in a product or a Software update for such product, must reproduce
     the above copyright notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the distribution.

     3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
     may be used to endorse or promote products or services derived from this Software,
     without specific prior written permission.

     4. This Software, with or without modification, must only be used in conjunction
     with Wiliot's Pixel or with Wiliot's cloud service.

     5. If any Software is provided in binary form under this license, you must not
     do any of the following:
     (a) modify, adapt, translate, or create a derivative work of the Software; or
     (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
     discover the source code or non-literal aspects (such as the underlying structure,
     sequence, organization, ideas, or algorithms) of the Software.

     6. If you create a derivative work and/or improvement of any Software, you hereby
     irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
     royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
     right and license to reproduce, use, make, have made, import, distribute, sell,
     offer for sale, create derivative works of, modify, translate, publicly perform
     and display, and otherwise commercially exploit such derivative works and improvements
     (as applicable) in conjunction with Wiliot's products and services.

     7. You represent and warrant that you are not a resident of (and will not use the
     Software in) a country that the U.S. government has embargoed for use of the Software,
     nor are you named on the U.S. Treasury Department’s list of Specially Designated
     Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
     You must not transfer, export, re-export, import, re-import or divert the Software
     in violation of any export or re-export control laws and regulations (such as the
     United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
     and use restrictions, all as then in effect

   THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
   OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
   WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
   QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
   IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
   ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
   OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
   FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
   (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
   (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
   (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
   (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""
import logging
import time
import os
import datetime
import threading
import json
from enum import Enum
import pandas as pd
import numpy as np

from wiliot_core import WiliotDir
from wiliot_core import WiliotGateway, ActionType, DataType, valid_output_power_vals
from wiliot_core import PacketList
from wiliot_testers.wiliot_tester_tag_result import WiliotTesterTagResultList, WiliotTesterTagResult, FailureCodes

try:
    from wiliot_core import DecryptedPacketList, DecryptedPacket
    print('tag test: decryption mode is supported if needed')
except Exception as e:
    pass

supported_gw_version = [3, 5, 2]


class TesterName(Enum):
    OFFLINE = 'offline'
    SAMPLE = 'sample'
    SYSTEM_TEST = 'system_test'
    TAL15K = 'tal15k'
    YIELD = 'yield'


class LoggerName(Enum):
    MAIN = 'main'
    GW = 'gw'
    RESULTS = 'results'


class WiliotTesterTagTest(object):
    """
    Wiliot Tags Tester according to configurations provided by user
    """

    def __init__(self, selected_test, test_suite=None, gw_obj=None, black_list=None,
                 stop_event_trig=None, tester_name=TesterName.OFFLINE,
                 logger_name=None, logger_result_name=None, logger_gw_name=None,
                 lock_print=None, inlay=None, verbose=True):  # TODO add selected test dict
        """
        :param logger_name: if specified the main logger is based on a predefine logger with the specified name.
                            otherwise the logger is set by the app
        :type logger_name: str
        :param logger_result_name: if specified the results logger is based on a predefine logger with the
                                   specified name. otherwise the logger is set by the app
        :type logger_result_name: str
        :param logger_gw_name: if specified the gw logger is based on a predefine logger with the specified name.
                               otherwise the logger is set by the app
        :type logger_gw_name: str
        :param tester_name: the tester type from the TesterName list
        :type tester_name: TesterName
        :param test_suite: the test suite contains all the parameters of the test.
                           the test suite structure should be as following:
                            test_suite = {"Dual Band": {"plDelay": 100,
                                                        "rssiThresholdHW": 95,
                                                        "rssiThresholdSW": 80,
                                                        "maxTtfp": 5,
                                                        "tests": [
                                                            {"name": "first_packets_ble_band",
                                                             "rxChannel": 37,
                                                             "energizingPattern": 18,
                                                             "timeProfile": [5, 10],
                                                             "absGwTxPowerIndex": -1,
                                                             "maxTime": 5,
                                                             "delayBeforeNextTest": 0,
                                                             "stop_criteria": {"num_packets": [1, 99]},
                                                             "quality_param": {"ttfp": [0, 5]}
                                                             },
                                                            {"name": "sub1G_band",
                                                             "rxChannel": 37,
                                                             "energizingPattern": 52,
                                                             "timeProfile": [5, 10],
                                                             "absGwTxPowerIndex": -1,
                                                             "maxTime": 5,
                                                             "stop_criteria": {"num_packets": [2, 99]},
                                                             "quality_param": {}
                                                             }
                                                        ]}}
        :type test_suite: dict
        :param selected_test: the name of test from the provided test suite (e.g. 'Dual Band' from the example above)
        :type selected_test: str
        :param gw_obj: if specified the gw object is based on the predefined specified gw obj,
                      otherwise the gw obj is defined by the app
        :type gw_obj: WiliotGateway
        :param black_list: a list with all the tags that are known as a noise or already tested tag that should not
                           be part of the current test
        :type black_list: list
        :param stop_event_trig: an event from outer scope which stops the app when it is triggered (set)
        :type stop_event_trig: threading.Event
        :param lock_print: if specified the logging prints according to the specified lock
        :type lock_print: threading.Lock()
        :param inlay: the tag inlay. most relevant for decrypted packets
        :type inlay: InlayTypes
        :param verbose: if True print all debug messages as well
        :type verbose: bool
        """

        self.GwObj = gw_obj
        self.gw_ver = ''
        self.tester_name = tester_name
        self.selected_test = {}
        self.time_expired = False
        self.test_end = False
        self.first_packet_timer = None
        self.test_timer = None
        self.start_test = False
        self.dev_mode = False
        self.run_all = False
        self.max_ttfp = None
        if logger_name is None:
            wiliot_logger = WiliotTesterLog(run_name='wiliot_test')

            wiliot_dir = WiliotDir()
            log_path = os.path.join(wiliot_dir.get_common_dir(), 'logs')
            if not os.path.isdir(log_path):
                os.makedirs(log_path)
            wiliot_logger.set_logger(log_path=log_path)
            self.logger = wiliot_logger.logger
            self.logger_results = wiliot_logger.results_logger
            self.logger_gw = wiliot_logger.gw_logger

        else:
            self.logger = logging.getLogger(logger_name)
            if logger_result_name is None:
                self.logger_results = logging.getLogger(logger_name)
            else:
                self.logger_results = logging.getLogger(logger_result_name)
            if logger_gw_name is None:
                self.logger_gw = logging.getLogger(logger_name)
            else:
                self.logger_gw = logging.getLogger(logger_gw_name)

        if lock_print is None:
            self._lock_print = threading.Lock()
        else:
            self._lock_print = lock_print
        self.verbose = verbose
        # Global test params
        self.set_test_suite(selected_test, test_suite, inlay)  # Set Test suite file - tests configuration

        self.gw_init()  # Set GW Object
        self.gw_reset_and_config()  # Init values for GW Object
        # prepare the gw for the next tag test:
        self.init_gw_test(sub_test=self.selected_test['tests'][0], is_start_gw_app=False)

        if black_list is None:
            self.black_list = []
        else:
            self.black_list = black_list

        self.stop_event_trig = stop_event_trig
        self.test_results = WiliotTesterTagResultList()
        self.tag_results = None

    def check_gw_version(self):
        """
        check if gw version is supported
        :return: True if version is supported
        :rtype: bool
        """
        self.gw_ver, __ = self.GwObj.get_gw_version()
        gw_ver_num = [int(x, 16) for x in self.gw_ver.split('.')]
        for ind, expect_ver in enumerate(supported_gw_version):
            if gw_ver_num[ind] > expect_ver:
                return True
            if gw_ver_num[ind] < expect_ver:
                raise Exception('GW version should be at least {}.{}.{} to support accurate tester features'.
                                format(supported_gw_version[0], supported_gw_version[1], supported_gw_version[2]))

        return True

    def gw_init(self):
        """
        initialize gw and the data listener thread
        """
        if self.GwObj is None:
            self.GwObj = WiliotGateway(auto_connect=True, logger_name=self.logger_gw.name, is_multi_processes=True,
                                       lock_print=threading.Lock())
        try:
            if self.GwObj.connected:
                self.GwObj.reset_buffer()
                self.GwObj.start_continuous_listener()
                if self.check_gw_version():
                    self._printing_func('GW obj initialized')
            else:
                raise Exception('gateway was not detected, please check connection')
        except Exception as e:
            self._printing_func(str(e), log_level=logging.WARNING)
            raise e

    def get_gw_version(self):
        """
        get the gw firmware version
        :return: gw firmware version
        :rtype: str
        """
        return self.gw_ver

    def set_test_suite(self, selected_test, test_suite=None, inlay=None):
        """
        import the test suite
        :param selected_test: the test name from the test suites
        :type selected_test: str
        :param test_suite: if specified the dict of test suites as explain in the class init
        :type test_suite: dict
        :param inlay: the tag inlay (optional)
        :type inlay: InlayTypes
        """
        # upload test suite:
        if test_suite is None:
            try:
                test_suite = load_test_suite_file(tester_name=self.tester_name.value)
            except Exception as e:
                self._printing_func('Test Suite input is wrong', log_level=logging.WARNING)
                raise Exception(e)

        if test_suite is None:
            msg = 'Test Suite input in wrong'
            self._printing_func(msg, log_level=logging.WARNING)
            raise Exception(msg)
        else:
            if selected_test in test_suite:
                self.selected_test = test_suite[selected_test]
                self.selected_test['inlay'] = inlay
                if 'devMode' in self.selected_test:
                    self.dev_mode = True if self.selected_test['devMode'].lower() == 'true' else False
                if 'maxTtfp' in self.selected_test:
                    self.max_ttfp = int(self.selected_test['maxTtfp'])
                if 'run_all' in self.selected_test:
                    if self.selected_test['run_all'].lower() == 'true':
                        self.run_all = True
                self.selected_test['ignore_test_mode'] = 'ignore_test_mode' in self.selected_test
                for i, t in enumerate(self.selected_test['tests']):
                    if 'sub1gGwTxPower' in t.keys():
                        self.selected_test['tests'][i]['sub1g_power'] = t['sub1gGwTxPower']
                    else:
                        self.selected_test['tests'][i]['sub1g_power'] = None
                    if 'absGwTxPowerIndex' in t.keys():
                        self.selected_test['tests'][i]['gw_power_dict'] = \
                            valid_output_power_vals[t['absGwTxPowerIndex']]
                    elif 'absGwTxPower' in t.keys():
                        self.selected_test['tests'][i]['gw_power_dict'] = \
                            valid_output_power_vals[[p['abs_power']
                                                     for p in valid_output_power_vals].index(t['absGwTxPower'])]
                    elif 'GwTxPower' in t.keys():
                        self.selected_test['tests'][i]['gw_power_dict'] = \
                            valid_output_power_vals[
                                [p['gw_output_power'] for p in valid_output_power_vals].index(t['GwTxPower'])]
                    else:
                        self.selected_test['tests'][i]['gw_power_dict'] = None
                        if 'sub1gGwTxPower' not in t.keys():  # both output power are not defined
                            raise Exception('invalid tx gw power')

            else:
                msg = 'the selected test: {} was not found in the tests suite'.format(selected_test)
                self._printing_func(msg, log_level=logging.WARNING)
                raise Exception(msg)

    def gw_reset_and_config(self):
        """
        reset gw and config it to tester mode
        """
        self.GwObj.reset_gw(reset_port=False)
        self.GwObj.reset_listener()
        time.sleep(0.5)
        if not self.GwObj.is_gw_alive():
            self._printing_func('gw_reset_and_config: wait more time since gw did not respond')
            time.sleep(5)
        self.GwObj.write('!set_tester_mode 1', with_ack=True)
        self.GwObj.write('!pl_gw_config 1', with_ack=True)
        self.GwObj.write('!listen_to_tag_only 1', with_ack=True)
        self.GwObj.write('!sub1g_sync 1', with_ack=True)

        self.GwObj.config_gw(rssi_thr_val=int(self.selected_test['rssiThresholdHW']),
                             time_profile_val=self.selected_test['tests'][0]['timeProfile'],
                             pl_delay_val=self.selected_test['plDelay'], start_gw_app=False, with_ack=True,
                             combined_msg=False)
        if not self.GwObj.is_gw_alive():
            raise Exception('Could not get responds from the Gateway, please check connection and re-run')

    def check_if_trigger_was_received(self):
        n_gw_msg = self.GwObj.com_rsp_str_input_q.qsize()
        for i in range(n_gw_msg):
            gw_rsp = self.GwObj.com_rsp_str_input_q.get(timeout=None)
            if "Start Production Line GW" in gw_rsp['raw']:
                return True
        return False

    def wait_for_trigger(self, wait_for_gw_trigger):
        """
        wait for gw trigger, i.e. send 'Start Production Line' msg.
        if trigger was not received, gw reset and re-config to make sure there is no gw problem.
        :param wait_for_gw_trigger: the time [seconds] to wait to trigger,
                                    if the elapsed time is larger the function return False
        :type wait_for_gw_trigger: int or float
        :return: if trigger was detected return True
        :rtype: bool
        """
        gw_answer = ''
        gw_trigger_init = datetime.datetime.now()
        dt = datetime.datetime.now() - gw_trigger_init
        while gw_answer == '' and dt.total_seconds() < wait_for_gw_trigger:
            if self.is_stopped_by_user():
                break
            gw_answer = self.GwObj.read_specific_message(msg="Start Production Line GW", read_timeout=1)
            dt = datetime.datetime.now() - gw_trigger_init
        is_trigger_received = "Start Production Line GW" in gw_answer
        if is_trigger_received:
            self.GwObj.reset_start_time()
        else:
            self._printing_func('no trigger was detected. reset and config gw again', log_level=logging.INFO)
            self.gw_reset_and_config()
            self.init_gw_test(sub_test=self.selected_test['tests'][0], is_start_gw_app=False)
        return is_trigger_received

    def power_index_to_value(self, power_index, abs_power=False, gw_output=False):
        """
        convert gw ouput power index to value according to valid_output_power_vals
        :param power_index: the index of the valid_output_power_vals list
        :type power_index: int
        :param abs_power: true if the desired value is the absolute output power value
        :type abs_power: bool
        :param gw_output: true if the desired value is the gw command output power value
        :type gw_output: bool
        :return: the desired value
        :rtype: int or str
        """
        all_power = self.GwObj.valid_output_power_vals
        if abs_power:
            return all_power[power_index]['abs_power']
        if gw_output:
            return all_power[power_index]['gw_output_power']

    def end_of_time(self, timer_type=''):
        """
        trigger when the test timers are set (the defined test time was elapsed)
        and reset the timers
        :param timer_type: the timer name
        :type timer_type: str
        """
        self._printing_func('{} time has expired'.format(timer_type), logger_name=LoggerName.RESULTS)
        self.time_expired = True
        self.reset_timers()

    def packet_filter(self, packet_list, filter_param='rssi', param_limits=None, ignore_test_mode_packet=False):
        """
        filter the packets from the packet_list according to the filter_param and the param_limits.
        packets that were filtered out of the test does no take into account during the test and considered as noise

        :param packet_list: the incoming packets list
        :type packet_list: PacketList or DecryptedPacketList
        :param filter_param: one of the packet dataframe column names
        :type filter_param: str
        :param param_limits: list of two elements [x, y] that defines the range of the valid param (x,y including)
        :type param_limits: list
        :param ignore_test_mode_packet: if true, it shall filter out test mode packet
        :type ignore_test_mode_packet: bool
        :return: the filtered packet list
        :rtype: PacketList or DecryptedPacketList
        """

        def update_custom_data(packet, key, value):
            if key in packet.custom_data.keys():
                packet.custom_data[key].append(value)
            else:
                packet.custom_data[key] = [value]

        if param_limits is None:
            param_limits = [0, float('inf')]
        filtered_packet_list = PacketList() if not self.dev_mode else DecryptedPacketList()

        for p in packet_list:
            # filter packets from black list:
            if p.packet_data['adv_address'] in self.black_list:
                p.add_custom_data(custom_data={'packet_status': 'blacklist'})
            elif ignore_test_mode_packet and p.packet_data['test_mode'] == 1:
                p.add_custom_data(custom_data={'packet_status': 'test_mode'})  # TODO: check if it really help
            else:
                # filter packets by filter param:
                packet_param_list = p.extract_packet_data_by_name(filter_param)
                sprinkler_ids = []
                for i, param in enumerate(packet_param_list):
                    if param_limits[0] <= param <= param_limits[-1]:
                        update_custom_data(p, 'packet_status', 'good')
                        sprinkler_ids.append(i)
                    else:
                        update_custom_data(p, 'packet_status', filter_param)

                if len(sprinkler_ids) > 0:
                    filtered_packet_list.append(p.filter_by_sprinkler_id(sprinkler_ids=sprinkler_ids))

        return filtered_packet_list

    def select_tag_under_test(self, optional_tags):
        """
        select which tag is under test even if more than one tag sends packets
        :param optional_tags: all tags that transmits during the tag-test
        :type optional_tags: list
        :return: the packet list of the selected tag under test
        :rtype: PacketList or DecryptedPacketList
        """
        selected_adva = None
        self.tag_results.all_tags = self.tag_results.add_packets_to_multi_tags(packets_in=self.tag_results.all_packets,
                                                                               multi_tag_out=self.tag_results.all_tags)
        self._printing_func('Starting to decide which tag is under test')
        optional_tags = list(set(optional_tags))
        if len(optional_tags) == 0:
            selected_adva = ''
        elif len(optional_tags) == 1:
            selected_adva = optional_tags[0]
            self.tag_results.selected_tag = self.tag_results.all_tags.tags[selected_adva]
        else:  # more than one tag reach the stop criteria:
            tags_in_tie = False
            min_rssi = None
            max_size = None
            for adva in optional_tags:
                cur_mean_rssi = self.tag_results.filtered_tags.get_avg_rssi_by_id(id=adva)
                if min_rssi is None or cur_mean_rssi < min_rssi:  # best tag
                    min_rssi = cur_mean_rssi
                    max_size = self.tag_results.filtered_tags.tags[adva].size()
                    selected_adva = adva
                elif min_rssi is not None and cur_mean_rssi == min_rssi:  # tiebreak between tags
                    if self.tag_results.filtered_tags.tags[adva].size() > max_size:
                        max_size = self.tag_results.filtered_tags.tags[adva].size()
                        selected_adva = adva
                    if self.tag_results.filtered_tags.tags[adva].size() == max_size:
                        self._printing_func('we cannot select which tag is under test since both tags: {}, {} have '
                                            'the same rssi mean and number of packets'.format(adva, selected_adva))
                        tags_in_tie = True
                elif min_rssi is not None and cur_mean_rssi > min_rssi:  # noisy tag
                    self.black_list.append(adva)
                    self._printing_func('tag: {} was added to blacklist'.format(adva))

            if selected_adva is None:
                msg = 'no rssi was found for the selected packets'
                self._printing_func(msg, log_level=logging.WARNING)
                raise Exception(msg)
            elif tags_in_tie:
                pass
            else:
                self.tag_results.selected_tag = self.tag_results.all_tags.tags[selected_adva]

        return selected_adva

    def get_packets(self, filter_param='rssi', filter_value=0, data_type=DataType.PACKET_LIST):
        """
        receive packets from the gw (via the listener) and filter them according to packet_filter()
        :param filter_param: one of the packet dataframe column names (for packet_filter)
        :type filter_param: str
        :param filter_value: the max valid value of the specified param
        :type filter_value: int
        :param data_type: data type of the received packets
        :type data_type: DataType
        :return: True if packet were received
        :rtype: bool
        """
        packets_received_list = None
        if self.GwObj.is_data_available():
            packets_received_list = self.GwObj.get_packets(action_type=ActionType.ALL_SAMPLE,
                                                           data_type=data_type,
                                                           tag_inlay=self.selected_test['inlay'])
        if packets_received_list:
            if packets_received_list.size() > 1:
                self._printing_func('pulled more than one packet from the queue, check analysis performance')

            self._printing_func('got {} packets'.format(
                ['ADVA:' + p.get_adva() + ',    FLOW:' + p.get_flow() + ',    RSSI:' +
                 p.get_rssi() + ',    ' + p.get_packet_string() for p in packets_received_list]),
                log_level=logging.DEBUG)
            filtered_packets = self.packet_filter(packets_received_list, filter_param=filter_param,
                                                  param_limits=[0, filter_value],
                                                  ignore_test_mode_packet=self.selected_test['ignore_test_mode'])
            self.tag_results.all_packets.__add__(packets_received_list)
            if filtered_packets.size():
                self.tag_results.filtered_tags = \
                    self.tag_results.add_packets_to_multi_tags(filtered_packets, self.tag_results.filtered_tags)
                self._printing_func('and {} pass the packet filter'.format(
                    ['ADVA:' + p.get_adva() + ',    FLOW:' + p.get_flow() + ',    RSSI:' + p.get_rssi() + ',    ' +
                     p.get_packet_string() for p in packets_received_list]), log_level=logging.DEBUG)
            return True
        else:
            return False

    def check_stop_criteria(self, stop_criteria_dict=None, check_type='general'):
        """
        check if the received packet met the stop criteria and the test should be stopped
        :param stop_criteria_dict: dictionary according to the test suite definition, (e.g. {"num_packets": [1, 99]})
        :type stop_criteria_dict: dict
        :param check_type: specified the type of stop criteria to improve performance
        :type check_type: str
        :return: the tags which reached the stop criteria
        :rtype: list
        """

        if stop_criteria_dict == {}:
            return []
        if check_type == 'packets':
            tags_stat_df = pd.DataFrame()
            for tag_id, tag in self.tag_results.filtered_tags.tags.items():
                tags_stat_dict = {'adv_address': tag_id, 'num_packets': tag.size()}
                tag_id_df = pd.DataFrame(tags_stat_dict, index=[0])
                tags_stat_df = pd.concat([tags_stat_df, tag_id_df], axis=0)
        elif check_type == 'external_sensor' and self.dev_mode:
            tags_stat_df = pd.DataFrame()
            for tag_id, tag in self.tag_results.filtered_tags.tags.items():
                external_sensor_list = [p.decoded_data['external_sensor']
                                        for p in tag if 'external_sensor' in p.decoded_data.keys()]
                tags_stat_dict = {'adv_address': tag_id,
                                  'external_sensor_mean': np.mean(external_sensor_list)
                                  if len(external_sensor_list) else None}
                tag_id_df = pd.DataFrame(tags_stat_dict, index=[0])
                tags_stat_df = pd.concat([tags_stat_df, tag_id_df], axis=0)
        else:
            tags_stat_df = self.tag_results.filtered_tags.get_statistics()
        tags_reached_criteria = []
        if tags_stat_df.size > 0:
            for _, tag in tags_stat_df.iterrows():
                try:
                    criteria_status = [v[0] <= tag[k] <= v[-1] if k in tag.keys() and not pd.isnull(tag[k]) else False
                                       for k, v in stop_criteria_dict.items()]
                    if all(criteria_status):
                        tags_reached_criteria.append(tag['adv_address'] if 'adv_address' in tag.keys() else
                                                     tag['tag_id'])
                except Exception as e:
                    raise e

        return tags_reached_criteria

    def is_gw_fetal_error(self, packet_list=None):
        """
        check if the gw reset itself for some reason or if it needs to be reset
        :param packet_list: the received packets list
        :type packet_list: PacketList
        :return:
        :rtype:
        """
        if not self.GwObj.is_connected():
            self._printing_func('GW was disconnected. trying to initiate connection...', log_level=logging.WARNING)
            self.GwObj.open_port(self.GwObj.port, self.GwObj.baud)
            return True

        if self.GwObj.get_read_error_status():
            self._printing_func('A GW reading Error was detected', log_level=logging.WARNING)
            return True

        if packet_list is None:
            return False
        # check if GW's clock was reset (relevant only to GW ver 3.8.14 and lower)
        try:
            is_old_gw_ver = int(self.get_gw_version().split('.')[0]) < 4
        except Exception as e:
            is_old_gw_ver = True  # do the test next test anyway

        if is_old_gw_ver:
            counter = 0
            for p in packet_list:
                if p.gw_data['stat_param'].size > 1:
                    for s in p.gw_data['stat_param']:
                        if s == 0:
                            counter = counter + 1
                            if counter > 1:
                                return True
                else:
                    if p.gw_data['stat_param'] == 0:
                        counter = counter + 1
                        if counter > 1:
                            return True
        return False

    def statistics_analyzer(self, test_param=None, test_num=None):
        """
        test the quality of the test according to test_param
        :param test_param: the test parameters including the quality parameters which defines if
                           the tag passed or failed the test (e.g.
        :type test_param: dict
        :param test_num: the test number
        :type test_num: int
        :return: True if the tag passed the test
        :rtype: bool
        """

        # add test num to the packets:
        self.tag_results.add_selected_tag_statistics(custom_data={'test_num': test_num})
        if self.is_gw_fetal_error(self.tag_results.selected_tag):
            self.logger_results.warning('gw fetal error was detected')
            self.gw_reset_and_config()
            self.init_gw_test(sub_test=self.selected_test['tests'][0], is_start_gw_app=False)
            self.tag_results.test_status = FailureCodes.GW_ERROR
            targets_status = [False]
        elif 'quality_param' in test_param and len(test_param['quality_param']) > 0:
            targets_status = [v[0] <= self.tag_results.selected_tag_statistics[k] <= v[-1]
                              if k in self.tag_results.selected_tag_statistics.keys() else False
                              for k, v in test_param['quality_param'].items()]
            temp_values = {k: self.tag_results.selected_tag_statistics[k]
                           if k in self.tag_results.selected_tag_statistics.keys() else None
                           for k in test_param['quality_param'].keys()}
            self.logger_results.info(f'selected tag values: {temp_values}')
            self.tag_results.set_quality_test_failure(test_param['quality_param'], targets_status)

        else:
            targets_status = [True]

        return all(targets_status)

    def init_gw_test(self, sub_test, is_start_gw_app=True):
        # Config GW according to Test Suite
        self.GwObj.reset_listener()
        is_gw_commands = 'gw_commands' in sub_test
        self.GwObj.config_gw(energy_pattern_val=sub_test['energizingPattern'],
                             received_channel=int(sub_test['rxChannel']),
                             time_profile_val=sub_test['timeProfile'],
                             output_power_val=sub_test['gw_power_dict']['gw_output_power'],
                             bypass_pa_val=sub_test['gw_power_dict']['bypass_pa'],
                             sub1g_output_power_val=sub_test['sub1g_power'],
                             start_gw_app=is_start_gw_app and not is_gw_commands, with_ack=True, combined_msg=False)
        if is_gw_commands:
            for cmd in sub_test['gw_commands']:
                self.GwObj.write(cmd=cmd, with_ack=True)
            self.GwObj.config_gw(start_gw_app=is_start_gw_app, with_ack=True)

    def init_test(self, sub_test, is_start_gw_app=True, test_num=0):
        """
        initialize the test
        :param sub_test: the test parameter according to the test suite definition
        :type sub_test: dict
        :param is_start_gw_app: if True, the gw starts its application (transmit and receive)
        :type is_start_gw_app: bool
        :param test_num: the number of the sub=test in the same test
        :type test_num: int
        """
        self.test_end = False
        self.time_expired = False
        self.tag_results.test_start = datetime.datetime.now()

        self.logger_results.info(
            'Input parameters for GW:\nStage name : {}\nPattern '
            ': {}\nTime Profile : {}\nGW Power : {}dBm\nsub1G Power : {}dBm\nRX Channel : {}\n-----------------------'
            '--------------------------------------------------'.format(
                sub_test['name'], sub_test['energizingPattern'], sub_test['timeProfile'],
                sub_test['gw_power_dict']['abs_power'], sub_test['sub1g_power'], sub_test['rxChannel']))

        # Config GW according to Test Suite
        if test_num > 0:  # first sub-test is already config before the trigger
            self.init_gw_test(sub_test=sub_test, is_start_gw_app=is_start_gw_app)

        # doc config param
        self.tag_results.add_run_data(test_param=sub_test)

    def init_test_timers(self, max_ttfp, sub_test):
        """
        initialize the test timers - the whole test timer and the timer for ttfp if specified
        :param max_ttfp: the maximal ttfp (i.e. time to first packet) to wait before failing the test [in seconds]
        :type max_ttfp: float
        :param sub_test: the test parameters according to the test suite
        :type sub_test: dict
        """
        if max_ttfp is not None:
            self.first_packet_timer = threading.Timer(int(max_ttfp), self.end_of_time, ['First Packet'])
            self.first_packet_timer.start()
            self.logger.info('Timer for first packet has been set for {} seconds, test time is {} seconds'.format(
                max_ttfp, sub_test['maxTime']))
        else:
            self.logger.info('Timer for test has been set {} seconds'.format(sub_test['maxTime']))
        self.test_timer = threading.Timer(int(sub_test['maxTime']), self.end_of_time, ['Test'])
        self.test_timer.start()

    def reset_timers(self, only_first_packet_timer=False):
        """
        reset the test timers
        :param only_first_packet_timer: if True only the ttfp timer is reset
        :type only_first_packet_timer: bool
        :return:
        :rtype:
        """
        if self.first_packet_timer:
            self.first_packet_timer.cancel()
        if not only_first_packet_timer and self.test_timer:
            self.test_timer.cancel()

    def is_stopped_by_user(self):
        return self.stop_event_trig is not None and self.stop_event_trig.isSet()

    def _printing_func(self, msg, logger_name=LoggerName.MAIN, log_level=logging.INFO):
        """
        internal function to print the logs
        :param msg: the message to print
        :type msg: str
        :param logger_name: the logger name
        :type logger_name: LoggerName
        :param log_level: the log level
        :type log_level: logging.INFO
        """
        if self.verbose or log_level != logging.DEBUG:
            with self._lock_print:
                if logger_name.value == 'main':
                    self.logger.log(log_level, msg)
                elif logger_name.value == 'gw':
                    self.logger_gw.log(log_level, msg)
                elif logger_name.value == 'results':
                    self.logger_results.log(log_level, msg)

    def add_to_blacklist(self, new_blacklist):
        """
        add tags advertising address to the black list
        :param new_blacklist: new tag id to add to the black list
        :type new_blacklist: str or list
        """
        if isinstance(new_blacklist, list):
            self.black_list += new_blacklist
        elif isinstance(new_blacklist, str):
            self.black_list.append(new_blacklist)
        else:
            raise Exception('trying to add new member to black list of unsupported type: {}'.format(new_blacklist))

    def init_run(self):
        self.test_results = WiliotTesterTagResultList()
        self.tag_results = WiliotTesterTagResult(self.dev_mode)

    @staticmethod
    def check_type_per_test(stop_criteria_dict):
        check_type = 'general'
        if len(stop_criteria_dict.keys()) != 1:
            return check_type
        elif 'num_packets' in stop_criteria_dict:
            check_type = 'packets'
        elif 'external_sensor_mean' in stop_criteria_dict:
            check_type = 'external_sensor'
        return check_type

    def run(self, wait_for_gw_trigger=None, need_to_manual_trigger=True):
        """
        Flow:
        1. wait for trigger if wait_for_gw_trigger is specified.
        2. Collect filtered packets (e.g. filtered by rssi)
        3. Check if we reached stop criteria - according to stop criteria list
        4. Check if test passed according to performance criteria:
            A. identify the tag under test
            B. test the selected tag performance

        Stop Criteria list:
        1. test time expired
        2. time to first packet expired if max_ttfp is specified
        3. external stop event, is stop_event_trig was specified whn init the class
        4. parameter according to the tests_suite.json (e.g. number of packets)

        :param wait_for_gw_trigger: if specified, the test waits the specified seconds for the gw trigger and
                                    starts only when triggered
        :type wait_for_gw_trigger: float or NoneType
        :param need_to_manual_trigger: if True and wait_for_gw_trigger is not specified, a serial command is sent to
                                       the gw at the start of the test
        :return: the test results including all the tags and test information
        :rtype: WiliotTesterTagResultList
        """

        self._printing_func('New tag test starts from API', logger_name=LoggerName.RESULTS)

        self.init_run()

        # wait for trigger if needed
        if wait_for_gw_trigger is None:
            self.start_test = True
            if need_to_manual_trigger:
                self.GwObj.config_gw(start_gw_app=True, with_ack=True)
                self.GwObj.reset_start_time()
        else:
            self._printing_func('Wait for GW trigger for {} second'.format(wait_for_gw_trigger))
            self.start_test = self.wait_for_trigger(wait_for_gw_trigger)

        # check if test can be started:
        if self.is_stopped_by_user():
            self._printing_func('Run was stopped by the stop event before it started', log_level=logging.INFO)
            return self.test_results

        if not self.start_test:
            return self.test_results

        self.test_results.set_trigger_time()

        # Test begins
        self._printing_func('Trigger received')

        num_of_tests = len(self.selected_test['tests'])
        for test_num in range(num_of_tests):
            sub_test = self.selected_test['tests'][test_num]

            test_check_type = self.check_type_per_test(sub_test['stop_criteria'])

            # init sub-test
            self._printing_func('---------------------Started stage {} out of {} stages-----------------------'.
                                format(test_num + 1, num_of_tests), logger_name=LoggerName.RESULTS)
            self.tag_results = WiliotTesterTagResult(self.dev_mode)
            self.init_test(sub_test=sub_test, test_num=test_num)

            # Begin test timers
            self.init_test_timers(self.max_ttfp, sub_test)

            # Start test check
            tags_reached_criteria = []
            while not self.test_end and not self.time_expired:
                if self.is_stopped_by_user():
                    break
                # check if trigger was received during run:
                if self.check_if_trigger_was_received():
                    self._printing_func('Gateway got trigger during run. Please check the Machine')
                    raise Exception('Gateway got trigger during run. Please check the Machine')

                # collect filtered packets
                data_type = DataType.PACKET_LIST if not self.dev_mode else DataType.DECODED
                is_received_packet = self.get_packets(filter_value=self.selected_test['rssiThresholdSW'],
                                                      data_type=data_type)
                if is_received_packet:
                    self.reset_timers(only_first_packet_timer=True)
                    # check if we reached stop criteria:
                    tags_reached_criteria = self.check_stop_criteria(stop_criteria_dict=sub_test['stop_criteria'],
                                                                     check_type=test_check_type)

                    if len(tags_reached_criteria):
                        self._printing_func('test reached stop criteria - starting to analyze the results')
                        self.test_end = True
                else:
                    time.sleep(0)  # allow time for recovery
                    # check if GW ERROR occurred and fix it:
                    if self.is_gw_fetal_error():
                        self.logger_results.warning('gw fetal error was detected')
                        if not self.GwObj.is_connected():
                            raise Exception('Could not reconnect to the GW. please check connections')
                        self.gw_reset_and_config()
                        self.init_gw_test(sub_test=sub_test, is_start_gw_app=True)
                        self.tag_results.test_status = FailureCodes.GW_ERROR

            # stop gw from transmitting
            is_stopped = self.GwObj.stop_gw_app()
            if not is_stopped:
                self.logger_results.warning('could not stop GW app')
                self.gw_reset_and_config()
                self.init_gw_test(sub_test=sub_test, is_start_gw_app=True)

            # check again stop criteria:
            tags_reached_criteria = self.check_stop_criteria(stop_criteria_dict=sub_test['stop_criteria'],
                                                             check_type=test_check_type)
            if len(tags_reached_criteria) and not self.test_end:
                self._printing_func('test reached stop criteria just before time expired')
                self.test_end = True

            # check why the test is over
            if self.is_stopped_by_user():  # Stop event was triggered
                self._printing_func('Stop was triggered')
                self._printing_func('Tag marked as Fail', logger_name=LoggerName.RESULTS)
                self.reset_timers()
                self.tag_results.test_status = FailureCodes.STOP_BY_USER
                self.test_results.append(self.tag_results)

            elif self.test_end or sub_test['stop_criteria'] == {}:
                if sub_test['stop_criteria'] != {}:
                    selected_tag = self.select_tag_under_test(optional_tags=tags_reached_criteria)  # Get the best tag
                else:
                    all_optional_tags = list(self.tag_results.filtered_tags.tags.keys())
                    selected_tag = self.select_tag_under_test(optional_tags=all_optional_tags)  # Get the best tag

                all_selected_tags = self.test_results.get_test_unique_adva()
                is_diff_tag_btwn_sub_tests = selected_tag not in all_selected_tags and len(all_selected_tags) > 0
                if selected_tag and not is_diff_tag_btwn_sub_tests:
                    self._printing_func('Tag {} was selected'.format(selected_tag))
                    # selected tag performance:
                    self.tag_results.is_test_passed = self.statistics_analyzer(test_param=sub_test, test_num=test_num)
                    if self.tag_results.is_test_passed:
                        self.tag_results.test_status = FailureCodes.PASS
                        self._printing_func('Stage {} out of {} Passed'.format(test_num + 1, num_of_tests),
                                            logger_name=LoggerName.RESULTS)
                    else:
                        self._printing_func('Tag failed quality test', logger_name=LoggerName.RESULTS,
                                            log_level=logging.DEBUG)
                        self._printing_func('Stage {} out of {} Failed'.format(test_num + 1, num_of_tests),
                                            logger_name=LoggerName.RESULTS)
                elif selected_tag == '':
                    self.tag_results.test_status = FailureCodes.NO_RESPONSE
                    self._printing_func("No Responds during run_all mode")
                else:  # selected_tag is None:
                    self.tag_results.test_status = FailureCodes.SEVERAL_TAGS_UNDER_TEST
                    self._printing_func("Couldn't decide which tag transmitting, it will fail")

                self.reset_timers()
                self.test_results.append(self.tag_results)

            elif self.time_expired:  # time expired before reaching stop criteria
                # check again stop criteria:

                self._printing_func('Stage {} Failed - Timeout'.format(test_num + 1),
                                    logger_name=LoggerName.RESULTS)
                if self.tag_results.test_status == FailureCodes.GW_ERROR:
                    pass
                elif self.tag_results.all_packets.size() == 0:
                    self.tag_results.test_status = FailureCodes.NO_RESPONSE
                elif len(self.tag_results.filtered_tags) == 0:
                    self.tag_results.test_status = FailureCodes.NO_PACKETS_UNDER_RSSI_THR
                else:
                    self.tag_results.all_tags = self.tag_results.add_packets_to_multi_tags(
                        packets_in=self.tag_results.all_packets,
                        multi_tag_out=self.tag_results.all_tags)
                    self.tag_results.test_status = FailureCodes.NOT_ENOUGH_PACKETS
                self.test_results.append(self.tag_results)

            else:
                self.reset_timers()
                msg = 'test was stopped due to unknown reason'
                self._printing_func(msg, log_level=logging.WARNING)
                raise Exception('test was stopped due to unknown reason')

            # check if delays between stages/sub-test
            if 'delayBeforeNextTest' in sub_test:
                self._printing_func('Going to sleep for {} second '.format(sub_test['delayBeforeNextTest']))
                t_i = datetime.datetime.now()
                dt = datetime.datetime.now() - t_i
                while dt.total_seconds() < float(sub_test['delayBeforeNextTest']):
                    dt = datetime.datetime.now() - t_i
            # end of test:
            self.tag_results.test_end = datetime.datetime.now()
            if self.tag_results.test_status != FailureCodes.PASS and not self.run_all:
                break  # stop the test if one of the stages was failed

        # prepare gw for the next run:
        if num_of_tests > 1:
            self.init_gw_test(sub_test=self.selected_test['tests'][0], is_start_gw_app=False)
        self.reset_timers()
        return self.test_results

    def exit_tag_test(self, need_to_close_port=True):
        self.reset_timers()
        if need_to_close_port:
            self.GwObj.close_port(is_reset=True)
            self.GwObj.exit_gw_api()
        else:
            self.GwObj.reset_gw()
        self.GwObj.exit_gw_api()


def load_test_suite_file(tester_name):
    tester_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], tester_name)
    tests_suites_path = os.path.join(os.path.join(tester_path, 'configs'), 'tests_suites.json')
    tests_suites_eng = os.path.join(os.path.join(tester_path, 'configs'), 'tests_suites_eng.json')
    if os.path.isfile(tests_suites_eng):
        tests_suites_path = tests_suites_eng
    if os.path.isfile(tests_suites_path):
        with open(tests_suites_path) as json_file:
            test_suite = json.load(json_file)
    else:
        raise Exception(f'cannot find config file tests_suites.json under {tests_suites_path}')
    return test_suite


if __name__ == '__main__':
    from csv import DictWriter
    import os

    from wiliot_testers.wiliot_tester_log import WiliotTesterLog
    from wiliot_testers.wiliot_tester_tag_result import ConversionTypes, SurfaceTypes, FailureCodes
    from wiliot_testers.utils.get_version import get_version
    from wiliot_core import InlayTypes

    def stop_run():
        my_stop_event.set()


    def dict_to_csv(dict_in, path, append=False, only_titles=False):
        if append:
            method = 'a'
        else:
            method = 'w'
        with open(path, method, newline='') as f:
            dict_writer = DictWriter(f, fieldnames=dict_in.keys())
            if not append:
                dict_writer.writeheader()
            if not only_titles:
                dict_writer.writerow(dict_in)
            f.close()


    def update_run_data(run_data_path, run_data, res=None, save_to_csv=True):
        if res is not None:
            run_data['total_run_tested'] += 1
            run_data['total_run_passed_offline'] += res.get_total_test_status()
            run_data['run_responsive_tags_yield'] = \
                (run_data['total_run_responding_tags'] / run_data['total_run_tested']) * 100
            run_data['run_offline_yield'] = \
                (run_data['total_run_passed_offline'] / run_data['total_run_tested']) * 100

        if save_to_csv:
            dict_to_csv(dict_in=run_data, path=run_data_path)


    def update_packet_data(packets_data_path, res=None, test_data=None, only_titles=False):

        def save_default_packet_data(summary=None):
            default_data = {'raw_packet': None, 'adv_address': None, 'decrypted_packet_type': None,
                            'group_id': None, 'flow_ver': None,
                            'test_mode': None, 'en': None, 'type': None, 'data_uid': None, 'nonce': None,
                            'enc_uid': None, 'mic': None, 'enc_payload': None, 'gw_packet': None, 'rssi': None,
                            'stat_param': None, 'time_from_start': None, 'counter_tag': None,
                            'is_valid_tag_packet': None, 'common_run_name': test_data['common_run_name'],
                            'tag_run_location': test_data['tag_run_location'],
                            'total_test_duration': None, 'total_location_duration': None, 'status_offline': None,
                            'fail_bin': test_data['fail_bin'], 'fail_bin_str': test_data['fail_bin_str'],
                            'external_id': None,
                            'qr_validated': test_data['qr_validated'], 'test_num': test_data['test_num'],
                            'trigger_time': test_data['trigger_time'], 'packet_status': None,
                            'number_of_responding_tags': test_data['number_of_responding_tags']}
            if summary is None:
                default_sum = {'is_test_pass': None, 'selected_tag': None, 'test_start_time': None,
                               'test_end_time': None, 'test_status': None, 'rx_channel': None,
                               'energizing_pattern': None, 'time_profile': None, 'num_packets': 0,
                               'num_cycles': 0, 'sprinkler_counter_mean': None, 'sprinkler_counter_std': None,
                               'sprinkler_counter_min': None, 'sprinkler_counter_max': None, 'tbp_mean': None,
                               'tbp_std': None, 'tbp_min': None, 'tbp_max': None, 'tbp_num_vals': None,
                               'per_mean': None, 'per_std': None, 'rssi_mean': None, 'rssi_std': None,
                               'rssi_min': None, 'rssi_max': None, 'ttfp': None, 'rx_rate_normalized': None,
                               'rx_rate': None}
            else:
                default_sum = summary

            default_packet_att = {'is_valid_packet': None, 'inlay_type': None}
            default_dict = {**default_data, **default_sum, **default_packet_att}
            default_ordered_dict = {k: default_dict[k] for k in packet_headers_default}
            dict_to_csv(dict_in=default_ordered_dict, path=packets_data_path, append=(not only_titles),
                        only_titles=only_titles)

        if res is not None:
            test_data['status_offline'] = int(res.get_total_test_status())
            test_data['total_test_duration'] = res.get_total_test_duration()
            test_data['fail_bin'] = res.get_total_fail_bin()
            test_data['fail_bin_str'] = res.get_total_fail_bin(as_name=True)
            test_data['trigger_time'] = res.get_trigger_time()
            for i, r in enumerate(res):
                test_data['test_num'] = i
                r_sum = r.get_summary()

                # add packets info:
                if r.all_packets.size():
                    # we received packets
                    for p in r.all_packets:
                        p.add_custom_data(
                            custom_data={**test_data, **r_sum})
                    r.all_packets.to_csv(path=packets_data_path, append=True, export_packet_id=False,
                                         columns=packet_headers_default)
                else:
                    # no responds in current test
                    save_default_packet_data(summary=r_sum)

        else:
            test_data['test_num'] = 0
            save_default_packet_data()


    log_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    black_list = ['A', 'B']
    test_suite = {"Dual Band": {
        "plDelay": 100,
        "rssiThresholdHW": 86,
        "rssiThresholdSW": 56,
        "maxTtfp": 3,
        "tests": [
            {"name": "first_packets_ble_band",
             "rxChannel": 37,
             "energizingPattern": 18,
             "timeProfile": [5, 15],
             "absGwTxPowerIndex": -1,
             "maxTime": 3,
             "delayBeforeNextTest": 0,
             "stop_criteria": {"num_packets": [1, 99]},
             "quality_param": {"ttfp": [0, 3]},
             # 'gw_commands': ['!set_sub_1_ghz_energizing_frequency 916000',
             #                 '!set_dyn_energizing_pattern 6 0 1 2480',
             #                 '!set_beacons_pattern 375 3 2402 2426 2478']
             },
            {"name": "sub1G_band",
             "rxChannel": 37,
             "energizingPattern": 52,
             "timeProfile": [5, 15],
             "absGwTxPowerIndex": -1,
             "sub1gGwTxPower": 9,
             "maxTime": 3,
             "stop_criteria": {"num_packets": [2, 99]},
             "quality_param":
                 {
                 }
             }
        ]
    }}
    run_data = {'common_run_name': 'test_test', 'tester_station_name': 'Wiliot',
                'operator': 'Shunit', 'reel_run_start_time': None, 'reel_run_end_time': None,
                'batch_name': 'reel1', 'tester_type': 'offline', 'comments': '',
                'total_run_tested': 0, 'total_run_responding_tags': 0,
                'total_run_passed_offline': 0,
                'total_missing_labels': 0, 'run_responsive_tags_yield': float('nan'),
                'run_offline_yield': float('nan'), 'ttfp_avg': float('nan'),
                'conversion_type': ConversionTypes.STANDARD.value, 'inlay': InlayTypes.TEO_086.value,
                'test_suite': list(test_suite.keys())[0], 'test_suite_dict': test_suite,
                'surface': SurfaceTypes.AIR.value, 'to_print': True, 'qr_validation': True,
                'print_pass_job_name': 'job_name', 'printing_format': 'SGTIN',
                'external_id_prefix': 'aaa',
                'external_id_suffix_init_value': 0,
                'coupler_partnumber': 'abcd',
                'gw_version': None, 'py_wiliot_version': get_version(), 'upload_date': None, 'owner_id': 'wiliot-ops'}
    packet_headers_default = ['common_run_name', 'tag_run_location', 'test_num', 'external_id',
                              'time_from_start', 'raw_packet', 'rssi', 'packet_status', 'adv_address',
                              'selected_tag',
                              'is_test_pass', 'status_offline', 'fail_bin', 'fail_bin_str', 'test_status',
                              'num_packets', 'num_cycles', 'sprinkler_counter_mean', 'sprinkler_counter_std',
                              'sprinkler_counter_min', 'sprinkler_counter_max', 'tbp_mean', 'tbp_std',
                              'tbp_min', 'tbp_max', 'tbp_num_vals', 'per_mean', 'per_std', 'rssi_mean',
                              'rssi_std', 'rssi_min', 'rssi_max', 'ttfp', 'rx_rate_normalized', 'rx_rate',
                              'total_test_duration', 'total_location_duration', 'test_start_time',
                              'trigger_time', 'test_end_time',
                              'qr_validated', 'rx_channel', 'energizing_pattern', 'time_profile',
                              'decrypted_packet_type', 'group_id', 'flow_ver', 'test_mode', 'en',
                              'type', 'data_uid', 'nonce', 'enc_uid', 'mic', 'enc_payload', 'gw_packet',
                              'stat_param']
    run_name = run_data['common_run_name'] + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    my_logger = WiliotTesterLog(run_name=run_name)
    my_logger.set_logger(log_path=log_path)

    my_logger.create_data_dir(data_path=log_path, tester_name='offline', run_name=run_name)
    my_stop_event = threading.Event()

    wiliot_tag_test = WiliotTesterTagTest(selected_test='Dual Band', test_suite=test_suite,
                                          stop_event_trig=my_stop_event,
                                          logger_name=my_logger.logger.name,
                                          logger_result_name=my_logger.results_logger.name,
                                          logger_gw_name=my_logger.gw_logger.name,
                                          black_list=black_list,
                                          inlay=run_data['inlay'])

    run_data['gw_version'] = wiliot_tag_test.get_gw_version()
    wait_for_gw_trigger = None
    max_ttfp = test_suite['Dual Band']['maxTtfp']
    cont_run = True

    my_timer = threading.Timer(20, stop_run)
    my_timer.start()
    missing_label = False
    run_data['reel_run_start_time'] = datetime.datetime.now()
    test_data = {'common_run_name': run_data['common_run_name'], 'tag_run_location': 0, 'total_test_duration': None,
                 'total_location_duration': None,
                 'status_offline': False, 'fail_bin': FailureCodes.NONE.value, 'fail_bin_str': FailureCodes.NONE.name,
                 'external_id': 0, 'qr_validated': True,
                 'test_num': 0, 'trigger_time': None, 'number_of_responding_tags': 0}
    # update data files
    update_run_data(run_data_path=my_logger.run_data_path, run_data=run_data)
    update_packet_data(packets_data_path=my_logger.packets_data_path, only_titles=True, test_data=test_data)
    all_tags = []
    ttfp_num = 0
    ttfp_sum = 0
    while cont_run:
        # init test data:
        loc_start_time = datetime.datetime.now()
        test_data['total_test_duration'] = None
        test_data['status_offline'] = False
        # check if tag exists at the test env
        if missing_label:
            # TODO add here the logic for missing label
            run_data['total_missing_labels'] = run_data['total_missing_labels'] + 1
            test_data['fail_bin'] = FailureCodes.MISSING_LABEL.value
            test_data['tag_run_location'] = test_data['tag_run_location'] + 1

            update_run_data(run_data_path=my_logger.run_data_path, run_data=run_data)
            update_packet_data(packets_data_path=my_logger.packets_data_path, test_data=test_data)
            continue
        # ##################### test the tag ############################## #
        rsp = wiliot_tag_test.GwObj.write(cmd='!trigger_pl', with_ack=True)
        print(rsp)
        res = wiliot_tag_test.run(wait_for_gw_trigger=wait_for_gw_trigger)
        if res.is_results_empty():
            my_timer.cancel()
            raise Exception('Test was stopped before it started due to some reason')
        # ##################### test the tag ############################## #
        if res.is_all_tests_passed():
            print('********* PASS ************')
        # add ttfp avg:
        for r in res:
            if 'ttfp' in r.selected_tag_statistics:
                ttfp_sum = ttfp_sum + r.selected_tag_statistics['ttfp']
                ttfp_num = ttfp_num + 1

            # for p in r.all_packets:
            #     print('packet: {}, len:{}, status: {}'.format(p.packet_data['raw_packet'], len(p),
            #                                                   p.custom_data['packet_status']))
        if ttfp_num:
            run_data['ttfp_avg'] = ttfp_sum / ttfp_num

        # TODO move machine to the next tag
        total_loc_time = datetime.datetime.now() - loc_start_time
        test_data['total_location_duration'] = total_loc_time.total_seconds()
        # check duplication:
        selected_tag = res.check_and_get_selected_tag_id()
        if selected_tag != '':
            if selected_tag in all_tags:
                res.set_total_fail_bin(FailureCodes.DUPLICATION_OFFLINE)
                res.set_total_test_status(status=False)
                wiliot_tag_test.add_to_blacklist(selected_tag)
                res.set_packet_status(adv_address=selected_tag, status='duplication')
            else:
                all_tags.append(selected_tag)
        run_data['total_run_responding_tags'] = len(all_tags)
        test_data['number_of_responding_tags'] = len(res.get_test_unique_adva())

        # add packets to packet_data.csv:
        update_packet_data(res=res, packets_data_path=my_logger.packets_data_path, test_data=test_data)
        # update run_data:
        update_run_data(run_data_path=my_logger.run_data_path, run_data=run_data, res=res)

        if my_stop_event.isSet():
            cont_run = False
            my_timer.cancel()

        # end of tag test actions
        test_data['tag_run_location'] = test_data['tag_run_location'] + 1
        if res.is_all_tests_passed():
            test_data['external_id'] = test_data['external_id'] + 1

        time.sleep(0)

    wiliot_tag_test.exit_tag_test()
    run_data['reel_run_end_time'] = datetime.datetime.now()
    run_data['upload_date'] = datetime.datetime.now()
    dict_to_csv(run_data, path=my_logger.run_data_path)
    # upload data to cloud
    # TODO add here function to upload data to database/cloud
    print('blacklist: {}'.format(wiliot_tag_test.black_list))
    print('done')
