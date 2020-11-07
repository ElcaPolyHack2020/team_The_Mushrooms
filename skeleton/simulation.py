from time import sleep
import sys
import traci
import traci.constants as tc

class bus:
    def __init__(self, bus_id):
        self.id = bus_id
        self.busy = True

class Simulation:
    def __init__(self, simulation_steps, sleep_time, pedestrians, bus_depot_start_edge, bus_depot_end_edge):
        self.simulation_steps = simulation_steps
        self.sleep_time = sleep_time
        self.pedestrians = pedestrians
        self.bus_depot_start_edge = bus_depot_start_edge
        self.bus_depot_end_edge = bus_depot_end_edge
        self.buses = []
        #self.persons = []

    def append_edges(self, cur_rou, e_fr, e_to, bus_id):
        add_rou = traci.simulation.findRoute(e_fr, e_to).edges
        if len(cur_rou) != 0:
            cur_rou.pop()      
        cur_rou.extend(add_rou)
        traci.vehicle.setRoute(str(bus_id), cur_rou)

    #Return: closest bus index or -1 when all full/busy
    def find_bus(self, pers_edge):
        closest_time = 1000000000
        closest_id = -1
        for b in self.buses:
            if traci.vehicle.getPersonNumber(str(b.id)) == traci.vehicle.getPersonCapacity(str(b.id)):
                continue
            if b.busy:
                continue
            cur_time = traci.simulation.findRoute(pers_edge, traci.vehicle.getRoadID(str(b.id))).travelTime
            if cur_time < closest_time:
                closest_time = cur_time
                closest_id = b.id
        return closest_id
    
    def new_bus(self, bus_id, ed_to, p_id):
        print("bus_id: ", bus_id)
        p = self.pedestrians[int(p_id)]
        traci.vehicle.add(vehID=str(bus_id), typeID="BUS_S", routeID="", depart=p.depart, departPos=0, departSpeed=0, departLane=0, personCapacity=4)
        self.buses.append(bus(bus_id))
        traci.vehicle.changeTarget(str(bus_id), ed_to)
        traci.vehicle.setStop(vehID=str(bus_id), edgeID=ed_to, pos=p.position_from, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)
        o_r = list(traci.vehicle.getRoute(str(bus_id)))            
        self.append_edges(o_r, p.edge_from, p.edge_to, str(bus_id))
        traci.vehicle.setStop(vehID=str(bus_id), edgeID=p.edge_to, pos=p.position_to, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)
        
    def run(self):
        #self.pedestrians = sorted(self.pedestrians, key = lambda x: x.depart)
        # Create a bus for the persons
        '''
        bus_index = 0
        for person in self.pedestrians:
            bus_id = f'bus_{bus_index}'
            bus_index += 1
            try:
                traci.vehicle.add(vehID=bus_id, typeID="BUS_S", routeID="", depart=person.depart + 0.0, departPos=0, departSpeed=0, departLane=0, personCapacity=4)
                traci.vehicle.setRoute(bus_id, [self.bus_depot_start_edge])
               
                traci.vehicle.changeTarget(bus_id, person.edge_from)
                o_r = list(traci.vehicle.getRoute(bus_id))

                traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)              

                self.append_edges(o_r, person.edge_from, person.edge_to, bus_id)

                traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_to, pos=person.position_to, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)

                self.append_edges(o_r, person.edge_to, self.bus_depot_end_edge, bus_id)

            except traci.exceptions.TraCIException as err:
                print("TraCIException: {0}".format(err))
            except:
                print("Unexpected error:", sys.exc_info()[0])
        '''

        #traci.vehicle.subscribe('bus_0', (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION, tc.VAR_POSITION , tc.VAR_NEXT_STOPS ))

        p_id = 0
        step = 0
        n_buses = 0
        while step <= self.simulation_steps:
            for b in self.buses:
                #print(traci.vehicle.getRoute(str(b.id)))
                #print(traci.vehicle.getStops(str(b.id)))
                if bool(traci.vehicle.getStopState(str(b.id))):
                    b.busy = False
                    if len(traci.vehicle.getPersonIDList(str(b.id))) > 0:
                        p_str = traci.vehicle.getPersonIDList(str(b.id))[-1]
                        p_str = p_str[7:]
                        #print("p_str: ", p_str)

                        traci.vehicle.changeTarget(str(b.id), self.pedestrians[int(p_str)].edge_to)
            
            while self.pedestrians[p_id].depart <= step:
                cur_ped = self.pedestrians[p_id]
                best_bus_id = self.find_bus(cur_ped.edge_from)
                if(best_bus_id != -1):
                    traci.vehicle.changeTarget(str(best_bus_id), cur_ped.edge_from)
                    self.buses[best_bus_id].id += 1
                else:
                    self.new_bus(n_buses, cur_ped.edge_from, p_id)
                    n_buses += 1
                p_id += 1
                
            traci.simulationStep()
            if self.sleep_time > 0: 
                sleep(self.sleep_time)

            step += 1
            #print(traci.vehicle.getSubscriptionResults('bus_0'))

        traci.close()
