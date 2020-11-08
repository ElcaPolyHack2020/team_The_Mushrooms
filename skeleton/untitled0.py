# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 19:26:43 2020

@author: gian-
"""

        for person in self.pedestrians:
            bus_id = f'bus_{bus_index}'
            bus_index += 1
            ###
            try:
                traci.vehicle.add(vehID=bus_id, typeID="BUS_S", routeID="", depart=person.depart + 0.0, departPos=0, departSpeed=0, departLane=0, personCapacity=4)
                
                o_r=[];
                self.append_edges(o_r, self.bus_depot_start_edge, person.edge_from, bus_id)
                 
                traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)              

                self.append_edges(o_r, person.edge_from, person.edge_to, bus_id)

                traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_to, pos=person.position_to, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)

                self.append_edges(o_r, person.edge_to, self.bus_depot_end_edge, bus_id)

            except traci.exceptions.TraCIException as err:
                print("TraCIException: {0}".format(err))
            except:
                print("Unexpected error:", sys.exc_info()[0])
###