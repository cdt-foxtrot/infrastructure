import socket
import subprocess
import threading
from flask import Flask, jsonify, request
import time
import concurrent.futures
import random
import pymysql
import requests
import logging
import os
from datetime import datetime

# Configure logging
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Create endpoint logger
endpoint_logger = logging.getLogger('endpoint')
endpoint_logger.setLevel(logging.INFO)
endpoint_file_handler = logging.FileHandler(os.path.join(log_directory, 'endpoint.log'))
endpoint_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
endpoint_logger.addHandler(endpoint_file_handler)

# Create scan logger
scan_logger = logging.getLogger('scan')
scan_logger.setLevel(logging.INFO)
scan_file_handler = logging.FileHandler(os.path.join(log_directory, 'scan.log'))
scan_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
scan_logger.addHandler(scan_file_handler)

app = Flask(__name__)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Disable Flask's default logging to console
import logging as flask_logging
flask_logging.getLogger('werkzeug').disabled = True
app.logger.disabled = True


class Points:
    def __init__(self):
        self.points = 0.5

    def get_points(self):
        return self.points

    def set_points(self, num):
        self.points = num

points = Points()

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
                endpoint_logger.info("Scoring DB Connection Established")
                # Load box information from the database
                self.load_box_info()
        except Exception as e:
            print(f"Error: {e}")
            endpoint_logger.error(f"Database connection error: {e}")

    def get_connection(self):
        return self.connection
    
    def close_connection(self):
        if self.connection is not None:
            self.connection.close()
            print("Scoring DB Connection Closed")
            endpoint_logger.info("Scoring DB Connection Closed")
    
    def load_box_info(self):
        """Load box information from the database"""
        try:
            sql = "SELECT box, service, building, os, ip, port FROM scoring"
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            
            # Clear existing mappings
            global box_info, service_to_box, building_to_box
            box_info = {}
            service_to_box = {}
            building_to_box = {}
            
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
                building_to_box[building_name.lower()] = box_num
                
            print(f"Loaded information for {len(box_info)} boxes from database")
            endpoint_logger.info(f"Loaded information for {len(box_info)} boxes from database")
        except Exception as e:
            print(f"Error loading box information from database: {e}")
            endpoint_logger.error(f"Error loading box information from database: {e}")

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
building_to_box = {}

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
        is_open = result == 0
        scan_logger.info(f"Port check for {ip}:{port} - {'Open' if is_open else 'Closed'}")
        return is_open
    except Exception as e:
        scan_logger.error(f"Error checking port {port} on {ip}: {e}")
        return False
    
def scan_service(box_num):
    """Generic service scanning function"""
    service = get_box_service(box_num)
    box_ip = get_box_ip(box_num)
    building = get_box_building(box_num)
    ports = get_box_ports(box_num)

    scan_logger.info(f"Scanning Box {box_num}: {service} at {box_ip} ({building})")
    
    # Check if all required ports are open
    port_results = []
    for port in ports:
        port_open = is_port_open(box_ip, port)
        port_status = "open" if port_open else "closed"
        scan_logger.info(f"Port {port} on {box_ip} is {port_status}")
        port_results.append(port_open)
    
    # Return True only if all ports are open
    result = all(port_results)
    scan_logger.info(f"Scan result for Box {box_num}: {'UP' if result else 'DOWN'}")
    return result

