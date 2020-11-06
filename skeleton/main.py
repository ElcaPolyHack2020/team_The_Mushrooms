import os
import sys
from time import sleep
import xml.etree.ElementTree as ET
import random
import csv

# Add the traci python library to the tools path
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

# Load traci
import traci
import traci.constants as tc


def main():

    # number of simulation step (24 h * 60 min * 60 s = 86400 steps)
    simulation_steps = 86400
    # sleep time between 2 simulation step. no sleep is set to 0.0
    sleep_time = 0.01

    # seed and scale factor for creating pedestrians
    pedestrians_seed = 30
    pedestrians_scale_factor = 10.0

    # location of the XML file containing the city network
    network_xml_file = r'..\..\trafficmap\aarhus\osm.net.xml'

    if not os.path.exists('./logs'):
        os.makedirs('./logs')
    
    sumoBinary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo-gui')
    sumoCmd = [sumoBinary, "-c", r"..\..\trafficmap\aarhus\osm.sumocfg", "--log", "./logs/sumo.log"]

    traci.start(sumoCmd, traceFile='./logs/traci.log')

    people = generate_random_people(seed=pedestrians_seed, scale_factor=pedestrian_scale_factor, net_xml_file=network_xml_file)

    for person in people:
        id = person.id
        edge_from = person.edge_from
        edge_to = person.edge_to
        position_from = person.position_from
        position_to = person.position_to
        depart = person.depart

        traci.person.add(personID=id, edgeID=edge_from, pos=position_from, depart=depart, typeID='DEFAULT_PEDTYPE')
        stage = traci.simulation.Stage(type=tc.STAGE_DRIVING, line="ANY", edges=[edge_to],
                                       departPos=0, arrivalPos=position_to, description="Driven as passenger")
        traci.person.appendStage(id, stage)
        waitingStage = traci.simulation.Stage(type=tc.STAGE_WAITING, edges=[edge_to], travelTime=200, description="Arrived at destination")
        traci.person.appendStage(id, waitingStage)

    # Create a bus for the persons
    bus_index = 0
    bus_depot_start_edge = '744377000#0'
    bus_depot_end_edge = '521059831#0'
    for person in people:
        bus_id = f'bus_{bus_index}'
        bus_index += 1

        traci.vehicle.add(vehID=bus_id, typeID="BUS_S", routeID="", depart=0, departPos=0, departSpeed=0, departLane=0, personCapacity=4)
        traci.vehicle.setRoute(bus_id, [bus_depot_start_edge])
        
        traci.vehicle.changeTarget(bus_id, person.edge_from)
        traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)
        

        traci.vehicle.setRoute(bus_id, [person.edge_from])
        traci.vehicle.changeTarget(bus_id, person.edge_to)
        traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_to, pos=person.position_to, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)
        

        #traci.vehicle.changeTarget(bus_id, bus_depot_end_edge)

        
        

        #traci.vehicle.add(vehID=bus_id, typeID="BUS_S", routeID="", depart=0, departPos=0, departSpeed=0, departLane=0, personCapacity=4)
        #traci.vehicle.setRoute(bus_id, ['744377000#0'])
        #traci.vehicle.setVia(bus_id, person.edge_from)
        #traci.vehicle.changeTarget(bus_id, person.edge_from)
        #traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)
        ##traci.vehicle.setRoute(bus_id, [person.edge_from])
        #traci.vehicle.changeTarget(bus_id, person.edge_to)
        #traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_to, pos=person.position_to, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)
        #traci.vehicle.changeTarget(bus_id, '521059831#0')

    traci.vehicle.subscribe('bus_0', (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION, tc.VAR_POSITION , tc.VAR_NEXT_STOPS ))

    step = 0
    while step <= simulation_steps:
        traci.simulationStep()
        if sleep_time > 0: 
            sleep(sleep_time)
        step += 1
        #print(traci.vehicle.getSubscriptionResults('bus_0'))

    traci.close()


def generate_random_people(seed: int, scale_factor: float, net_xml_file: str):
    tree = ET.parse(net_xml_file)
    root = tree.getroot()

    edges = []
    for edge in root.findall('.//edge'):
        if edge.attrib['id'].startswith(':cluster_'):
            continue
        if not ('type' in edge.attrib):
            continue
        if float(edge.findall('./lane')[0].attrib['length']) < 40:
            continue
        edges.append(edge)
    random.seed(seed)

    pedestrian_weights = parse_pedestrian_weights()

    people = []
    for pedestrian_weight in pedestrian_weights:
        t0 = pedestrian_weight.t0
        t1 = pedestrian_weight.t1
        weight = pedestrian_weight.weight * scale_factor
        
        count = 0
        while count < weight:
            count += 1
            edge1_index = random.randint(0, len(edges) - 1)
            edge2_index = random.randint(0, len(edges) - 1)

            edge1 = edges[edge1_index]
            edge2 = edges[edge2_index]

            len1 = float(edge1.findall('./lane')[0].attrib['length'])
            len2 = float(edge2.findall('./lane')[0].attrib['length'])

            pos1 = random.uniform(len1 * 0.4, len1 * 0.6)
            pos2 = random.uniform(len2 * 0.4, len2 * 0.6)

            depart = random.uniform(t0, t1)

            i = len(people)
            person = Person(f'person_{i}', edge1.attrib['id'], edge2.attrib['id'], pos1, pos2, depart)
            people.append(person)
    return people

def parse_pedestrian_weights():
    pedestrian_weights = []
    with open('pedestrians_weights.csv', encoding='utf8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        first_line = True
        for row in csv_reader:
            if first_line:
                first_line = False
                continue
            else:
                pedestrian_weight = PedestrianWeight(int(row[0]), int(row[1]), float(row[2]))
                pedestrian_weights.append(pedestrian_weight)

    return pedestrian_weights

class Person:
    # init method or constructor
    def __init__(self, id: str, edge_from: str, edge_to: str, position_from: float, position_to: float, depart: float):
        self.id = id
        self.edge_from = edge_from
        self.edge_to = edge_to
        self.position_from = position_from
        self.position_to = position_to
        self.depart = depart

class PedestrianWeight:
    # init method or constructor
    def __init__(self, t0: int, t1: int, weight: float):
        self.t0 = t0
        self.t1 = t1
        self.weight = weight

if __name__ == '__main__':
    main()
