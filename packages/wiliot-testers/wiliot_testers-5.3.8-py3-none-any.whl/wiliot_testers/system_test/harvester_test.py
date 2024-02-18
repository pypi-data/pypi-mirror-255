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
'''
Eduard Tatievski
'''

import matplotlib.pyplot as plt
from wiliot_testers.calibration_test.calibration_test_by_tbp import *
from wiliot_core.packet_data import packet_list, packet, tag_collection
from wiliot_testers.test_equipment import Attenuator, EquipmentError
from wiliot_testers.wiliot_tester_log import *
import PySimpleGUI as SimGUI
import os
import pathlib
import datetime
import csv
import pandas as pd
import collections


class Harvester(object):

    def __init__(self):
        # Getting all wanted values
        self.num_of_chambers = 1  # Number of chambers connected
        self.min_tags_answering = 1
        self.gui_values = self.init_gui()
        # Create log folder if not exist and build new name
        self.init_name_path()
        # Create log class
        self.my_logger = WiliotTesterLog(self.run_name_date)
        self.my_logger.set_logger(self.log_path, tester_name='Harvester')
        # Connect to GW and Attenuator if selected
        self.init_hw()
        # Build new power list according to gui inputs
        # self.power_range = self.build_range()
        self.power = re.split('(d)', self.gui_values['power'])[0]
        self.my_logger.results_logger.info('Starting scan on power: {}'.format(self.power))
        self.frequency_range = list(range(int(self.gui_values['start_freq']), int(self.gui_values['stop_freq']) + 1,
                                          int(self.gui_values['step'])))
        self.all_results = pd.DataFrame({'Adva': [], 'Frequency': [], 'TBP': [], 'BB': []})
        self.scan()

    def calibrate_bb(self):
        if self.gw_obj.connected:
            self.gw_obj.reset_buffer()
            self.gw_obj.start_continuous_listener()
        for bb_val in reversed(self.bb_list):
            self.gw_obj.config_gw(energy_pattern_val=self.gui_values['pattern'],
                                  time_profile_val=[self.gui_values['onTime'], self.gui_values['totalTime']],
                                  output_power_val='pos3dBm',
                                  beacons_backoff_val=bb_val)

    def build_range(self):
        if not self.sub1g_enable:
            if self.attn_enable:
                for index, nrg in enumerate(self.abs_att_power_list):
                    if self.gui_values['lowerPower'] == nrg:
                        low_limit = index
                    if self.gui_values['higherPower'] == nrg:
                        high_limit = index
                power_range = self.abs_att_power_list[low_limit:high_limit + 1]
            else:
                for index, nrg in enumerate(self.abs_power_list):
                    if self.gui_values['lowerPower'] == nrg:
                        low_limit = index
                    if self.gui_values['higherPower'] == nrg:
                        high_limit = index
                power_range = self.abs_power_list[low_limit:high_limit + 1]

        else:
            if self.attn_enable:
                for index, nrg in enumerate(self.valid_attn_sub1g_output_power):
                    if self.gui_values['lowerPower'] == nrg:
                        low_limit = index
                    if self.gui_values['higherPower'] == nrg:
                        high_limit = index
                power_range = self.valid_attn_sub1g_output_power[low_limit:high_limit + 1]
            else:
                for index, nrg in enumerate(self.valid_sub1g_output_power):
                    if self.gui_values['lowerPower'] == nrg:
                        low_limit = index
                    if self.gui_values['higherPower'] == nrg:
                        high_limit = index
                power_range = self.valid_sub1g_output_power[low_limit:high_limit + 1]

        output_power = []
        for power in power_range:
            if int(power[:-3]) < 0:
                output_power.append('neg' + power[1:])
            else:
                output_power.append('pos' + power)

        return output_power

    def convert_power(self, power, sub1g=False):
        gw_power = None
        attn_power = None
        # Convert from neg3dBm to -3
        if power[:3] == 'neg':
            abs_power = 0 - int(power[3:-3])
        elif power[:3] == 'pos':
            abs_power = int(power[3:-3])
        else:
            abs_power = int(power[:-3])

        # Find the value for attenuator if available
        if sub1g:
            if self.attn_enable:
                for power_scan in self.valid_sub1g_output_power:
                    if int(power_scan[:-3]) > abs_power:
                        gw_power = int(power_scan[:-3])
                        attn_power = int(gw_power[:-3]) - abs_power
            else:
                gw_power = abs_power
                attn_power = 0

        else:
            if self.attn_enable:
                for power_scan in self.abs_power_list:
                    if int(power_scan[:-3]) > abs_power:
                        gw_power = int(power_scan[:-3])
                        attn_power = int(gw_power[:-3]) - abs_power
            else:
                gw_power = abs_power
                attn_power = 0
        return gw_power, attn_power

    def init_hw(self):

        try:
            self.gw_obj = WiliotGateway(auto_connect=True, logger_name=self.my_logger.gw_logger.name, verbose=False)
            time.sleep(1)
            if self.gw_obj.connected:
                self.gw_obj.reset_gw()
                self.gw_obj.reset_buffer()
                time.sleep(1.5)
                self.gw_obj.start_continuous_listener()
                self.gw_obj.write('!set_tester_mode 1', with_ack=True)
                self.gw_obj.write('!pl_gw_config 1', with_ack=True)
                self.gw_obj.write('!enable_brg_mgmt 0', with_ack=True)
                self.gw_obj.write('!listen_to_tag_only 1', with_ack=True)
                self.gw_obj.write('!energizing_prob_set 100', with_ack=True)
                self.my_logger.gw_logger.info('GW config finished')
            else:
                raise EquipmentError('Gateway Error - Verify WiliotGateway connection')
        except Exception as e:
            self.my_logger.gw_logger.warning(e)
            raise EquipmentError('Gateway Error - Verify WiliotGateway connection')
            self.gw_obj.close_port()

        if self.attn_enable:
            self.attntype = self.gui_values['attntype']
            self.attnval = int(self.gui_values['attnval'])

            try:
                self.attn_obj = Attenuator(str(self.attntype)).GetActiveTE()
                current_attn = self.attn_obj.Getattn()
                self.my_logger.gw_logger.info('Current attenuator values: {}'.format(current_attn))
            except Exception:
                raise EquipmentError('Attenuator Error - Verify Attenuator connection')

    def init_name_path(self):
        self.log_path = os.path.join('', 'logs')
        if not os.path.exists(self.log_path):
            pathlib.Path(self.log_path).mkdir(parents=True, exist_ok=True)
        self.time_start = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_name_date = str(self.gui_values['testName']) + '_' + str(self.time_start)
        self.full_name_path = os.path.join(self.log_path, self.run_name_date)
        self.packets_csv_path = os.path.join(self.full_name_path, self.run_name_date + '.csv')
        self.test_csv_path = os.path.join(self.full_name_path, self.run_name_date + '_tests.csv')

    def init_gui(self):

        # self.bb_list = [0, 2, 7, 12, 19, 20, 21, 22, 23, 24, 25, 27, 29, 30, 31, 32, 33, 36, 40]
        self.bb_list = [40, 36, 33, 32, 31, 30, 29, 27, 25, 24, 23, 22, 21, 20, 19, 12, 7, 2, 0]
        # self.bb_list = [12, 7, 2, 0]

        self.valid_sub1g_output_power = ['17dBm', '18dBm', '19dBm', '20dBm', '21dBm', '22dBm',
                                         '23dBm', '24dBm', '25dBm', '26dBm', '27dBm', '28dBm', '29dBm']

        self.valid_attn_sub1g_output_power = ['-10dBm', '-9dBm', '-8dBm', '-7dBm', '-6dBm', '-5dBm',
                                              '-4dBm', '-3dBm', '-2dBm', '-1dBm', '0dBm', '1dBm',
                                              '2dBm', '3dBm', '4dBm', '5dBm', '6dBm', '7dBm', '8dBm',
                                              '9dBm', '10dBm', '11dBm', '12dBm', '13dBm', '14dBm', '15dBm',
                                              '16dBm', '17dBm', '18dBm', '19dBm', '20dBm', '21dBm', '22dBm',
                                              '23dBm', '24dBm']

        self.abs_power_list = ['-21dBm', '-18dBm', '-15dBm', '-12dBm', '-8dBm', '-5dBm', '-2dBm',
                               '-1dBm', '0dBm', '1dBm', '2dBm', '3dBm', '4dBm', '6dBm',
                               '10dBm', '15dBm', '20dBm', '21dBm', '22dBm']

        self.abs_att_power_list = ['-35dbm', '-34dbm', '-33dbm', '-32dbm', '-31dbm', '-30dbm',
                                   '-29dbm', '-28dbm', '-27dbm', '-26dbm', '-25dbm', '-24dbm',
                                   '-23dbm', '-22dbm', '-21dbm', '-20dbm', '-19dbm', '-18dbm',
                                   '-17dbm', '-16dbm', '-15dbm', '-14dbm', '-13dbm', '-12dbm',
                                   '-11dbm', '-10dbm', '-9dbm', '-8dbm', '-7dbm', '-6dbm',
                                   '-5dbm', '-4dbm', '-3dbm', '-2dbm', '-1dbm', '0dbm',
                                   '1dbm', '2dbm', '3dbm', '4dbm', '5dbm', '6dbm',
                                   '7dbm', '8dbm', '9dbm', '10dbm', '11dbm',
                                   '12dbm', '13dbm', '14dbm', '15dbm', '16dbm', '17dbm']

        self.valid_output_power_vals = [
            {'abs_power': -21, 'gw_output_power': 'neg20dBm', 'bypass_pa': '1'},
            {'abs_power': -18, 'gw_output_power': 'neg16dBm', 'bypass_pa': '1'},
            {'abs_power': -15, 'gw_output_power': 'neg12dBm', 'bypass_pa': '1'},
            {'abs_power': -12, 'gw_output_power': 'neg8dBm', 'bypass_pa': '1'},
            {'abs_power': -8, 'gw_output_power': 'neg4dBm', 'bypass_pa': '1'},
            {'abs_power': -5, 'gw_output_power': 'pos0dBm', 'bypass_pa': '1'},
            {'abs_power': -2, 'gw_output_power': 'pos2dBm', 'bypass_pa': '1'},
            {'abs_power': -1, 'gw_output_power': 'pos3dBm', 'bypass_pa': '1'},
            {'abs_power': 0, 'gw_output_power': 'pos4dBm', 'bypass_pa': '1'},
            {'abs_power': 1, 'gw_output_power': 'pos5dBm', 'bypass_pa': '1'},
            {'abs_power': 2, 'gw_output_power': 'pos6dBm', 'bypass_pa': '1'},
            {'abs_power': 3, 'gw_output_power': 'pos7dBm', 'bypass_pa': '1'},
            {'abs_power': 4, 'gw_output_power': 'pos8dBm', 'bypass_pa': '1'},
            {'abs_power': 6, 'gw_output_power': 'neg12dBm', 'bypass_pa': '0'},
            {'abs_power': 10, 'gw_output_power': 'neg8dBm', 'bypass_pa': '0'},
            {'abs_power': 15, 'gw_output_power': 'neg4dBm', 'bypass_pa': '0'},
            {'abs_power': 20, 'gw_output_power': 'pos0dBm', 'bypass_pa': '0'},
            {'abs_power': 21, 'gw_output_power': 'pos2dBm', 'bypass_pa': '0'},
            {'abs_power': 22, 'gw_output_power': 'pos3dBm', 'bypass_pa': '0'}]

        SimGUI.theme('GreenTan')
        layout = [[SimGUI.Text('Test Name', auto_size_text=True)],
                  [SimGUI.Input(key='testName', readonly=False, size=(30, 1))],
                  [SimGUI.Text('Num of tags'),
                   SimGUI.Input(key='tagsNum', readonly=False, default_text=self.min_tags_answering, size=(4, 1))],
                  [SimGUI.Text('Test Time'),
                   SimGUI.Input(key='testTime', default_text='10', size=(7, 1))],
                  # [SimGUI.Text('Which TBP requested?'),
                  #  SimGUI.Input(key='requestedTBP', default_text='250', size=(7, 1))],
                  [SimGUI.Text('Frequency range: Start [MHz]:'),
                   SimGUI.Input(key='start_freq', default_text='2402', size=(5, 1)),
                   SimGUI.Text('Stop [MHz]:'),
                   SimGUI.Input(key='stop_freq', default_text='2480', size=(5, 1)),
                   SimGUI.Text('Step [MHz]'),
                   SimGUI.Input(key='step', default_text='2', size=(4, 1))],
                  [SimGUI.Text('Energy : ', size=(14, 1)),
                   SimGUI.InputCombo(tuple(self.abs_power_list), default_value=self.abs_power_list[0], key='power')],
                  # SimGUI.InputCombo(tuple(self.abs_power_list),
                  #                   default_value=self.abs_power_list[0], key='lowerPower'),
                  # SimGUI.InputCombo(tuple(self.abs_power_list),
                  #                   default_value=self.abs_power_list[-1], key='higherPower')],
                  [SimGUI.Text('Beacons backoff', size=(14, 1)),
                   SimGUI.InputCombo(tuple(self.bb_list),
                                     default_value=self.bb_list[0], key='lowerBB'),
                   SimGUI.InputCombo(tuple(self.bb_list),
                                     default_value=self.bb_list[-1], key='higherBB')],
                  [SimGUI.Button('2.4Ghz', button_color=('white', '#158225'), key='2.4mode', size=(10, 1)),
                   SimGUI.Button('Sub1G', button_color=('white', '#821515'), key='sub1gmode', size=(10, 1))],
                  [SimGUI.Text('Time profile - On:'),
                   SimGUI.Input(key='onTime', default_text='5', size=(3, 1)),
                   SimGUI.Text('Off:'),
                   SimGUI.Input(key='totalTime', default_text='15', size=(3, 1))],
                  [SimGUI.Button('Enable Attenuator', button_color=('white', '#158225'), key='attn', size=(20, 1))],
                  [SimGUI.Text('Attenuator Disabled', size=(40, 1), key='-ATTN-', text_color='Dark Red')],
                  [SimGUI.Text('Attenuator type: ', size=(14, 1), visible=False, key='attntypeen'),
                   SimGUI.InputCombo(('API', 'MCDI', 'MCDI-USB'),
                                     default_value='API', key='attntype', visible=False)],
                  [SimGUI.Text('Attenuation in dBm', visible=False, key='attnvalen'),
                   SimGUI.Input(key='attnval', visible=False, default_text='0', size=(4, 1))],
                  [SimGUI.Text(size=(40, 1), key='-OUTPUT-', text_color='red', font='bold')],
                  [SimGUI.Button('Submit', button_color=('white', '#0e6251'))]]

        window = SimGUI.Window('Harvester Test', layout, auto_size_text=True, auto_size_buttons=False)
        self.attn_enable = False
        self.sub1g_enable = False
        while True:
            event, values = window.read()
            # See if user wants to quit or window was closed
            if event == 'sub1gmode':
                self.sub1g_enable = True
                window['2.4mode'].update(button_color=('white', '#821515'))
                window['sub1gmode'].update(button_color=('white', '#158225'))
                window['power'].update(values=tuple(self.valid_sub1g_output_power),
                                       value=self.valid_sub1g_output_power[0])
                window['start_freq'].update(value='850')
                window['stop_freq'].update(value='940')
                # if self.attn_enable:
                #     window['lowerPower'].update(value=self.valid_attn_sub1g_output_power[0],
                #                                 values=tuple(self.valid_attn_sub1g_output_power))
                #     window['higherPower'].update(values=tuple(self.valid_attn_sub1g_output_power),
                #                                  value=self.valid_attn_sub1g_output_power[-1])
                # else:
                #     window['lowerPower'].update(values=tuple(self.valid_sub1g_output_power),
                #                                 value=self.valid_sub1g_output_power[0])
                #     window['higherPower'].update(values=tuple(self.valid_sub1g_output_power),
                #                                  value=self.valid_sub1g_output_power[-1])

            if event == '2.4mode':
                self.sub1g_enable = False
                window['2.4mode'].update(button_color=('white', '#158225'))
                window['sub1gmode'].update(button_color=('white', '#821515'))
                window['power'].update(values=tuple(self.abs_power_list),
                                       value=self.abs_power_list[0])
                window['start_freq'].update(value='2402')
                window['stop_freq'].update(value='2480')
                # if self.attn_enable:
                #     window['lowerPower'].update(value=self.abs_att_power_list[0],
                #                                 values=tuple(self.abs_att_power_list))
                #     window['higherPower'].update(values=tuple(self.abs_att_power_list),
                #                                  value=self.abs_att_power_list[-1])
                # else:
                #     window['lowerPower'].update(values=tuple(self.abs_power_list),
                #                                 value=self.abs_power_list[0])
                #     window['higherPower'].update(values=tuple(self.abs_power_list),
                #                                  value=self.abs_power_list[-1])

            if event == 'attn':
                self.attn_enable = not self.attn_enable
                if self.attn_enable:
                    window['-ATTN-'].update('Attenuator Enabled', text_color='Dark Green')
                    window['attn'].update('Disable Attenuator', button_color=('white', '#821515'))
                    window['attntype'].update(visible=True)
                    window['attntypeen'].update(visible=True)
                    window['attnval'].update(visible=True)
                    window['attnvalen'].update(visible=True)
                    # if self.sub1g_enable:
                    #     window['lowerPower'].update(value=self.valid_attn_sub1g_output_power[0],
                    #                                 values=tuple(self.valid_attn_sub1g_output_power))
                    #     window['higherPower'].update(values=tuple(self.valid_attn_sub1g_output_power),
                    #                                  value=self.valid_attn_sub1g_output_power[-1])
                    # else:
                    #     window['lowerPower'].update(value=self.abs_att_power_list[0],
                    #                                 values=tuple(self.abs_att_power_list))
                    #     window['higherPower'].update(values=tuple(self.abs_att_power_list),
                    #                                  value=self.abs_att_power_list[-1])

                else:
                    window['-ATTN-'].update('Attenuator Disabled', text_color='Dark Red')
                    window['attn'].update('Enable Attenuator', button_color=('white', '#158225'))
                    window['attntype'].update(visible=False)
                    window['attntypeen'].update(visible=False)
                    window['attnval'].update(visible=False)
                    window['attnvalen'].update(visible=False)
                    # if self.sub1g_enable:
                    #     window['lowerPower'].update(values=tuple(self.valid_sub1g_output_power),
                    #                                 value=self.valid_sub1g_output_power[0])
                    #     window['higherPower'].update(values=tuple(self.valid_sub1g_output_power),
                    #                                  value=self.valid_sub1g_output_power[-1])
                    # else:
                    #     window['lowerPower'].update(values=tuple(self.abs_power_list),
                    #                                 value=self.abs_power_list[0])
                    #     window['higherPower'].update(values=tuple(self.abs_power_list),
                    #                                  value=self.abs_power_list[-1])

            if event == SimGUI.WINDOW_CLOSED or event is None:
                print('User exited program')
                sys.exit(0)
            if event == 'Submit':
                if ' ' in values['testName'] or '/' in values['testName'] or '\\' in values['testName'] or values[
                    'testName'] == '':
                    window['-OUTPUT-'].update('Please enter valid run name without / or spaces')
                    continue
                else:
                    try:
                        # requestedTBP = int(values['requestedTBP'])
                        onTime = int(values['onTime'])
                        totalTime = int(values['totalTime'])
                        start_f = int(values['start_freq'])
                        stop_f = int(values['stop_freq'])
                        step_f = int(values['step'])
                        self.min_tags_answering = int(values['tagsNum'])
                        start_index = self.bb_list.index(values['lowerBB'])
                        end_index = self.bb_list.index(values['higherBB'])
                        direction = -1 if start_index > end_index else 1
                        self.new_bb_list = self.bb_list[start_index:end_index + direction:direction]
                        if self.sub1g_enable:
                            if start_f not in range(849, 941) or stop_f not in range(849, 941):
                                window['-OUTPUT-'].update(
                                    'Please enter valid Frequency range for Sub1G')
                                continue
                        else:
                            if start_f not in range(2400, 2490) or stop_f not in range(2400, 2490):
                                window['-OUTPUT-'].update(
                                    'Please enter valid Frequency range for 2.4GHz')
                                continue
                        break
                    except Exception:
                        window['-OUTPUT-'].update('Please enter valid Time Profile/ Test Time / Frequency values')
                        continue

        window.close()
        return values

    def packet_filter(self, packet_list, filter_param='rssi', param_limits=None):
        """
        filter the packets from the packet_list according to the filter_param and the param_limits.
        packets that were filtered out of the test does no take into account during the test and considered as noise
        :param packet_list: the incoming packets list
        :type packet_list: PacketList
        :param filter_param: one of the packet dataframe column names
        :type filter_param: str
        :param param_limits: list of two elements [x, y] that defines the range of the valid param (x,y including)
        :type param_limits: list
        :return: the filtered packet list
        :rtype: PacketList
        """

        def update_custom_data(packet, key, value):
            if key in packet.custom_data.keys():
                packet.custom_data[key].append(value)
            else:
                packet.custom_data[key] = [value]

        if param_limits is None:
            param_limits = [0, float('inf')]
        filtered_packet_list = PacketList()

        for p in packet_list:
            # filter packets from black list:
            if p.packet_data['adv_address'] in self.black_list:
                p.add_custom_data(custom_data={'packet_status': 'blacklist'})
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

    def init_timer(self):
        self.timeout = False
        self.success = False
        self.clean_gw()
        self.timer = threading.Timer(int(self.gui_values['testTime']), self.time_expire)

    def start_analyze(self, power=None, freq=None, bb=None):
        tbp = None
        for tag_adva in self.all_tags.tags:
            if self.is_gw_fetal_error(self.all_tags.tags[tag_adva]):
                self.my_logger.gw_logger.warning('gw fetal error was detected')
                self.gw_reset_and_config()
            for packet in self.all_tags.tags[tag_adva].packet_list:
                self.all_tests.append(packet)
            try:
                tbp = self.all_tags.get_avg_tbp_by_id(tag_adva)
                packets_sum = self.all_tags.get_statistics_by_id(tag_adva)['num_packets']
            except Exception as e:
                self.my_logger.logger.info(
                    'Exception receiving TBP or Packets num on tag {}, exception {}'.format(tag_adva, e))
                tbp = None
            new_row = {'Adva': tag_adva, 'Frequency': freq, 'TBP': tbp, 'BB': bb}
            new_df = pd.DataFrame(new_row, index=[0])
            self.all_results = pd.concat([self.all_results, new_df], ignore_index=True)
            details = {'Test Num': self.test_num, 'BB': bb, 'Frequency': freq, 'Power': power, 'Packets': packets_sum,
                       'TBP': tbp}
            if self.all_tests.tags[tag_adva].list_custom_data.__len__() == 0:
                self.all_tests.tags[tag_adva].list_custom_data['Data'] = []
            self.all_tests.tags[tag_adva].list_custom_data['Data'].append(details)

    def get_packets(self, filter_param='rssi', filter_value=100, power=None, freq=None, bb=None):
        """
        receive packets from the gw (via the listener) and filter them according to packet_filter()
        :param filter_param: one of the packet dataframe column names (for packet_filter)
        :type filter_param: str
        :param filter_value: the max valid value of the specified param
        :type filter_value: int
        :return: True if packet were received
        :rtype: bool
        """
        packets_received_list = None
        self.num_good_tags = 0
        self.num_bad_tags = 0
        if self.gw_obj.is_data_available():
            packets_received_list = self.gw_obj.get_packets(action_type=ActionType.ALL_SAMPLE,
                                                            data_type=DataType.PACKET_LIST)
        if packets_received_list:
            for packet in packets_received_list:
                packet_param_list = int(packet.get_average_rssi())
                if filter_value >= packet_param_list:
                    self.my_logger.logger.info('got packet {}'.format(packet.packet_data['raw_packet']))
                    self.all_tags.append(packet=packet.copy())
                else:
                    self.my_logger.logger.info(
                        'got packet {} but with high rssi {}'.format(packet.packet_data['raw_packet'],
                                                                     packet_param_list))
                    continue

                if self.all_tags.tags.__len__() > 0:  # self.num_of_chambers:  # If we got more then X chamber tags and at least X chambers * 4 packets for each tag
                    for packet_list in self.all_tags.tags:
                        try:
                            avg_tbp = self.all_tags.tags[packet_list].get_avg_tbp()
                            if avg_tbp > 0:
                                self.num_good_tags += 1
                        except Exception:
                            pass
                        if self.num_good_tags >= self.min_tags_answering:
                            self.num_bad_tags = self.all_tags.tags.__len__() - self.num_good_tags
                            self.success = True
                        else:
                            continue
                if self.success:
                    self.my_logger.logger.info(
                        'Found {} tags\n{} tags TBP was calculated\n{} tags TBP wasnt calculated\nStarting analyzing'.format(
                            self.all_tags.tags.__len__(), self.num_good_tags, self.num_bad_tags))
                    break

        if self.success:
            self.timer.cancel()
            self.gw_obj.stop_gw_app()
            self.clean_gw()
            self.gw_obj.stop_continuous_listener()
            self.start_analyze(power, freq, bb)

    def is_gw_fetal_error(self, packet_list):
        """
        check if the gw reset itself for some reason
        :param packet_list: the received packets list
        :type packet_list: PacketList
        :return:
        :rtype:
        """
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

    def get_result(self):
        return self.all_tests

    def time_expire(self):
        self.timeout = True
        self.timer.cancel()
        # self.gw_obj.stop_gw_app()
        self.my_logger.results_logger.info(
            'Timeout - found {} tags but didnt received enough packets to calculate TBP for all, calculated only for {} tags'.format(
                self.all_tags.tags.__len__(), self.num_good_tags))

    def gw_reset_and_config(self):
        self.gw_obj.reset_gw()
        time.sleep(2)
        self.gw_obj.write('!set_tester_mode 1', with_ack=True)
        self.gw_obj.write('!enable_brg_mgmt 0', with_ack=True)
        self.gw_obj.write('!listen_to_tag_only 1', with_ack=True)
        self.gw_obj.write('!energizing_prob_set 100', with_ack=True)

    def clean_gw(self):
        self.gw_obj.reset_buffer()
        self.gw_obj.reset_listener()

    def data_read_analyze(self, dict=None):

        # Get unique BB values
        self.all_results = self.all_results.dropna(subset=['TBP'])

        unique_bbs = self.all_results['BB'].unique()

        # Set up subplots
        fig, axes = plt.subplots(nrows=1, ncols=unique_bbs.size, figsize=(10, 4))

        # Loop over unique BB values and plot graphs
        for i, bb in enumerate(unique_bbs):
            # Get data for current BB value
            bb_df = self.all_results[self.all_results['BB'] == bb]
            # Get unique Adva names for current BB value
            unique_adv = bb_df['Adva'].unique()

            # Plot graph for current BB value on the appropriate subplot
            ax = axes[i]
            ax.set_title(f"Beacon Backoff = {bb}")
            freq_ticks = sorted(self.all_results['Frequency'].unique())
            ax.set_xticks(self.x_grid, rotation=90)
            ax.set_xlabel("Frequency")
            ax.set_ylabel("TBP")
            for adv in unique_adv:
                adv_df = bb_df[bb_df['Adva'] == adv]
                ax.plot(adv_df['Frequency'], adv_df['TBP'], label=adv)
            ax.legend()

        # Show the plot
        plt.show()

    def finish(self):
        # Start writing all data to file
        self.all_results = self.all_results.groupby('Adva').apply(
            lambda x: x.sort_values(by=['Frequency', 'BB'], ascending=[True, False])).reset_index(drop=True)

        self.my_logger.results_logger.info(self.all_results)
        for i in self.all_results:
            self.my_logger.results_logger.info(i)
        self.all_packet_list = self.all_tests.to_packet_list()
        all_data = []
        custom_data = {'Test Num': '', 'Adva': '', 'BeaconBackoff': '', 'Frequency': '', 'Power': '', 'Packets': '',
                       'TBP': ''}
        for packet_list in self.all_tests.tags:
            for custom in self.all_tests.tags[packet_list].list_custom_data['Data']:
                p_list_data = {'Test Num': '', 'Adva': '', 'BeaconBackoff': '', 'Frequency': '', 'Power': '',
                               'Packets': '', 'TBP': ''}
                p_list_data['Adva'] = packet_list
                p_list_data['Test Num'] = custom['Test Num']
                p_list_data['BeaconBackoff'] = custom['BB']
                p_list_data['Frequency'] = custom['Frequency']
                p_list_data['Power'] = custom['Power']
                p_list_data['Packets'] = custom['Packets']
                p_list_data['TBP'] = custom['TBP'] if custom['TBP'] is not None else 0
                all_data.append(p_list_data)
        try:
            with open(self.test_csv_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=custom_data)
                writer.writeheader()
                writer.writerows(all_data)

        except IOError:
            print("I/O error")

        try:
            self.all_tests.to_csv(path=self.packets_csv_path, val='adv_address')
        except Exception:
            self.my_logger.logger.warning('Empty list')
        # Read data from file organized with pandas

        # Draw graphs according to post process correlated to TBP requested
        if len(self.frequency_range) > 8:
            self.x_grid = self.frequency_range[::3]
            if len(self.frequency_range) > 15:
                self.x_grid = self.frequency_range[::4]
                if len(self.frequency_range) > 28:
                    self.x_grid = self.frequency_range[::5]
        else:
            self.x_grid = self.frequency_range
        self.data_read_analyze()
        # The End
        self.my_logger.logger.info('Finished')

    def config_gw(self, power, freq, bb):
        if not self.sub1g_enable:
            # ---------------------------------------------------------------------------------------------------------------------
            # 2.4 + Attenuator
            if self.attn_enable:
                # abs_power_val, abs_attn_val = self.convert_power(power, sub1g=False)
                # for list_power_val in self.valid_output_power_vals:
                #     if abs_power_val == list_power_val['abs_power']:
                #         gw_out_power = list_power_val['gw_output_power']
                self.my_logger.logger.info(
                    'Setting GW power: {}, Attenuation value: {} Frequency {} Beacaon Backoff val {}'.format(
                        power, self.attnval, freq, bb))
                self.attn_obj.Setattn(self.attnval)
                self.gw_obj.config_gw(energy_pattern_val=18,
                                      time_profile_val=[self.gui_values['onTime'],
                                                        self.gui_values['totalTime']],
                                      beacons_backoff_val=bb,
                                      received_channel='37',
                                      effective_output_power_val=int(power),
                                      start_gw_app=True,
                                      with_ack=True)
            # ---------------------------------------------------------------------------------------------------------------------
            # 2.4 + No Attenuator
            else:
                # abs_power_val, abs_attn_val = self.convert_power(power, sub1g=False)
                # if int(abs_power_val) > 5:
                #     bypass_pa_val = 0
                # else:
                #     bypass_pa_val = 1
                # for list_power_val in self.valid_output_power_vals:
                #     if abs_power_val == int(list_power_val['abs_power']):
                #         gw_out_power = list_power_val['gw_output_power']
                self.my_logger.logger.info(
                    'Setting GW power: {}, No attenuation Frequency {} Beacaon Backoff val {}'.format(
                        power, freq, bb))
                self.gw_obj.config_gw(energy_pattern_val=18,
                                      time_profile_val=[self.gui_values['onTime'],
                                                        self.gui_values['totalTime']],
                                      beacons_backoff_val=bb,
                                      received_channel='37',
                                      effective_output_power_val=int(power),
                                      start_gw_app=True,
                                      with_ack=True)
        # ---------------------------------------------------------------------------------------------------------------------
        # Sub1G
        else:
            # ---------------------------------------------------------------------------------------------------------------------
            # Sub1G + Attenuator
            if self.attn_enable:
                # abs_power_val, abs_attn_val = self.convert_power(power, sub1g=True)
                self.my_logger.logger.info(
                    'Setting Sub1G GW power: {}, Attenuation value: {} Frequency {} Beacaon Backoff val {}'.format(
                        power, self.attnval, freq, bb))
                self.attn_obj.Setattn(self.attnval)
                self.gw_obj.config_gw(energy_pattern_val=50,
                                      time_profile_val=[self.gui_values['onTime'],
                                                        self.gui_values['totalTime']],
                                      beacons_backoff_val=bb,
                                      received_channel='37',
                                      effective_output_power_val=22,
                                      sub1g_output_power_val=power,
                                      start_gw_app=True,
                                      with_ack=True)
            # ---------------------------------------------------------------------------------------------------------------------
            # Sub1G + No Attenuator
            else:
                # abs_power_val, abs_attn_val = self.convert_power(power, sub1g=True)
                self.my_logger.logger.info(
                    'Setting Sub1G GW power: {}, No attenuation value Frequency {} Beacaon Backoff val {}'.format(
                        power, freq, bb))
                self.gw_obj.config_gw(energy_pattern_val=50,
                                      time_profile_val=[self.gui_values['onTime'],
                                                        self.gui_values['totalTime']],
                                      beacons_backoff_val=bb,
                                      received_channel='37',
                                      effective_output_power_val=22,
                                      sub1g_output_power_val=power,
                                      start_gw_app=True,
                                      with_ack=True)
        # ---------------------------------------------------------------------------------------------------------------------
        if self.sub1g_enable:
            self.gw_obj.write('!set_dyn_energizing_pattern 6 1 0 0', with_ack=True)
            self.gw_obj.write('!set_beacons_pattern 550 3 2402 2426 2480', with_ack=True)
            self.gw_obj.write('!set_sub_1_ghz_energizing_frequency {}'.format(freq), with_ack=True)

        else:
            self.gw_obj.write('!set_dyn_energizing_pattern 6 0 1 {}'.format(freq), with_ack=True)
            self.gw_obj.write('!set_beacons_pattern 550 3 2402 2426 2480', with_ack=True)

    def scan(self):
        self.all_tests = TagCollection()
        self.test_num = 0
        self.results = []
        # Scan power
        power = self.power
        self.my_logger.logger.info('Sweeping freq {}'.format(self.frequency_range))
        # Scan frequency
        for freq in self.frequency_range:
            # Scan beacon backoff
            for index, bb in enumerate(self.new_bb_list):
                self.test_num += 1
                # 2.4Ghz
                self.all_tags = TagCollection()
                self.gw_obj.start_continuous_listener()
                self.init_timer()  # Init timeout flag and reset success flag
                self.timer.start()  # Start timer thread
                self.my_logger.results_logger.info(
                    '-' * 30 + 'New Test - Power {} Frequency {} Beacon Backoff {}'.format(power, freq,
                                                                                           bb) + '-' * 30)

                self.config_gw(power=power, freq=freq, bb=bb)

                # Start receiving packets
                while not self.timeout and not self.success:  # While function to work until timeout or success test
                    time.sleep(0.01)
                    self.get_packets(power=power, freq=freq,
                                     bb=bb)  # Will start to get packets, then analyze them and add to self.all_tests with custom data of which test it came from

                self.clean_gw()  # clear the buffers
                time.sleep(0.5)

        self.gw_obj.close_port(is_reset=True)
        self.gw_obj.stop_continuous_listener()
        self.finish()


if __name__ == '__main__':
    harvest = Harvester()
    results = harvest.get_result()
    pass

