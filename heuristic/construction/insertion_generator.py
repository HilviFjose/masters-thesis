import numpy as np 

class InsertionGenerator:
    def __init__(self, construction_heuristic, route_plan, patients_df):
        #Heuristikken brukes til å hente ut dataframsene. Altså dataverdiene fra de fortåene
        self.heuristic = construction_heuristic   
        #Ruteplanen eksisterer ikke i utganspunktet. Den har blitt laget også sendt inn 
        self.route_plan = route_plan


        #TODO:Bruke patient df til å lage en liste over aktiviteter som skal inn 
        self.requestActivities = np.empty(0, dtype=object)
        treatment = patients_df["treatment"]
        if isinstance(treatment,str):
            self.treatment = treatment.split(',')
        else: 
            self.treatment = [treatment]
        self.treatments = None 
        self.visits = None 
        self.activites = None 

        #Den har jo en pasient og en mulig objektivverdi. 
        #Du kan ikke sende en ny pasient inn etterpå, fordi noen av parameterne er endret på 
        #Så objektet er låst til pasienten man ser på

    def generate_insertions(self):
        state = True
        #TODO: Her skal en pasient puttes inn i planen. Ma sjekke om det går 
        
        
        #Det er mulig å printe objekter fra denne klassen 
        return self.route_plan, 0
    
    def getTreatments(self): 
        return self.treatment
    

