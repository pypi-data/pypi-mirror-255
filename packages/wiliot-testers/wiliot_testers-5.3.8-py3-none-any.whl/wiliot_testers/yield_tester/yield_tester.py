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
"""
Calculating Yield fraction by the following steps (with elaboration):
1)Counting the unique advas in AdvaProcess class
2)Counting number of tags in CountThread
3)Creating two threads in MultiThreadingCalculation in order to run AdvaProcess instance and CountThread instance
at the same time
4)Calculating the Yield fraction according to the results we got from the instances
5)Creating two threads in MainWindow class in order to calculate the fraction by MultiThreadingCalculation instance
and to run the GUI function (open_session) at the same time.
"""
import sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from wiliot_core import *
from wiliot_testers.test_equipment import YoctoSensor
from configs.inlay_data import csv_dictionary

import serial
from wiliot_testers.tester_utils import dict_to_csv
import logging
import threading
import time
import datetime
import matplotlib
import PySimpleGUI as sg
import json
import matplotlib.pyplot as plt

from wiliot_testers.utils.get_version import get_version
from wiliot_testers.utils.upload_to_cloud_api import upload_to_cloud_api
from wiliot_testers.yield_tester.simulation.yield_simulation_utils import get_simulated_gw_port, \
    AUTO_TRIGGERS, AUTO_PACKET, TIME_BETWEEN_AUTO_TRIGGERS
from wiliot_testers.yield_tester.utils.get_arduino_ports import get_arduino_ports

SECONDS_WITHOUT_PACKETS = 60
SECONDS_FOR_GW_ERROR_AFTER_NO_PACKETS = 120
RED_COLOR = 'red'
BLACK_COLOR = 'black'
SET_VALUE_MORE_THAN_100 = 110
VALUE_WHEN_NO_SENSOR = -10000
MIN_Y_FOR_PLOTS = 0
MAX_Y_FOR_PLOTS = 112
FIRST_STEP_SIZE = 10
BAUD_ARDUINO = 1000000
MAND_FIELDS = ['wafer_lot', 'wafer_num', 'matrix_sec', 'matrix_num', 'thermodes_col',
               'rows_number']  # mandatory fields in GUI before the run
PACKET_DATA_FEATURES_TITLE = [
    'raw_packet', 'adv_address', 'decrypted_packet_type', 'group_id',
    'flow_ver', 'test_mode', 'en', 'type', 'data_uid', 'nonce', 'enc_uid',
    'mic', 'enc_payload', 'gw_packet', 'rssi', 'stat_param', 'time_from_start',
    'counter_tag', 'is_valid_tag_packet', 'gw_process', 'is_valid_packet', 'inlay_type'
]

script_dir = os.path.dirname(__file__)
json_file_path = os.path.join(script_dir, 'configs', 'user_inputs.json')
try:

    with open(json_file_path) as f:
        user_inputs = json.load(f)
except Exception as e:
    user_inputs = {
        "min_cumulative": "60",
        "min_cumulative_line": "yes",
        "min_current": "20",
        "min_current_line": "yes",
        "max_temperature": "40",
        "min_temperature": "10",
        "temperature_type": "C",
        "min_humidity": "20",
        "max_humidity": "90",
        "min_light_intensity": "0",
        "max_light_intensity": "1500",
        "red_line_cumulative": "85",
        "red_line_current": "50"
    }
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
    with open(json_file_path, 'w') as f:
        json.dump(user_inputs, f, indent=4)

matplotlib.use('TkAgg')
inlay_types_dict = {item.name: item.value for item in InlayTypes}
today = datetime.date.today()
formatted_today = today.strftime("%Y%m%d")  # without -
formatted_date = today.strftime("%Y-%m-%d")
current_time = datetime.datetime.now()
cur_time_formatted = current_time.strftime("%I%M%S")  # without :
time_formatted = current_time.strftime("%I:%M:%S")
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
root_logger = logging.getLogger()

for handler in root_logger.handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.setLevel(logging.INFO)

sg.theme('GreenTan')


