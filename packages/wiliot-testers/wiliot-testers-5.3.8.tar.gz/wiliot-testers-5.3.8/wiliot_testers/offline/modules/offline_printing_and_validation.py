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

from queue import Queue
import socket
from wiliot_testers.tester_utils import open_json_cache
from wiliot_testers.offline.modules.offline_utils import R2rGpio, ConfigDefaults, get_printed_value, \
    get_print_user_config_file, DefaultGUIValues
from wiliot_testers.test_equipment import BarcodeScanner, CognexDataMan
from wiliot_testers.wiliot_tester_tag_result import FailureCodes, WiliotTesterTagResultList
from wiliot_testers.offline.configs.global_vars_and_enums import PrintingAndValidationDefaults, ASTRIX

import os
import json
import time
import logging
from threading import Event
import datetime
from enum import Enum


class PrintingAndValidationException(Exception):
    def __init__(self, msg):
        self.message = msg
        super().__init__(f'PrintingAndValidation Exception: {self.message}')


class PrinterException(PrintingAndValidationException):
    def __init__(self, msg):
        super().__init__(f'Printer: {msg}')


class ScannerException(PrintingAndValidationException):
    def __init__(self, msg):
        super().__init__(f'Scanner: {msg}')


class R2RException(PrintingAndValidationException):
    def __init__(self, msg):
        super().__init__(f'R2R: {msg}')


class ValidationStates(Enum):
    IDLE = 0
    STOP = 99
    WAIT_MOH = 88
    WAIT_START = 81
    WAIT_END = 82
    START_TEST = 1
    PRE_VALIDATION = 2
    VALIDATION = 3
    PRINTER_ACK = 4
    SET_NEXT_PRINT = 5
    END_TEST = 6
    NEXT_TAG = 7
    LOG_DATA = 8


class ValidatedBin(Enum):
    # even values are good
    UNTESTED = 0  # not tested by the scanner
    PRINT_ACK_ONLY = 2  # got acknowledgement from printer
    MATCH = 4  # ext. id/black square as expected
    # odd values are bad
    MISMATCH = 3  # ex id/black square not as expected (should be a different ex.id or black square)
    NO_READ = 1  # expect to read ex id, but no success reading it
    ERROR = 99


