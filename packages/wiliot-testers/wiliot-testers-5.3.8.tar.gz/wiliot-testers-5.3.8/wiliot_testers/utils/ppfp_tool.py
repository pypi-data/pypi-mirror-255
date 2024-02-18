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

import os
import time
from PIL import Image
import PySimpleGUI as sg
from wiliot_core import check_user_config_is_ok, WiliotDir, open_json
from wiliot_api import ManufacturingClient

class DataPullGUI:

    """
    To create .exe file for this script use the next line:
    pywiliot-testers> pyinstaller --onefile --windowed --add-data "./wiliot_testers/docs/wiliot_logo.png;./docs" ./wiliot_testers/utils/ppfp_tool.py
    """

    def __init__(self, owner_id='', single_crn='', output_dir=None):
        current_script = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_script)
        os.chdir(current_dir)
        try:
            wiliot_logo = os.path.join('docs', 'wiliot_logo.png')
            if os.path.exists(wiliot_logo):
                pass
            else:
                raise Exception('Trying to locate .png')
        except Exception:
            wiliot_logo = os.path.join('..', 'docs', 'wiliot_logo.png')
        wiliot_logo_image = Image.open(wiliot_logo)
        wiliot_logo_image = wiliot_logo_image.resize((128, 50), Image.BICUBIC)
        wiliot_logo_image.save(wiliot_logo, format="png")
        sg.theme('GreenTan')
        self.layout = [
            [sg.Column([[sg.Image(wiliot_logo)]], justification='center')],
            [sg.Text('Owner ID', size=(15, 1)), sg.InputText(key='owner_id', default_text=owner_id)],
            [sg.Text('Environment'),
             sg.Combo(['Production', 'Test'], default_value='Production', key='env')],
            [sg.Text('Tester Type'),
             sg.Combo(['Offline', 'Sample'], default_value='Offline', key='tester_type')],
            [sg.Text('Select mode for Common Run Name Insert')],
            [sg.Radio('Single CRN', "RADIO1", default=True, key='single_crn', enable_events=True),
             sg.Radio('CRN List (CSV)', "RADIO1", key='csv', enable_events=True)],
            [sg.Column([[sg.Text('CRN', size=(15, 1)), sg.InputText(key='crn', default_text=single_crn)]], key='crn_col', visible=True),
             sg.Column([[sg.Text('CSV File', size=(15, 1)), sg.InputText(),
                         sg.FileBrowse(key='csv_file')]], key='csv_file_col', visible=False)],
            [sg.Text('Select Target Directory')],
            [sg.Text('Directory', size=(15, 1)),
             sg.InputText(output_dir if output_dir is not None else ''),
             sg.FolderBrowse(key='target_dir', initial_folder=output_dir)],
            [sg.Submit(), sg.Cancel()]
        ]

    def run(self):
        window = sg.Window('PPFP Tool', self.layout, finalize=True, size=(600, 350))

        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, 'Cancel'):
                break
            elif event == 'Submit':
                try:
                    env_dirs = WiliotDir()
                    config_dir_path = env_dirs.get_config_dir()
                    user_config_file_path = env_dirs.get_user_config_file()
                    loading_window = sg.Window('Loading', [[sg.Text('Loading...')]], finalize=True, no_titlebar=True,
                                               grab_anywhere=True)

                    if os.path.exists(user_config_file_path):
                        cfg_data = open_json(folder_path=config_dir_path, file_path=user_config_file_path)

                    window.minimize()
                    tester_type = 'offline-test' if values['tester_type'] == 'Offline' else 'sample-test'
                    file_path, api_key, is_successful = check_user_config_is_ok(env=values['env'][0:4].lower(),
                                                                                owner_id=values['owner_id'])
                    if not is_successful:
                        sg.popup_error('User configuration check failed')
                        continue
                    client = ManufacturingClient(api_key=api_key, env=values['env'][0:4].lower())
                    rsp = None

                    if values['single_crn']:
                        common_run_name_list = [values['crn'].strip()]
                    else:
                        common_run_name_list = []
                        with open(values['csv_file'], 'r') as f:
                            for line in f:
                                common_run_name_list.append(line.strip())
                    try:
                        for common_run_name in common_run_name_list:
                            out_file_path = os.path.join(values['target_dir'], f'{common_run_name}.zip')
                            with open(out_file_path, 'wb') as out_file:
                                rsp = client.get_file_for_ppfp(common_run_name, tester_type, out_file)
                    except Exception as e:
                        print(f'problem get file from cloud due to {e}')
                        loading_window.close()
                        sg.popup_error(f'An error occurred while loading CSV file - please check it', title='Error')
                        continue

                    loading_window.close()
                    if rsp:
                        print('Job Success')
                        done_window = sg.Window('Finish', [[sg.Text('Job Success')]], finalize=True, no_titlebar=True,
                                                grab_anywhere=True, auto_close=True, auto_close_duration=5)
                        time.sleep(5)
                        done_window.close()
                        window.close()
                    else:
                        sg.popup_error(f'An error occurred while getting data from cloud', title='Error')
                    break

                except Exception as e:
                    print(e)
                    sg.popup_error(f'An error occurred: {e}', title='Error')
                    break
            elif event == 'single_crn':
                window['csv_file_col'].update(visible=False)
                window['crn_col'].update(visible=True)
            elif event == 'csv':
                window['csv_file_col'].update(visible=True)
                window['crn_col'].update(visible=False)

        window.close()


if __name__ == '__main__':
    gui = DataPullGUI()
    gui.run()