class AdvaProcess(object):
    """
    Counting the number of unique advas
    """

    def __init__(self, stop_event, received_channel, time_profile_val, energy_pattern_val, inlay_type, logging_file,
                 advas_before_tags, listener_path):
        self.gw_error_connection = False
        self.second_without_packets = False
        self.gw_instance = None
        self.logger_file = logging_file
        self.listener_path = listener_path
        self.all_tags = Queue()
        self.advas_before_tags = advas_before_tags
        self.stop = stop_event
        self.received_channel = received_channel
        self.gw_start_time = datetime.datetime.now()
        self.init_gw(listener_path)
        self.time_profile_val = ''
        try:
            self.time_profile_val = [int(time_pr) for time_pr in time_profile_val]
        except Exception as ee:
            raise Exception(f'could not retireive time profile from inlay_data value for {inlay_type}.\n'
                            f'time profile should be x,y but was {time_profile_val} [{ee}]')
        self.energy_pattern_val = energy_pattern_val
        self.inlay_type = inlay_type
        self.gw_reset_config()
        time.sleep(1)

    def init_gw(self, listener_path=None):

        try:
            if self.gw_instance is None:
                gw_port = get_simulated_gw_port() if AUTO_PACKET else None
                self.gw_instance = WiliotGateway(auto_connect=True,
                                                 logger_name='yield',
                                                 is_multi_processes=sys.platform != "darwin",
                                                 log_dir_for_multi_processes=listener_path,
                                                 port=gw_port,
                                                 np_max_packet_in_buffer_before_error=10)
            else:
                # reconnect
                is_connected = self.gw_instance.is_connected()
                if is_connected:
                    self.gw_instance.close_port()
                self.gw_instance.open_port(self.gw_instance.port, self.gw_instance.baud)

            is_connected = self.gw_instance.is_connected()
            if is_connected:
                self.gw_instance.start_continuous_listener()
            else:
                self.logger_file.warning("Couldn't connect to GW in main thread")
                raise Exception(f"Couldn't connect to GW in main thread")

        except Exception as ee:
            raise Exception(f"Couldn't connect to GW in main thread, error: {ee}")

    def get_gw_start_time(self):
        return self.gw_start_time

    def get_gw_error_connection(self):
        return self.gw_error_connection

    def gw_reset_config(self, start_gw_app=False):
        """
        Configs the gateway
        """
        if self.gw_instance.connected:
            self.gw_instance.reset_gw()
            self.gw_instance.reset_listener()
            time.sleep(2)
            if not self.gw_instance.is_gw_alive():
                self.logger_file.warning('gw_reset_and_config: gw did not respond')
                raise Exception('gw_reset_and_config: gw did not respond after rest')
            self.gw_instance.config_gw(received_channel=self.received_channel, time_profile_val=self.time_profile_val,
                                       energy_pattern_val=self.energy_pattern_val,
                                       start_gw_app=start_gw_app, with_ack=True,
                                       effective_output_power_val=22, sub1g_output_power_val=29, max_wait=400)
        else:
            raise Exception('Could NOT connect to GW')

    def run(self):
        """
        Receives available data then counts and returns the number of unique advas.
        """
        self.gw_instance.config_gw(start_gw_app=True, max_wait=400)
        self.gw_instance.reset_start_time()
        self.gw_start_time = datetime.datetime.now()
        got_new_adva = False
        no_data_start_time = None  # Time when we first detect no data available

        while not self.stop.is_set():
            if self.gw_instance.is_data_available():
                raw_packets_in = self.gw_instance.get_packets(action_type=ActionType.ALL_SAMPLE,
                                                              data_type=DataType.RAW, tag_inlay=self.inlay_type)
                self.all_tags.put(raw_packets_in)
                got_new_adva = True
                no_data_start_time = None

            else:
                if no_data_start_time is None:
                    no_data_start_time = time.time()
                if time.time() - no_data_start_time >= SECONDS_WITHOUT_PACKETS:
                    got_new_adva = False
                    if not self.second_without_packets:
                        self.logger_file.warning("One minute without packets..")
                        self.second_without_packets = True
                    time.sleep(5)
                    if not self.gw_instance.is_connected():
                        self.reconnect()
                if time.time() - no_data_start_time >= SECONDS_FOR_GW_ERROR_AFTER_NO_PACKETS:
                    self.gw_error_connection = True
                    break
                if self.gw_instance.get_read_error_status():
                    self.logger_file.warning("Reading error.. Listener did recovery flow.")
                time.sleep(0.050 if not got_new_adva else 0)

        self.gw_instance.exit_gw_api()

    def reconnect(self):
        self.logger_file.info('Trying to reconnect to GW')
        try:
            self.init_gw()
            self.gw_reset_config(start_gw_app=True)
        except Exception as e:
            self.logger_file.warning(f"Couldn't reconnect GW, due to: {e}")

    def get_raw_packets_queue(self):
        """
        Returns the packet queue that is created above
        """
        return self.all_tags


class CountThread(object):
    """
    Counting the number of tags
    """

    def __init__(self, stop_event, logger_file, matrix_size=1, max_movement_time=3, ther_cols=1):
        self.arduino_connection_error = False
        self.max_movement_time = max_movement_time
        self.logger_file = logger_file
        self.last_arduino_trigger_time = datetime.datetime.now()
        self.comPortObj = None
        self.trigger_port = None
        if not AUTO_TRIGGERS:
            self.connect()
        self.matrix_size = matrix_size
        self.ther_cols = ther_cols
        self.stop = stop_event
        self.tested = 0

    def connect(self):
        optional_ports = get_arduino_ports()
        if len(optional_ports) == 0:
            raise Exception("NO ARDUINO")
        for port in optional_ports:
            try:
                self.comPortObj = serial.Serial(port, BAUD_ARDUINO, timeout=0.1)
                time.sleep(2)
                initial_message = self.comPortObj.readline().decode().strip()
                if "Wiliot Yield Counter" in initial_message:
                    self.trigger_port = port
            except Exception as e:
                raise Exception(f'could not connect to port {port} due to {e}')

    def raising_trigger(self):
        self.last_arduino_trigger_time = datetime.datetime.now()
        self.tested += self.matrix_size

    def reconnect(self):
        """
        Attempts to reconnect to the Arduino.
        """
        connected = False
        start_time = time.time()
        while not connected and not self.stop.is_set() and time.time() - start_time < 60:
            try:
                self.comPortObj = serial.Serial(self.trigger_port, BAUD_ARDUINO, timeout=0.1)
                connected = True
                self.logger_file.info("Reconnected to Arduino")
            except serial.SerialException:
                self.logger_file.error("Reconnection failed. Trying again...")
                time.sleep(5)
        if not connected:
            self.arduino_connection_error = True

    def run(self):
        """
        Tries to read data and then counts the number of tags
        """
        while not self.stop.is_set():
            time.sleep(0.100)
            data = ''
            if not AUTO_TRIGGERS:
                try:
                    data = self.comPortObj.readline()
                    if data.__len__() > 0:
                        try:
                            tmp = data.decode().strip(' \t\n\r')
                            if "pulses detected" in tmp:
                                self.raising_trigger()
                        except Exception as ee:
                            self.logger_file.error(f'Warning: Could not decode counter data or Warning: {ee}')
                except serial.SerialException as e:
                    # Handle disconnection here
                    self.logger_file.error("Arduino is disconnected   ", e)
                    self.reconnect()
                except Exception as ee:
                    self.logger_file.error(f"NO READLINE: {ee}")
            else:
                self.raising_trigger()
                time.sleep(TIME_BETWEEN_AUTO_TRIGGERS)

        if not AUTO_TRIGGERS:
            self.comPortObj.close()

    def get_tested(self):
        """
        returns the number of tags
        """
        return self.tested

    def get_last_arduino_trigger_time(self):
        return self.last_arduino_trigger_time

    def get_arduino_connection_error(self):
        return self.arduino_connection_error


