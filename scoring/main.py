import threading
from flask import Flask, jsonify, request
import time
import concurrent.futures
import random
import pymysql

app = Flask(__name__)

############################
# MySQL Connection Establishment (connected/not connected)
############################

class MySQL:
    def __init__(self):
        self.connection = None

    def start_connection(self, host, user, password, database):
        try:
            self.connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            if self.connection is not None:
                print("Scoring DB Connection Established")
        except Error as e:
            print(f"Error: {e}") 

    def get_connection(self):
        return self.connection
    
    def close_connection(self):
        if self.connection is not None:
            self.connection.close()
            print("Scoring DB Connection Closed")

mysql = MySQL()

############################
# Thread synchronization for competition status (started/not started)
############################

class CompState:
    def __init__(self):
        # inital state of false, aka competition isn't started when this script is started
        self.started = False
        self.lock = threading.Lock()
    
    def get(self):
        with self.lock:
            return self.started
    
    def set(self, value):
        with self.lock:
            self.started = value

# Initialize the shared state object
comp_state = CompState()

############################
# Service scanning functions
############################

def scan_AD_DNS():
    print("Scanning Box 1: AD/DNS")

    # Replace with actual AD/DNS service check
    return random.choice([True, False])

def scan_Apache():
    print("Scanning Box 2: Apache")

    # Replace with actual Apache service check
    return random.choice([True, False])

def scan_ELK():
    print("Scanning Box 3: ELK")

    # Replace with actual ELK service check
    return random.choice([True, False])

def scan_IIS_FTP():
    print("Scanning Box 4: IIS/FTP")

    # Replace with actual IIS/FTP service check
    return random.choice([True, False])

def scan_Mail():
    print("Scanning Box 5: Mail")

    # Replace with actual Mail service check
    return random.choice([True, False])

def scan_MySQL():
    print("Scanning Box 6: MySQL")

    # Replace with actual MySQL service check
    return random.choice([True, False])

def scan_Nginx():
    print("Scanning Box 7: Nginx")

    # Replace with actual Nginx service check
    return random.choice([True, False])

def scan_NTP():
    print("Scanning Box 8: NTP")

    # Replace with actual NTP service check
    return random.choice([True, False])

def scan_Samba():
    print("Scanning Box 9: Samba")

    # Replace with actual Samba service check
    return random.choice([True, False])

def scan_WinRM():
    print("Scanning Box 10: WinRM")

    # Replace with actual WinRM service check
    return random.choice([True, False])

# Service to box mapping
service_to_box = {
    "AD_DNS": 1,
    "Apache": 2,
    "ELK": 3,
    "IIS_FTP": 4,
    "Mail": 5,
    "MySQL": 6,
    "Nginx": 7,
    "NTP": 8,
    "Samba": 9,
    "WinRM": 10
}

# Box to service mapping
box_to_service = {
    1: "AD/DNS",
    2: "Apache", 
    3: "ELK",
    4: "IIS_FTP",
    5: "Mail",
    6: "MySQL",
    7: "Nginx",
    8: "NTP",
    9: "Samba",
    10: "WinRM"
}

# Service scanning function mapping
service_scan_functions = [
    (scan_AD_DNS, "AD/DNS"),
    (scan_IIS_FTP, "IIS/FTP"),
    (scan_Nginx, "Nginx"),
    (scan_WinRM, "WinRM"),
    (scan_Apache, "Apache"),
    (scan_MySQL, "MySQL"),
    (scan_Mail, "Mail"),
    (scan_Samba, "Samba"),
    (scan_ELK, "ELK"),
    (scan_NTP, "NTP")
]

############################
# Routes
############################

@app.route('/scan', methods=['GET'])
def scan():
    if comp_state.get():
        print("Starting scan of all services")
        results = []
        
        # Use a thread pool to scan machines in parallel (hopefully means fast scans)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all machine scanning functions
            future_to_service = {executor.submit(scan_func): (box_num, service_name) 
                               for box_num, (scan_func, service_name) in enumerate(service_scan_functions, 1)}
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_service):
                box_num, service_name = future_to_service[future]
                try:
                    service_up = future.result()
                    status = "online" if service_up else "offline"
                    
                    # If service is down, deduct 0.5 points
                    if not service_up:
                        subPoints(0.5, box_num)
                    
                    results.append({
                        "box": box_num,
                        "service": service_name,
                        "status": status
                    })
                    print(f"Box {box_num} ({service_name}) scan complete - Status: {status}")
                    
                except Exception as exc:
                    print(f"Box {box_num} ({service_name}) scan generated an exception: {exc}")
                    results.append({
                        "box": box_num,
                        "service": service_name,
                        "status": "error", 
                        "error": str(exc)
                    })
                    # Treat exceptions as service being down
                    subPoints(0.5, box_num)
        
        return jsonify({'data': results})
    else:
        print("Competition hasn't started")
        return jsonify({'comp': 'not started'})

