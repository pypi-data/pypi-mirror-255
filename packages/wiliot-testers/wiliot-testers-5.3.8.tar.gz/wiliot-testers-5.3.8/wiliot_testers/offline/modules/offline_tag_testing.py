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
import numpy as np
from enum import Enum
from wiliot_testers.wiliot_tester_tag_test import WiliotTesterTagTest
from wiliot_testers.wiliot_tester_tag_result import FailureCodes, WiliotTesterTagResultList
from wiliot_testers.test_equipment import Attenuator, YoctoTemperatureSensor
from wiliot_core import InlayTypes, WiliotGateway
from wiliot_testers.offline.configs.global_vars_and_enums import TagTestingDefaults


class TagTestingException(Exception):
    def __init__(self, msg):
        self.message = msg
        super().__init__(f'TagTesting Exception: {self.message}')


class MissingLabelException(TagTestingException):
    def __init__(self, msg):
        super().__init__(f'Missing Label: {msg}')


class AttenuatorException(TagTestingException):
    def __init__(self, msg):
        super().__init__(f'Attenuator: {msg}')


class SensorException(TagTestingException):
    def __init__(self, msg):
        super().__init__(f'Sensor: {msg}')


MAX_MAIN_STATES = 5


class TagStates(Enum):
    IDLE = 0
    STOP = 99
    WAIT_MOH = 88
    GET_TRIGGER = 1
    START_TEST = 2
    TAG_TEST = 3
    PROCESS_TEST = 4
    END_TEST = 5


