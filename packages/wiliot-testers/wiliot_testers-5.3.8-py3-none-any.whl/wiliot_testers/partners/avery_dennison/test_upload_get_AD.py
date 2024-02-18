import PySimpleGUI as sg
import threading
from wiliot_testers.utils.ppfp_tool import DataPullGUI
from wiliot_testers.partners.avery_dennison.simple_test import SimpleTest

OWNER_ID = 'averydennison_rfid'


def custom_progress_bar(window, title, total_time, shared_status):
    layout = [[sg.Text(title, key='-STATUS-')],
              [sg.ProgressBar(total_time, orientation='h', size=(20, 20), key='-PROGRESS-')],
              [sg.Cancel()]]

    progress_window = sg.Window('Progress', layout, keep_on_top=True)
    for i in range(total_time):
        if ((shared_status.get('test_complete', False) and title == 'Processing')
                or (shared_status.get('upload_complete', False) and title == 'Uploading')):
            break
        event, _ = progress_window.read(timeout=1000)
        if event in (sg.WIN_CLOSED, 'Cancel'):
            break
        progress_window['-PROGRESS-'].update_bar(i + 1)

    progress_window.close()


def run_simple_test(owner_id, test_name, output_path, window, test_time, shared_status):
    try:
        test = SimpleTest(owner_id=owner_id,
                          test_name=test_name,
                          output_path=output_path,
                          test_time=test_time,
                          tester_type='offline',
                          test_env='prod')
    except Exception:
        sg.popup_error('Problem initializing the test')
        return
    shared_status['test'] = test
    shared_status['test_complete'] = True
    window.write_event_value('-TEST COMPLETE-', None)


def upload_to_cloud(window, shared_status):
    if shared_status.get('test'):
        shared_status['test'].cloud_upload()
        shared_status['upload_complete'] = True
        window.write_event_value('-UPLOAD COMPLETE-', None)


def create_gui():
    sg.theme('GreenTan')

    left_layout = [
        [sg.Text('Test and cloud upload')],
        [sg.Text('Test Name'), sg.InputText(key='test_name', default_text='SimpleTest', size=(15, 1))],
        [sg.Text('Time to Test'), sg.InputText(key='test_time', default_text='10', size=(5, 1))],
        [sg.Text('Output')],
        [sg.InputText(size=(20, 1)), sg.FolderBrowse(key='target_dir')],
        [sg.Button('Start Test')],
        [sg.Text('Upload data to cloud', visible=False, key='-UPLOAD TEXT-')],
        [sg.Button('Upload', visible=False, key='-UPLOAD BUTTON-')]]

    right_layout = [
        [sg.Text('Cloud data pull', size=(20, 1))],
        [sg.Text('Test Name', visible=False), sg.InputText(key='cloud_test_name', visible=False)],
        [sg.Text('Output Directory', visible=False), sg.InputText(key='cloud_output_dir', visible=False)],
        [sg.Button('Get Results')]]

    layout = [
        [sg.Column(left_layout), sg.VSeparator(), sg.Column(right_layout)]]

    window = sg.Window('AD GUI', layout, size=(450, 250))

    shared_status = {'test_complete': False, 'test': None, 'upload_complete': False}

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break

        elif event == 'Start Test':
            run_and_upload = threading.Thread(target=run_simple_test,

                                              args=(OWNER_ID, values['test_name'], values['target_dir'], window,
                                                    values['test_time'], shared_status),

                                              daemon=True)
            run_and_upload.start()
            custom_progress_bar(window, 'Processing', int(values['test_time']) + 10, shared_status)

        elif event == '-TEST COMPLETE-':
            window['-UPLOAD TEXT-'].update(visible=True)
            window['-UPLOAD BUTTON-'].update(visible=True)

        elif event == '-UPLOAD BUTTON-':
            threading.Thread(target=upload_to_cloud, args=(window, shared_status), daemon=True).start()
            custom_progress_bar(window, 'Uploading', 10, shared_status)

        elif event == '-UPLOAD COMPLETE-':
            common_run_name = shared_status['test'].get_common_run_name()
            out_dir = shared_status['test'].get_out_put_dir()
            window['cloud_test_name'].update(value=common_run_name, visible=True)
            window['cloud_output_dir'].update(value=values['target_dir'], visible=True)

        elif event == 'Get Results':
            gui = DataPullGUI(owner_id=OWNER_ID, single_crn=values['cloud_test_name'],
                              output_dir=values['cloud_output_dir'])
            gui.run()

    window.close()


if __name__ == '__main__':
    create_gui()