class MainWindow:
    """
    The main class the runs the GUI and supervise the multi-threading process of fraction's calculation and GUI viewing
    """

    def __init__(self):
        self.user_response_after_arduino_connection_error = False
        self.advanced_window = None
        self.user_response_after_gw_connection_error = False
        self.env_choice = 'prod'
        self.matrix_size = None
        self.latest_yield_value = None
        self.filling_missed_field = None
        self.latest_yield_formatted = 0
        self.number_of_unique_advas = None
        self.start_run = None
        self.inlay_select = None
        self.energy_pat = None
        self.time_pro = None
        self.rec_channel = None
        self.logger = None
        self.ttfp = None
        self.cnt = None
        self.curr_adva_for_log = None
        self.matrix_tags = None
        self.conversion = None
        self.surface = None
        self.matrix_sec = None
        self.adva_process = None
        self.adva_process_thread = None
        self.count_process = None
        self.count_process_thread = None
        self.folder_path = None
        self.py_wiliot_version = None
        self.final_path_run_data = None
        self.run_data_dict = None
        self.tags_num = 0
        self.last_printed = 0
        self.stop = threading.Event()
        self.neg_col = 0
        self.thermodes_col = None
        self.print_neg_advas = True
        self.selected = ''
        self.wafer_lot = ''
        self.wafer_number = ''
        self.matrix_num = ''
        self.operator = ''
        self.tester_type = 'yield'
        self.tester_station_name = ''
        self.comments = ''
        self.gw_energy_pattern = None
        self.gw_time_profile = None
        self.rows_number = 1
        self.upload_flag = True
        self.cmn = ''
        self.final_path_packets_data = ''
        self.seen_advas = set()
        self.not_neg_advas = 0  # used only to be shown in the small window
        self.update_packet_data_flag = False
        self.first_time_between_0_and_100 = False
        self.tags_counter_time_log = 0
        self.advas_before_tags = set()

    def setup_logger(self):
        # Logger setup
        self.init_file_path()
        self.logger = logging.getLogger('yield')
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        self.logger.setLevel(logging.INFO)
        final_path_log_file = os.path.join(self.folder_path, self.cmn + '@yield_log.log')
        file_handler = logging.FileHandler(final_path_log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p'))
        file_handler.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    def get_result(self):
        """
        Calculates the yield fraction
        """
        result = 100
        tags_num = self.count_process.get_tested()
        if tags_num > 0:
            result = (self.not_neg_advas / tags_num) * 100
        return result

    def run(self):
        """
        Viewing the window and checking if the process stops
        """
        self.open_session()
        if self.start_run:
            self.init_processes(self.rec_channel, self.time_pro, self.energy_pat, self.inlay_select, self.matrix_sec)
            time.sleep(0.5)
            self.init_run_data()
            self.start_processes()
            self.overlay_window()
        else:
            self.logger.warning('Error Loading Program')

    def init_file_path(self):
        self.py_wiliot_version = get_version()
        d = WiliotDir()
        d.create_tester_dir(tester_name='yield_tester')
        yield_test_app_data = d.get_tester_dir('yield_tester')
        self.cmn = self.wafer_lot + '.' + self.wafer_number
        run_path = os.path.join(yield_test_app_data, self.cmn)
        if not os.path.exists(run_path):
            os.makedirs(run_path)
        self.cmn = self.wafer_lot + '.' + self.wafer_number + '_' + formatted_today + '_' + cur_time_formatted
        self.folder_path = os.path.join(run_path, self.cmn)
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

    def init_run_data(self):
        self.final_path_run_data = os.path.join(self.folder_path, self.cmn + '@run_data.csv')
        gw_version = self.adva_process.gw_instance.get_gw_version()[0]
        start_time = datetime.datetime.now()
        run_start_time = start_time.strftime("%I:%M:%S")
        value = csv_dictionary[self.selected]
        self.run_data_dict = {'common_run_name': self.cmn, 'tester_station_name': self.tester_station_name,
                              'operator': self.operator, 'received_channel': value['received_channel'],
                              'run_start_time': formatted_date + ' ' + run_start_time, 'run_end_time': '',
                              'wafer_lot': self.wafer_lot, 'wafer_number': self.wafer_number,
                              'matrix_num': self.matrix_num, 'upload_date': formatted_date + ' ' + time_formatted,
                              'tester_type': self.tester_type, 'gw_energy_pattern': self.gw_energy_pattern,
                              'comments': self.comments, 'inlay': self.selected, 'total_run_tested': 0,
                              'total_run_responding_tags': 0, 'conversion_type': self.conversion,
                              'gw_version': gw_version, 'surface': self.surface, 'matrix_tags': self.matrix_tags,
                              'py_wiliot_version': self.py_wiliot_version, 'thermodes_col': self.thermodes_col,
                              'gw_time_profile': self.gw_time_profile, 'rows_number': self.rows_number}

    @staticmethod
    def update_run_data_file(run_data_path, run_data_dict, run_end_time, tags_num, advas, result, conversion, surface):
        """
        Updates the run_data CSV file while running the program
        """
        run_data_dict['run_end_time'] = run_end_time
        run_data_dict['total_run_tested'] = tags_num
        run_data_dict['total_run_responding_tags'] = advas
        run_data_dict['yield'] = result
        run_data_dict['conversion_type'] = conversion
        run_data_dict['surface'] = surface
        dict_to_csv(dict_in=run_data_dict, path=run_data_path)

    def calc_tag_matrix_ttfp(self, packet_time, trigger_time):
        try:
            tag_matrix_ttfp = (self.adva_process.get_gw_start_time() - trigger_time).total_seconds() + packet_time
        except Exception as e:
            self.logger.warning(f'could not calculate tag matrix ttfp due to {e}')
            tag_matrix_ttfp = -1.0
        return tag_matrix_ttfp

    def update_packet_data(self):
        """
        Updates the run_data CSV file while running the program
        """

        raw_packet_queue = self.adva_process.get_raw_packets_queue()

        self.number_of_unique_advas = len(self.seen_advas)
        trigger_time = self.count_process.get_last_arduino_trigger_time()
        if not raw_packet_queue.empty():
            cur_df = pd.DataFrame()
            n_elements = raw_packet_queue.qsize()
            # Collecting Packets from the queue and putting them into a TagCollection
            for _ in range(n_elements):
                for p in raw_packet_queue.get():
                    tag_matrix_ttfp = self.calc_tag_matrix_ttfp(p['time'], trigger_time)
                    cur_p = Packet(p['raw'], time_from_start=p['time'], inlay_type=self.inlay_select,
                                   custom_data={
                                       'common_run_name': self.cmn,
                                       'matrix_tags_location': self.cnt,
                                       'matrix_timestamp': trigger_time,
                                       'tag_matrix_ttfp': tag_matrix_ttfp,
                                       'environment_light_intensity': self.light_intensity,
                                       'environment_humidity': self.humidity,
                                       'environment_temperature': self.temperature})
                    if not cur_p.is_valid_packet:
                        continue
                    tag_id = cur_p.get_adva()
                    if tag_id not in self.seen_advas and tag_id not in self.advas_before_tags:
                        cur_p_df = cur_p.as_dataframe(sprinkler_index=0)
                        cur_df = pd.concat([cur_df, cur_p_df], ignore_index=True)
                        self.seen_advas.add(tag_id)

            # writing to DataFrame and then to CSV
            if not cur_df.empty:
                self.final_path_packets_data = os.path.join(self.folder_path, f"{self.cmn}@packets_data.csv")
                try:
                    if not self.update_packet_data_flag:
                        cur_df.to_csv(self.final_path_packets_data, mode='w', header=True, index=False)
                        self.update_packet_data_flag = True
                    else:
                        cur_df.to_csv(self.final_path_packets_data, mode='a', header=False, index=False)
                except Exception as ee:
                    self.logger.error(f"Exception occurred: {ee}")

    def stop_button(self, window, run_end_time, tags_num, advas, result):
        """
        Finishing the program and saves the last changes after pressing Stop in the second window
        """
        self.stop.set()
        window.close()
        self.fig_canvas_agg1.get_tk_widget().destroy()
        self.adva_process_thread.join()
        self.count_process_thread.join()

        self.update_run_data_file(self.final_path_run_data, self.run_data_dict, formatted_date + ' ' + run_end_time,
                                  tags_num, advas, result, self.conversion, self.surface)
        self.update_packet_data()

    def init_processes(self, rec_channel, time_pro, energy_pat, inlay_select, max_movement_time):
        """
        Initializing the two main instances and threads in order to start working
        """
        try:
            self.adva_process = AdvaProcess(self.stop, rec_channel, time_pro, energy_pat,
                                            inlay_select, self.logger,
                                            self.advas_before_tags, self.folder_path)
            self.adva_process_thread = threading.Thread(target=self.adva_process.run, args=())
        except Exception as e:
            self.logger.warning(f"{e}")
            sg.popup_error("GW is not connected. Please connect it.", keep_on_top=True)
            raise Exception('GW is not connected')
        try:
            self.count_process = CountThread(self.stop, self.logger, self.matrix_size, max_movement_time,
                                             self.thermodes_col)
            self.count_process_thread = threading.Thread(target=self.count_process.run, args=())

        except Exception as e:
            self.logger.warning(f"{e}")
            sg.popup_error("Arduino is not connected. Please connect it.", keep_on_top=True)
            raise Exception('Arduino is not connected')

    def start_processes(self):
        """
        Starting the work of the both threads
        """
        self.adva_process_thread.start()
        self.count_process_thread.start()

    def draw_figure(self, canvas, figure):
        """
        Embeds a Matplotlib figure in a PySimpleGUI Canvas Element
        """
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
        return figure_canvas_agg

    def upload_to_cloud(self):
        yes_or_no = ['Yes', 'No']
        layout = [
            [sg.Text('Do you want to stop or upload?')],
            [sg.Text('Upload:', font=6)],
            [sg.Combo(values=yes_or_no, default_value=yes_or_no[0], key='upload', font=4, enable_events=True)],
            [sg.Text("Select Environment:")],
            [sg.Combo(['prod', 'test'], default_value='prod', key='env_choice', size=(10, 1),
                      enable_events=True)],
            [sg.Button('Finish')]
        ]
        window = sg.Window('Application Options', layout)
        while True:
            event, values = window.read()
            if event == 'upload':
                self.upload_flag = values['upload'] == 'Yes'
            elif event == 'env_choice':
                self.env_choice = values['env_choice']
            if event in (sg.WINDOW_CLOSED, 'Finish'):
                break
        window.close()

        if self.upload_flag:
            try:
                is_uploaded = upload_to_cloud_api(self.cmn, self.tester_type + '-test',
                                                  run_data_csv_name=self.final_path_run_data,
                                                  packets_data_csv_name=self.final_path_packets_data,
                                                  env=self.env_choice, is_path=True)

            except Exception as ee:
                is_uploaded = False
                self.logger.error(f"Exception occurred: {ee}")
                exit()

            if is_uploaded:
                self.logger.info("Successful upload")
            else:
                sg.popup_ok(
                    "Run upload failed. Check exception error at the console and check Internet connection is available"
                    " and upload logs manually", title='Upload Error', font='Calibri', keep_on_top=True,
                    auto_close=False, no_titlebar=True)

    def error_popup(self, error_type):

        layout = [
            [sg.Column([[sg.Text(f'{error_type} Connection error occurred.\nYield test was stopped',
                                 text_color='red', font=('Helvetica', 16, 'bold'))]],
                       justification='center')],
            [sg.Column([[sg.Button('OK', size=(10, 2), font=('Helvetica', 14))]],
                       justification='center')]
        ]

        window = sg.Window('Timeout Notification', layout, size=(400, 150), resizable=True)

        while True:
            try:
                event, values = window.read(timeout=100)
                if event == sg.WIN_CLOSED or event == 'OK':
                    time.sleep(1)
                    break
            except Exception as e:
                self.logger.error('Error while waiting user response')

        window.close()

    def overlay_window(self):
        """
        The small window open session
        """

        # taking values from user_input json file
        temperature_type = user_inputs.get('temperature_type', 'F')
        min_current = float(user_inputs.get('min_current', '0'))
        min_cumulative = float(user_inputs.get('min_cumulative', '0'))
        min_humidity = float(user_inputs.get('min_humidity', '0'))
        max_humidity = float(user_inputs.get('max_humidity', '0'))
        max_light_intensity = float(user_inputs.get('max_light_intensity', '2500'))
        min_light_intensity = float(user_inputs.get('min_light_intensity', '2500'))
        min_temperature = float(user_inputs.get('min_temperature', '0'))
        max_temperature = float(user_inputs.get('max_temperature', '0'))
        red_line_current = float(user_inputs.get('red_line_current', '0'))
        red_line_cumulative = float(user_inputs.get('red_line_cumulative', '0'))
        layout = [
            [
                sg.Column([
                    [sg.Text('Number of tags:', font=('Helvetica', 20, 'bold')),
                     sg.Text(key='num_rows', font=('Helvetica', 20, 'bold'))],
                    [sg.Text('Number of advas:', font=('Helvetica', 20, 'bold')),
                     sg.Text(key='num_advas', font=('Helvetica', 20, 'bold'))],
                    [sg.Text('Light Intensity:', font=('Helvetica', 15)),
                     sg.Text(f'{self.light_intensity} lux', key='light_intensity_value',
                             font=('Helvetica', 15)),
                     sg.Text('', size=(31, 1)),
                     sg.Text('Temperature:', font=('Helvetica', 14)),
                     sg.Text(f'{self.temperature} {temperature_type}', key='temperature_value', font=('Helvetica', 15)),
                     sg.Text('', size=(31, 1)),
                     sg.Text('Humidity:', font=('Helvetica', 15)),
                     sg.Text(f'{self.humidity} %', key='humidity_value', font=('Helvetica', 15)),
                     sg.Text('', size=(31, 1)),
                     sg.Text(f'Matrix num: {self.matrix_num}', key='matrix_num_value', font=('Helvetica', 15))]
                ]),
            ],
            [
                sg.Canvas(key='-CANVAS1-', size=(850, 600)),
                sg.Canvas(key='-CANVAS2-', size=(850, 600))
            ],
            [
                sg.Button('Stop', size=(10, 1)),
                sg.Text('', size=(21, 1)),
                sg.Text('', size=(20, 1), key='-current_status-', font=('Helvetica', 14, 'bold')),
                sg.Text('', size=(10, 1), key='-current_status_value-', font=('Helvetica', 18, 'bold')),
                sg.Text('', size=(45, 1)),
                sg.Text('', size=(23, 1), key='-cumulative_status-', font=('Helvetica', 14, 'bold')),
                sg.Text('', size=(5, 1), key='-cumulative_status_value-', font=('Helvetica', 18, 'bold')),
                sg.Text('', size=(21, 1)), sg.Button('Advanced Settings')
            ]
        ]
        screen_width, screen_height = sg.Window.get_screen_size()
        window = sg.Window('Wiliot Yield Tester', layout, modal=True, finalize=True, size=(screen_width - 100, screen_height - 100), resizable=True)

        # initialize num_advas and num_rows
        num_rows_text_elem = window['num_rows']
        num_advas_text_elem = window['num_advas']
        num_rows = (self.rows_number * self.neg_col)
        num_advas = 0
        num_rows_text_elem.update(f"{num_rows}", font=('Helvetica', 20, 'bold'))
        num_advas_text_elem.update(f"{num_advas}", font=('Helvetica', 20, 'bold'))

        # create the main figure and two subplots
        fig, (ax, axy) = plt.subplots(1, 2, figsize=(20, 6))

        # initialize the first graph
        prev_tests = 0
        prev_val = 100
        ax.set_xlabel('Number of tags', fontweight='bold')
        ax.set_ylabel('Yield %', fontweight='bold')
        ax.set_ylim([-MIN_Y_FOR_PLOTS, MAX_Y_FOR_PLOTS])
        ax_y_ticks = np.arange(MIN_Y_FOR_PLOTS, MAX_Y_FOR_PLOTS + 10, FIRST_STEP_SIZE)
        ax.set_yticks(ax_y_ticks)
        plt.ion()
        ax.yaxis.grid(True)
        text_box = ax.text(0.18, 1.05, f"Current Matrix Yield: {self.latest_yield_formatted:.2f} %",
                           transform=ax.transAxes, fontweight='bold')
        if user_inputs.get('min_current_line') == 'yes':
            ax.axhline(y=min_current, color='black', linestyle='--')
        # initialize the second graph
        prev_tests1 = 0
        prev_val1 = 100
        axy.set_xlabel('Number of tags', fontweight='bold')
        axy.set_ylabel('Yield %', fontweight='bold')
        axy.set_ylim([MIN_Y_FOR_PLOTS, MAX_Y_FOR_PLOTS])
        axy_y_ticks = np.arange(MIN_Y_FOR_PLOTS, MAX_Y_FOR_PLOTS + 10, FIRST_STEP_SIZE)
        axy.set_yticks(axy_y_ticks)
        plt.ion()
        axy.yaxis.grid(True)
        text_box1 = axy.text(0.18, 1.05, f"Cumulative Yield: {prev_val:.2f} %", transform=axy.transAxes,
                             fontweight='bold')
        if user_inputs.get('min_cumulative_line') == 'yes':
            axy.axhline(y=min_cumulative, color='black', linestyle='--')
        # embed the plots in the PySimpleGUI window
        canvas_elem1 = window['-CANVAS1-']
        self.fig_canvas_agg1 = self.draw_figure(canvas_elem1.TKCanvas, fig)

        # values before running
        self.neg_advas = len(self.seen_advas)
        self.curr_adva_for_log = len(self.seen_advas)
        self.cnt = 1
        stop_window = None
        sub = False
        current_min_y_value = MIN_Y_FOR_PLOTS
        current_max_y_value = MAX_Y_FOR_PLOTS
        current_size_value = FIRST_STEP_SIZE
        cumulative_min_y_value = MIN_Y_FOR_PLOTS
        cumulative_max_y_value = MAX_Y_FOR_PLOTS
        cumulative_size_value = FIRST_STEP_SIZE
        prev_tested = 0
        result = float('inf')

        while True:

            event, values = window.read(timeout=100)
            new_num_rows = self.count_process.get_tested() + (self.rows_number * self.neg_col)
            new_num_advas = len(self.seen_advas) - self.neg_advas
            self.not_neg_advas = new_num_advas
            # update packet data
            self.update_packet_data()
            if event == 'Advanced Settings':
                advanced_layout = [
                    [
                        sg.Column([
                            [sg.Text('"Current" min y:'), sg.Input(key='current_min_y_value', size=(10, 1))],
                            [sg.Text('"Current" max y:'), sg.Input(key='current_max_y_value', size=(10, 1))],
                            [sg.Text('"Current" step:'), sg.Input(key='current_size_value', size=(10, 1))]
                        ]),
                        sg.Column([
                            [sg.Text('"Cumulative" min y:'), sg.Input(key='cumulative_min_y_value', size=(10, 1))],
                            [sg.Text('"Cumulative" max y'), sg.Input(key='cumulative_max_y_value', size=(10, 1))],
                            [sg.Text('"Cumulative" step:'), sg.Input(key='cumulative_size_value', size=(10, 1))]
                        ])
                    ],
                    [sg.Text('Matrix num:'), sg.Input(key='matrix_num', size=(10, 1))],
                    [sg.Button('Reset'), sg.Button('OK')]]

                self.advanced_window = sg.Window('Advanced Settings', advanced_layout, modal=True)

            elif event == 'Stop' or self.adva_process.get_gw_error_connection() or \
                    self.count_process.get_arduino_connection_error():
                try:
                    self.logger.info('Final Yield: %s, Final Tags: %05d, Final Advas: %05d,',
                                     result, self.count_process.get_tested(), len(self.seen_advas), )
                except Exception as e:
                    result = 0
                    self.logger.info('Final Yield: %s, Final Tags: %05d, Final Advas: %05d,',
                                     result, self.count_process.get_tested(), len(self.seen_advas), )
                window.close()
                if not self.adva_process.get_gw_error_connection() and \
                        not self.count_process.get_arduino_connection_error():  # uploading after connection error
                    # pressing 'OK'
                    self.upload_to_cloud()
                else:
                    if self.count_process.get_arduino_connection_error():
                        self.user_response_after_arduino_connection_error = True
                    else:
                        self.user_response_after_gw_connection_error = True
                end_time = datetime.datetime.now()
                run_end_time = end_time.strftime("%I:%M:%S")
                advas = len(self.seen_advas)
                tags_num = self.count_process.get_tested()
                result = float(100 * (advas / tags_num)) if tags_num != 0 else float('inf')
                self.stop_button(window, run_end_time, tags_num, advas, result)
                sub = True
            elif event in (None, sg.WINDOW_CLOSED):
                window.close()
                break
            # ignoring all advas before receiving the first arduino trigger
            elif new_num_rows < self.matrix_size + (self.rows_number * self.neg_col):
                if self.adva_process.gw_instance.is_data_available():
                    packet_list_in = self.adva_process.gw_instance.get_packets(action_type=ActionType.ALL_SAMPLE,
                                                                               tag_inlay=self.adva_process.inlay_type)
                    for packet in packet_list_in:
                        adva = packet.get_adva()
                        self.adva_process.advas_before_tags.add(adva)
                self.not_neg_advas = 0
                new_num_rows = self.count_process.get_tested() + (self.rows_number * self.neg_col)
                continue
            else:
                if self.advanced_window:

                    adv_event, adv_values = self.advanced_window.read(timeout=10)

                    if adv_event == 'OK':
                        if adv_values['matrix_num']:
                            self.matrix_num = int(adv_values['matrix_num'])
                            window['matrix_num_value'].update(f'Matrix num: {self.matrix_num}')
                        if adv_values['current_min_y_value']:
                            current_min_y_value = float(adv_values['current_min_y_value'])
                        if adv_values['current_max_y_value']:
                            current_max_y_value = float(adv_values['current_max_y_value'])
                        if adv_values['current_size_value']:
                            current_size_value = float(adv_values['current_size_value'])

                        if adv_values['cumulative_min_y_value']:
                            cumulative_min_y_value = float(adv_values['cumulative_min_y_value'])
                        if adv_values['cumulative_max_y_value']:
                            cumulative_max_y_value = float(adv_values['cumulative_max_y_value'])
                        if adv_values['cumulative_size_value']:
                            cumulative_size_value = float(adv_values['cumulative_size_value'])

                        ax.set_ylim([current_min_y_value, current_max_y_value])
                        ax.set_yticks(np.arange(current_min_y_value, current_max_y_value + current_size_value,
                                                current_size_value))

                        axy.set_ylim([cumulative_min_y_value, cumulative_max_y_value])
                        axy.set_yticks(np.arange(cumulative_min_y_value, cumulative_max_y_value + cumulative_size_value,
                                                 cumulative_size_value))

                        self.fig_canvas_agg1.draw()

                        self.advanced_window.close()
                        self.advanced_window = None
                    elif adv_event in (None, sg.WINDOW_CLOSED):
                        self.advanced_window.close()
                        self.advanced_window = None
                    elif adv_event == 'Reset':
                        default_values = {
                            'current_min_y_value': 0,
                            'current_max_y_value': 120,
                            'current_size_value': 10,
                            'cumulative_min_y_value': 0,
                            'cumulative_max_y_value': 120,
                            'cumulative_size_value': 10
                        }
                        # Reset the values and update the input fields
                        for key in default_values:
                            self.advanced_window[key].update(default_values[key])
                            globals()[key] = default_values[key]

                        # Update the graph with reset values
                        ax.set_ylim([current_min_y_value, current_max_y_value])
                        ax.set_yticks(np.arange(current_min_y_value, current_max_y_value + current_size_value,
                                                current_size_value))

                        axy.set_ylim([cumulative_min_y_value, cumulative_max_y_value])
                        axy.set_yticks(np.arange(cumulative_min_y_value, cumulative_max_y_value + cumulative_size_value,
                                                 cumulative_size_value))

                        self.fig_canvas_agg1.draw()

                # updating number of rows in GUI
                if new_num_rows != num_rows:
                    num_rows = new_num_rows
                    num_rows_text_elem.update(f"{num_rows}")

                # updating number of advas in GUI
                if new_num_advas != num_advas and new_num_advas > -1:
                    num_advas = new_num_advas
                    num_advas_text_elem.update(f"{num_advas - self.neg_advas}")
                # writing the number of neglected advas in LOG
                if self.print_neg_advas:
                    self.logger.info('neglected advas:  %05d', len(self.advas_before_tags))
                    self.print_neg_advas = False
                # all processes when getting a new matrix
                current_tested = self.count_process.get_tested()
                if (current_tested - prev_tested) % (self.matrix_size * int(self.matrix_num)) \
                        == 0 and current_tested != self.last_printed:
                    temperature_display = f"{self.temperature:.2f} °C"
                    if self.main_sensor:
                        self.light_intensity = self.main_sensor.get_light()
                        self.humidity = self.main_sensor.get_humidity()
                        self.temperature = self.main_sensor.get_temperature()
                    if temperature_type == "F":
                        temperature_display = f"{self.temperature * 9 / 5 + 32:.2f} °F"  # Convert to Fahrenheit

                    temperature_color = BLACK_COLOR \
                        if (min_temperature <= self.temperature <= max_temperature) else RED_COLOR
                    light_intensity_color = BLACK_COLOR \
                        if (min_light_intensity <= self.light_intensity <= max_light_intensity) else RED_COLOR
                    humidity_color = BLACK_COLOR if (min_humidity <= self.humidity <= max_humidity) else RED_COLOR
                    window['temperature_value'].update(f'{temperature_display}', text_color=temperature_color,
                                                       font=('Helvetica', 15))
                    window['light_intensity_value'].update(f'{self.light_intensity} lux',
                                                           text_color=light_intensity_color, font=('Helvetica', 15))
                    window['humidity_value'].update(f'{self.humidity} %', text_color=humidity_color,
                                                    font=('Helvetica', 15))

                    yield_result = "%.5f" % self.get_result()
                    latest_adva = len(self.seen_advas) - self.curr_adva_for_log
                    self.latest_yield_value = float(latest_adva / self.matrix_size) * 100
                    self.latest_yield_formatted = "{:.5f}".format(self.latest_yield_value).zfill(9)
                    text_box.set_text(f"Current Matrix Yield : {self.latest_yield_value:.2f} %")
                    if '.' in yield_result and len(yield_result.split('.')[0]) < 2:
                        yield_result = "0" + yield_result
                    latest_adva = len(self.seen_advas) - self.curr_adva_for_log
                    self.latest_yield_formatted = "{:.5f}".format(float(latest_adva / self.matrix_size) * 100).zfill(9)
                    self.logger.info(
                        'Matrix Number: %05d, Cumulative Yield: %s, Cumulative Tags: %05d, Cumulative Advas: %05d,'
                        'Latest Yield: %s, Latest Tags: %05d, Latest Advas: %05d, Light Intensity: '
                        '%05.1f, Humidity: %05.1f, Temperature: %05.1f',
                        (self.count_process.get_tested() / self.matrix_size),
                        yield_result, self.count_process.get_tested(), len(self.seen_advas),
                        self.latest_yield_formatted,
                        self.matrix_size, latest_adva, self.light_intensity, self.humidity, self.temperature)

                    # updating the first graph
                    curr_tests = new_num_rows
                    curr_val = 100 * ((len(self.seen_advas) - self.curr_adva_for_log) / self.matrix_size)
                    if curr_val > 100:
                        curr_val = SET_VALUE_MORE_THAN_100
                    self.curr_adva_for_log = len(self.seen_advas)

                    if curr_val < min_current:
                        font_color_current = RED_COLOR
                        status_message_current = f'Current yield is lower than'
                        status_value_current = f'{min_current}%'
                    else:
                        font_color_current = 'white'
                        status_message_current = ''
                        status_value_current = ''
                    figure_color_current = 'red' if curr_val < red_line_current else 'blue'

                    window['-current_status-'].update(status_message_current, text_color=font_color_current)
                    window['-current_status_value-'].update(status_value_current, text_color=font_color_current)
                    ax.plot([prev_tests, curr_tests], [prev_val, curr_val], color=figure_color_current)
                    prev_tests = curr_tests
                    prev_val = curr_val
                    prev_tested = current_tested
                    self.last_printed = current_tested
                    self.cnt += 1

                # updating the second graph
                curr_tests1 = new_num_rows
                curr_val1 = self.get_result()

                if curr_val1 > 100:
                    curr_val1 = SET_VALUE_MORE_THAN_100
                elif 0 < curr_val1 < 101:
                    self.first_time_between_0_and_100 = True
                if curr_val1 < min_cumulative:
                    font_color_cumulative = RED_COLOR
                    status_message_cumulative = f'Cumulative yield is lower than'
                    status_value_cumulative = f'{min_cumulative} % '
                else:
                    font_color_cumulative = 'white'
                    status_message_cumulative = ''
                    status_value_cumulative = ''
                figure_color_cumulative = 'red' if curr_val1 < red_line_cumulative else 'blue'

                window['-cumulative_status-'].update(status_message_cumulative, text_color=font_color_cumulative)
                window['-cumulative_status_value-'].update(status_value_cumulative, text_color=font_color_cumulative)

                if new_num_rows != 0 and self.first_time_between_0_and_100:
                    axy.plot([prev_tests1, curr_tests1], [prev_val1, curr_val1], color=figure_color_cumulative)
                prev_tests1 = curr_tests1
                prev_val1 = curr_val1
                text_box1.set_text(f"Cumulative Yield : {curr_val1:.2f} %")
                self.fig_canvas_agg1.draw()

                # updating run_data_file
                end_time = datetime.datetime.now()
                run_end_time = end_time.strftime("%I:%M:%S")
                advas = len(self.seen_advas)
                tags_num = self.count_process.get_tested()
                result = float(100 * (advas / tags_num)) if tags_num != 0 else float('inf')
                self.update_run_data_file(self.final_path_run_data, self.run_data_dict,
                                          formatted_date + ' ' + run_end_time,
                                          tags_num, advas, result, self.conversion, self.surface)
            if self.user_response_after_gw_connection_error or self.user_response_after_arduino_connection_error:
                connection_error = ''
                if self.user_response_after_gw_connection_error:
                    connection_error = 'GW'
                else:
                    connection_error = 'Arduino'
                self.error_popup(connection_error)
                self.upload_to_cloud()
            if sub:
                break

        return sub

    def open_session(self):
        """
        opening a session for the process
        """
        # save data to configs file
        if os.path.exists("configs/gui_input_do_not_delete.json"):
            with open("configs/gui_input_do_not_delete.json", "r") as f:
                previous_input = json.load(f)

        else:
            previous_input = {'inlay': '', 'number': '', 'received_channel': '',
                              'energy_pattern_val': '', 'tester_station_name': '',
                              'comments': '', 'operator': '', 'wafer_lot': '', 'wafer_num': '', 'conversion_type': '',
                              'surface': '', 'matrix_tags': '', 'thermodes_col': '0', 'gw_energy_pattern': '',
                              'gw_time_profile': '', 'rows_number': '0', 'matrix_sec': '', 'matrix_num': ''}

        # update fields from configs
        self.start_run = False
        selected_inlay = csv_dictionary[previous_input['inlay']]
        energy_pat = selected_inlay['energy_pattern_val']
        time_pro = selected_inlay['time_profile_val']
        rec_channel = selected_inlay['received_channel']
        lst_inlay_options = list(inlay_types_dict.keys())
        conv_opts = ['Not converted', 'Standard', 'Durable']
        surfaces = ['Air', 'Cardboard', 'RPC', 'General Er3', 'General Er3.5']
        default_matrix_tags = int(previous_input['thermodes_col']) * int(previous_input['rows_number'])
        layout = [
            [sg.Text('Wafer Lot:', size=(13, 1), font=4),
             sg.InputText(previous_input['wafer_lot'], key='wafer_lot', font=4),
             sg.Text('Wafer Number:', size=(13, 1), font=4),
             sg.InputText(previous_input['wafer_num'], key='wafer_num', font=4)],

            [
                sg.Text('Time of matrix:', size=(13, 1), font=4),
                sg.InputText(previous_input['matrix_sec'], key='matrix_sec', font=4),
                sg.Text('Num of matrices:', size=(13, 1), font=4),
                sg.InputText(previous_input['matrix_num'], key='matrix_num', font=4)],

            [sg.Text('Thermode Col:', size=(13, 1), font=4),
             sg.InputText(previous_input['thermodes_col'], key='thermodes_col', font=4, enable_events=True),
             sg.Text('Rows Number :', size=(13, 1), font=4),
             sg.InputText(previous_input['rows_number'], key='rows_number', font=4, enable_events=True)],

            [sg.Text('Matrix tags: ', size=(13, 1), font=4),
             sg.Text(str(default_matrix_tags), key='matrix_tags', font=4)],

            [sg.Text('Inlay:', size=(13, 1), font=4),
             sg.Combo(values=lst_inlay_options, default_value=previous_input['inlay'], key='inlay', font=4,
                      enable_events=True), sg.Text('Energy Pattern:', font=4),
             sg.Text(energy_pat, key='energy_pattern_val', font=4),
             sg.Text('Time Profile:', font=4), sg.Text(time_pro, key='time_profile_val', font=4),
             sg.Text('Received Channel:', font=4), sg.Text(rec_channel, key='received_channel', font=4)],

            [sg.Text('Tester Station:', size=(13, 1), font=4),
             sg.InputText(previous_input['tester_station_name'], key='tester_station_name', font=4),
             sg.Text('Comments:', size=(13, 1), font=4),
             sg.InputText(previous_input['comments'], key='comments', font=4)],

            [sg.Text('Operator:', size=(13, 1), font=4),
             sg.InputText(previous_input['operator'], key='operator', font=4),
             sg.Text('Conversion:', size=(13, 1), font=4),
             sg.Combo(values=conv_opts, default_value=previous_input['conversion_type'], key='conversion_type', font=4,
                      enable_events=True), sg.Text('Surface:', font=4),
             sg.Combo(values=surfaces, default_value=previous_input['surface'], key='surface', font=4,
                      enable_events=True)],

            [sg.Submit()]
        ]

        window = sg.Window('WILIOT Yield Tester', layout, finalize=True)

        while True:
            event, values = window.read(timeout=100)
            inlay_select = values['inlay']
            self.selected = values['inlay']
            if event == 'inlay':
                inlay_select = values['inlay']
                self.selected = values['inlay']
                if inlay_select in csv_dictionary:
                    selected_inlay = csv_dictionary[inlay_select]
                    energy_pat = selected_inlay['energy_pattern_val']
                    time_pro = selected_inlay['time_profile_val']
                    rec_channel = selected_inlay['received_channel']
                else:
                    energy_pat = 'Invalid Selection'
                    time_pro = 'Invalid Selection'
                    rec_channel = 'Invalid Selection'

                window.find_element('rows_number').Update(value=self.rows_number)
                window.find_element('energy_pattern_val').Update(value=energy_pat)
                window.find_element('time_profile_val').Update(value=time_pro)
                window.find_element('received_channel').Update(value=rec_channel)
            if event == 'Submit':
                self.matrix_sec = (values['matrix_sec'])
                self.wafer_lot = values['wafer_lot']
                self.wafer_number = values['wafer_num']
                self.matrix_num = values['matrix_num']
                self.comments = values['comments']
                self.rows_number = int(values['rows_number'])
                self.gw_energy_pattern = energy_pat
                self.gw_time_profile = time_pro
                self.thermodes_col = values['thermodes_col']
                self.matrix_tags = str(int(values['thermodes_col']) * int(values['rows_number']))
                self.conversion = values['conversion_type']
                self.surface = values['surface']
                self.tester_station_name = values['tester_station_name']
                self.operator = values['operator']
                self.matrix_size = int(self.thermodes_col) * int(self.rows_number)
                # checking all mandatory fields
                missing_fields = []
                self.filling_missed_field = []
                while True:
                    for field in MAND_FIELDS:
                        value = values[field].strip()
                        if not value:
                            missing_fields.append(field)
                            self.filling_missed_field.append(field)
                    if missing_fields:
                        error_msg = f"Please fill all the mandatory fields" \
                                    f" {', '.join([f'[{field}]' for field in missing_fields])}"
                        sg.PopupError(error_msg)
                        missing_fields.clear()
                        event, values = window.read()
                        if event in (sg.WIN_CLOSED, 'Exit'):
                            break
                    else:
                        break

                # if there are missing fields, to fill their values
                for missed_field in self.filling_missed_field:
                    setattr(self, missed_field, values[missed_field])

                try:
                    self.main_sensor = YoctoSensor(self.logger)
                except Exception as ee:
                    self.main_sensor = None
                    print(f'No sensor is connected ({ee})')
                if self.main_sensor:
                    self.light_intensity = self.main_sensor.get_light()
                    self.humidity = self.main_sensor.get_humidity()
                    self.temperature = self.main_sensor.get_temperature()
                else:
                    self.temperature = VALUE_WHEN_NO_SENSOR
                    self.humidity = VALUE_WHEN_NO_SENSOR
                    self.light_intensity = VALUE_WHEN_NO_SENSOR
                self.setup_logger()
                # starting the main run
                self.rec_channel, self.time_pro, self.energy_pat, self.inlay_select = \
                    rec_channel, time_pro, energy_pat, inlay_select
                self.start_run = True
                with open("configs/gui_input_do_not_delete.json", "w") as f:
                    json.dump(values, f)
                break
            elif event == 'thermodes_col' or event == 'rows_number':
                try:
                    self.matrix_size = int(values['thermodes_col']) * int(values['rows_number'])
                    window['matrix_tags'].update(str(self.matrix_size))
                except ValueError:
                    window['matrix_tags'].update('')
            elif event == sg.WIN_CLOSED:
                exit()
        window.close()


if __name__ == '__main__':
    m = MainWindow()
    m.run()
