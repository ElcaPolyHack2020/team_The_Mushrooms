'''
The Mushrooms
Levels 1 to 3
You may adapt parameters "optimize" and "n_pickup" in run()
Then you can just run this python code
Code may take a couple min to load at start, depending on parameter choice,
but it's fast afterwards
You may want to only simulate part of the day for a faster startup,
but full day simulation is very much possible
Code is quite refined and readable
'''

from time import sleep
import sys
import traci
import traci.constants as tc
import itertools # to get permutations for bruteforce traveling salesman for small n

class Simulation:
    def __init__(self, simulation_steps, sleep_time, pedestrians, bus_depot_start_edge, bus_depot_end_edge):
        self.simulation_steps = simulation_steps
        self.sleep_time = sleep_time
        self.pedestrians = pedestrians
        self.bus_depot_start_edge = bus_depot_start_edge
        self.bus_depot_end_edge = bus_depot_end_edge

    # Args: bus id, (list)current route, edge to start from, edge to go to
    # Post: Add edges between e_fr and e_to to bus route 
    def append_edges(self, bus_id, cur_rou, e_fr, e_to):
        add_rou = traci.simulation.findRoute(e_fr, e_to).edges    
        if len(cur_rou) != 0:
            cur_rou.pop()    
        cur_rou.extend(add_rou)
        traci.vehicle.setRoute(bus_id, cur_rou)

    # Args: bus id, edge to stop at, position to stop at
    # Post: Make bus stop at e_stop, pos_stop
    def bus_stop(self, bus_id, e_stop, pos_stop):
        traci.vehicle.setStop(vehID=bus_id, edgeID=e_stop, pos=pos_stop, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)

    # Args: bus id, person
    # Post: Add routes of person to bus route
    def add_route(self, bus_id, p):
        cur_rou = list(traci.vehicle.getRoute(bus_id))
        self.append_edges(bus_id, cur_rou, p.edge_from, p.edge_to)
        self.bus_stop(bus_id, p.edge_to, p.position_to)
        
    # Args: bus id, person, last edge from before
    # Post: Add route to pickup and deliver person as bus route
    def add_pers_route(self, bus_id, p, e_before):
        cur_rou = list(traci.vehicle.getRoute(bus_id))
        self.append_edges(bus_id, cur_rou, e_before, p.edge_from)
        self.bus_stop(bus_id, p.edge_from, p.position_from)
        self.add_route(bus_id, p)

    # Args: bus id, person
    # Post: Create new bus for person and routes it to person pickup + delivery
    def new_bus(self, bus_id, p):
        traci.vehicle.add(vehID=bus_id, typeID="BUS_S", routeID="", depart=p.depart+1.0, departPos=0, departSpeed=0, departLane=0, personCapacity=4)
        traci.vehicle.setRoute(bus_id, [self.bus_depot_start_edge])
        self.add_pers_route(bus_id, p, self.bus_depot_start_edge)

    # Args: bus id, edge bus comes from
    # Post: Send bus to depot
    def bye_bus(self, bus_id, e_fr):
        cur_rou = list(traci.vehicle.getRoute(bus_id)) 
        self.append_edges(bus_id, cur_rou, e_fr, self.bus_depot_end_edge)

    # Args: person, last edge from before
    # Return: length of person pickup + delivery route
    def add_pers_route_len(self, p, e_before):
        len = traci.simulation.findRoute(e_before, p.edge_from).travelTime
        return len + traci.simulation.findRoute(p.edge_from, p.edge_to).travelTime

    # Args: person
    # Return: length of first person pickup + delivery route
    def new_bus_len(self, p):
        len = traci.simulation.findRoute(self.bus_depot_start_edge, p.edge_from).travelTime
        return len + traci.simulation.findRoute(p.edge_from, p.edge_to).travelTime
                
    # Args: edge bus comes from
    # Return: length of drive to depot
    def bye_bus_len(self, e_fr):
        return traci.simulation.findRoute(e_fr, self.bus_depot_end_edge).travelTime
    
    # Post: Assign busses to people and runs simulation
    def run(self):
        # Sort list by depart time, as it's not sorted by default!
        self.pedestrians = sorted(self.pedestrians, key = lambda x: x.depart)
         
        ############################# Parameters #############################
        # set to False for faster program (still takes some minutes)
        optimize = True # whether to optimize bus routing

        # set to small number for faster program
        n_pickup = 4 # number of passengers to deliver per bus
        # Warning: do not both set optimize to True and n_pickup to a high number,
        # because then running time is multiplied with (n_pickup)! (n factorial)
        #
        # If optimize is False, runtime is quadratic in n_pickup
        #
        # In any case startup is faster when reducing simulation_steps
        ######################################################################

        pos = 0
        bus_n = 0
        while pos < len(self.pedestrians):
            to_id = min(pos + n_pickup, len(self.pedestrians)) # exclusive
            bus_id = "bus_" + str(bus_n)

            if optimize:
                best_perm = range(0, (to_id-pos)) # default (in depart order)
                best_len = 1000000000
                # Only try optimizing if there is no risk of arriving before passenger spawn
                min_pers_dist = 1000000000
                for p_id in range(pos, to_id):
                    p = self.pedestrians[p_id]
                    min_pers_dist = min(min_pers_dist, traci.simulation.findRoute(p.edge_from, p.edge_to).travelTime)
                if min_pers_dist * 0.8 > self.pedestrians[to_id - 1].depart - self.pedestrians[pos].depart: #No risk
                    # Compute best permutation (bruteforce traveling salesman)
                    for perm in list(itertools.permutations(range(0, (to_id-pos)))): # Try all permutations for bus
                        cur_len = 0
                        p = self.pedestrians[pos + perm[0]]
                        cur_len += self.new_bus_len(p)
                        for p_id in range(1, (to_id-pos)):              
                            e_before = self.pedestrians[pos + perm[p_id - 1]].edge_to
                            p = self.pedestrians[pos + perm[p_id]]
                            cur_len += self.add_pers_route_len(p, e_before)
                            if p_id == (to_id-pos)-1:
                                cur_len += self.bye_bus_len(p.edge_to)
                        if cur_len < best_len: # better permutation found
                            best_len = cur_len
                            best_perm = perm

                # Use best permutation
                p = self.pedestrians[pos + best_perm[0]]
                self.new_bus(bus_id, p)
                for p_id in range(1, (to_id-pos)):              
                    e_before = self.pedestrians[pos + best_perm[p_id - 1]].edge_to
                    p = self.pedestrians[pos + best_perm[p_id]]
                    self.add_pers_route(bus_id, p, e_before)
                    if p_id == (to_id-pos)-1:
                        self.bye_bus(bus_id, p.edge_to)

            else: # no optimization          
                p = self.pedestrians[int(pos)]
                self.new_bus(bus_id, p)
                for p_id in range(pos+1, to_id):              
                    e_before = self.pedestrians[p_id-1].edge_to
                    p = self.pedestrians[p_id]
                    self.add_pers_route(bus_id, p, e_before)
                    if p_id == to_id-1:
                        self.bye_bus(bus_id, p.edge_to)
            pos += n_pickup
            bus_n += 1
            
        step = 0
        while step <= self.simulation_steps:
            traci.simulationStep()
            if self.sleep_time > 0: 
                sleep(self.sleep_time)
            step += 1

        traci.close()
