from time import sleep
import sys
import traci
import traci.constants as tc

class Simulation:
    def __init__(self, simulation_steps, sleep_time, pedestrians, bus_depot_start_edge, bus_depot_end_edge):
        self.simulation_steps = simulation_steps
        self.sleep_time = sleep_time
        self.pedestrians = pedestrians
        self.bus_depot_start_edge = bus_depot_start_edge
        self.bus_depot_end_edge = bus_depot_end_edge
        

    def append_edges(self, cur_rou, e_fr, e_to, bus_id,change_route):
        add_rou = traci.simulation.findRoute(e_fr, e_to).edges
        cur_rou=list(cur_rou)
        route=[]
        if len(cur_rou) != 0:
                    cur_rou.pop() 
        if not change_route:            
            cur_rou.extend(add_rou)
            routed=cur_rou
        else:
            routed=list(add_rou)
        try:
            traci.vehicle.setRoute(bus_id, routed)

        except:
            print('Annoying junction bug')
            return 1
            #index=traci.vehicle.getRouteIndex(bus_id)
            #e_fr=cur_rou[index+1]
            #add_rou = traci.simulation.findRoute(e_fr, e_to).edges
            #route=add_rou
            #traci.vehicle.setRoute(bus_id, route)
        
    def find_closest_bus(self, bus_list,person,distances):
        x=[]
        for bus in bus_list:
            place=traci.vehicle.getRoadID(bus.id)
            if place!="":
                x.append([self.time2go(person.edge_from,bus.id,place),bus.id])
        if bus_list!=[] :
            distances=sorted(x, key=lambda tup: tup[0])
            return distances
        else:
            return []
            
            
    def spawn_bus(self,person,bus_list,bus_index):
        bus_id = f'bus_{bus_index}'
        cur_rou=[]
        bus=[]
        traci.vehicle.add(vehID=bus_id, typeID="BUS_L", routeID="", depart=person.depart + 0.0, departPos=0, departSpeed=0, departLane=0, personCapacity=4)
        self.append_edges(cur_rou,self.bus_depot_start_edge,person.edge_from, bus_id,False)        
        traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)              
        self.append_edges(traci.vehicle.getRoute(bus_id),person.edge_from,person.edge_to, bus_id,False)        
        traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_to, pos=person.position_to, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)              
        bus=Bus(bus_id,[person.edge_from],[person.edge_to],[person.position_from],[person.position_to],0,True,self.bus_depot_end_edge)
        bus_list.append(bus)
        
    
    def call_closest_bus(self,distances,person,bus_list,):
        #Check find first bus with room and no task
        for i in distances:
            for bus in bus_list:
                if bus.id==i[1]:
                    if  not bus.tasked and bus.passengers<bus.capacity:
                       try:
                        cur_rou=traci.vehicle.getRoute(bus.id)
                        error=self.append_edges(cur_rou,traci.vehicle.getRoadID(bus.id),person.edge_from,bus.id,True)
                        if error:
                            return 0
                        traci.vehicle.setStop(vehID=bus.id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)              
                        self.append_edges(traci.vehicle.getRoute(bus.id),person.edge_from,person.edge_to, bus.id,False)        
                        traci.vehicle.setStop(vehID=bus.id, edgeID=person.edge_to, pos=person.position_to, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)
                        bus.tasked=True
                        bus.edge_from.append(person.edge_from)
                        bus.edge_to.append(person.edge_to)
                        bus.position_from.append(person.position_from)
                        bus.position_to.append(person.position_to)
                        bus.passengers+=1
                        return 1
                       except:
                         return 0
        return 0          
        # Make a bus refusing if he could drop of someone closer.
                
    
    def time2go(self, person,bus,place):
                
                    return traci.simulation.findRoute(place, person).travelTime

               
    def get_new_task(self,bus,bus_list):    
         #Remove reached target

     
             try:
                 index=bus.edge_from.index(traci.vehicle.getRoadID(bus.id))
                 del bus.edge_from[index]
                 del bus.position_from[index]
                 bus.passengers+=1
             except:
                 index=bus.edge_to.index(traci.vehicle.getRoadID(bus.id))
                 del bus.edge_to[index]
                 del bus.position_to[index]
                 bus.passengers-=1
             if bus.edge_to==[]:
                 cur_rou=[];
                 self.append_edges(cur_rou,traci.vehicle.getRoadID(bus.id),self.bus_depot_end_edge, bus.id,False)
             else: #make closest!
                 self.append_edges([],traci.vehicle.getRoadID(bus.id),bus.edge_to[0], bus.id,False)
                 traci.vehicle.setStop(vehID=bus.id, edgeID=bus.edge_to[0], pos=bus.position_to[0], laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)
             bus.tasked=False  
        
    def run(self):
        # Create a bus for the persons
        bus_index = 0

        #traci.vehicle.subscribe('bus_0', (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION, tc.VAR_POSITION , tc.VAR_NEXT_STOPS ))

        step = 0
        
        bus_list=[]
        white_list=[]
        
        while step <= self.simulation_steps:
            traci.simulationStep()
            for i, item in enumerate(white_list):
                if item[1]<step-50:
                    del white_list[i]
            
            for i in bus_list:
                try:
                    traci.vehicle.getRoadID(i.id)
                              
                except: 
                    bus_list.remove(i)
                    break                          
                if traci.vehicle.getStopState(i.id)%2==1:
                    #if i.id not in white_list:
  
                    if not any(i.id in row for row in white_list) :
                        self.get_new_task(i,bus_list)
                        white_list.append([i.id,step])

                    
                            
            increment=50
            if step%increment==0:
                for person in self.pedestrians:#>traci.time:
                    if person.depart>step and person.depart<step+increment:
                        #bus_id = f'bus_{bus_index}'
                        
                        distances=[]
                        distances=self.find_closest_bus(bus_list,person,distances)
                        if distances!=[]:
                            ret=self.call_closest_bus(distances,person,bus_list)
                            if ret==0:
                                self.spawn_bus(person,bus_list,bus_index)
                                bus_index += 1   
                        if distances==[]:
                            self.spawn_bus(person,bus_list,bus_index)
                            bus_index += 1
            #Garbage Collector. Probably not necessary.
                       #Garbage
            if step%(increment*20)==0:
                
                for person in self.pedestrians:
                    if person.depart<step-800 and person.id in traci.person.getIDList():
                        distances=[]
                        distances=self.find_closest_bus(bus_list,person,distances)
                        if distances!=[]:
                            ret=self.call_closest_bus(distances,person,bus_list)
                            if ret==0:
                                self.spawn_bus(person,bus_list,bus_index)
                                bus_index += 1   
                        if distances==[]:
                            self.spawn_bus(person,bus_list,bus_index)
                            bus_index += 1
            
            
            if self.sleep_time > 0: 
                sleep(self.sleep_time)
            step += 1
            #print(traci.vehicle.getSubscriptionResults('bus_0'))

        traci.close()
class Bus:
        # init method or constructor
        def __init__(self, id: str, edge_from: list, edge_to: list, position_from: list, position_to: list,passengers: int, tasked: bool, end_edge: str):
            self.id = id
            self.edge_from = edge_from
            self.edge_to = edge_to
            self.position_from = position_from
            self.position_to = position_to
            self.tasked=tasked
            self.passengers=passengers
            self.home = end_edge
            self.capacity=8