class PrintingAndValidation(object):
    def __init__(self, test_start_event, test_end_event, stop_app_event, moh_object, test_object,
                 exception_queue, tag_results_queue, log_obj=None, user_config=None, gw_version=''):
        """

        @param test_start_event: event is set when tag is under test
        @type test_start_event: Event
        @param test_end_event: event is set when tag test was completed
        @type test_end_event: Event
        @param moh_object: an object contains all functions related to MOH event, Manual Operation Handling
        @type moh_object: Object
        @param test_object: an object contains all functions related to test parameters
        @type test_object: TestParameters
        @param exception_queue: queue for all exceptions, handled in the main class
        @type exception_queue: Queue
        @param tag_results_queue: queue for tag test results, sent from the tag test class
        @type tag_results_queue: Queue
        @param user_config: all user configuration inputs
        @type user_config: dict or None
        """
        self.test_start_event = test_start_event
        self.test_end_event = test_end_event
        self.stop_app_event = stop_app_event
        self.exception_q = exception_queue
        self.tag_results_q = tag_results_queue
        self.end_of_test_tags = []
        self.moh = moh_object
        self.test = test_object
        self.logger = logging.getLogger(log_obj.get_logger_name())
        self.is_print = user_config['toPrint'].lower() == 'yes'
        self.is_scanner = user_config['QRRead'].lower() == 'yes'
        self.is_r2r = user_config['isR2R'].lower() == 'yes' if 'isR2R' in user_config else True
        self.last_state = ValidationStates.IDLE
        self.tag_run_location = -1
        self.external_id_counter = 0
        self.tag_result_to_validate = None

        self.is_init = False
        try:
            self.printer = Printer(is_print=self.is_print,
                                   exception_queue=exception_queue,
                                   logger_name=log_obj.get_logger_name(),
                                   printing_config=log_obj.get_log_config())

            self.r2r = R2R(is_r2r=self.is_r2r,
                           exception_queue=exception_queue,
                           logger_name=log_obj.get_logger_name())

            self.scanner = Scanner(is_scanner=self.is_scanner,
                                   exception_queue=exception_queue,
                                   logger_name=log_obj.get_logger_name(),
                                   scanning_config=user_config,
                                   is_print=self.is_print)

            self.data_logging = log_obj
            self.data_logging.run_data_init(is_printing=self.is_print, gw_version=gw_version,
                                            test_suite_dict=test_object.get_selected_test_suite())

            self.is_init = True
        except Exception as e:
            if isinstance(e, PrintingAndValidationException):
                self.exception_q.put(f'init: {e}', block=False)
            else:
                self.exception_q.put(PrintingAndValidationException(f'{e}').__str__(), block=False)
            return

        # init Queues
        try:
            self.validation_q = None
            self.init_validation_q()
            self.printing_type_q = None
            self.init_printing_type_q()
        except Exception as e:
            if isinstance(e, PrintingAndValidationException):
                self.exception_q.put(f'init: queues: {e}', block=False)
            else:
                self.exception_q.put(PrintingAndValidationException(f'init: queues: {e}').__str__(), block=False)
            return

        # move to the first tag:
        try:
            if self.is_print:
                self.set_next_printing_type(False)
            self.r2r.move_to_the_first_tag()
        except Exception as e:
            if isinstance(e, PrintingAndValidationException):
                self.exception_q.put(f'init: move to the first tag: {e}', block=False)
            else:
                self.exception_q.put(PrintingAndValidationException(f'init: move to the first tag: {e}').__str__(),
                                     block=False)
            return

    def init_validation_q(self):
        if self.is_scanner:
            q_size = self.scanner.scanning_config['QRoffset']
        elif self.is_print:
            q_size = self.printer.printing_config['printOffset'] + PrintingAndValidationDefaults.QUEUE_VALIDATION_OFFSET
        else:
            q_size = 1  # No validation is needed
        self.validation_q = Queue(maxsize=int(q_size))

    def init_printing_type_q(self):
        offset_printing = 0
        if self.is_print:
            q_size = self.printer.printing_config['printOffset']
            # Since when using gpio and not line selection the pulse selects the next print
            offset_printing = 0 if self.printer.printing_config['enableLineSelection'].lower() == 'yes' else 1
        else:
            q_size = 0  # No Printing is needed
        self.printing_type_q = Queue(maxsize=q_size)
        if q_size == 0:
            return

        for k in range(q_size - offset_printing):
            self.printing_type_q.put(False, block=False)

    def run(self):
        state = ValidationStates.IDLE
        next_tag_status = False
        self.printer.reset_printer_ack()

        while True:
            time.sleep(0)
            try:
                state = self.update_state(state)
                self.logger.info(f'PrintingAndValidation: start state {state}')
                if state == ValidationStates.STOP:
                    self.logger.info('Stop running PrintingAndValidation main loop')
                    break

                elif state == ValidationStates.WAIT_MOH:
                    # wait if Manual Operation Handling is needed:
                    self.wait_for_moh()

                elif state == ValidationStates.WAIT_START:
                    # wait till event start_testing is set
                    self.wait_for_new_event(event=self.test_start_event,
                                            time_to_wait=PrintingAndValidationDefaults.EVENT_WAIT_TIME)

                elif state == ValidationStates.START_TEST:
                    # Stop R2R if long test
                    self.tag_run_location += 1
                    self.logger.info(f'{ASTRIX} PrintingAndValidation: START_TEST: '
                                     f'new tag location {self.tag_run_location} {ASTRIX}')
                    if self.is_r2r and \
                            self.test.get_total_test_time() > PrintingAndValidationDefaults.MAX_R2R_WAIT_TIME:
                        self.r2r.send_stop_to_r2r()

                elif state == ValidationStates.PRE_VALIDATION:
                    # Validation
                    self.tag_result_to_validate = None
                    if self.validation_q.full() or self.stop_app_event.is_set():
                        self.tag_result_to_validate = self.validation_q.get(block=False)
                    else:
                        self.logger.info('PrintingAndValidation: PRE_VALIDATION: Waiting for the first tag to arrive')

                elif state == ValidationStates.VALIDATION:
                    if self.tag_result_to_validate is not None:
                        self.validation(self.tag_result_to_validate)

                elif state == ValidationStates.PRINTER_ACK:
                    if self.need_to_check_printer_ack():
                        is_ack = self.printer.get_printing_ack()
                        if not is_ack:
                            raise PrinterException('did not get printing acknowledgement (PRC)')

                elif state == ValidationStates.SET_NEXT_PRINT:
                    if not self.printer.printing_during_movement:
                        time.sleep(PrintingAndValidationDefaults.PRINTER_90_DEG_WAIT_LSL)
                    # select next printing type
                    if self.is_print:
                        if self.printing_type_q.empty():
                            self.logger.info(
                                'PrintingAndValidation: SET_NEXT_PRINT: set next printing to False since queue empty')
                            next_tag_status = False
                            self.logger.info('PrintingAndValidation: SET_NEXT_PRINT: '
                                             'set printing type to false since queue is empty')
                        else:
                            next_tag_status = self.printing_type_q.get(block=False)
                        self.set_next_printing_type(next_tag_status)

                elif state == ValidationStates.WAIT_END:
                    # wait till event end_of_testing is set
                    self.wait_for_new_event(
                        event=self.test_end_event,
                        time_to_wait=self.test.get_total_test_time() + PrintingAndValidationDefaults.EVENT_WAIT_TIME)

                elif state == ValidationStates.END_TEST:
                    # update class queue:
                    if self.tag_results_q.empty():
                        if self.is_print:
                            self.logger.info(f'Empty tag_results_q during {state}')
                            self.add_end_of_test_tags()

                    else:
                        cur_tag_to_print = self.tag_results_q.get(timeout=0.1, block=False)
                        cur_tag_to_print.set_test_info({'tag_run_location': self.tag_run_location,
                                                        'tag_reel_location': self.get_tag_reel_location()})
                        self.add_external_id_to_tag_results(tag_result_to_validate=cur_tag_to_print)
                        self.validation_q.put(cur_tag_to_print, block=False)
                        if self.is_print:
                            self.printing_type_q.put(cur_tag_to_print.is_all_tests_passed(), block=False)

                elif state == ValidationStates.NEXT_TAG:
                    # send signal to the r2r to move
                    self.printer.reset_printer_ack()
                    self.r2r.move_r2r(is_pass=next_tag_status)

                elif state == ValidationStates.LOG_DATA:
                    # log data
                    if self.tag_result_to_validate is not None:
                        self.log_data(self.tag_result_to_validate)
                        self.tag_result_to_validate = None
                    if self.is_print:
                        self.update_printer_configs()

                self.logger.info(f'PrintingAndValidation: end state {state}')
            except Exception as e:
                if isinstance(e, PrintingAndValidationException):
                    self.exception_q.put(f'run: state{state.name}: {e}', block=False)
                else:
                    self.exception_q.put(PrintingAndValidationException(f'run: state{state.name}: {e}').__str__(),
                                         block=False)
                if state == ValidationStates.VALIDATION:
                    tag_info = self.tag_result_to_validate.get_test_info()
                    if 'validated' not in tag_info or ValidatedBin[tag_info['validated']].value % 2 == 0:
                        self.tag_result_to_validate.set_test_info({'validated': ValidatedBin.ERROR.name})
                        self.tag_result_to_validate.set_total_fail_bin(fail_code=FailureCodes.SOFTWARE_GENERAL_ERROR,
                                                                       overwrite=True)
                        self.logger.warning(f'PrintingAndValidation: run: state{state.name}: '
                                            f'Error during validation: {tag_info}')
                    else:
                        self.tag_result_to_validate.set_total_fail_bin(fail_code=FailureCodes.BAD_PRINTING)

        self.stop()

    def update_state(self, state):
        # after MOH was done, continue to the next state
        if state == ValidationStates.WAIT_MOH:
            state = self.last_state

        # when event occurred
        if self.stop_app_event.is_set():
            if self.validation_q.empty() and self.tag_results_q.empty():
                if state == ValidationStates.LOG_DATA:
                    state = ValidationStates.STOP
                if state == ValidationStates.END_TEST:
                    state = ValidationStates.NEXT_TAG  # skip NEXT_TAG stage since this is the last iteration
        elif self.moh.get_manual_operation_is_needed():
            self.last_state = state
            state = ValidationStates.WAIT_MOH

        # main flow
        if state == ValidationStates.IDLE:
            state = ValidationStates.WAIT_START
        elif state == ValidationStates.WAIT_START:
            state = ValidationStates.START_TEST
        elif state == ValidationStates.START_TEST:
            state = ValidationStates.PRE_VALIDATION
        elif state == ValidationStates.PRE_VALIDATION:
            state = ValidationStates.VALIDATION
        elif state == ValidationStates.VALIDATION:
            state = ValidationStates.PRINTER_ACK
        elif state == ValidationStates.PRINTER_ACK:
            state = ValidationStates.SET_NEXT_PRINT
        elif state == ValidationStates.SET_NEXT_PRINT:
            state = ValidationStates.WAIT_END
        elif state == ValidationStates.WAIT_END:
            state = ValidationStates.END_TEST
        elif state == ValidationStates.END_TEST:
            state = ValidationStates.NEXT_TAG
        elif state == ValidationStates.NEXT_TAG:
            state = ValidationStates.LOG_DATA
        elif state == ValidationStates.LOG_DATA:
            state = ValidationStates.WAIT_START

        return state

    def need_to_check_printer_ack(self):
        return self.is_print and self.is_scanner and self.printer.printing_config['enablePrinterAck'].lower() == 'yes'

    def add_external_id_to_tag_results(self, tag_result_to_validate):
        expected_external_id = ''
        configs = self.data_logging.get_log_config()
        if self.is_print:
            if tag_result_to_validate.is_all_tests_passed():
                expected_external_id = self.printer.get_expected_external_id(counter=self.external_id_counter)
                self.external_id_counter += 1
            else:
                expected_external_id = ''
                if configs['printingFormat'] == 'prePrint':
                    self.external_id_counter += 1
            tag_result_to_validate.set_test_info({'external_id': expected_external_id})
            self.logger.info(f'PrintingAndValidation: assigned external id {expected_external_id}')
        return expected_external_id

    def get_validation_q_size(self):
        return self.validation_q.qsize()

    def get_validation_q_maxsize(self):
        return self.validation_q.maxsize

    def get_tag_reel_location(self):
        configs = self.data_logging.get_log_config()
        offset = int(configs['tag_reel_location']) if 'tag_reel_location' in configs.keys() else 0
        return self.tag_run_location + offset

    def update_scanning_results_after_exception(self):
        if not self.is_scanner:
            return ''
        test_info = {'external_id': 'unknown'}
        try:
            test_info = self.tag_result_to_validate.get_test_info()
            self.validation(self.tag_result_to_validate)
            self.tag_result_to_validate.set_total_fail_bin(fail_code=FailureCodes.PASS, overwrite=True)
        except Exception as e:
            self.logger.warning(f'update_scanning_results_after_exception: {e}')
            return f"Re-Validation for external id {test_info['external_id']} Failed: {e}"
        return f"Re-Validation for external id {test_info['external_id']} was successful"

    def set_next_printing_type(self, is_pass):
        """

        @param is_pass:
        @type is_pass: bool or None
        @return:
        @rtype:
        """
        if is_pass is None:
            is_pass = False
        if self.is_print:
            if self.printer.enable_line_selection:
                try:
                    self.printer.set_printing_type(is_tag_passed=is_pass)
                except Exception as e:
                    raise PrinterException(f'set_next_printing_type: {e}')

    def wait_for_new_event(self, event, time_to_wait):
        t_start = datetime.datetime.now()
        while not event.is_set():
            if self.stop_app_event.is_set():
                self.logger.info('stop application during waiting for event')
                time.sleep(PrintingAndValidationDefaults.MIN_WAIT_TIME)
                break
            elif self.moh.get_manual_operation_is_needed():
                self.wait_for_moh()
                t_start = datetime.datetime.now()
            event.wait(0.1)
            dt = (datetime.datetime.now() - t_start).total_seconds()

            if dt > time_to_wait and not self.moh.get_manual_operation_is_needed():
                raise PrintingAndValidationException('wait_for_new_event: did not receive ack for '
                                                     'starting/ending tag test')
        event.clear()

    def wait_for_moh(self):
        try:
            if self.is_r2r:
                self.r2r.send_stop_to_r2r()
        except Exception as e:
            self.logger.warning(f'Could not stop R2R during wait for manual operation handling due to {e}')
        self.logger.info('PrintingAndValidation: wait for manual operation handling')
        while True:
            time.sleep(1)
            if not self.moh.get_manual_operation_is_needed():
                break
            if self.stop_app_event.is_set():
                break

    def validation(self, expected_result):
        """

        @param expected_result:
        @type expected_result: WiliotTesterTagResultList
        @return:
        @rtype:
        """
        is_validated = ValidatedBin.UNTESTED
        test_info = {"external_id": ''}
        hw_exc = ''

        if self.is_print and self.is_scanner:
            # scan and compare
            test_info = expected_result.get_test_info()
            try:
                is_validated = self.scanner.validated_scan_data(expected_value=test_info['external_id'])
            except Exception as e:
                is_validated = ValidatedBin.NO_READ
                hw_exc = f' [{e}]'

        elif self.is_print and not self.is_scanner:
            # get_status from printer
            if not self.printer.printing_during_movement:
                time.sleep(PrintingAndValidationDefaults.PRINTER_90_DEG_WAIT_TIME)
            status = self.printer.get_printer_status(counter=self.r2r.get_counter(),
                                                     is_pass=expected_result.is_all_tests_passed())
            if status:
                is_validated = ValidatedBin.PRINT_ACK_ONLY
            else:
                is_validated = ValidatedBin.MISMATCH

        elif not self.is_print and self.is_scanner:
            raise PrintingAndValidationException('validation: Currently scanning without printing is not supported')
        else:  # no print and no scanner
            pass

        expected_result.set_test_info({'validated': is_validated.name})
        if is_validated.value % 2 == 1:
            raise PrintingAndValidationException(
                f'Validation Failed due to: {is_validated} for external id: {test_info["external_id"]}{hw_exc}')

    def log_data(self, new_tag_results):
        # update packet data
        self.data_logging.update_packets_data(res=new_tag_results)
        # update run data
        self.data_logging.update_run_data(res=new_tag_results)

    def add_end_of_test_tags(self):
        if self.is_print:
            dummy_dict = {'tag_run_location': self.tag_run_location,
                          'tag_reel_location': self.get_tag_reel_location(),
                          'fail_bin': FailureCodes.END_OF_TEST.value,
                          'fail_bin_str': FailureCodes.END_OF_TEST.name}
            self.end_of_test_tags.append(dummy_dict)

    def add_end_of_test_to_log(self):
        for dummy_tag in self.end_of_test_tags:
            # Update only packet data
            self.data_logging.update_default_test_data(dummy_tag)
            self.data_logging.update_packets_data()

    def update_printer_configs(self):
        # update printing config:
        configs = self.data_logging.get_log_config()
        if not configs['toPrint'].lower() == 'yes':
            return
        file_name = get_print_user_config_file(configs['printingFormat'])
        config_path = os.path.join(self.test.dir_config, file_name)
        data = open_json_cache(folder_path=self.test.dir_config,
                               file_path=config_path,
                               default_values=DefaultGUIValues(configs['printingFormat']).default_gui_values)
        data['firstPrintingValue'] = self.printer.get_expected_external_id(
            counter=self.external_id_counter)[-PrintingAndValidationDefaults.TAG_COUNT_SIZE:]
        data['tagLocation'] = str(self.tag_run_location)
        data['tag_reel_location'] = str(self.get_tag_reel_location() +
                                        PrintingAndValidationDefaults.R2R_START_OFFSET)
        with open(config_path, "w") as f:
            json.dump(data, f)

    def stop(self):
        if self.end_of_test_tags:
            self.add_end_of_test_to_log()
        if self.printer.enable:
            self.update_printer_configs()
            self.printer.exit()
        if self.scanner.enable:
            self.scanner.exit()
        if self.r2r.enable:
            self.r2r.exit()


