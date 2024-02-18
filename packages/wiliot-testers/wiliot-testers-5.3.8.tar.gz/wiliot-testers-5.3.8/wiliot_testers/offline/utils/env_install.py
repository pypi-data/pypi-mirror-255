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
import os
from threading import local
import PySimpleGUI as SimGUI
import subprocess
import pathlib
import time
import logging

'''
Installing libraries:
Wiliot
Appdirs
Winshell

Checking if testerStationName and R2R_station_name are in System Variables , 
if it doesn't -> GUI will be opened to set the right names and it will be set.

It will set all the env folders for logs and create desktop shortcut for the logs.
'''


def set_new(tester_name, r2r_name):
    layout = [[SimGUI.Text("Do you want to change your environment?", key='question_txt')],
              [SimGUI.Text("Tester Name: " + str(tester_name), key='tester_name_txt')],
              [SimGUI.Text("R2R Name: " + str(r2r_name), key='r2r_name_txt')],
              [SimGUI.Button('Yes'), SimGUI.Button('No', button_color=('white', '#0e6251'))]]
    
    window = SimGUI.Window('Rechange environment', layout)
    submit = False
    
    while True:
        event, values = window.read()
        if event == 'Yes':
            submit = True
            break
        elif event == 'No':
            break
        elif event == SimGUI.WIN_CLOSED or event == 'Cancel':
            print('User exited the program')
            window.close()
            exit()
    
    window.close()
    return submit


def def_env_values(tester_name, r2r_name):
    if tester_name is None:
        tester_name = ''
    if r2r_name is None:
        r2r_name = ''
    layout = [[SimGUI.Text("Please enter testers name", key='tester_name_txt'),
               SimGUI.Input(tester_name, key='tester_name_gui')],
              [SimGUI.Text("<company name> + _Station + <station number>", key='tester_name_gui_example')],
              [SimGUI.Text("Please enter r2r name", key='r2r_name_txt'),
               SimGUI.Input(r2r_name, key='r2r_name_gui')],
              [SimGUI.Text("<company name> + _Station + <station number>", key='r2r_name_gui_example')],
              [SimGUI.Text(size=(60, 3), key='-OUTPUT-')],
              [SimGUI.Button('Submit', button_color=('white', '#0e6251'))]]
    
    window = SimGUI.Window('Set Environments', layout)
    submit = False
    while True:
        event, values = window.read()
        
        if event == 'Submit':
            if ' ' in values['tester_name_gui'] or '/' in values['tester_name_gui'] or '\\' in values[
                'tester_name_gui'] or ' ' in values['r2r_name_gui'] or '/' in values['r2r_name_gui'] or '\\' in values[
                'r2r_name_gui']:
                window['-OUTPUT-'].update('Please dont use white spaces, / or \\')
                submit = False
            else:
                submit = True
        
        if submit:
            break
        
        if event == SimGUI.WIN_CLOSED or event == 'Cancel':
            print('User exited the program')
            window.close()
            exit()
    
    window.close()
    return values


def env_init():
    reconfig = False
    tester_name = os.getenv('testerStationName')
    r2r_name = os.getenv('R2R_station_name')
    if tester_name is None or r2r_name is None:
        reconfig = True
    else:
        reconfig = set_new(tester_name, r2r_name)
    
    if reconfig:
        new_values = def_env_values(tester_name, r2r_name)
        os.environ['testerStationName'] = new_values['tester_name_gui']
        os.environ['R2R_station_name'] = new_values['r2r_name_gui']
        set_tester = 'setx testerStationName ' + str(new_values['tester_name_gui'])
        set_r2r = 'setx R2R_station_name ' + str(new_values['r2r_name_gui'])
        print('Please wait few second for environment set')
        try:
            subprocess.Popen(set_tester, shell=True).wait()
            subprocess.Popen(set_r2r, shell=True).wait()
            print('Done')
        except Exception:
            print('Problem with setting environment, please set in manually')


def dir_init():
    local_app_data = user_data_dir('offline', 'wiliot')
    logs_dir = os.path.join(local_app_data, 'logs')
    if not os.path.isdir(logs_dir):
        pathlib.Path(logs_dir).mkdir(parents=True, exist_ok=True)
    
    desktop = winshell.desktop()
    path = os.path.join(desktop, 'logs_output.lnk')
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    # shortcut.WorkingDirectory = logs_dir
    shortcut.Targetpath = logs_dir
    shortcut.save()


def wiliot_init():
    print('Installing libraries')
    try:
        subprocess.Popen('pip install wiliot[advance]', shell=True).wait()
        subprocess.Popen('pip install appdirs', shell=True).wait()
        subprocess.Popen('pip install winshell', shell=True).wait()
        subprocess.Popen('pip install pypiwin32', shell=True).wait()
        print('Done')
    
    except Exception:
        print('Problem with installing libraries')


if __name__ == "__main__":
    wiliot_init()
    from appdirs import *
    import winshell
    from win32com.client import Dispatch
    import win32api
    
    env_init()
    dir_init()
    print('Computer will be reseted in 3 seconds')
    time.sleep(3)
    try:
        win32api.InitiateSystemShutdown()
    except Exception:
        os.system("shutdown /r /t 1")
