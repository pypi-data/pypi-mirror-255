import serial
import time
import threading
from time import sleep
import serial.tools.list_ports
import logging
import os
from datetime import datetime


class CountThread(object):
    """
    Counting the number of tags
    """

    def __init__(self, stop_event, rows=1, max_movement_time=18, ther_cols=1):
        self.max_movement_time = max_movement_time
        self.available_ports = [s.device for s in serial.tools.list_ports.comports()]
        self.get_ports_of_arduino()
        self.baud = 1000000
        self.ports = self.get_ports_of_arduino()
        self.logger_file = self.setup_logger()
        try:
            self.comPortObj = serial.Serial(self.ports[0], self.baud, timeout=0.1)
            sleep(1)
            self.config()
        except serial.SerialException:
            self.logger_file.error("NO ARDUINO")
            raise Exception('could not connect to the Arduino')
        self.rows = rows
        self.ther_cols = ther_cols
        self.stop = stop_event
        self.tested = 0

    def setup_logger(self):
        user_home = os.path.expanduser("~")
        now = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        log_path = os.path.join(user_home, 'Downloads', f'{now}.log')
        logging.basicConfig(filename=log_path, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger()

    def config(self):
        """
        @return:
        @rtype:
        """
        self.comPortObj.write(f'*time_btwn_triggers {int(self.max_movement_time)}'.encode())
        rsp = self.comPortObj.readline()
        if rsp == b'' or rsp != b'No pulses yet...\r\n':
            raise Exception('A problem in the first message of Arduino')
        for i in range(5):
            sleep(0.500)
            rsp = self.comPortObj.readline()
            if rsp.decode() == f'Max movement time was set to {int(self.max_movement_time)}[sec]\r\n':
                self.logger_file.info(f'config Arduino and got the following msg: {rsp.decode()}')
                return
        raise Exception('Arduino Configuration was failed')

    def get_ports_of_arduino(self):
        """
        Gets all the ports we have, then chooses Arduino's ports
        """
        arduino_ports = []
        for p in serial.tools.list_ports.comports():
            if 'Arduino' in p.description:
                arduino_ports.append(p.device)
        if not arduino_ports:
            self.logger_file.info('NO ARDUINO')
        return arduino_ports

    def run(self):
        """
        Tries to read data and then counts the number of tags
        """
        while not self.stop.is_set():
            time.sleep(0.100)
            data = ''
            try:
                data = self.comPortObj.readline()
            except Exception as ee:
                self.logger_file.error(f"NO READLINE: {ee}")
            if data.__len__() > 0:
                try:
                    tmp = data.decode().strip(' \t\n\r')
                    if "pulses detected" in tmp:
                        self.tested += (self.rows * int(self.ther_cols))
                    self.logger_file.info(f'Arduino msg: {tmp}')

                except Exception as ee:
                    self.logger_file.error(f'Warning: Could not decode counter data or Warning: {ee}')
                    continue
        self.comPortObj.close()

    def get_tested(self):
        """
        returns the number of tags
        """
        return self.tested


def run_count_thread():
    stop_event = threading.Event()

    class Logger:
        def error(self, msg):
            self.logger_file.info(f'error: {msg}')

        def info(self, msg):
            self.logger_file.info(f"msg: {msg}")

    logger = Logger()

    rows_number = 1
    max_movement_time = 18
    thermodes_col = 1

    count_process = CountThread(stop_event, rows_number, max_movement_time, thermodes_col)
    count_process_thread = threading.Thread(target=count_process.run)

    count_process_thread.start()

    prev_tested_count = 0

    try:
        while True:
            current_tested_count = count_process.get_tested()

            if current_tested_count != prev_tested_count:
                print(f"Number of tags tested: {current_tested_count}")
                prev_tested_count = current_tested_count

            time.sleep(1)

    except KeyboardInterrupt:
        stop_event.set()
        count_process_thread.join()
        print("\nStopped counting and exited gracefully.")


if __name__ == "__main__":
    run_count_thread()
