import socket
import subprocess
import threading
from flask import Flask, jsonify, request
import time
import concurrent.futures
import random
import pymysql
import requests

app = Flask(__name__)

############################
# MySQL Connection Establishment (connected/not connected)
############################

class MySQL:
    def __init__(self):
        self.connection = None
        self.cursor = None

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
                # Load box information from the database
                self.load_box_info()
        except Exception as e:
            print(f"Error: {e}") 

    def get_connection(self):
        return self.connection
    
    def close_connection(self):
        if self.connection is not None:
            self.connection.close()
            print("Scoring DB Connection Closed")
    
    def load_box_info(self):
        """Load box information from the database"""
        try:
            sql = "SELECT box, service, building, os, ip, port FROM scoring"
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            
            # Clear existing mappings
            global box_info, service_to_box
            box_info = {}
            service_to_box = {}
            
            # Populate mappings from database
            for row in results:
                box_num, service_name, building_name, os_name, ip_address, port = row
                box_info[box_num] = {
                    "service": service_name,
                    "os": os_name,
                    "buildingName": building_name,
                    "ip": ip_address,
                    "port" : port
                }
                service_to_box[service_name.replace("/", "_")] = box_num
                
            print(f"Loaded information for {len(box_info)} boxes from database")
        except Exception as e:
            print(f"Error loading box information from database: {e}")

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
# Box information mapping
############################

# Initialize empty mappings - will be populated from database
box_info = {}
service_to_box = {}

# Simple access functions to get box information
def get_box_service(box_num):
    return box_info.get(box_num, {}).get("service", "Unknown")

def get_box_building(box_num):
    return box_info.get(box_num, {}).get("buildingName", "Unknown")

def get_box_ip(box_num):
    return box_info.get(box_num, {}).get("ip", "Unknown")

def get_box_os(box_num):
    return box_info.get(box_num, {}).get("os", "Unknown")

def get_box_ports(box_num):
    return box_info.get(box_num, {}).get("port", "Unknown").split(",")