class Printer(object):
    def __init__(self, is_print, exception_queue, logger_name, printing_config=None):
        """

        @param exception_queue:
        @type exception_queue: Queue
        @param logger_name:
        @type logger_name: str
        @param printing_config:
        @type printing_config: dict
        """
        self.exception_queue = exception_queue
        self.logger = logging.getLogger(logger_name)
        self.printing_config = printing_config
        self.got_printer_ack = False
        self.enable = True
        if printing_config is None or not is_print:
            self.logger.info('Printer is disable')
            self.enable = False
            return

        self.printer_socket = None
        self.dir_config = os.path.abspath(os.path.join(os.path.dirname(__file__), '../configs'))

        self.enable_line_selection = self.printing_config['enableLineSelection'].lower() == 'yes'
        self.printing_during_movement = self.printing_config['printingDuringMovement'].lower() == 'yes'
        self.cur_value = 0

        try:
            printer_configs = self.set_printer_config()
            self.printing_config = {**self.printing_config, **printer_configs}
            self.init_printer_hw_connection()
            self.init_printing_protocols()
            self.logger.info('PRINTER: printer is ready after initialization')
        except Exception as e:
            raise PrinterException(f'init: {e}')

    def init_printer_hw_connection(self):
        self.open_printer_socket()
        self.logger.info('PRINTER: printer is connected')
        self.set_printer_to_running()
        self.logger.info('PRINTER: printer is running')

    def get_expected_external_id(self, counter=0):
        if self.enable:
            tag_counter = counter + int(self.printing_config['firstPrintingValue']
                                        if 'firstPrintingValue' in self.printing_config.keys() else 0)
            printed_external_id, is_ok = get_printed_value(
                self.printing_config['stringBeforeCounter'],
                str(tag_counter))
            if not is_ok:
                raise PrinterException('get_expected_external_id: failed to get a valid printed value')
            return printed_external_id

    def set_printer_config(self):
        try:
            defaults = ConfigDefaults()

            file_config = os.path.abspath(os.path.join(self.dir_config, 'configs_for_printer_values.json'))
            printer_configs = open_json_cache(self.dir_config, file_config, defaults.get_printer_defaults())
        except Exception as e:
            raise PrinterException(f'init: set_printer_config: {e}')
        return printer_configs

    def is_connected(self):
        try:
            if self.printer_socket is None:
                return False
            self.query(self.get_state_request())
            return True
        except Exception as e:
            return False

    def open_printer_socket(self):
        """
        opens the printer socket
        """
        try:
            if not self.is_connected():
                self.printer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.printer_socket.settimeout(PrintingAndValidationDefaults.PRINTER_SOCKET_TIMEOUT)
                self.printer_socket.connect((self.printing_config['TCP_IP'],
                                             int(self.printing_config['TCP_PORT'])))
        except Exception as e:
            raise PrinterException(f'could not open_printer_socket: {e}')

    def exit(self):
        try:
            time.sleep(4)  # wait for printer to finish last print
            self.query(self.set_state_command('2'))  # for regular closure (not when connection error happens)
            self.printer_socket.close()
        except Exception as e:
            self.logger.warning(f'Could not exit printer due to: {e}')

    def set_printer_to_running(self):
        """
        sets the printer to running mode
        Zipher Text Communications Protocol
        printer state machine:
           0 -> 1                      shutdown
           1 -> 4 (automatically)      starting-up
           2 -> 0 (automatically)      shutting-down
           3 -> 2, 4                   running
           4 -> 2, 3                   offline
        @except: PrinterNeedsResetException('Printer failed to switch to running mode')
        @return: None
        """
        res = self.query(self.get_state_request())
        parts = res.split('|')
        if len(parts) < 2:
            raise PrinterException(f'set_printer_to_running: got unexpected results {res}')
        if parts[1] == '0':  # (Shut down)
            res = self.query(self.set_state_command('1'))
            if res == 'ACK':
                counter = 0
                while counter < 10:
                    time.sleep(1)
                    res = self.query(self.set_state_command('3'))
                    if res == 'ACK':
                        return
                    counter += 1
        elif parts[1] == '3':  # (Running)
            return
        elif parts[1] == '4':  # (Offline)
            res = self.query(self.set_state_command('3'))
            if res == 'ACK':
                return
        e = 'Printer failed to switch to running mode'
        raise PrinterException(f'set_printer_to_running: {e}')

    def query(self, cmd, ignore_printer_ack=True):
        """Send the input cmd string via TCPIP Socket
        @type cmd: str
        @param cmd: command to send to printer
        @type ignore_printer_ack: bool
        @param ignore_printer_ack: if True, ack printer msg is ignored (PRC)
        @return: the reply string
        """
        cmd_str = cmd.strip('\r\n')
        self.logger.info(f'Sent command to printer: {cmd_str}')
        self.printer_socket.send(cmd.encode())
        values = self.read(cmd=cmd)
        if 'PRC' in values:
            self.got_printer_ack = True
            if len(set(values)) == 1:  # only PRC was received
                values = self.read(cmd=cmd)
        for value in values:
            if value != 'PRC' and value != '':
                return value

        raise Exception(f'Printer: query: did not ack to the following cmd :{cmd}')

    def read(self, cmd=''):
        data = self.printer_socket.recv(int(self.printing_config['TCP_BUFFER']))
        self.logger.info(f'Received RAW answer from printer: {data}')
        if len(data) == 0:
            raise PrinterException(f'query: did not ack to the following cmd :{cmd}' if cmd else '')
        value = data.decode("utf-8")
        str_split = '\r\n'
        if str_split not in value:
            str_split = '\r' if '\r' in value else '\n'

        values = value.split(str_split)[:-1]
        self.logger.info(f'Received answer from printer: {values}')
        return values

    def reset_printer_ack(self):
        self.got_printer_ack = False

    def get_printing_ack(self):
        if self.got_printer_ack:
            self.got_printer_ack = False
            return True
        t_i = datetime.datetime.now()
        dt = 0.0
        while dt < PrintingAndValidationDefaults.MIN_TEST_TIME:
            try:
                values = self.read()
                if 'PRC' in values:
                    return True
                raise PrinterException(f'while waiting for ack, received a different response: {values}')
            except Exception as e:
                self.logger.info(f'Printer got exception, try again ({e})')
                dt = (datetime.datetime.now() - t_i).total_seconds()
                time.sleep(PrintingAndValidationDefaults.TIME_BTWN_PRINTER_REQUESTS)
        return False

    def get_printer_status(self, counter, is_pass):
        t_i = datetime.datetime.now()
        dt = 0.0
        while dt < PrintingAndValidationDefaults.MIN_TEST_TIME:
            try:
                status = self.printer_status(counter=self.cur_value + counter, is_pass=is_pass)
                if status:
                    return True
                dt = (datetime.datetime.now() - t_i).total_seconds()
                time.sleep(PrintingAndValidationDefaults.TIME_BTWN_PRINTER_REQUESTS)
            except Exception as e:
                raise PrinterException(f'get_printer_status: exception:({e})')

        return False

    @staticmethod
    def get_state_request():
        """
        gets the situation of the printer
        @return: the situation in the printer in the following format:
            STS|<overallstate>|<errorstate>|<currentjob>|<batchcount>|<totalcount>|<
        """
        cmd = 'GST\r\n'
        return cmd

    @staticmethod
    def set_state_command(desired_state):
        """
        builds the command to send to printer for setting a printer state
        @param desired_state: the state to enter to, according to the following description
        0 Shut down
        1 Starting up
        2 Shutting down
        3 Running
        4 Offline
        @return: the cmd to send to printer
        """
        cmd = 'SST|' + str(desired_state) + '|\r\n'
        return cmd

    @staticmethod
    def get_line_selection_cmd(is_pass):
        line = PrintingAndValidationDefaults.PASS_JOB_NUM if is_pass else PrintingAndValidationDefaults.FAIL_JOB_NUM
        return f"LSL|{line}|\r\n"

    def set_job_fields(self, tag_num_offset=0):
        pass_job_name = self.printing_config['passJobName']
        fail_job_name = self.printing_config['failJobName']
        reel_id = self.printing_config["stringBeforeCounter"]

        tag_num_int = int(self.printing_config["firstPrintingValue"]) + tag_num_offset
        tag_num_str = str(tag_num_int).zfill(4)
        if 'BARCODE' in pass_job_name.upper():
            job_fields = [f'reel_num={reel_id}T']
        elif 'SGTIN' in pass_job_name.upper():
            job_fields = [f'sgtin={reel_id[:18]}',
                          f'reel_num={reel_id[18:26]}T']
        elif 'BLANK' in pass_job_name.upper():
            job_fields = []
        else:
            raise PrinterException('Job Name inserted is not supported at the moment')

        if pass_job_name != 'BLANK':
            job_fields.append(f'tag_number={tag_num_str}')
        job_fields.append('\r\n')
        job_fields_str = '|'.join(job_fields)

        pass_job_fields_cmd = f'LAS|{pass_job_name}|{PrintingAndValidationDefaults.PASS_JOB_NUM}|' + job_fields_str
        fail_job_fields_str = '\r\n' if fail_job_name != pass_job_name else job_fields_str
        fail_job_fields_cmd = f'LAS|{fail_job_name}|{PrintingAndValidationDefaults.FAIL_JOB_NUM}|' + fail_job_fields_str

        return pass_job_fields_cmd, fail_job_fields_cmd

    def init_printing_protocols(self, tag_num_offset=0):

        try:
            pass_job_fields_cmd, fail_job_fields_cmd = self.set_job_fields(tag_num_offset=tag_num_offset)

            cmds = ['CAF\r\n',
                    'CQI\r\n',
                    f'CLN|{PrintingAndValidationDefaults.PASS_JOB_NUM}|\r\n',
                    f'CLN|{PrintingAndValidationDefaults.FAIL_JOB_NUM}|\r\n',
                    pass_job_fields_cmd,
                    fail_job_fields_cmd]

            for cmd in cmds:
                value = self.query(cmd)
                time.sleep(0.1)
                # check if the return value is good, if not retry again for 10 times
                counter = 0
                while counter < 10:
                    # 'CQI' fails if the queue is empty
                    if value == 'ERR' and 'CQI' not in cmd:
                        counter += 1
                        time.sleep(0.1)
                        value = self.query(cmd)
                    else:
                        break
                if counter >= 10:
                    raise PrinterException('initialization process has failed in command: ' + cmd)
            # get the current counter value
            value = self.query(self.get_state_request())
            if value == 'ERR':
                raise PrinterException('initialization process has failed in command: ' + self.get_state_request())
            else:
                parts = [p for p in value.split("|")]
                if len(parts) < 6:
                    raise PrinterException(f'init_printing_protocols: got unexpected results {value}')
                self.cur_value = int(parts[5])

        except Exception as e:
            raise PrinterException(f'init_printing_protocols: {e}')

    def set_printing_type(self, is_tag_passed):
        """
        line selection
        @return:
        @rtype:
        """
        try:
            line_selection_msg = self.get_line_selection_cmd(is_tag_passed)
            rsp = ''
            t_0 = datetime.datetime.now()
            dt = 0
            timeout_ack = 1
            while rsp != 'ACK' and dt < timeout_ack:
                rsp = self.query(line_selection_msg)
                if rsp == 'ACK':
                    return
                dt = (datetime.datetime.now() - t_0).total_seconds()
            raise PrinterException('set_printing_type: Did not get ACK for Line Selection')
        except Exception as e:
            raise PrinterException(f'set_printing_type: Did not get ACK for Line Selection: {e}')

    def printer_status(self, counter, is_pass):
        """
        checks if the printing value matches the values registered to the logs
        should be called only after self.events.r2r_ready was set
        Exceptions:
            @except Exception('The printer printed Pass to the previous tag'):
                    printer printed pass while it should have been print fail
            @except Exception('The printer printed Fail to the previous tag')
                    printer printed fail while it should have been print pass
            @except Exception('The printer have not printed on the last tag')
                    printer did not print while it should have been
        """
        res = self.query(
            self.get_state_request())  # STS|<overallstate>|<errorstate>|<currentjob>|<batchcount>|<totalcount>
        parts = [p for p in res.split("|")]
        if len(parts) < 6:
            raise PrinterException(f'printer_status: got unexpected results {res}')
        if parts[1] == '3':
            if parts[2] == '0':
                if int(parts[5]) == counter:
                    if not self.printing_config['printingFormat'] != 'Test':
                        job_name = self.printing_config['passJobName'] if is_pass else \
                            self.printing_config['failJobName']

                        if parts[3] == job_name:
                            self.logger.debug(f'Compare success with type {job_name} and counter {counter}')
                            return True
                        else:
                            self.logger.info(f'Printer type was not right (expected: {job_name}, got: {parts[3]}')
                            return False
                    else:
                        self.logger.debug(f'Compare success with counter {counter}')
                        return True
                else:
                    self.logger.info(f'The printer counter is not synced (expected: {counter}, got: {parts[5]}'
                                     f', trying again')
                    return False
            else:
                if parts[2] == '1':
                    raise PrinterException('error-state is Warnings present')
                if parts[2] == '2':
                    raise PrinterException('error-state is Faults present')
        else:
            if parts[1] == '0':
                raise PrinterException('over-all-state is Shutdown')
            if parts[1] == '1':
                raise PrinterException('over-all-state is Starting up')
            if parts[1] == '2':
                raise PrinterException('over-all-state is Shutting down')
            if parts[1] == '4':
                raise PrinterException('over-all-state is Offline')
            if parts[2] == '1':
                raise PrinterException('error-state is Warnings present')
            if parts[2] == '2':
                raise PrinterException('error-state is Faults present')


