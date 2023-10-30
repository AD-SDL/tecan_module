import os
import pyautogui
import csv
import time
import sys
import wmi
import shutil
import time
from pathlib import Path
from datetime import datetime
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class NewFileHandler(FileSystemEventHandler):
    def __init__(self, observer):
        super().__init__()
        self.latest_file_path = None
        self.observer = observer

    def on_created(self, event):
        print(f'New file created: {event.src_path}')
        self.latest_file_path = event.src_path
        creation_time = os.path.getctime(self.latest_file_path)
        if time.time() - creation_time < 60: # if file was created within the last 60 seconds, then observer stops
            self.observer.stop()

def correct_file_name(file_name):
    file_name = file_name[0]
    if file_name.startswith("P_demo"):
        file_name = "ECP" + file_name[1:]
    elif file_name.startswith("CP_demo"):
         file_name = "E" + file_name  
    return file_name 

class Tecan():

    def __init__(self):
        self.wmi_service = wmi.WMI()
        self.library_path = "C:/Users/Public/Documents/Tecan/Magellan Pro/mth/ECP-350-800-Yukun.mth"
        self.asc_folder_path = "C:/Users/Public/Documents/Tecan/Magellan Pro/asc/"
        self.csv_folder_path = "C:/Users/cnmuser/Desktop/Polybot/tecan_code/uv_vis_data"
                
    def tecan_already_running(self):
        # Function to check if the tecan machine is already running
        try:
            wmi_service = wmi.WMI()
            for process in wmi_service.Win32_Process():
                if process.Name == "Magellan.exe":
                    return True
            return False
        except:
            return False

    def open_tecan(self, protocol_file_path = None):
        # Function to load the correct library for the measurements
        if not protocol_file_path:
            os.startfile(self.library_path) 
        else:
            os.startfile(protocol_file_path)
        # os.startfile(self.library_path)
        print("Loading the measurements library")
        time.sleep(50) # time to open the software
        return_dict = {
        'action_response': "0",
        'action_msg': "Succsess",
        'action_log': "run completed"
        }
        return return_dict
    
    def click_start_button(self):
        # Function to click the start button in the software
        x1,y1 = 1251, 699 #814, 290
        pyautogui.leftClick(x1,y1)


    def select_boxes_with_spectra(self, iteration): # this might change depending on the number of experiments we are going to run
        
        # Function to select the boxes with the spectra
        x1,y1 = 804, 207 
        y1 = y1 + iteration*77
        pyautogui.moveTo(x1,y1 )
        # pyautogui.leftClick(x1,y1)
        x1_a, y1_a = 1183, 216
        y1_a = y1_a + iteration*77
        pyautogui.dragTo(x1_a, y1_a, button='left', duration=4)
        # Function to right-click and select the get_graphs tab
        pyautogui.rightClick(x1_a,y1_a)
        time.sleep(2)
        # Select the graphs 
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('enter')

        # Function to right-click and select the save ascii tab
        pyautogui.rightClick(x1,y1)
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('down')
        pyautogui.press('enter')
        time.sleep(2)
        pyautogui.typewrite(f"ECP_demo_batch_{iteration}")
        pyautogui.press('enter')
        pyautogui.press('enter')
        #close the spectra window
        x2,y2 = 1654, 18
        pyautogui.leftClick(x2,y2)

        x3,y3 = 1899, 9
        pyautogui.leftClick(x3,y3)

        x4,y4= 1029, 569
        pyautogui.leftClick(x4,y4) 
        time.sleep(10)

    def move_and_rename_file(self):
        # Function to move and rename the file
        file = [f for f in os.listdir(self.asc_folder_path) if f.endswith('.asc')]
        print("before", file)
        file = correct_file_name(file)
        # print("after", file)
        source_path = os.path.join(self.asc_folder_path, os.path.basename(file))
        destination_path = os.path.join(self.csv_folder_path, os.path.basename(file))
        shutil.move(source_path, destination_path)
        return destination_path

    def convert_file_to_csv(self, file_path, iteration):    
        # Function to convert the file to CSV format
        csv_file_path = f"{self.csv_folder_path}/ECP_demo_batch_{iteration}.csv"
        with open(file_path, 'r') as input_file, open(csv_file_path, 'w', newline='') as output_file:
            csv_writer = csv.writer(output_file)
            for line in input_file:
                fields = line.strip().split()
                csv_writer.writerow(fields)

    def close_tecan(self, tecan_file_path=None):
        #time to wait until the ur5e pick up the plate
        time.sleep(60)
        # closing the first window
        x1, y1 = 686, 705
        pyautogui.leftClick(x1,y1)
        pyautogui.leftClick(x1,y1)    
        return_dict = {
        'action_response': "0",
        'action_msg': "Succsess",
        'action_log': "run completed"
        }

        if tecan_file_path is not None:
                import paramiko
                with paramiko.SSHClient() as ssh:
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    pkey_path = 'C:/Users/cnmuser/.ssh/batman/id_rsa'
                    pkey = paramiko.RSAKey.from_private_key_file(pkey_path)
                    ssh.connect(hostname='146.139.48.79', username='rpl', pkey=pkey)
                    with ssh.open_sftp() as sftp:
                        filename = Path(tecan_file_path).name
                        batman_tecan_file_path = f"/home/rpl/workspace/polybot_workcell/polybot_app/demo_files/from_tecan/{filename}"
                        sftp.put(tecan_file_path, batman_tecan_file_path)
        return return_dict
    
    def get_output_file(self, folder_path, result):   
        """keeps checking the output folder for a newly created file"""
        observer = Observer()
        event_handler = NewFileHandler(observer)
        observer.schedule(event_handler, folder_path, recursive=True)
        observer.start()
        while observer.is_alive():
            print('Watching folder')
            observer.join(1)        
        result[0] = event_handler.latest_file_path

    def run_tecan(self, tecan_iteration=None):

        action_log = ""
        if tecan_iteration is None:
            iteration = 0
        else:
            iteration=tecan_iteration

        try:
            result = [None] 
            self.click_start_button() # Detects and clicks the start buttom
            time.sleep(300) # wait until the measurement is done               
            # iteration = 0
            self.select_boxes_with_spectra(iteration) # Select the boxes with the spectra from the software page
            observer_thread = threading.Thread(target = self.get_output_file, args=(self.csv_folder_path,result))
            observer_thread.start()
            self.move_and_rename_file() # Move the generated files to our folder
            observer_thread.join()
            file_path = result[0]
            
            print('file_path', file_path)
            return_dict = {
                    'action_response': "0",
                    'action_msg': "Succsess",
                    'action_log': file_path
                    }
                
        except Exception as error_msg: 
            print(error_msg)
            return_dict = {
                    'action_response': "-1",
                    'action_msg': error_msg,
                    'action_log': "run failed"
                    }

        return return_dict
        

if __name__ == "__main__":
    '''
    Runs Teacan measurement workflow.
    '''
    tecan = Tecan()
    # tecan.open_tecan()
    tecan.run_tecan()
    # tecan.close_tecan()

    