@app.route('/scores', methods=['GET'])
def scores():
    return jsonify({'data2': 'test2'})

############################
# Helper Functions
############################

def addPoints(points, machine):
    print(f'add {points} points to Box {machine} ({box_to_service.get(machine, "Unknown")})')
    cursor = mysql.connection.cursor()
    sql = "UPDATE scoring SET health = health+%s WHERE service = %s"
    cursor.execute(sql, (points, ({box_to_service.get(machine, "Unknown")})))
    mysql.connection.commit()

# Testing MYSQL Modifications Still
def subPoints(points, machine):
    print(f'subtract {points} points from Box {machine} ({box_to_service.get(machine, "Unknown")})')
    cursor = mysql.connection.cursor()
    sql = "UPDATE scoring SET health = health-%s WHERE service = %s"
    cursor.execute(sql, (points, ({box_to_service.get(machine, "Unknown")})))
    mysql.connection.commit()

def setPoints(points, machine):
    print(f'set Box {machine} ({box_to_service.get(machine, "Unknown")}) to {points} points')
    cursor = mysql.connection.cursor()
    sql = "UPDATE scoring SET health = %s WHERE service = %s"
    cursor.execute(sql, (points, ({box_to_service.get(machine, "Unknown")})))
    mysql.connection.commit()

# Successfully starts connection
def start():
    print('Competition started')
    comp_state.set(True)
    mysql.start_connection('localhost', 'greyteam', 'greyteam', 'Scoring')
    

def end():
    print('Competition ended')
    comp_state.set(False)
    
    if mysql.connection is not None:
        mysql.close_connection()

def help():
    print("\n========================= Available Commands =========================")
    print("add <points> <box>     - Add points to the box's score")
    print("sub <points> <box>     - Subtract points from the box's score")
    print("set <points> <box>     - Set box points")
    print("start                  - Start competition and make endpoints reachable")
    print("end                    - Disable endpoints and stop competition")
    print("help                   - Show this help menu")
    print("============================ Box Maping ===============================")
    print("Box to Service Mapping:")
    for box_num, service in box_to_service.items():
        print(f"  Box {box_num}: {service}")
    print("======================================================================\n")

############################
# Terminal Input
############################

def command_listener():
    """Listen for terminal commands while Flask is running."""
    while True:
        command = input("Enter command: ").strip().lower()
        if command.startswith("add"):
            try:
                cmd_parts = command.split()
                points = cmd_parts[1]
                machine = int(cmd_parts[2])
                addPoints(points, machine)
            except (IndexError, ValueError):
                print("Command arguments not provided or invalid. Correct usage: add <points> <box_number>")
            
        elif command.startswith("sub"):
            try:
                cmd_parts = command.split()
                points = cmd_parts[1]
                machine = int(cmd_parts[2])
                subPoints(points, machine)
            except (IndexError, ValueError):
                print("Command arguments not provided or invalid. Correct usage: sub <points> <box_number>")
        elif command.startswith("set"):
            try:
                cmd_parts = command.split()
                points = cmd_parts[1]
                machine = int(cmd_parts[2])
                setPoints(points, machine)
            except (IndexError, ValueError):
                print("Command arguments not provided or invalid. Correct usage: set <points> <box_number>")
        elif command.startswith("start"):
            start()
        elif command.startswith("end"):
            end()
            print("Shutting down...")
            break
        elif command == "help":
            help()
        else:
            print("Unknown command")

if __name__ == '__main__':
    # Initialize help message
    help()
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False})
    flask_thread.daemon = True
    flask_thread.start()
    print("Flask server started at http://0.0.0.0:5000/")

    # Start listening for terminal commands
    command_listener()