class Scanner(object):
    def __init__(self, is_scanner, exception_queue, logger_name, scanning_config, is_print=False):
        """

        @param exception_queue:
        @type exception_queue:
        @param logger_name:
        @type logger_name:
        @param scanning_config: all scanner configuration
        @type scanning_config: dict
        @param is_print: True if run with printing
        @type is_print: bool
        """
        self.exception_queue = exception_queue
        self.logger = logging.getLogger(logger_name)

        self.enable = True
        if scanning_config is None or not is_scanner:
            self.logger.info('Scanner is disable')
            self.enable = False
            return

        self.scanning_config = scanning_config

        scanner_port = f'COM{scanning_config["QRcomport"]}'
        try:
            if self.scanning_config["scannerType"].lower() == 'rtscan':
                self.scanner = BarcodeScanner(com_port=scanner_port, log_type='LOG', write_to_log=not is_print,
                                              timeout=str(self.scanning_config['QRtimeout']))
            elif self.scanning_config["scannerType"].lower() == 'cognex':
                self.scanner = CognexDataMan(port=scanner_port, timeout=self.scanning_config['QRtimeout'],
                                             trigger_type=PrintingAndValidationDefaults.TRIGGER_TYPE)
            else:
                raise Exception('scanner type is not supported. Please use rtscan or cognex')
            self.logger.info('Connected to scanner at port {}'.format(scanner_port))
        except Exception as e:
            raise ScannerException(f'init: could not connect to barcode scanner {e}')

    def reconnect(self):
        try:
            if not self.scanner.is_open():
                self.scanner.open_port(com_port=self.scanner.com_port, timeout=str(self.scanning_config['QRtimeout']))
        except Exception as e:
            raise ScannerException(f'reconnect: could not connect to barcode scanner {e}')

    def validated_scan_data(self, expected_value=None):
        validated_status = ValidatedBin.UNTESTED
        t_i = datetime.datetime.now()
        dt = 0.0
        is_first = True
        while dt < PrintingAndValidationDefaults.MIN_TEST_TIME:
            try:
                scanned_data, _, _, _ = \
                    self.scanner.scan_ext_id(
                        need_to_trigger=is_first or PrintingAndValidationDefaults.TRIGGER_TYPE == 0)
                self.logger.info(f'{ASTRIX} SCANNING: expected: {expected_value}, scanned: {scanned_data} {ASTRIX}')
                if expected_value is None:
                    validated_status = ValidatedBin.UNTESTED
                elif scanned_data == expected_value or (expected_value == '' and scanned_data is None):
                    return ValidatedBin.MATCH
                elif scanned_data is None:
                    validated_status = ValidatedBin.NO_READ
                else:
                    validated_status = ValidatedBin.MISMATCH

                dt = (datetime.datetime.now() - t_i).total_seconds()
                time.sleep(PrintingAndValidationDefaults.TIME_BTWN_PRINTER_REQUESTS)
                is_first = False
            except Exception as e:
                self.scanner.trigger_off()
                raise ScannerException(f'get_scan_data: got exception from scanner ({e})')
        self.scanner.trigger_off()
        return validated_status

    def exit(self):
        try:
            self.scanner.close_port()
        except Exception as e:
            self.logger.warning(f'Could not exit scanner due to: {e}')


