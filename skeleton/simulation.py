from time import sleep
import sys
import traci
import traci.constants as tc

class bus:
    def __init__(self, bus_id):
        self.id = bus_id
        self.busy = True
        self.arrived = False

class Simulation:
    def __init__(self, simulation_steps, sleep_time, pedestrians, bus_depot_start_edge, bus_depot_end_edge):
        self.simulation_steps = simulation_steps
        self.sleep_time = sleep_time
        self.pedestrians = pedestrians
        self.bus_depot_start_edge = bus_depot_start_edge
        self.bus_depot_end_edge = bus_depot_end_edge

    #Args: bus id, (list)current route, edge start from, edge go to
    #Adds edges between e_fr and e_to to bus route 
    def append_edges(self, bus_id, cur_rou, e_fr, e_to):
        add_rou = traci.simulation.findRoute(e_fr, e_to).edges    
        if len(cur_rou) != 0:
            cur_rou.pop()    
        cur_rou.extend(add_rou)
        traci.vehicle.setRoute(bus_id, cur_rou)

    #Args: bus id, edge to stop at, pos to stop at
    #Post: Makes bus stop at e_stop, pos_stop
    def bus_stop(self, bus_id, e_stop, pos_stop):
        traci.vehicle.setStop(vehID=bus_id, edgeID=e_stop, pos=pos_stop, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)

    #Args: bus id, person
    #Post: Add routes of person to bus route
    def add_route(self, bus_id, p):
        cur_rou = list(traci.vehicle.getRoute(bus_id))
        self.append_edges(bus_id, cur_rou, p.edge_from, p.edge_to)
        self.bus_stop(bus_id, p.edge_to, p.position_to)
        
    #Args: bus id, person
    #Post: adds route to person + person route as bus route
    def add_pers_route(self, bus_id, p, e_before):
        cur_rou = list(traci.vehicle.getRoute(bus_id))
        self.append_edges(bus_id, cur_rou, e_before, p.edge_from)
        self.bus_stop(bus_id, p.edge_from, p.position_from)
        self.add_route(bus_id, p)

    #Args: bus id, person
    #Post: creates new bus for person and routes it to person
    def new_bus(self, bus_id, p):
        traci.vehicle.add(vehID=bus_id, typeID="BUS_S", routeID="", depart=p.depart+1.0, departPos=0, departSpeed=0, departLane=0, personCapacity=4)
        traci.vehicle.setRoute(bus_id, [self.bus_depot_start_edge])
        self.add_pers_route(bus_id, p, self.bus_depot_start_edge)

    #Args: bus id, edge bus comes from
    #Post: sends bus home
    def bye_bus(self, bus_id, e_fr):
        cur_rou = list(traci.vehicle.getRoute(bus_id)) 
        self.append_edges(bus_id, cur_rou, e_fr, self.bus_depot_end_edge)
    
    #Post: Assigns busses to people and runs simulation
    def run(self):
        #list not sorted by default!
        self.pedestrians = sorted(self.pedestrians, key = lambda x: x.depart)

        pos = 0
        bus_n = 0
        while pos < len(self.pedestrians):
            to_id = min(pos+4, len(self.pedestrians))
            bus_id = "bus_" + str(bus_n)
            p = self.pedestrians[int(pos)]
            self.new_bus(bus_id, p)
            for p_id in range(pos+1, to_id):              
                e_before = self.pedestrians[int(p_id-1)].edge_to
                p = self.pedestrians[int(p_id)]
                self.add_pers_route(bus_id, p, e_before)
                if p_id == to_id-1:
                    self.bye_bus(bus_id, p.edge_to)
            pos += 4
            bus_n += 1
            
        step = 0
        while step <= self.simulation_steps:
            traci.simulationStep()
            if self.sleep_time > 0: 
                sleep(self.sleep_time)
            step += 1

        traci.close()