class TagTesting(object):
    def __init__(self, test_start_event, test_end_event, stop_app_event, moh_object,
                 exception_queue, tag_results_queue, log_obj, user_config=None, hw_config=None):
        self.test_start_event = test_start_event
        self.test_end_event = test_end_event
        self.stop_app_event = stop_app_event
        self.exception_q = exception_queue
        self.tag_results_q = tag_results_queue
        self.moh = moh_object
        self.logger = logging.getLogger(log_obj.get_logger_name())
        self.user_config = user_config
        self.tested = 0
        self.missing_labels = 0
        self.need_to_manual_trigger = False
        self.all_selected_tags = []
        self.all_tags = []
        self.is_passed_list = []
        self.ttfp_list = []
        self.last_state = TagStates.IDLE
        self.is_init = False

        try:
            # init gateway:
            self.gw_obj = WiliotGateway(auto_connect=True, logger_name=self.logger.name, is_multi_processes=True,
                                        log_dir_for_multi_processes=log_obj.get_test_folder())

            # init tester class
            self.wiliot_tester = WiliotTesterTagTest(
                selected_test=self.user_config['testName'],
                gw_obj=self.gw_obj,
                logger_name=self.logger.name,
                logger_result_name=log_obj.get_results_logger_name(),
                logger_gw_name=log_obj.get_gw_logger_name(),
                stop_event_trig=self.stop_app_event,
                inlay=InlayTypes(self.user_config['inlay']))

            # init timeout for trigger:
            self.logger.info(f'Maximum time for gw trigger (i.e. missing label) '
                             f'is {TagTestingDefaults.TIMEOUT_FOR_MISSING_LABEL}')

            # init external hw
            self.attenuator_handle = AttenuatorHandle(logger_name=self.logger.name, exception_q=exception_queue,
                                                      attenuator_configs=hw_config)
            self.temperature_sensor_handle = TemperatureSensorHandle(logger_name=self.logger.name,
                                                                     exception_q=exception_queue,
                                                                     sensor_configs=hw_config)
            self.is_init = True

        except Exception as e:
            if isinstance(e, TagTestingException):
                self.exception_q.put(f'init: {e}', block=False)
            else:
                self.exception_q.put(TagTestingException(f'init: {e}').__str__(), block=False)

    def run(self):
        tester_res = WiliotTesterTagResultList()  # Empty list
        state = TagStates.IDLE

        while True:
            time.sleep(0)
            try:
                state = self.update_state(state)
                self.logger.info(f'TagTesting: start state {state}')
                if state == TagStates.GET_TRIGGER:
                    self.get_trigger()

                elif state == TagStates.START_TEST:
                    self.start_test()

                elif state == TagStates.TAG_TEST:
                    tester_res = self.tag_test()
                    self.need_to_manual_trigger = False

                elif state == TagStates.PROCESS_TEST:
                    self.process_test(tester_res=tester_res)

                elif state == TagStates.END_TEST:
                    self.end_test(tester_res=tester_res)

                elif state == TagStates.STOP:
                    self.logger.info('Stop running TagTesting main loop')
                    break

                elif state == TagStates.WAIT_MOH:
                    self.wait_for_moh()

                self.logger.info(f'TagTesting: end state {state}')

            except Exception as e:
                if isinstance(e, TagTestingException):
                    self.exception_q.put(f'run: state{state.name}: {e}', block=False)
                else:
                    self.exception_q.put(TagTestingException(f'run: state{state.name}: {e}').__str__(), block=False)

                if state == TagStates.GET_TRIGGER:
                    self.need_to_manual_trigger = True
                elif state == TagStates.TAG_TEST:
                    tester_res = WiliotTesterTagResultList()
                elif state == TagStates.PROCESS_TEST:
                    tester_res.set_total_fail_bin(fail_code=FailureCodes.SOFTWARE_GENERAL_ERROR, overwrite=True)
                elif state == TagStates.END_TEST or state == TagStates.WAIT_MOH:
                    self.logger.warning(f'TagTesting Got exception during {state}: {e}')

        self.stop()

    def update_state(self, state):
        # after MOH was done, continue to the next state
        if state == TagStates.WAIT_MOH:
            state = self.last_state

        # when event occurred
        if self.stop_app_event.is_set():
            if state == TagStates.TAG_TEST or state == TagStates.PROCESS_TEST:
                pass  # finish the cycle
            else:
                state = TagStates.STOP
        elif self.moh.get_manual_operation_is_needed():
            self.last_state = state
            state = TagStates.WAIT_MOH

        # main flow
        if state == TagStates.IDLE:
            state = TagStates.GET_TRIGGER
        elif state == TagStates.GET_TRIGGER:
            state = TagStates.START_TEST
        elif state == TagStates.START_TEST:
            state = TagStates.TAG_TEST
        elif state == TagStates.TAG_TEST:
            state = TagStates.PROCESS_TEST
        elif state == TagStates.PROCESS_TEST:
            state = TagStates.END_TEST
        elif state == TagStates.END_TEST:
            state = TagStates.GET_TRIGGER

        return state

    def get_trigger(self):
        pulse_received = self.wiliot_tester.wait_for_trigger(
            wait_for_gw_trigger=TagTestingDefaults.TIMEOUT_FOR_MISSING_LABEL)
        if not pulse_received:
            while self.moh.get_manual_operation_is_needed():
                self.wait_for_moh()
                if self.stop_app_event.is_set():
                    return
                pulse_received = self.wiliot_tester.wait_for_trigger(
                    wait_for_gw_trigger=TagTestingDefaults.TIMEOUT_FOR_MISSING_LABEL)
                if pulse_received:
                    break
            if not pulse_received:
                self.missing_labels += 1
                if TagTestingDefaults.ENABLE_MISSING_LABEL and \
                        self.missing_labels < TagTestingDefaults.MAX_MISSING_LABEL_ENGINEERING:
                    self.need_to_manual_trigger = True
                    self.logger.info((f'MISSING LABEL. no trigger was received for '
                                      f'{TagTestingDefaults.TIMEOUT_FOR_MISSING_LABEL} seconds. Continue to test.'))
                    return

                raise MissingLabelException(f'MISSING LABEL. no trigger was received for '
                                            f'{TagTestingDefaults.TIMEOUT_FOR_MISSING_LABEL} seconds')

    def start_test(self):
        self.test_start_event.set()
        if self.attenuator_handle.enable:
            self.attenuator_handle.set_dynamic_value()

    def tag_test(self):
        if not self.is_printing_calibration():
            tester_res = self.wiliot_tester.run(wait_for_gw_trigger=None,
                                                need_to_manual_trigger=self.need_to_manual_trigger)
        else:
            tester_res = WiliotTesterTagResultList()
            time.sleep(TagTestingDefaults.TIME_BETWEEN_TEST_PRINTING)

        self.tested += 1
        return tester_res

    def process_test(self, tester_res):
        is_pass = False
        if self.is_printing_calibration():
            tester_res.set_total_test_status(True)
            is_pass = True
        elif tester_res.is_all_tests_passed():
            selected_tag = tester_res.check_and_get_selected_tag_id()
            if selected_tag == '':
                if not self.wiliot_tester.run_all and not self.is_printing_calibration():
                    raise TagTestingException("run: ANALYSIS TEST: Test Status is PASS but could not select tag")
                else:
                    is_pass = True

            elif selected_tag in self.all_selected_tags:
                # Duplication
                tester_res.set_total_fail_bin(FailureCodes.DUPLICATION_OFFLINE)
                tester_res.set_packet_status(adv_address=selected_tag, status='duplication')
                self.logger.warning(f'DUPLICATION for Adva: {selected_tag}')
            else:
                # PASS
                self.all_selected_tags.append(selected_tag)
                is_pass = True
        if not is_pass:
            self.logger.warning(f'Tag {self.tested} Failed - {tester_res.get_total_fail_bin(as_name=True)}')
        self.all_tags += tester_res.get_test_unique_adva()
        self.all_tags = list(set(self.all_tags))
        self.is_passed_list.append(is_pass)

    def is_printing_calibration(self):
        return self.user_config['printingFormat'].lower() == 'test' and self.user_config['toPrint'].lower() == 'yes'

    @staticmethod
    def calculating_ttfp_avg(ttfp_list):
        ttfp_list_no_nan = [x for x in ttfp_list if not np.isnan(x)]
        if ttfp_list_no_nan:
            return np.mean(ttfp_list_no_nan)
        return float(-1)

    def end_test(self, tester_res):
        self.ttfp_list.append(tester_res.get_total_ttfp())
        test_data = {'temperature_sensor': float(-1),
                     'tested': self.get_tested(),
                     'passed': self.get_passed(),
                     'responded': self.get_responded(),
                     'missing_label': self.get_missing_label_count(),
                     'ttfp_avg': self.calculating_ttfp_avg(self.ttfp_list)}
        if self.temperature_sensor_handle.enable:
            try:
                test_data['temperature_sensor'] = self.temperature_sensor_handle.get_temperature()
            except Exception as e:
                self.logger.warning(f'end test: could not read from sensor due to {e}')
        tester_res.set_test_info(test_info=test_data)
        if self.tag_results_q.full():
            raise TagTestingException('end_test: tag results queue is full - error in offset definition')
        self.tag_results_q.put(tester_res, block=False)
        self.test_end_event.set()

    def wait_for_moh(self):
        self.logger.info('TagTesting: wait for manual operation handling')
        while True:
            time.sleep(1)
            if not self.moh.get_manual_operation_is_needed():
                break
            if self.stop_app_event.is_set():
                break

    def get_tested(self):
        return self.tested

    def get_responded(self):
        return len(self.all_tags)

    def get_passed(self):
        return len(self.all_selected_tags)

    def get_missing_label_count(self):
        return self.missing_labels

    def get_is_passed_list(self):
        return self.is_passed_list.copy()

    def get_ttfp_list(self):
        return self.ttfp_list

    def stop(self):
        self.wiliot_tester.exit_tag_test()
        self.logger.info('TagTesting Thread is done')

    def get_gw_version(self):
        return self.wiliot_tester.get_gw_version()


