import PySimpleGUI as sg
from wiliot_testers.test_equipment import *

try:
    main_sensor = YoctoSensor(None)
except Exception as ee:
    main_sensor = None
    raise Exception('No sensor is connected')

layout = [[sg.Text("Lightmeter Read")], [sg.Input(key='right_value')],
          [sg.Button('Calibrate'), sg.Button('Remove Calibrate'), sg.Button('Quit')]]

window = sg.Window('Lightmeter Read GUI', layout)
while True:
    event, values = window.read()
    if event == 'Calibrate':
        main_sensor.calibration(int(values['right_value']), True)
        break
    elif event == 'Remove Calibrate':
        main_sensor.calibration(0, False)
        break
    else:
        break
window.close()