'''
Lurer på: hva er selve insertion objektet? Hvorfor er ikke dette en metode i construksjonen? 
Er det fordi den er så stor, så de har lagt den utenfor? Eller er det en egen enhet

Burde tenke litt over hva slags egenskaper den insertionene skal ha.
Vil vi ha det på en spessiell måte. 

Alternativ til slik de har det. Det generes en inserter for hver pasient som skal inn
Insertern har en egen struktur som tar varer på alle de ulike

Kategorisere hva som er metode og hva som er tilstand: 
Vil ha en metode som legger til en pasient 
Det må igjen ha metode som legger til treatments
Legger til visits 
Må ha tilstand i form av at man vet om pasienten kan legges til, og hva som er nåværende ruteplan

Hvor skal ruteplanen inn, den må være en egen enitet som oppdateres 


#TODO: Finne ut om patterns, treatments som er vnaskeligst å plassere skal først. 
Må lage en liste på det for å bestemme hvem som skal insertes når

'''
'''      
   def generate_insertions(self, route_plan, request, rid):
        possible_insertions = {}  # dict: delta objective --> route plan
        for introduced_vehicle in self.heuristic.introduced_vehicles:
            # generate all possible insertions

            if not route_plan[introduced_vehicle]:
                # it is trivial to add the new request
                temp_route_plan = copy.deepcopy(route_plan)

                temp_route_plan[introduced_vehicle] = self.add_initial_nodes(
                    request=request, introduced_vehicle=introduced_vehicle, rid=rid, vehicle_route=temp_route_plan[introduced_vehicle])

                # calculate change in objective
                new_objective = self.heuristic.new_objective(
                    temp_route_plan, self.heuristic.infeasible_set)
                possible_insertions[new_objective] = temp_route_plan

            else:
                # the vehicle already has other nodes in its route
                # will be set to True if both pickup and dropoff of the request have been added
                feasible_request = False
                activated_checks = False  # will be set to True if there is a test that fails
                temp_route_plan = copy.deepcopy(route_plan)

                vehicle_route = route_plan[introduced_vehicle]

                # check if there are any infeasible matches with current request
                preprocessed_check_activated = self.preprocess_check(
                    rid=rid, vehicle_route=vehicle_route)

                if not preprocessed_check_activated:
                    possible_pickup_nodes = self.generate_possible_nodes(
                        request, vehicle_route, None)

                    s = S_W if request["Wheelchair"] else S_P
                    dropoff_time = request["Requested Pickup Time"] + self.heuristic.travel_time(
                        rid-1, self.heuristic.n + rid-1, True) + 2*timedelta(minutes=s)
                    pickup_time = request["Requested Pickup Time"] + \
                        timedelta(minutes=s)

                    for start_idx in possible_pickup_nodes:
                        temp_route_plan = copy.deepcopy(route_plan)
                        test_vehicle_route = copy.deepcopy(vehicle_route)

                        s_p_node, s_p_time, s_p_d, s_p_p, s_p_w, _ = vehicle_route[start_idx]
                        if start_idx == len(vehicle_route) - 1:
                            # there is no other end node, and we only need to check the travel time from start to the node
                            s_p = s_p_node % int(s_p_node)
                            start_id = int(
                                s_p_node - 0.5 - 1 + self.heuristic.n if s_p else s_p_node - 1)
                            s_p_travel_time = self.heuristic.travel_time(
                                rid-1, start_id, True)

                            if s_p_time + (L_D-s_p_d) + s_p_travel_time <= pickup_time:
                                push_back = s_p_time + s_p_travel_time - pickup_time if pickup_time - \
                                    s_p_time - s_p_travel_time < timedelta(0) else 0

                                # check capacities
                                activated_checks = self.check_capacities(
                                    vehicle_route=temp_route_plan[introduced_vehicle], request=request, rid=rid,
                                    start_id=start_idx + 1, dropoff_id=start_idx + 2,
                                    activated_checks=activated_checks)

                                if not activated_checks:

                                    # update backward to test vehicle route
                                    if push_back:
                                        test_vehicle_route, activated_checks = self.update_check_backward(
                                            vehicle_route=test_vehicle_route, start_idx=start_idx, push_back=push_back, activated_checks=activated_checks, rid=rid, request=request, introduced_vehicle=introduced_vehicle)

                                    # add pickup node to test vehicle route
                                    pickup_id, test_vehicle_route = self.add_node(
                                        vehicle_route=test_vehicle_route, request=request, time=pickup_time, pickup=True, rid=rid, node_idx=start_idx)

                                    # add dropoff node to test vehicle route
                                    dropoff_id, test_vehicle_route = self.add_node(
                                        vehicle_route=test_vehicle_route, request=request, time=dropoff_time, pickup=False, rid=rid, node_idx=start_idx+1)

                                    # check max ride time between nodes on test vehicle route
                                    activated_checks = self.check_max_ride_time(
                                        vehicle_route=test_vehicle_route,
                                        activated_checks=activated_checks, rid=rid, request=request)

                                    # check min ride time between nodes on test vehicle route
                                    activated_checks = self.check_min_ride_time(
                                        vehicle_route=test_vehicle_route,
                                        activated_checks=activated_checks, rid=rid, request=request)

                                    if not activated_checks:
                                        # can update temp route plan
                                        # update backward
                                        if push_back:
                                            temp_route_plan[introduced_vehicle], activated_checks = self.update_check_backward(
                                                vehicle_route=temp_route_plan[introduced_vehicle], start_idx=start_idx,
                                                push_back=push_back, activated_checks=activated_checks, rid=rid,
                                                request=request, introduced_vehicle=introduced_vehicle)

                                        # add pickup node
                                        pickup_id, vehicle_route = self.add_node(
                                            vehicle_route=temp_route_plan[introduced_vehicle], request=request,
                                            time=pickup_time, pickup=True, rid=rid,
                                            node_idx=start_idx)

                                        # add dropoff node
                                        dropoff_id, vehicle_route = self.add_node(
                                            vehicle_route=temp_route_plan[introduced_vehicle], request=request, time=dropoff_time,
                                            pickup=False, rid=rid, node_idx=start_idx + 1)

                                        feasible_request = True

                                        self.check_remove(rid, request)

                                        # calculate change in objective
                                        new_objective = self.heuristic.new_objective(
                                            temp_route_plan, self.heuristic.infeasible_set)
                                        possible_insertions[new_objective] = temp_route_plan
                        else:
                            e_p_node, e_p_time, e_p_d, e_p_p, e_p_w, _ = vehicle_route[start_idx + 1]
                            s_p = s_p_node % int(s_p_node)
                            e_p = e_p_node % int(e_p_node)
                            start_id_p = int(
                                s_p_node - 0.5 - 1 + self.heuristic.n if s_p else s_p_node - 1)
                            end_id_p = int(
                                e_p_node - 0.5 - 1 + self.heuristic.n if e_p else e_p_node - 1)

                            s_p_travel_time = self.heuristic.travel_time(
                                rid - 1, start_id_p, True)
                            p_e_travel_time = self.heuristic.travel_time(
                                rid - 1, end_id_p, True)

                            if s_p_time + (L_D - s_p_d) + s_p_travel_time <= pickup_time and \
                                    pickup_time + p_e_travel_time <= e_p_time + (U_D - e_p_d):
                                push_forward_p = pickup_time + p_e_travel_time - e_p_time if e_p_time - pickup_time - p_e_travel_time < timedelta(
                                    0) else 0
                                push_back_p = s_p_time + s_p_travel_time - pickup_time if pickup_time - s_p_time - s_p_travel_time < timedelta(
                                    0) else 0

                                # update forward
                                if push_forward_p:
                                    test_vehicle_route, activated_checks = self.update_check_forward(
                                        vehicle_route=test_vehicle_route, start_idx=start_idx,
                                        push_forward=push_forward_p, activated_checks=activated_checks, rid=rid,
                                        request=request)

                                # update backward
                                if push_back_p:
                                    test_vehicle_route, activated_checks = self.update_check_backward(
                                        vehicle_route=test_vehicle_route, start_idx=start_idx,
                                        push_back=push_back_p, activated_checks=activated_checks, rid=rid,
                                        request=request, introduced_vehicle=introduced_vehicle)

                                # add pickup node to test vehicle route
                                pickup_id, test_vehicle_route = self.add_node(
                                    vehicle_route=test_vehicle_route, request=request,
                                    time=pickup_time, pickup=True, rid=rid,
                                    node_idx=start_idx)

                                s_p_node, s_p_time, s_p_d, s_p_p, s_p_w, _ = test_vehicle_route[
                                    start_idx]
                                e_p_node, e_p_time, e_p_d, e_p_p, e_p_w, _ = test_vehicle_route[
                                    start_idx + 1]

                                before_depot_test = copy.deepcopy(
                                    test_vehicle_route)
                                before_depot_temp = copy.deepcopy(
                                    temp_route_plan)
                                possible_dropoff_nodes = self.generate_possible_nodes(
                                    request, vehicle_route, dropoff_time)

                                for end_idx in possible_dropoff_nodes:
                                    temp_route_plan = copy.deepcopy(
                                        before_depot_temp)
                                    test_vehicle_route = copy.deepcopy(
                                        before_depot_test)
                                    s_d_node, s_d_time, s_d_d, s_d_p, s_d_w, _ = test_vehicle_route[
                                        end_idx]

                                    if end_idx == len(test_vehicle_route) - 1:
                                        # there is no other end node, and we only need to check the travel time from start to the node
                                        e_d_node = None
                                    else:
                                        e_d_node, e_d_time, e_d_d, e_d_p, e_d_w, _ = test_vehicle_route[
                                            end_idx + 1]

                                    s_d = s_d_node % int(s_d_node)
                                    e_d = e_d_node % int(
                                        e_d_node) if e_d_node else None

                                    start_id_d = int(
                                        s_d_node - 0.5 - 1 + self.heuristic.n if s_d else s_d_node - 1)
                                    if e_d_node:
                                        end_id_d = int(
                                            e_d_node - 0.5 - 1 + self.heuristic.n if e_d else e_d_node - 1)

                                    s_d_travel_time = self.heuristic.travel_time(
                                        rid - 1 + self.heuristic.n, start_id_d, True)
                                    d_e_travel_time = self.heuristic.travel_time(
                                        rid - 1 + self.heuristic.n, end_id_d, True) if e_d_node else None

                                    if s_p_time + (L_D - s_p_d) + s_p_travel_time <= pickup_time and pickup_time + p_e_travel_time <= e_p_time + (U_D - e_p_d) and s_d_time + (
                                            L_D - s_d_d) + s_d_travel_time <= dropoff_time:
                                        push_back_d = s_d_time + s_d_travel_time - dropoff_time if \
                                            dropoff_time - \
                                            s_d_time - s_d_travel_time < timedelta(
                                                0) else 0
                                        if e_d_node:
                                            if dropoff_time + d_e_travel_time <= e_d_time + (
                                                    U_D - e_d_d):
                                                push_forward_d = dropoff_time + d_e_travel_time - e_d_time if e_d_time - \
                                                    dropoff_time - d_e_travel_time < timedelta(
                                                        0) else 0
                                            else:
                                                activated_checks = True
                                                push_forward_d = None

                                        # update forward
                                        if e_d_node:
                                            if push_forward_d:
                                                test_vehicle_route, activated_checks = self.update_check_forward(
                                                    vehicle_route=test_vehicle_route, start_idx=start_idx,
                                                    push_forward=push_forward_d, activated_checks=activated_checks,
                                                    rid=rid,
                                                    request=request)

                                        # update backward
                                        if push_back_d:
                                            test_vehicle_route, activated_checks = self.update_check_backward(
                                                vehicle_route=test_vehicle_route, start_idx=start_idx,
                                                push_back=push_back_d, activated_checks=activated_checks,
                                                rid=rid,
                                                request=request, introduced_vehicle=introduced_vehicle)

                                        # add dropoff node to test vehicle route
                                        dropoff_id, test_vehicle_route = self.add_node(
                                            vehicle_route=test_vehicle_route, request=request,
                                            time=dropoff_time, pickup=False, rid=rid,
                                            node_idx=end_idx)

                                        # check capacities
                                        activated_checks = self.check_capacities(
                                            vehicle_route=test_vehicle_route, request=request,
                                            rid=rid,
                                            start_id=start_idx + 1, dropoff_id=end_idx + 1,
                                            activated_checks=activated_checks)

                                        # check max ride time between nodes
                                        activated_checks = self.check_max_ride_time(
                                            vehicle_route=test_vehicle_route,
                                            activated_checks=activated_checks, rid=rid, request=request)

                                        # check min ride time between nodes on test vehicle route
                                        activated_checks = self.check_min_ride_time(
                                            vehicle_route=test_vehicle_route,
                                            activated_checks=activated_checks, rid=rid, request=request)

                                        if not activated_checks:
                                            # update forward
                                            if push_forward_p:
                                                temp_route_plan[introduced_vehicle], activated_checks = self.update_check_forward(
                                                    vehicle_route=temp_route_plan[introduced_vehicle], start_idx=start_idx,
                                                    push_forward=push_forward_p, activated_checks=activated_checks,
                                                    rid=rid,
                                                    request=request)

                                            # update backward
                                            if push_back_p:
                                                temp_route_plan[introduced_vehicle], activated_checks = self.update_check_backward(
                                                    vehicle_route=temp_route_plan[introduced_vehicle], start_idx=start_idx,
                                                    push_back=push_back_p, activated_checks=activated_checks, rid=rid,
                                                    request=request, introduced_vehicle=introduced_vehicle)

                                            # update forward
                                            if e_d_node:
                                                if push_forward_d:
                                                    temp_route_plan[introduced_vehicle], activated_checks = self.update_check_forward(
                                                        vehicle_route=temp_route_plan[introduced_vehicle], start_idx=start_idx,
                                                        push_forward=push_forward_d,
                                                        activated_checks=activated_checks,
                                                        rid=rid,
                                                        request=request)

                                            # update backward
                                            if push_back_d:
                                                temp_route_plan[introduced_vehicle], activated_checks = self.update_check_backward(
                                                    vehicle_route=temp_route_plan[introduced_vehicle], start_idx=start_idx,
                                                    push_back=push_back_d, activated_checks=activated_checks,
                                                    rid=rid,
                                                    request=request, introduced_vehicle=introduced_vehicle)

                                            # add pickup node
                                            pickup_id, vehicle_route = self.add_node(
                                                vehicle_route=temp_route_plan[introduced_vehicle], request=request,
                                                time=pickup_time, pickup=True, rid=rid,
                                                node_idx=start_idx)

                                            # add dropoff node
                                            dropoff_id, vehicle_route = self.add_node(
                                                vehicle_route=temp_route_plan[introduced_vehicle],
                                                request=request,
                                                time=dropoff_time, pickup=False, rid=rid,
                                                node_idx=end_idx)

                                            feasible_request = True

                                            self.check_remove(
                                                rid, request)

                                            # calculate change in objective
                                            new_objective = self.heuristic.new_objective(
                                                temp_route_plan, self.heuristic.infeasible_set)
                                            possible_insertions[new_objective] = temp_route_plan

                        # update capacity between pickup and dropoff
                        if feasible_request:
                            temp_route_plan[introduced_vehicle] = self.update_capacities(
                                vehicle_route=temp_route_plan[introduced_vehicle], request=request, rid=rid,
                                start_id=pickup_id, dropoff_id=dropoff_id)

        # check if no possible insertions have been made and introduce a new vehicle

        if not len(possible_insertions):
            if self.heuristic.vehicles:
                temp_route_plan = copy.deepcopy(route_plan)
                new_vehicle = self.heuristic.vehicles.pop(0)
                temp_route_plan.append([])
                self.heuristic.introduced_vehicles.add(new_vehicle)
                temp_route_plan[new_vehicle] = self.add_initial_nodes(
                    request=request, introduced_vehicle=new_vehicle, rid=rid, vehicle_route=temp_route_plan[new_vehicle])

                # calculate change in objective
                new_objective = self.heuristic.new_objective(
                    temp_route_plan, self.heuristic.infeasible_set)
                possible_insertions[new_objective] = temp_route_plan

            # if no new vehicles available, append the request in an infeasible set
            else:
                if (rid, request) not in self.heuristic.infeasible_set:
                    self.heuristic.infeasible_set.append((rid, request))

        return possible_insertions[min(possible_insertions.keys())] if len(possible_insertions) else route_plan, min(possible_insertions.keys()) if len(possible_insertions) else timedelta(0)
'''  