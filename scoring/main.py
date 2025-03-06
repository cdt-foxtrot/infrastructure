import threading
from flask import Flask, jsonify, request

app = Flask(__name__)

comp_started = False

@app.route('/scan', methods=['GET'])
def scan():
    if comp_started:
        print("start scan")
        return jsonify({'data': 'test'})
    else:
        print("comp hasn't started")
        return jsonify({'comp': 'not started'})
    

@app.route('/scores', methods=['GET'])
def scores():
    return jsonify({'data2': 'test2'})

def addPoints(points, machine):
    print(f'add {points} points to {machine}')

def subPoints(points, machine):
    print(f'subtract {points} points to {machine}')

def setPoints(points, machine):
    print(f'set {machine} to {points} points')

def start():
    print('start')
    comp_started = True

def end():
    print('end')
    comp_started = False

def help():
    print("\n========================= Available Commands =========================")
    print("add <points> <machine>     - Add points to the machine's score")
    print("sub <points> <machine>     - Subtract points from the machine's score")
    print("set <points> <machine>     - Set machine points")
    print("start                      - Start machines and make endpoints reachable")
    print("end                        - Disable endpoints and stop machines")
    print("help                       - Show this help menu")
    print("======================================================================\n")

def command_listener():
    """Listen for terminal commands while Flask is running."""
    while True:
        command = input("Enter command: ").strip().lower()
        if command.startswith("add"):
            try:
                points = command.split()[1]
                machine = command.split()[2]
                addPoints(points, machine)
            except:
                print("Command arguments not provided. Correct usage: add <points> <machine>")
            
        elif command.startswith("sub"):
            try:
                points = command.split()[1]
                machine = command.split()[2]
                subPoints(points, machine)
            except:
                print("Command arguments not provided. Correct usage: sub <points> <machine>")
        elif command.startswith("set"):
            try:
                points = command.split()[1]
                machine = command.split()[2]
                setPoints(points, machine)
            except:
                print("Command arguments not provided. Correct usage: set <points> <machine>")
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
    flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False})
    flask_thread.daemon = True
    flask_thread.start()

    # Start listening for terminal commands
    command_listener()