def scan_AD_DNS():
    # 389
    box_num = 1
    box_ip = get_box_ip(box_num)
    realm = "overworld.net"

    scan_logger.info(f"Scanning AD/DNS box {box_num} at {box_ip}")

    # check to see if the port is up
    if not scan_service(box_num):
        scan_logger.info(f"Basic port scan failed for AD/DNS box {box_num}")
        return False
    
    dns_working = False
    try:
        result = subprocess.run(
            ["nslookup", realm, box_ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=3
        )
        dns_output = result.stdout.decode('utf-8', errors='ignore')
        
        # Check if the output contains the domain name and IP address
        dns_working = (result.returncode == 0 and 
                      realm in dns_output and 
                      box_ip in dns_output)
        
        scan_logger.info(f"DNS check result: {'Success' if dns_working else 'Failed'}")
        if not dns_working:
            scan_logger.debug(f"DNS output: {dns_output}")
    except Exception as e:
        scan_logger.error(f"DNS check failed: {e}")
        dns_working = False
    
    ldap_working = False
    try:
        # ldap query
        result = subprocess.run(
            ["ldapsearch", "-x", "-H", f"ldap://{box_ip}", 
             "-D", "cn=greyteam,cn=Users,dc=overworld,dc=net", 
             "-w", "SteveSexy!", 
             "-b", "dc=overworld,dc=net", 
             "-s", "sub", "(objectClass=user)", "sAMAccountName"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=3
        )
        ldap_output = result.stdout.decode('utf-8', errors='ignore')
        ldap_error = result.stderr.decode('utf-8', errors='ignore')
        
        # Check if we got valid results
        ldap_working = (result.returncode == 0 and 
                       "# numEntries:" in ldap_output and 
                       "result:" not in ldap_error)
        
        scan_logger.info(f"LDAP check result: {'Success' if ldap_working else 'Failed'}")
        if not ldap_working:
            scan_logger.debug(f"LDAP error: {ldap_error}")
    except Exception as e:
        scan_logger.error(f"LDAP check failed: {e}")
        ldap_working = False
    
    # Return True only if both DNS and LDAP are working
    final_result = dns_working and ldap_working
    scan_logger.info(f"AD/DNS combined check result: {'UP' if final_result else 'DOWN'}")
    return final_result

def scan_IIS():
    # 80
    box_num = 2
    box_ip = get_box_ip(box_num)

    scan_logger.info(f"Scanning IIS box {box_num} at {box_ip}")

    # check to see if the port is up
    if not scan_service(box_num):
        scan_logger.info(f"Basic port scan failed for IIS box {box_num}")
        return False
    
    # try to get the webpage
    try:
        response = requests.get(f"http://{box_ip}", timeout=3)
        server_header = response.headers.get('Server', '')
        result = 'IIS' in server_header or 'Microsoft' in server_header or response.status_code < 400
        scan_logger.info(f"IIS check result: {'UP' if result else 'DOWN'} (Status code: {response.status_code}, Server header: {server_header})")
        return result
    except Exception as e:
        scan_logger.error(f"IIS check failed: {e}")
        return False

def scan_Nginx():
    # 80
    box_num = 3
    box_ip = get_box_ip(box_num)

    scan_logger.info(f"Scanning Nginx box {box_num} at {box_ip}")

    # check to see if the port is up
    if not scan_service(box_num):
        scan_logger.info(f"Basic port scan failed for Nginx box {box_num}")
        return False
    
    # try to get the webpage
    try:
        response = requests.get(f"http://{box_ip}", timeout=3)
        server_header = response.headers.get('Server', '')
        result = 'nginx' in server_header.lower() or response.status_code < 400
        scan_logger.info(f"Nginx check result: {'UP' if result else 'DOWN'} (Status code: {response.status_code}, Server header: {server_header})")
        return result
    except Exception as e:
        scan_logger.error(f"Nginx check failed: {e}")
        return False

def scan_WinRM():
    # 5985
    box_num = 4
    scan_logger.info(f"Scanning WinRM box {box_num}")
    # check to see if the port is up
    return scan_service(box_num)

def scan_Apache():
    # 80
    box_num = 5
    box_ip = get_box_ip(box_num)

    scan_logger.info(f"Scanning Apache box {box_num} at {box_ip}")

    # check to see if the port is up
    if not scan_service(box_num):
        scan_logger.info(f"Basic port scan failed for Apache box {box_num}")
        return False
    
    # try to get the webpage
    try:
        response = requests.get(f"http://{box_ip}", timeout=3)
        server_header = response.headers.get('Server', '')
        result = 'apache' in server_header.lower() or response.status_code < 400
        scan_logger.info(f"Apache check result: {'UP' if result else 'DOWN'} (Status code: {response.status_code}, Server header: {server_header})")
        return result
    except Exception as e:
        scan_logger.error(f"Apache check failed: {e}")
        return False
    

def scan_MySQL():
    # 3306
    box_num = 6
    box_ip = get_box_ip(box_num)

    scan_logger.info(f"Scanning MySQL box {box_num} at {box_ip}")

    # check to see if the port is up
    if not scan_service(box_num):
        scan_logger.info(f"Basic port scan failed for MySQL box {box_num}")
        return False
    
    try:
        connection = pymysql.connect(
            host=box_ip,
            user='test', 
            password='test',
            connect_timeout=3
        )
        connection.close()
        scan_logger.info(f"MySQL check result: UP (Connected successfully)")
        return True
    except pymysql.err.OperationalError as e:
        # Error code 1045 means authentication failed but server is up
        if e.args[0] == 1045:
            scan_logger.info(f"MySQL check result: UP (Authentication failed but server is up)")
            return True
        scan_logger.error(f"MySQL check failed: {e}")
        return False
    except Exception as e:
        scan_logger.error(f"MySQL check failed: {e}")
        return False

def scan_Mail():
    # 143
    box_num = 7
    box_ip = get_box_ip(box_num)

    scan_logger.info(f"Scanning Mail box {box_num} at {box_ip}")

    # check to see if the port is up
    if not scan_service(box_num):
        scan_logger.info(f"Basic port scan failed for Mail box {box_num}")
        return False
    '''
    smtp_working = False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((box_ip, 25))
        banner = sock.recv(1024).decode('utf-8', errors='ignore')
        sock.close()
        smtp_working = len(banner) > 0 and ('SMTP' in banner or '220' in banner)
        scan_logger.info(f"SMTP check result: {'UP' if smtp_working else 'DOWN'} (Banner: {banner.strip()})")
    except Exception as e:
        scan_logger.error(f"SMTP check failed: {e}")
        return False
    '''
    imap_working = False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((box_ip, 143))
        banner = sock.recv(1024).decode('utf-8', errors='ignore')
        sock.close()
        imap_working = len(banner) > 0 and ('OK' in banner or 'IMAP' in banner)
        scan_logger.info(f"IMAP check result: {'UP' if imap_working else 'DOWN'} (Banner: {banner.strip()})")
    except Exception as e:
        scan_logger.error(f"IMAP check failed: {e}")
        return False
    
    final_result = imap_working #and smtp_working
    scan_logger.info(f"Mail combined check result: {'UP' if final_result else 'DOWN'}")
    return final_result

def scan_FTP():
    # 20 & 21
    box_num = 8
    box_ip = get_box_ip(box_num)

    scan_logger.info(f"Scanning FTP box {box_num} at {box_ip}")

    # check to see if the port is up
    if not scan_service(box_num):
        scan_logger.info(f"Basic port scan failed for FTP box {box_num}")
        return False
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((box_ip, 21))
        # Read the banner
        banner = sock.recv(1024)
        sock.close()
        result = len(banner) > 0
        scan_logger.info(f"FTP check result: {'UP' if result else 'DOWN'} (Banner received: {len(banner) > 0})")
        return result
    except Exception as e:
        scan_logger.error(f"FTP check failed: {e}")
        return False

def scan_Samba():
    # 139
    box_num = 9
    box_ip = get_box_ip(box_num)

    scan_logger.info(f"Scanning Samba box {box_num} at {box_ip}")

    # check to see if the port is up
    if not scan_service(box_num):
        scan_logger.info(f"Basic port scan failed for Samba box {box_num}")
        return False
    
    try:
        result = subprocess.run(
                ["smbclient", "-L", box_ip, "-N"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=3
            )
        cmd_result = result.returncode == 0
        scan_logger.info(f"Samba check result: {'UP' if cmd_result else 'DOWN'} (Return code: {result.returncode})")
        return cmd_result
    except Exception as e:
        scan_logger.error(f"Samba check failed: {e}")
        # Fall back to port check result if command fails
        scan_logger.info("Falling back to port check result for Samba")
        return True

def scan_ELK():
    # 9200 & 5044 & 5601
    box_num = 10
    box_ip = get_box_ip(box_num)

    scan_logger.info(f"Scanning ELK box {box_num} at {box_ip}")

    # check to see if the port is up
    if not scan_service(box_num):
        scan_logger.info(f"Basic port scan failed for ELK box {box_num}")
        return False
    
    # try to get the ELK dashboard
    try:
        response = requests.get(f"http://{box_ip}:9200", timeout=3)
        result = response.status_code == 200
        scan_logger.info(f"ELK check result: {'UP' if result else 'DOWN'} (Status code: {response.status_code})")
        return result
    except Exception as e:
        scan_logger.error(f"ELK check failed: {e}")
        return False

############################
# Routes
############################

@app.route('/scan', methods=['GET'])
def scan():
    endpoint_logger.info("Received request to /scan endpoint")
    client_ip = request.remote_addr
    endpoint_logger.info(f"Client IP: {client_ip}")
    
    if comp_state.get():
        try:
            endpoint_logger.info("Starting scan of all services")
            scan_logger.info("===== BEGINNING FULL SCAN =====")
            
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
                scan_results = {}
                
                for future in concurrent.futures.as_completed(future_to_box):
                    box_num = future_to_box[future]
                    
                    try:
                        service_up = future.result()
                        status = "up" if service_up else "down"
                        scan_results[box_num] = {"status": status}
                    
                        # If service is down, deduct DEDUCT_POINTS (at the top) points if health is above 0.
                        if not service_up:
                            subStr = subPoints(box_num, points.get_points())
                            if subStr:
                                scan_logger.info(subStr)

                            # If service is Down via Scan, but DB states its UP, update DB.
                            if isDBServiceStateUp(box_num):
                                setServiceState(box_num, "DOWN")
                                scan_logger.info(f"Updated Box {box_num} service state to DOWN in database")

                        # If service is Up via Scan, but DB states is DOWN, update DB.
                        else:
                            if not isDBServiceStateUp(box_num):
                                setServiceState(box_num, "UP")
                                scan_logger.info(f"Updated Box {box_num} service state to UP in database")

                        # If service has no more hp, display it.
                        if checkIsDead(box_num) is True:
                            deadStr = f'Box {box_num} ({get_box_building(box_num)} - {get_box_service(box_num)}) is out of HP!'
                            scan_logger.warning(deadStr)
                            scan_results[box_num]["isDead"] = True
                        
                        boxScanFin = f"Box {box_num} ({get_box_building(box_num)} - {get_box_ip(box_num)}) scan complete - Status: {status}"
                        scan_logger.info(boxScanFin)

                    except Exception as exc:
                        err = f"Box {box_num} ({get_box_building(box_num)} - {get_box_ip(box_num)}) scan generated an exception: {exc}"
                        # Treat exceptions as service being down
                        subStr = subPoints(points.get_points(), box_num)
                        if subStr:
                            scan_logger.info(subStr)
                        scan_logger.error(err)
                        scan_results[box_num] = {"status": "error", "message": str(exc)}
            
            scan_logger.info("===== SCAN COMPLETE =====")
            endpoint_logger.info("Scan completed successfully")
            
            return jsonify({"message": "Scan Complete!", "results": scan_results}), 200
            
        except Exception as e:
            error_msg = f"Error during scan: {e}"
            print(error_msg)
            endpoint_logger.error(error_msg)
            return jsonify({"error": "Scan failed due to an internal error"}), 500
    
    endpoint_logger.warning("Scan attempted but competition hasn't started")
    return jsonify({"error": "Competition hasn't started! Scan not attempted."}), 403

@app.route('/scores', methods=['GET'])
def scores():
    endpoint_logger.info("Received request to /scores endpoint")
    client_ip = request.remote_addr
    endpoint_logger.info(f"Client IP: {client_ip}")
    
    try:
        sql = "SELECT * FROM scoring"
        mysql.cursor.execute(sql)
        res = mysql.cursor.fetchall()

        # Get Column Names
        col = [desc[0] for desc in mysql.cursor.description]

        # Convert to list of dictionaries
        data = [dict(zip(col, row)) for row in res]

        result = {"boxes": data}
        
        endpoint_logger.info("Successfully retrieved scores")
        return jsonify(result)
    # Probably need a better exception here
    except Exception as exc:
        error_msg = f"Could not retrieve data | Error: {exc}"
        print(error_msg)
        endpoint_logger.error(error_msg)
        return jsonify({"error": "Failed to retrieve scores"}), 500


############################
# Helper Functions
############################

# Get box number from either number or building name
def get_box_number(box_identifier):
    """Convert box number or building name to box number"""
    # If it's already a number, just return it
    if isinstance(box_identifier, int):
        if box_identifier in box_info:
            return box_identifier
        else:
            raise ValueError(f"Box number {box_identifier} not found")
            
    # Try to parse as a number
    try:
        box_num = int(box_identifier)
        if box_num in box_info:
            return box_num
        else:
            raise ValueError(f"Box number {box_num} not found")
    except ValueError:
        # Try to match as a building name
        # Normalize building name (lowercase)
        building_name = box_identifier.strip().lower()
        
        # Check if the name matches any building
        if building_name in building_to_box:
            return building_to_box[building_name]
                
        # If we reach here, no match found
        raise ValueError(f"Building name '{box_identifier}' not found")

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
    endpoint_logger.info(f"Updated service {service} state to {state}")

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


def addPoints(machine, points):
    try:
        box_num = get_box_number(machine)
        service = get_box_service(box_num)
        building = get_box_building(box_num)
        
        if checkMaxHP(points, box_num, "add") is True:
            print(f'Setting Box {box_num} ({building} - {service}) to MAX Health')
            endpoint_logger.info(f'Setting Box {box_num} ({building} - {service}) to MAX Health')
            sql = "UPDATE scoring SET health = 20 WHERE service = %s"
            mysql.cursor.execute(sql, (service,))
        else:
            print(f'add {points} points to Box {box_num} ({building} - {service})')
            endpoint_logger.info(f'add {points} points to Box {box_num} ({building} - {service})')
            sql = "UPDATE scoring SET health = health+%s WHERE service = %s"
            mysql.cursor.execute(sql, (points, service))
        
        mysql.connection.commit()
        return True
    except ValueError as e:
        print(str(e))
        endpoint_logger.error(f"Error adding points: {e}")
        return False

def subPoints(machine, points):
    try:
        box_num = get_box_number(machine)
        service = get_box_service(box_num)
        building = get_box_building(box_num)

        if checkIsDead(box_num) is False:
            # First check current health
            sql_check = "SELECT health FROM scoring WHERE service = %s"
            mysql.cursor.execute(sql_check, (service,))
            result = mysql.cursor.fetchone()
            current_health = float(result[0])
            
            # Calculate new health
            new_health = max(0, current_health - float(points))
            
            # Update with new health value
            sql = "UPDATE scoring SET health = %s WHERE service = %s"
            mysql.cursor.execute(sql, (new_health, service))
            mysql.connection.commit()
            
            endpoint_logger.info(f'subtract {points} points from Box {box_num} ({building} - {service}), new health: {new_health}')
            return f'subtract {points} points from Box {box_num} ({building} - {service}), new health: {new_health}'
        return ""
    except ValueError as e:
        print(str(e))
        endpoint_logger.error(f"Error subtracting points: {e}")
        return ""
    except Exception as e:
        print(f"Database error: {e}")
        endpoint_logger.error(f"Database error in subPoints: {e}")
        return ""


def setPoints(machine, points):
    try:
        box_num = get_box_number(machine)
        service = get_box_service(box_num)
        building = get_box_building(box_num)
        
        if checkMaxHP(points, box_num, "set"):
            print(f'Setting Box {box_num} ({building} - {service}) to MAX Health')
            endpoint_logger.info(f'Setting Box {box_num} ({building} - {service}) to MAX Health')
            sql = "UPDATE scoring SET health = 20 WHERE service = %s"
            mysql.cursor.execute(sql, (service,))
        else:
            print(f'set Box {box_num} ({building} - {service}) to {points} points')
            endpoint_logger.info(f'set Box {box_num} ({building} - {service}) to {points} points')
            sql = "UPDATE scoring SET health = %s WHERE service = %s"
            mysql.cursor.execute(sql, (points, service))

        mysql.connection.commit()
        return True
    except ValueError as e:
        print(str(e))
        endpoint_logger.error(f"Error setting points: {e}")
        return False


# Successfully starts connection
def start():
    print('Competition started')
    comp_state.set(True)
    

def end():
    print('Competition ended')
    comp_state.set(False)

def hp_loss():
    """Set the points to be deducted when a service is down during scan."""
    print("\n========================= HP Loss Rate Settings =========================")
    print("1:  0.25 points per scan")
    print("2:  0.5  points per scan")
    print("3:  0.75 points per scan")
    print("4:  1.0  points per scan")

    try:
        selection = int(input("Enter your choice (1-4): "))
                
        if selection == 1:
            new_points = 0.25
        elif selection == 2:
            new_points = 0.5
        elif selection == 3:
            new_points = 0.75
        elif selection == 4:
            new_points = 1.0
        else:
            print("Error: Please enter a number between 1 and 4.")
            return
            
        # Set the new points value
        points.set_points(new_points)
        print(f"HP loss rate set to {new_points} points per scan")
        endpoint_logger.info(f"HP loss rate changed to {new_points} points per scan")
    
    except ValueError:
        print("Error: Please enter a valid number.")


def help():
    print("\n========================= Available Commands =========================")
    print("add <box> <points>     - Add points to the box's score (box can be number or building name)")
    print("sub <box> <points>     - Subtract points from the box's score (box can be number or building name)")
    print("set <box> <points>     - Set box points (box can be number or building name)")
    print("start                  - Start competition and make scan endpoint reachable")
    print("end                    - Disable scan endpoint and stop competition. Scores endpoint remains up")
    print("exit                   - Close database connection and exit gracefully")
    print("help                   - Show this help menu")
    print("hp                - Change Point Deduction Value")
    print("reload                 - Reload box information from database")
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
                if len(cmd_parts) < 3:
                    raise ValueError("Not enough arguments")
                    
                # Changed order: the second part is now the machine, the third part is the points
                # Join parts 1 to n-1 as they might be a building name with spaces
                machine = " ".join(cmd_parts[1:-1])
                points = cmd_parts[-1]
                addPoints(machine, points)
            except (IndexError, ValueError) as e:
                print(f"Error: {e}")
                print("Command arguments not provided or invalid. Correct usage: add <box_number_or_building_name> <points>")
            
        elif command.startswith("sub"):
            try:
                cmd_parts = command.split()
                if len(cmd_parts) < 3:
                    raise ValueError("Not enough arguments")
                    
                # Changed order: the second part is now the machine, the third part is the points
                machine = " ".join(cmd_parts[1:-1])
                points = cmd_parts[-1]
                result = subPoints(machine, points)
                if result:
                    print(result)
            except (IndexError, ValueError) as e:
                print(f"Error: {e}")
                print("Command arguments not provided or invalid. Correct usage: sub <box_number_or_building_name> <points>")
        elif command.startswith("set"):
            try:
                cmd_parts = command.split()
                if len(cmd_parts) < 3:
                    raise ValueError("Not enough arguments")
                    
                # Changed order: the second part is now the machine, the third part is the points
                machine = " ".join(cmd_parts[1:-1])
                points = cmd_parts[-1]
                setPoints(machine, points)
            except (IndexError, ValueError) as e:
                print(f"Error: {e}")
                print("Command arguments not provided or invalid. Correct usage: set <box_number_or_building_name> <points>")
        elif command.startswith("start"):
            start()
        elif command.startswith("end"):
            end()
        elif command.startswith("exit"):
            if mysql.connection is not None:
                mysql.close_connection()

            print("Shutting down...")
            break
        elif command == "help":
            help()
        elif command.startswith("hp"):
            hp_loss()
        elif command == "reload":
            if mysql.connection is not None:
                mysql.load_box_info()
                print("Box information reloaded from database")
            else:
                print("Database connection not established. Start the competition first.")
        else:
            print("Unknown command")

if __name__ == '__main__':
    # connect to db
    mysql.start_connection('localhost', 'greyteam', 'greyteam', 'Scoring')

    # Initialize help message
    help()

    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False})
    flask_thread.daemon = True
    flask_thread.start()
    print("Flask server started at http://0.0.0.0:5000/")
    
    # Start listening for terminal commands
    command_listener()