class AttenuatorHandle(object):
    def __init__(self, logger_name, exception_q, attenuator_configs=None):
        self.logger = logging.getLogger(logger_name)
        self.exception_q = exception_q
        self.enable = True
        if attenuator_configs is None or attenuator_configs['AutoAttenuatorEnable'].lower() == 'no':
            self.logger.info('Attenuator is disable')
            self.enable = False
            return

        self.attenuator_configs = attenuator_configs
        if self.attenuator_configs['attnComport'].upper() == 'AUTO':
            self.attenuator = Attenuator('API').GetActiveTE()
        else:
            self.attenuator = Attenuator('API', comport=f'COM{self.attenuator_configs["attnComport"]}').GetActiveTE()
        current_attn = self.attenuator.Getattn()
        self.logger.info(f'Attenuator is connected at port {self.attenuator.comport} and set to: {current_attn}')
        self.set_value()

    def set_value(self, attenuator_val=None):
        if attenuator_val is None:
            attenuator_val = self.attenuator_configs['attnval']
        try:
            set_attn_status = self.attenuator.Setattn(int(attenuator_val))
        except Exception as e:
            raise AttenuatorException(f'AttenuatorHandle Exception: set_value: {e}')
        if set_attn_status == attenuator_val:
            self.logger.info(f'Attenuation is set to {attenuator_val} dB')
        else:
            raise AttenuatorException(f'AttenuatorHandle Exception: set_value: failed to set attenuation value '
                                      f'(expected: {attenuator_val}, current: {set_attn_status})')

    def set_dynamic_value(self):
        pass


class TemperatureSensorHandle(object):
    def __init__(self, logger_name, exception_q, sensor_configs=None):
        self.logger = logging.getLogger(logger_name)
        self.exception_q = exception_q
        self.enable = True
        if sensor_configs is None or sensor_configs['temperatureSensorEnable'].lower() == 'no':
            self.logger.info('Temperature Sensor is disable')
            self.enable = False
            return

        self.sensor_configs = sensor_configs
        try:
            self.temp_sensor = YoctoTemperatureSensor()
            self.temp_sensor.connect()
            sensor_name = self.temp_sensor.get_sensor_name()
            self.logger.info(f'Connected to temperature sensor: {sensor_name}')
        except Exception as e:
            raise SensorException(f'TemperatureSensorHandle Exception: init: {e}')

    def get_temperature(self):
        try:
            cur_temp = self.temp_sensor.get_temperature()
            self.logger.info(f'Measured temperature from sensor: {cur_temp}')
            if cur_temp == float('nan'):
                self.logger.warning('TemperatureSensorHandle: Could not measure temperature from sensor')
            return cur_temp
        except Exception as e:
            raise Exception(f'SENSOR: TemperatureSensorHandle Exception: get_temperature: {e}')