class R2R(object):
    def __init__(self, is_r2r, exception_queue, logger_name):
        """

        @param exception_queue:
        @type exception_queue: Queue
        @param logger_name:
        @type logger_name: str
        """
        self.exception_queue = exception_queue
        self.logger = logging.getLogger(logger_name)
        self.counter = 0

        self.enable = True
        if not is_r2r:
            self.logger.info('R2R is disable')
            self.enable = False
            return

        self.is_running = False
        try:
            self.gpio = R2rGpio(logger_name=logger_name)
        except Exception as e:
            raise R2RException(f'init: could not connect to arduino: {e}')

    def reconnect(self):
        status = self.gpio.reconnect()
        if not status:
            raise R2RException(f'reconnect: could not connect to arduino')

    def move_to_the_first_tag(self):
        self.send_start_to_r2r()
        self.move_r2r(is_pass=False)

    def send_start_to_r2r(self):
        self.gpio.gpio_state(PrintingAndValidationDefaults.START_STOP_GPIO, "ON")
        self.logger.info('R2R: PC send start to R2R')
        self.is_running = True

    def send_stop_to_r2r(self):
        self.gpio.gpio_state(PrintingAndValidationDefaults.START_STOP_GPIO, "OFF")
        self.logger.info('R2R: PC send stop to R2R')
        self.is_running = False

    def move_r2r(self, is_pass):
        if not self.is_running:
            self.send_start_to_r2r()
        gpio = PrintingAndValidationDefaults.PASS_PULSE_GPIO \
            if is_pass else PrintingAndValidationDefaults.FAIL_PULSE_GPIO
        self.gpio.pulse(gpio, PrintingAndValidationDefaults.R2R_PULSE_DURATION)
        self.logger.info(f'{ASTRIX} R2R: PC send {"pass" if is_pass else "fail"} to R2R {ASTRIX}')
        self.counter += 1

    def enable_missing_label(self, is_enable):
        gpio_on_off = 'ON' if is_enable else 'OFF'
        self.gpio.gpio_state(PrintingAndValidationDefaults.MISSING_LABEL_GPIO, gpio_on_off)
        self.logger.info(f'R2R: PC send {"enable" if is_enable else "disable"} missing label msg to R2R')

    def end_of_run(self):
        self.send_stop_to_r2r()
        self.enable_missing_label(is_enable=False)

    def get_counter(self):
        return self.counter

    def reset_counter(self):
        self.counter = 0

    def exit(self):
        try:
            self.send_stop_to_r2r()
            self.gpio.__del__()
        except Exception as e:
            self.logger.warning(f'Could not exit R2R due to: {e}')
