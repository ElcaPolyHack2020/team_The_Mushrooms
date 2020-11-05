import os
import sys
from time import sleep
import xml.etree.ElementTree as ET
import random

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

    if not os.path.exists('./logs'):
        os.makedirs('./logs')
    sumoBinary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo-gui')
    sumoCmd = [sumoBinary, "-c", r"..\..\trafficmap\aarhus\osm.sumocfg", "--log", "./logs/sumo.log"]

    traci.start(sumoCmd, traceFile='./logs/traci.log')

    people = generate_random_people(seed=30, num_persons=5, net_xml_file=r'..\..\trafficmap\aarhus\osm.net.xml')

    for person in people:
        id = person.id
        edge_from = person.edge_from
        edge_to = person.edge_to
        position_from = person.position_from
        position_to = person.position_to

        traci.person.add(personID=id, edgeID=edge_from, pos=position_from, depart=0, typeID='DEFAULT_PEDTYPE')
        stage = traci.simulation.Stage(type=tc.STAGE_DRIVING, line="ANY", edges=[edge_to],
                                       departPos=0, arrivalPos=position_to, description="Driven as passenger")
        traci.person.appendStage(id, stage)
        waitingStage = traci.simulation.Stage(type=tc.STAGE_WAITING, edges=[edge_to], travelTime=200, description="Arrived at destination")
        traci.person.appendStage(id, waitingStage)

    # Create a bus for the persons
    bus_index = 0
    for person in people:
        bus_id = f'bus_{bus_index}'
        bus_index += 1
        traci.vehicle.add(vehID=bus_id, typeID="BUS_S", routeID="", depart=0, departPos=0, departSpeed=0, departLane=0, personCapacity=4)
        traci.vehicle.setVia(bus_id, person.edge_from)
        traci.vehicle.changeTarget(bus_id, person.edge_from)
        traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)
        traci.vehicle.setRoute(bus_id, [person.edge_from])
        traci.vehicle.changeTarget(bus_id, person.edge_to)
        traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_to, pos=person.position_to, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)

    step = 0
    while step < 1500:
        traci.simulationStep()
        sleep(0.02)
        step += 1

    traci.close()


def generate_random_people(seed: int, num_persons: int, net_xml_file: str):
    tree = ET.parse(net_xml_file)
    root = tree.getroot()

    edges = []
    for edge in root.findall('.//edge'):
        if edge.attrib['id'].startswith(':cluster_'):
            continue
        if float(edge.findall('./lane')[0].attrib['length']) < 40:
            continue
        edges.append(edge)
    random.seed(seed)

    people = []
    for i in range(num_persons):
        edge1_index = random.randint(0, len(edges) - 1)
        edge2_index = random.randint(0, len(edges) - 1)

        edge1 = edges[edge1_index]
        edge2 = edges[edge2_index]

        len1 = float(edge1.findall('./lane')[0].attrib['length'])
        len2 = float(edge2.findall('./lane')[0].attrib['length'])

        pos1 = random.uniform(len1 * 0.4, len1 * 0.6)
        pos2 = random.uniform(len2 * 0.4, len2 * 0.6)

        person = Person(f'person_{i}', edge1.attrib['id'], edge2.attrib['id'], pos1, pos2)
        people.append(person)
    return people


class Person:
    # init method or constructor
    def __init__(self, id: str, edge_from: str, edge_to: str, position_from: float, position_to: float):
        self.id = id
        self.edge_from = edge_from
        self.edge_to = edge_to
        self.position_from = position_from
        self.position_to = position_to


if __name__ == '__main__':
    main()
