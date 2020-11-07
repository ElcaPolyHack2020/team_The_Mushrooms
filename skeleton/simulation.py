from time import sleep
import sys
import traci
import traci.constants as tc

class Simulation:
    def __init__(self, simulation_steps, sleep_time, pedestrians, bus_depot_start_edge, bus_depot_end_edge):
        self.simulation_steps = simulation_steps
        self.sleep_time = sleep_time
        self.pedestrians = sorted(pedestrians,key=lambda x:pedestrians.depart)
        self.list_edge_from = [x.edge_from for x in pedestrians]
        self.bus_depot_start_edge = bus_depot_start_edge
        self.bus_depot_end_edge = bus_depot_end_edge

    def append_edges(self, cur_rou, e_fr, e_to, bus_id):
        add_rou = traci.simulation.findRoute(e_fr, e_to).edges
        if len(cur_rou) != 0:
            cur_rou.pop()
        cur_rou.extend(add_rou)
        traci.vehicle.setRoute(bus_id, cur_rou)
        
    def run(self):
        # Create a bus for the persons
        bus_index = 0
        for person in self.pedestrians:
            bus_id = f'bus_{bus_index}'
            bus_index += 1

            try:
                traci.vehicle.add(vehID=bus_id, typeID="BUS_S", routeID="", depart=person.depart + 0.0, departPos=0, departSpeed=0, departLane=0, personCapacity=4)
                route=[]
                route.append(self.bus_depot_start_edge)
                #traci.vehicle.setRoute(bus_id, [self.bus_depot_start_edge])
                first_route= traci.simulation.findRoute(self.bus_depot_start_edge, person.edge_from).edges
                for edge in first_route:
                    try:
                        index_pedestrian=self.list_edge_from.index(edge)
                        if(traci.simulation.getCurrentTime()>=pedestrians[index_pedestrian].depart):
                            stops.append(pedestrians[index_pedestrian].edge_from)
                    except:
                        continue
                        
                
                #traci.vehicle.changeTarget(bus_id, self.bus_depot_start_edge)
                
                #traci.vehicle.changeTarget(bus_id, person.edge_from)
                #traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)
                

                #traci.vehicle.setRoute(bus_id, [self.bus_depot_start_edge, person.edge_from, person.edge_to])
                #traci.vehicle.changeTarget(bus_id, person.edge_from)
                #traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)
                traci.vehicle.changeTarget(bus_id, person.edge_from)
                o_r = list(traci.vehicle.getRoute(bus_id))
                #print(o_r)
                #sleep(3)
                traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)

                # create fake vehicle
                self.append_edges(o_r, person.edge_from, person.edge_to, bus_id)

                traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_to, pos=person.position_to, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)

                self.append_edges(o_r, person.edge_to, self.bus_depot_end_edge, bus_id)

            except traci.exceptions.TraCIException as err:
                print("TraCIException: {0}".format(err))
            except:
                print("Unexpected error:", sys.exc_info()[0])

        traci.vehicle.subscribe('bus_0', (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION, tc.VAR_POSITION , tc.VAR_NEXT_STOPS ))

        step = 0
        while step <= self.simulation_steps:
            traci.simulationStep()
            if self.sleep_time > 0:
                sleep(self.sleep_time)
            step += 1
            #print(traci.vehicle.getSubscriptionResults('bus_0'))

        traci.close()
