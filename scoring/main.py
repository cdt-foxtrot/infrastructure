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
            self.cursor = self.connection.cursor()
            if self.connection is not None:
                print("Scoring DB Connection Established")
        except Error as e: # type: ignore
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
    "IIS": 4,
    "Mail": 5,
    "MySQL": 6,
    "Nginx": 7,
    "FTP": 8,
    "Samba": 9,
    "WinRM": 10
}

# Box to service mapping
box_to_service = {
    1: "AD/DNS",
    2: "Apache", 
    3: "ELK",
    4: "IIS",
    5: "Mail",
    6: "MySQL",
    7: "Nginx",
    8: "FTP",
    9: "Samba",
    10: "WinRM"
}

# Service scanning function mapping
service_scan_functions = [
    (scan_AD_DNS, "AD/DNS"),
    (scan_IIS_FTP, "IIS"),
    (scan_Nginx, "Nginx"),
    (scan_WinRM, "WinRM"),
    (scan_Apache, "Apache"),
    (scan_MySQL, "MySQL"),
    (scan_Mail, "Mail"),
    (scan_Samba, "Samba"),
    (scan_ELK, "ELK"),
    (scan_NTP, "FTP")
]

############################
# Routes
############################

@app.route('/scan', methods=['GET'])
def scan():
    # String to print all results at end of scan
    outString = ["\nScan Results:"]

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
                
                # Appends each box scan result to "outString" 
                boxString = [f'\nBox {box_num} Scan:']

                try:
                    service_up = future.result()
                    status = "online" if service_up else "offline"
                
                # If service is down, deduct 0.5 points if health is above 0.
                    if not service_up:
                        subStr = subPoints(0.5, box_num)
                        boxString.append(subStr)

                    # If service is Down via Scan, but DB states its UP, update DB. 
                        if isDBServiceStateUp(box_num):
                            setServiceState (box_num, "Offline")

                    # If service is Up via Scan, but DB states is DOWN, update DB.
                    else:
                        if not isDBServiceStateUp(box_num):
                            setServiceState (box_num, "Online")

                # If service has no more hp, display it.
                    if checkIsDead(box_num) is True:
                        deadStr = f'Box {box_num} ({box_to_service.get(box_num, "Unknown")}) is out of HP!'
                        boxString.append(deadStr)
                        # probably should incorporate a lives metric here
                    
                    boxScanFin = f"Box {box_num} scan complete - Status: {status}"
                    boxString.append(boxScanFin)
                    
                    for str in boxString:
                        outString.append(str)

                except Exception as exc:
                    err = f"Box {box_num} scan generated an exception: {exc}"
                    # Treat exceptions as service being down
                    subPoints(0.5, box_num)
                    return err
        
        for str in outString:
            print(str)

        return "Scan Complete!"
    
    return "Competition hasn't started! Scan not Attempted."


@app.route('/scores', methods=['GET'])
def scores():
    
    if comp_state.get():
        try:
            sql = "SELECT * FROM scoring"
            mysql.cursor.execute(sql)
            res = mysql.cursor.fetchall()

            # Get Column Names
            col = [desc[0] for desc in mysql.cursor.description]

            # Convert to list of dictionaries
            data = [dict(zip(col, row)) for row in res]
            return jsonify(data)
        # Probably need a better exception here
        except Exception as exc:
            print (f"Could not retrieve data | Error: {exc}")
    return None


############################
# Helper Functions
############################

# Checks Database to find current stored service 
def isDBServiceStateUp (machine):
    sql = "SELECT state FROM scoring WHERE service = %s"
    mysql.cursor.execute(sql, (({box_to_service.get(machine, "Unknown")})))
    status = str(mysql.cursor.fetchall()[0][0])
    
    if status == "Online":
        return True
    
    return False

# Sets the new DB states for a specific service
def setServiceState (machine, state):
    sql = "UPDATE scoring SET state = %s WHERE service = %s"
    mysql.cursor.execute(sql, (state, ({box_to_service.get(machine, "Unknown")})))
    mysql.connection.commit()

# Check if box has 0 HP
def checkIsDead (machine):
    sql = "SELECT health FROM scoring WHERE service = %s"
    mysql.cursor.execute(sql, {box_to_service.get(machine, "Unknown")})
    hp = mysql.cursor.fetchall()[0][0]

    if hp == 0:
        return True
    
    return False

# Check if points intended to add result in health > 20 or set = 20
def checkMaxHP (points, machine, func):
    
    if func is "add":
        sql = "SELECT health FROM scoring WHERE service = %s"
        mysql.cursor.execute(sql, {box_to_service.get(machine, "Unknown")})
        res = float(mysql.cursor.fetchall()[0][0]) + float(points)
        
        if res >= 20:
            return True
    else:
        if float(points) >= 20:
            return True
    
    return False


def addPoints(points, machine):
    
    if checkMaxHP(points, machine, "add") is True:
        print(f'Setting Box {machine} ({box_to_service.get(machine, "Unknown")}) to MAX Health')
        sql = "UPDATE scoring SET health = 20 WHERE service = %s"
        mysql.cursor.execute(sql, ({box_to_service.get(machine, "Unknown")}))
    else:
        print(f'add {points} points to Box {machine} ({box_to_service.get(machine, "Unknown")})')
        sql = "UPDATE scoring SET health = health+%s WHERE service = %s"
        mysql.cursor.execute(sql, (points, ({box_to_service.get(machine, "Unknown")})))
    
    mysql.connection.commit()


def subPoints(points, machine):

    if checkIsDead(machine) is False:
        sql = "UPDATE scoring SET health = health-%s WHERE service = %s"
        mysql.cursor.execute(sql, (points, ({box_to_service.get(machine, "Unknown")})))
        mysql.connection.commit()
        return f'subtract {points} points from Box {machine} ({box_to_service.get(machine, "Unknown")})'
    return ""


def setPoints(points, machine):
    
    if checkMaxHP(points, machine, "set"):
        print(f'Setting Box {machine} ({box_to_service.get(machine, "Unknown")}) to MAX Health')
        sql = "UPDATE scoring SET health = 20 WHERE service = %s"
        mysql.cursor.execute(sql, ({box_to_service.get(machine, "Unknown")}))
    else:
        print(f'set Box {machine} ({box_to_service.get(machine, "Unknown")}) to {points} points')
        sql = "UPDATE scoring SET health = %s WHERE service = %s"
        mysql.cursor.execute(sql, (points, ({box_to_service.get(machine, "Unknown")})))

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