############################
# Service scanning functions
############################
def is_port_open(ip, port, timeout=2):
    """Check if a port is open on the target IP."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, int(port)))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Error checking port {port} on {ip}: {e}")
        return False
    
def scan_service(box_num):
    """Generic service scanning function"""
    service = get_box_service(box_num)
    box_ip = get_box_ip(box_num)
    building = get_box_building(box_num)
    ports = get_box_ports(box_num)

    print(f"Scanning Box {box_num}: {service} at {box_ip} ({building})")
    
    # Check if all required ports are open
    port_results = []
    for port in ports:
        port_open = is_port_open(box_ip, port)
        port_status = "open" if port_open else "closed"
        print(f"Port {port} on {box_ip} is {port_status}")
        port_results.append(port_open)
    
    # Return True only if all ports are open
    return all(port_results)

def scan_AD_DNS():
    # 389
    box_num = 1
    box_ip = get_box_ip(box_num)

    # check to see if the port is up
    if not scan_service(box_num):
        return False
    
    return scan_service(box_num)

def scan_IIS():
    # 80
    box_num = 2
    box_ip = get_box_ip(box_num)

    # check to see if the port is up
    if not scan_service(box_num):
        return False
    
    # try to get the webpage
    try:
        response = requests.get(f"http://{box_ip}", timeout=3)
        server_header = response.headers.get('Server', '')
        return 'IIS' in server_header or 'Microsoft' in server_header or response.status_code < 400
    except Exception as e:
        print(f"IIS check failed: {e}")
        return False

def scan_Nginx():
    # 80
    box_num = 3
    box_ip = get_box_ip(box_num)

    # check to see if the port is up
    if not scan_service(box_num):
        return False
    
    # try to get the webpage
    try:
        response = requests.get(f"http://{box_ip}", timeout=3)
        server_header = response.headers.get('Server', '')
        return 'nginx' in server_header.lower() or response.status_code < 400
    except Exception as e:
        print(f"Nginx check failed: {e}")
        return False

def scan_WinRM():
    # 5985
    box_num = 4

    # check to see if the port is up
    return scan_service(box_num)

def scan_Apache():
    # 80
    box_num = 5
    box_ip = get_box_ip(box_num)

    # check to see if the port is up
    if not scan_service(box_num):
        return False
    
    # try to get the webpage
    try:
        response = requests.get(f"http://{box_ip}", timeout=3)
        server_header = response.headers.get('Server', '')
        return 'apache' in server_header.lower() or response.status_code < 400
    except Exception as e:
        print(f"Apache check failed: {e}")
        return False
    

def scan_MySQL():
    # 3306
    box_num = 6
    box_ip = get_box_ip(box_num)

    # check to see if the port is up
    if not scan_service(box_num):
        return False
    
    try:
        connection = pymysql.connect(
            host=box_ip,
            user='test', 
            password='test',
            connect_timeout=3
        )
        connection.close()
        return True
    except pymysql.err.OperationalError as e:
        # Error code 1045 means authentication failed but server is up
        if e.args[0] == 1045:
            return True
        print(f"MySQL check failed: {e}")
        return False
    except Exception as e:
        print(f"MySQL check failed: {e}")
        return False

def scan_Mail():
    # 25
    box_num = 7
    box_ip = get_box_ip(box_num)

    # check to see if the port is up
    if not scan_service(box_num):
        return False
    
    smtp_working = False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((box_ip, 25))
        banner = sock.recv(1024).decode('utf-8', errors='ignore')
        sock.close()
        smtp_working = len(banner) > 0 and ('SMTP' in banner or '220' in banner)
        print(f"SMTP banner received: {banner.strip()}")
    except Exception as e:
        print(f"SMTP check failed: {e}")
        return False

    imap_working = False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((box_ip, 143))
        banner = sock.recv(1024).decode('utf-8', errors='ignore')
        sock.close()
        imap_working = len(banner) > 0 and ('OK' in banner or 'IMAP' in banner)
        print(f"IMAP banner received: {banner.strip()}")
    except Exception as e:
        print(f"IMAP check failed: {e}")
        return False
    
    return imap_working and smtp_working

def scan_FTP():
    # 20 & 21
    box_num = 8
    box_ip = get_box_ip(box_num)

    # check to see if the port is up
    if not scan_service(box_num):
        return False
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((box_ip, 21))
        # Read the banner
        banner = sock.recv(1024)
        sock.close()
        return len(banner) > 0
    except Exception as e:
        print(f"FTP check failed: {e}")
        return False

def scan_Samba():
    # 139
    box_num = 9
    box_ip = get_box_ip(box_num)

    # check to see if the port is up
    if not scan_service(box_num):
        return False
    
    try:
        result = subprocess.run(
                ["smbclient", "-L", box_ip, "-N"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=3
            )
        return result.returncode == 0
    except Exception as e:
        print(f"Samba check failed: {e}")
        # Fall back to port check result if command fails
        return True

def scan_ELK():
    # 9200 & 5044 & 5601
    box_num = 10
    box_ip = get_box_ip(box_num)

    # check to see if the port is up
    if not scan_service(box_num):
        return False
    
    # try to get the ELK dashboard
    try:
        response = requests.get(f"http://{box_ip}:9200", timeout=3)
        return response.status_code == 200
    except Exception as e:
        print(f"ELK check failed: {e}")
        return False

############################
# Routes
############################

@app.route('/scan', methods=['GET'])
def scan():
    # String to print all results at end of scan
    outString = ["\nScan Results:"]

    if comp_state.get():
        try:
            print("Starting scan of all services")
            
            # Map of box numbers to their respective scan functions
            box_to_scan_function = {
                1: scan_AD_DNS,
                2: scan_IIS,
                3: scan_Nginx,
                4: scan_WinRM,
                5: scan_Apache,
                6: scan_MySQL,
                7: scan_Mail,
                8: scan_FTP,
                9: scan_Samba,
                10: scan_ELK
            }
            
            # Use a thread pool to scan machines in parallel (hopefully means fast scans)
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                # Submit all machine scanning functions
                future_to_box = {}
                for box_num in sorted(box_info.keys()):
                    # Use the specific scan function for each box if available, otherwise fall back to a basic port check
                    if box_num in box_to_scan_function:
                        future = executor.submit(box_to_scan_function[box_num])
                    else:
                        # For unknown boxes, scan common ports
                        future = executor.submit(lambda bn=box_num: scan_service(bn, [22, 80, 443]))
                    future_to_box[future] = box_num
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(future_to_box):
                    box_num = future_to_box[future]
                    
                    # Appends each box scan result to "outString" 
                    boxString = [f'\nBox {box_num} ({get_box_building(box_num)}) Scan:']

                    try:
                        service_up = future.result()
                        status = "up" if service_up else "down"
                    
                        # If service is down, deduct 0.5 points if health is above 0.
                        if not service_up:
                            subStr = subPoints(0.5, box_num)
                            boxString.append(subStr)

                            # If service is Down via Scan, but DB states its UP, update DB.
                            if isDBServiceStateUp(box_num):
                                setServiceState(box_num, "DOWN")

                        # If service is Up via Scan, but DB states is DOWN, update DB.
                        else:
                            if not isDBServiceStateUp(box_num):
                                setServiceState(box_num, "UP")

                        # If service has no more hp, display it.
                        if checkIsDead(box_num) is True:
                            deadStr = f'Box {box_num} ({get_box_building(box_num)} - {get_box_service(box_num)}) is out of HP!'
                            boxString.append(deadStr)
                        
                        boxScanFin = f"Box {box_num} ({get_box_building(box_num)} - {get_box_ip(box_num)}) scan complete - Status: {status}"
                        boxString.append(boxScanFin)
                        
                        for str in boxString:
                            outString.append(str)

                    except Exception as exc:
                        err = f"Box {box_num} ({get_box_building(box_num)} - {get_box_ip(box_num)}) scan generated an exception: {exc}"
                        # Treat exceptions as service being down
                        subPoints(0.5, box_num)
                        outString.append(err)
            
            for str in outString:
                print(str)

            return jsonify({"message": "Scan Complete!"}), 200
        except Exception as e:
            print(f"Error during scan: {e}")
            return jsonify({"error": "Scan failed due to an internal error"}), 500
    
    return jsonify({"error": "Competition hasn't started! Scan not attempted."}), 403

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
            print(f"Could not retrieve data | Error: {exc}")
            return jsonify({"error": "Failed to retrieve scores"}), 500
    return jsonify({"error": "Competition not started"}), 400


############################
# Helper Functions
############################

# Checks Database to find current stored service 
def isDBServiceStateUp(machine):
    service = get_box_service(machine)
    sql = "SELECT state FROM scoring WHERE service = %s"
    mysql.cursor.execute(sql, (service,))
    result = mysql.cursor.fetchall()
    
    if result and len(result) > 0:
        status = str(result[0][0])
        return status.upper() == "UP"
    
    return False

# Sets the new DB states for a specific service
def setServiceState(machine, state):
    service = get_box_service(machine)
    sql = "UPDATE scoring SET state = %s WHERE service = %s"
    mysql.cursor.execute(sql, (state, service))
    mysql.connection.commit()
    print(f"Updated service {service} state to {state}")

# Check if box has 0 HP
def checkIsDead(machine):
    service = get_box_service(machine)
    sql = "SELECT health FROM scoring WHERE service = %s"
    mysql.cursor.execute(sql, (service,))
    result = mysql.cursor.fetchall()
    
    if result and len(result) > 0:
        hp = result[0][0]
        return hp == 0
    
    return False

# Check if points intended to add result in health > 20 or set = 20
def checkMaxHP(points, machine, func):
    service = get_box_service(machine)
    
    if func == "add":
        sql = "SELECT health FROM scoring WHERE service = %s"
        mysql.cursor.execute(sql, (service,))
        result = mysql.cursor.fetchall()
        
        if result and len(result) > 0:
            res = float(result[0][0]) + float(points)
            return res >= 20
    else:
        if float(points) >= 20:
            return True
    
    return False


def addPoints(points, machine):
    service = get_box_service(machine)
    building = get_box_building(machine)
    
    if checkMaxHP(points, machine, "add") is True:
        print(f'Setting Box {machine} ({building} - {service}) to MAX Health')
        sql = "UPDATE scoring SET health = 20 WHERE service = %s"
        mysql.cursor.execute(sql, (service,))
    else:
        print(f'add {points} points to Box {machine} ({building} - {service})')
        sql = "UPDATE scoring SET health = health+%s WHERE service = %s"
        mysql.cursor.execute(sql, (points, service))
    
    mysql.connection.commit()


def subPoints(points, machine):
    service = get_box_service(machine)
    building = get_box_building(machine)

    if checkIsDead(machine) is False:
        sql = "UPDATE scoring SET health = health-%s WHERE service = %s"
        mysql.cursor.execute(sql, (points, service))
        mysql.connection.commit()
        return f'subtract {points} points from Box {machine} ({building} - {service})'
    return ""


def setPoints(points, machine):
    service = get_box_service(machine)
    building = get_box_building(machine)
    
    if checkMaxHP(points, machine, "set"):
        print(f'Setting Box {machine} ({building} - {service}) to MAX Health')
        sql = "UPDATE scoring SET health = 20 WHERE service = %s"
        mysql.cursor.execute(sql, (service,))
    else:
        print(f'set Box {machine} ({building} - {service}) to {points} points')
        sql = "UPDATE scoring SET health = %s WHERE service = %s"
        mysql.cursor.execute(sql, (points, service))

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
    print("============================ Box Mapping =============================")
    
    if box_info:
        print("Box to Service Mapping:")
        for box_num, info in sorted(box_info.items()):
            print(f"  Box {box_num}: {info['buildingName']} - {info['service']} ({info['os']}) - {info['ip']}")
    else:
        print("Box information not loaded yet. Start the competition to load box information.")
    
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
        elif command == "reload":
            if mysql.connection is not None:
                mysql.load_box_info()
                print("Box information reloaded from database")
            else:
                print("Database connection not established. Start the competition first.")
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
