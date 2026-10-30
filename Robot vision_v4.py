# !/usr/bin/env python3

from pyniryo import NiryoRobot, PinID, PinState, ConveyorDirection
from pymodbus.client import ModbusTcpClient

# Initialisation du Robot
IP_ROBOT = "192.168.99.239"
PORT_MODBUS = 5020

# Création de la communication Modbus Robot/Automate
client_Modbus = ModbusTcpClient(host=IP_ROBOT, port=PORT_MODBUS)
client_Modbus.connect()


# Adresse de test
COIL_START = 201
COMPTEUR = 300
COIL_ETAT_TAMPON = 250
COIL_DISPO_P1 = 202
COIL_CONFIRMATION_P2 = 200

# Connexion et initialisation du robot
robot = NiryoRobot(IP_ROBOT)
robot.clear_collision_detected()
robot.calibrate_auto()
robot.update_tool()
robot.wait(1)
print("Pret !")

HEIGTH_OFFSET = 0.07               # Décallage pour approcher la pièce

# Initialisation du Convoyeur et du capteur Infra Rouge
conveyor_id = robot.set_conveyor()
IR_sensor = PinID.DI5

# Définition des points
pPick = robot.get_pose_saved("pPick")                                                         # Point où on attrape la pièce
pAproPick = pPick.copy_with_offsets(0, 0, HEIGTH_OFFSET)
pPlace = robot.get_pose_saved("pPlace")                                                       # Point où on dépose la pièce
pAproPlace = pPlace.copy_with_offsets(0, 0, HEIGTH_OFFSET)
pPlaceTampon = robot.get_pose_saved("pPlaceTampon1")                                                       # Point où on dépose la pièce
pAproPlaceTampon = pPlaceTampon.copy_with_offsets(0, 0, HEIGTH_OFFSET)

# Creation de la boucle d'action du programme
robot.move_to_home_pose()                                                                     # Déplace le robot en position de repos
robot.open_gripper(speed=500, max_torque_percentage=100, hold_torque_percentage=150)           # Les paramètres sont facultatifs et sauvegardés tant qu'ils ne sont pas modifiés                                    

# Creation de la variable compteur du tampon

compteur = client_Modbus.read_holding_registers(300, count=2).registers[0]


print(compteur)

b =client_Modbus.read_coils(COIL_START, count=1).bits[0] 
print(b)

while True:
    if client_Modbus.read_coils(COIL_START, count=1).bits[0]:
        robot.run_conveyor(conveyor_id, speed=75, direction=ConveyorDirection.FORWARD)
        client_Modbus.write_coil(COIL_ETAT_TAMPON, False)
        if robot.digital_read(IR_sensor) == PinState.LOW and client_Modbus.read_coils(COIL_DISPO_P1, count=1).bits[0] == True:                                     
            robot.wait(2)                                                                   
            robot.stop_conveyor(conveyor_id)                                                                                                        
            robot.move(pAproPick)                                                            
            robot.move(pPick, linear = True)                                                  
            robot.close_gripper()
            robot.move(pAproPick, linear = True)
            robot.move(pAproPlace)
            robot.move(pPlace)
            robot.move(pPlace, linear = True) 
            robot.open_gripper()
            robot.move(pAproPlace, linear = True)
            robot.move_to_home_pose()
            robot.stop_conveyor(conveyor_id)
            client_Modbus.write_coil(COIL_CONFIRMATION_P2, True)
        if compteur < 6 and robot.digital_read(IR_sensor) == PinState.LOW and client_Modbus.read_coils(COIL_DISPO_P1, count=1).bits[0] == False:
            client_Modbus.write_coil(COIL_ETAT_TAMPON, True)
            robot.wait(2)                                                                
            robot.stop_conveyor(conveyor_id)                                                                                                 
            robot.move(pAproPick)                                                            
            robot.move(pPick, linear = True)                                                  
            robot.close_gripper()
            robot.move(pAproPick, linear = True)
            robot.move(pAproPlaceTampon)
            robot.move(pPlaceTampon)
            robot.move(pPlaceTampon, linear = True)
            robot.open_gripper()
            robot.move(pAproPlaceTampon, linear = True)
            robot.move_to_home_pose()
            robot.stop_conveyor(conveyor_id)
            client_Modbus.write_coil(COIL_CONFIRMATION_P2, True)
    if client_Modbus.read_coils(COIL_START, count=1).bits[0] == False:
        robot.stop_conveyor(conveyor_id)
 