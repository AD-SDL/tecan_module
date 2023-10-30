import os
import sys
import socket
import json

from datetime import datetime

from tecan_driver.autorun_tecan import Tecan

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("0.0.0.0",5557)
sock.bind(server_address)
sock.listen(1) # listen for one connection at at time
print("Tecan listening on port 5557")


while True:
    connection, client_address = sock.accept()
    tecan = Tecan()
    return_dict = {}
    try: 
        message = connection.recv(4096)
        print(f"Received: {message}")

        response = ""

        if message == b"SHUTDOWN":
            connection.sendall(b"Shutting down")
            break

        else:
            msg = json.loads(message.decode("utf-8"))

            try:  
                
                action_handle = msg['action_handle'] 
                action_vars = msg['action_vars']

                if action_handle == "run_tecan": 

                    try:
                        if "tecan_iteration" in action_vars.keys():
                            kwargs = {
                                'tecan_iteration': action_vars.get("tecan_iteration"),
                            }
                            return_dict = tecan.run_tecan(**kwargs)
                        else:                             
                            return_dict = tecan.run_tecan()
                        return_dict['action_log'] += (f"{datetime.now()} LISTEN Tecan: Tecan Run started\n")
                
                    except Exception as error_msg: 
                        return_dict = {
                            'action_response': -1,
                            'action_log': (f"{datetime.now()} ERROR LISTEN Tecan: Tecan client unable to run auto_click_tecan.ahk\n{error_msg}")
                        }
                    else: 
                        return_dict = {
                            'action_response': 0,
                            'action_log': (f"{datetime.now()} LISTEN tecan: tecan client completed run auto_click_tecan.ahk\n")
                        }
                elif action_handle == "open_gate":
                    try:
                        if "protocol_file_path" in action_vars.keys():
                            file_path = action_vars.get("protocol_file_path")
                            return_dict = tecan.open_tecan(protocol_file_path = file_path)
                        else:
                            return_dict = tecan.open_tecan() 
                        # return_dict = tecan.open_tecan()
                        return_dict['action_log'] += (f"{datetime.now()} LISTEN Tecan: Tecan open gate started\n")
                
                    except Exception as error_msg: 
                        return_dict = {
                            'action_response': -1,
                            'action_log': (f"{datetime.now()} ERROR LISTEN Tecan: Tecan client unable to run open gate\n{error_msg}")
                        }
                    else: 
                        return_dict = {
                            'action_response': 0,
                            'action_log': (f"{datetime.now()} LISTEN tecan: tecan client completed open gate\n")
                        }
                elif action_handle == "close_gate":
                    try:

                        if "tecan_file_path" in action_vars.keys():
                            kwargs = {
                                'tecan_file_path': action_vars.get("tecan_file_path"),
                            }
                            return_dict = tecan.close_tecan(**kwargs)
                        
                        else: 
                            return_dict = tecan.close_tecan()

                        return_dict['action_log'] += (f"{datetime.now()} LISTEN Tecan: Tecan close gate started\n")
                
                    except Exception as error_msg: 
                        return_dict = {
                            'action_response': -1,
                            'action_log': (f"{datetime.now()} ERROR LISTEN Tecan: Tecan client unable to run close gate\n{error_msg}")
                        }
                    else: 
                        return_dict = {
                            'action_response': 0,
                            'action_log': (f"{datetime.now()} LISTEN tecan: tecan client completed close gate\n")
                        }
                else:
                    return_dict = {
                        'action_response': -1,
                        'action_log': (f"{datetime.now()} ERROR LISTEN tecan: Unkown command:\n{action_handle}")
                    }
 
            except Exception as error_msg:  # msg is not formatted correctly
                return_dict = {
                    'action_response': -1,
                    'action_log': (f"{datetime.now()} ERROR LISTEN Tecan: Message received was not formatted correctly. Could not parse action handle\n{error_msg}\n")
                }
            
    except Exception as error_msg: 
        return_dict = {
            'action_response': -1,
            'action_log': (f"{datetime.now()} ERROR LISTEN tecan: Message could not be received.\n{error_msg}\n")
        }

    finally: 
        response = json.dumps(return_dict)
        connection.sendall(bytes(response, encoding='utf-8'))
        connection.close()

sock.close()