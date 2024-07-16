#========================================================
# Importing
from state_machine_graph import StateMachineGraph

class KTails:
    # Strings for red and blue nodes
    RED_NODE_NAME = "_R|E|D"
    BLUE_NODE_NAME = "_B|L|U|E"
    ACCEPT_SUFFIX = "_A|C|C|E|P|T"
    ACCEPT_RED_SUFFIX = ACCEPT_SUFFIX + RED_NODE_NAME
    ACCEPT_BLUE_SUFFIX = ACCEPT_SUFFIX + BLUE_NODE_NAME

    # Create new KTails object storing the list of traces, the number of traces and the length of the longest trace
    def __init__(self, pos_tracelist, neg_tracelist, ktails, improve1, improve2, improve3, filename):
        self.initialState = 1
        self.pos_tracelist = pos_tracelist
        self.neg_tracelist = neg_tracelist
        self.ktails = ktails
        self.filename = filename

        if ktails == 1:
            self.kheads = ktails
        else:
            self.kheads = ktails - 1
        
        if improve1 == 0:
            self.improvement1_active = False
            self.improvement1_enforce_klength = False
        elif improve1 == 1:
            self.improvement1_active = True
            self.improvement1_enforce_klength = False
        elif improve1 == 2:
            self.improvement1_active = True
            self.improvement1_enforce_klength = True
        
        if improve2[1] == 0:
            self.improvement2_active = False
        elif improve2[1] == 1:
            self.improvement2_active = True

            labels = improve2[0]
            if ',' in labels:
                self.transition_labels = labels.split(",")
            else:
                self.transition_labels = [labels]
        
        if improve3[1] == 0:
            self.improvement3_active = False
        elif improve3[1] == 1:
            self.improvement3_active = True

            labels2 = improve3[0]
            if ',' in labels2:
                self.transition_labels2 = labels2.split(",")
            else:
                self.transition_labels2 = [labels2]
    
    # ------------------------------------------------------------------
    # HELPER FUNCTIONS
    
    ### Return a list of either blue or red nodes
    def list_of_blue_or_red_nodes(self, full_pta, node_colour):
        finalList = []

        for state in full_pta:
            if state.endswith(node_colour):
                finalList.append(str(state))
        
        for state in full_pta:
            for key, value in full_pta[state].items():
                if value.endswith(node_colour) and value not in finalList:
                    finalList.append(str(value))

        return finalList
    
    ### Change all instances of a specified state name to another one
    def propagate_state_name_change(self, full_pta, oldChildName, newChildName):
        # Change main dictionary state names
        local_pta = {newChildName if key == oldChildName else key:value for key, value in full_pta.items()}
        new_pta = local_pta.copy()

        # Change the respective state names in the child dictionaries
        for state in local_pta:
            for key, value in local_pta[state].items():
                if value == oldChildName:
                    new_pta[state][key] = newChildName

        return new_pta
    
    ### Calculate which nodes should become blue nodes
    def label_state_ends(self, full_pta):
        local_pta = full_pta.copy()

        # List of the names of states that have future transitions
        stateNamesList = [a for a in local_pta.keys()]

        # Check whether any state names end in RED
        redNodeExists = [a.endswith(KTails.RED_NODE_NAME) for a in stateNamesList]

        # IF a RED node exists, iterate through and make its children BLUE nodes if not already a RED node
        if True in redNodeExists:
            for state in stateNamesList:
                # IF current state being checked is a RED node, check children
                if state.endswith(KTails.RED_NODE_NAME):
                    # IF a child is not a RED node and not a BLUE node, turn to BLUE
                    for key, value in local_pta[state].items():
                        childName = value

                        if childName.endswith(KTails.RED_NODE_NAME) == False and childName.endswith(KTails.BLUE_NODE_NAME) == False:
                            newChildName = childName + KTails.BLUE_NODE_NAME

                            local_pta = self.propagate_state_name_change(local_pta, childName, newChildName)

        # IF no RED nodes exist, make the initial state a RED node
        elif True not in redNodeExists:
            firstStateName = stateNamesList[0]
            newStateName = firstStateName + KTails.RED_NODE_NAME
            local_pta = self.propagate_state_name_change(local_pta, firstStateName, newStateName)
            # Then re-run algorithm to make the next state blue
            local_pta = self.label_state_ends(local_pta)

        return local_pta
    
    ### Compare the k-head of a red and blue node
    ### Return a positive number if it has matching incoming transitions and zero otherwise
    def compare_kheads(self, blue_node, red_node, state_machine, khead):
        matching_inputs = 0             # Counter to track list of inputs that match
        khead_count = khead - 1         # Count to keep track of how far along a transition path that the method should check
        khead_satisfied = False         # Boolean variable for whether the blue node and red node shared a previous path of length k-1

        inverse_dictionary = dict()                 # Inverse dictionary of a node's previous transitions
        inverse_dictionary[blue_node] = dict()      # Previous transitions of blue node
        inverse_dictionary[red_node] = dict()       # Previous transitions of red node

        # Creating an inverse dictionary for the blue and red node's previous transitions
        for state in state_machine:
            for input, next_state in state_machine[state].items():
                if next_state == blue_node:
                    inverse_dictionary[blue_node][input] = state
                if next_state == red_node:
                    inverse_dictionary[red_node][input] = state
        
        if len(inverse_dictionary[blue_node]) != 0 and len(inverse_dictionary[red_node]) != 0:
            for blue_input, blue_prev_state in inverse_dictionary[blue_node].items():
                for red_input, red_prev_state in inverse_dictionary[red_node].items():
                    if blue_input == red_input and khead_count > 0:
                        # Check the merge score for next possible states
                        next_matches, khead_satisfied_returned = self.compare_kheads(blue_prev_state, red_prev_state, state_machine, khead_count)

                        if khead_satisfied_returned == True:
                            khead_satisfied = True
                        
                        matching_inputs+= (1 + next_matches)
                    
                    elif blue_input == red_input and khead_count <= 0:
                        khead_satisfied = True

                        matching_inputs+= 1

        return matching_inputs, khead_satisfied
    
    ### Compare the k-tail of a red and blue node
    ### Return zero if it cannot be merged or a positive number if it can be merged.
    def compare_ktails(self, blue_node, red_node, state_machine, ktail):
        matching_inputs = 0             # Counter to track list of inputs that match
        candidate_merges = []           # List of additional states to merge if the current blue and red node are to be merged
        ktail_count = ktail - 1         # Count to keep track of how far along a transition path that the method should check
        ktail_satisfied = False         # Boolean variable for whether the blue node and red node shared a path of length k

        if blue_node in state_machine and red_node in state_machine:
            for blue_input, blue_next_state in state_machine[blue_node].items():
                for red_input, red_next_state in state_machine[red_node].items():
                    if blue_input == red_input and ktail_count > 0:
                        # Adding the name of the future states if their leading transitions match
                        candidate_merges.append((red_node, blue_node))

                        # Checking the merge score for the next possible states
                        next_matches, tuples_list, ktail_satisfied_returned = self.compare_ktails(blue_next_state, red_next_state, state_machine, ktail_count)

                        # Adding any recursively found future states that can be merged
                        for red_state, blue_state in tuples_list:
                            if (red_state, blue_state) not in candidate_merges:
                                candidate_merges.append((red_state, blue_state))
                        
                        if ktail_satisfied_returned == True:
                            ktail_satisfied = True

                        matching_inputs+= (1 + next_matches)

                    elif blue_input == red_input and ktail_count <= 0:
                        # Adding the name of the future states if their leading transitions match
                        candidate_merges.append((red_node, blue_node))

                        ktail_satisfied = True

                        matching_inputs+= 1

        return matching_inputs, candidate_merges, ktail_satisfied

    ### Merge a red node and a blue node and return the altered state machine
    def merge_red_and_blue_node(self, blue_node, red_node, state_machine):
        if blue_node in state_machine and red_node in state_machine:
            # Add all the transitions of the blue node to the red node
            for input, new_state in state_machine[blue_node].items():
                state_machine[red_node][input] = new_state
        
            # Remove the blue node and its transitions
            state_machine.pop(blue_node, None)

            merged_red_node_name = self.merged_node_name_creator(blue_node, red_node)

            # Loop through dictionary and change the main red node name to show the merged blue node
            state_machine = {merged_red_node_name if key == red_node else key:value for key, value in state_machine.items()}

            # Loop through dictionary and alter any state transitions leading to the blue node or red node to lead to the merged node
            for state in state_machine:
                for input, next_state in state_machine[state].items():
                    if next_state == blue_node or next_state == red_node:
                        state_machine[state][input] = merged_red_node_name
        
        else:
            red_node_exists = False
            blue_node_exists = False

            # Loop through dictionary and check if the red node and blue node exist
            for state in state_machine:
                if state == red_node:
                    red_node_exists = True
                elif state == blue_node:
                    blue_node_exists = True
                
                for input, next_state in state_machine[state].items():
                    if next_state == red_node:
                        red_node_exists = True
                    elif next_state == blue_node:
                        blue_node_exists = True
            
            if red_node_exists == True and blue_node_exists == True:
                merged_red_node_name = self.merged_node_name_creator(blue_node, red_node)

                if red_node in state_machine:
                    # Loop through dictionary and change the main red node name to show the merged blue node
                    state_machine = {merged_red_node_name if key == red_node else key:value for key, value in state_machine.items()}
                elif blue_node in state_machine:
                    # Loop through dictionary and change the main red node name to show the merged blue node
                    state_machine = {merged_red_node_name if key == blue_node else key:value for key, value in state_machine.items()}

                # Loop through dictionary and alter any state transitions leading to the blue node or red node to lead to the merged node
                for state in state_machine:
                    for input, next_state in state_machine[state].items():
                        if next_state == blue_node or next_state == red_node:
                            state_machine[state][input] = merged_red_node_name

        return state_machine

    ### Creates the name of a merged node
    def merged_node_name_creator(self, blue_node, red_node):
        # Making the merged node name
        original_red_node = ""
        original_blue_node = ""

        red_suffix_exists = False

        if red_node.endswith(KTails.RED_NODE_NAME):
            original_red_node = red_node.replace(KTails.RED_NODE_NAME, '')
            red_suffix_exists = True
        elif red_node.endswith(KTails.BLUE_NODE_NAME):
            original_red_node = red_node.replace(KTails.BLUE_NODE_NAME, '')
        if blue_node.endswith(KTails.BLUE_NODE_NAME):
            original_blue_node = blue_node.replace(KTails.BLUE_NODE_NAME, '')
        elif blue_node.endswith(KTails.RED_NODE_NAME):
            original_blue_node = blue_node.replace(KTails.RED_NODE_NAME, '')
            red_suffix_exists = True
            
            # If both the red and blue node is an accept state, change the merged node name to be an accept state
        if original_red_node.endswith(KTails.ACCEPT_SUFFIX) or original_blue_node.endswith(KTails.ACCEPT_SUFFIX):
                # Remove 'accept' suffix from the red and blue nodes (if it exists)
            if original_red_node.endswith(KTails.ACCEPT_SUFFIX):
                original_red_node = red_node.replace(KTails.ACCEPT_SUFFIX, '')
            if original_blue_node.endswith(KTails.ACCEPT_SUFFIX):
                original_blue_node = blue_node.replace(KTails.ACCEPT_SUFFIX, '')

                # If one of the nodes is a red node, make the merged node a red node, otherwise do not
            if red_suffix_exists:
                if original_red_node == '' and original_blue_node != '':
                    merged_red_node_name = original_blue_node + KTails.ACCEPT_SUFFIX + KTails.RED_NODE_NAME
                elif original_red_node != '' and original_blue_node == '':
                    merged_red_node_name = original_red_node + KTails.ACCEPT_SUFFIX + KTails.RED_NODE_NAME
                else:
                    merged_red_node_name = original_red_node + ', ' + original_blue_node + KTails.ACCEPT_SUFFIX + KTails.RED_NODE_NAME
            else:
                if original_red_node == '' and original_blue_node != '':
                    merged_red_node_name = original_blue_node + KTails.ACCEPT_SUFFIX
                elif original_red_node != '' and original_blue_node == '':
                    merged_red_node_name = original_red_node + KTails.ACCEPT_SUFFIX
                else:
                    merged_red_node_name = original_red_node + ', ' + original_blue_node + KTails.ACCEPT_SUFFIX
        else:
                # If one of the nodes is a red node, make the merged node a red node, otherwise do not
            if red_suffix_exists:
                if original_red_node == '' and original_blue_node != '':
                    merged_red_node_name = original_blue_node + KTails.RED_NODE_NAME
                elif original_red_node != '' and original_blue_node == '':
                    merged_red_node_name = original_red_node + KTails.RED_NODE_NAME
                else:
                    merged_red_node_name = original_red_node + ', ' + original_blue_node + KTails.RED_NODE_NAME
            else:
                if original_red_node == '' and original_blue_node != '':
                    merged_red_node_name = original_blue_node
                elif original_red_node != '' and original_blue_node == '':
                    merged_red_node_name = original_red_node
                else:
                    merged_red_node_name = original_red_node + ', ' + original_blue_node
        return merged_red_node_name
    
    ### Removes all red node suffixes on state names in the given state machine
    def state_name_cleanup(self, state_machine):
        names_cleaned = []

        for state_name in state_machine:
            # Clean the state names in the child dictionaries
            for input, next_state_name in state_machine[state_name].items():
                if KTails.RED_NODE_NAME in next_state_name:
                    new_next_state_name = next_state_name.replace(KTails.RED_NODE_NAME, '')
                if KTails.BLUE_NODE_NAME in new_next_state_name:
                    new_next_state_name = new_next_state_name.replace(KTails.BLUE_NODE_NAME, '')

                state_machine[state_name][input] = new_next_state_name

            # Add cleaned main dictionary state names to a list
            if KTails.RED_NODE_NAME in state_name:
                new_state_name = state_name.replace(KTails.RED_NODE_NAME, '')
            if KTails.BLUE_NODE_NAME in new_state_name:
                new_state_name = new_state_name.replace(KTails.BLUE_NODE_NAME, '')
            names_cleaned.append((state_name, new_state_name))
        
        # Clean main dictionary state names
        for old_name, cleaned_name in names_cleaned:
            new_state_machine = {cleaned_name if key == old_name else key:value for key, value in state_machine.items()}

            state_machine = new_state_machine.copy()
        
        return new_state_machine

    ### Find the merge pair with the highest score with some conditions
    def max_score(self, red_states_checked_and_satisfied, red_states_future_states):
        if len(red_states_checked_and_satisfied) != 0:
            # Calculate max score in dictionary
            best_red_node = max(red_states_checked_and_satisfied, key=red_states_checked_and_satisfied.get)
            best_red_node_score = red_states_checked_and_satisfied[best_red_node]

            for red_state, blue_state in red_states_future_states[best_red_node]:
                if red_state.endswith(KTails.RED_NODE_NAME):
                    new_red_state = red_state.replace(KTails.RED_NODE_NAME, '')
                elif red_state.endswith(KTails.BLUE_NODE_NAME):
                    new_red_state = red_state.replace(KTails.BLUE_NODE_NAME, '')
                else:
                    new_red_state = red_state
                
                if blue_state.endswith(KTails.RED_NODE_NAME):
                    new_blue_state = blue_state.replace(KTails.RED_NODE_NAME, '')
                elif blue_state.endswith(KTails.BLUE_NODE_NAME):
                    new_blue_state = blue_state.replace(KTails.BLUE_NODE_NAME, '')
                else:
                    new_blue_state = blue_state

                if not new_red_state.endswith(KTails.ACCEPT_SUFFIX) and new_blue_state.endswith(KTails.ACCEPT_SUFFIX):
                    # Remove the red node from the dictionaries if it asks to merge an accept state with a non-accept state
                    red_states_checked_and_satisfied.pop(best_red_node, None)

                    best_red_node, best_red_node_score, red_states_checked_and_satisfied = self.max_score(red_states_checked_and_satisfied, red_states_future_states)
                    break
                elif new_red_state.endswith(KTails.ACCEPT_SUFFIX) and not new_blue_state.endswith(KTails.ACCEPT_SUFFIX):
                    # Remove the red node from the dictionaries if it asks to merge an accept state with a non-accept state
                    red_states_checked_and_satisfied.pop(best_red_node, None)

                    best_red_node, best_red_node_score, red_states_checked_and_satisfied = self.max_score(red_states_checked_and_satisfied, red_states_future_states)
                    break

            if best_red_node_score == 0:
                best_red_node = 0

        elif len(red_states_checked_and_satisfied) == 0:
            best_red_node = 0
            best_red_node_score = 0
        
        return best_red_node, best_red_node_score, red_states_checked_and_satisfied

    ### Constructing PTA from list of positive traces and negative traces
    def construct_pta(self):
        full_pta = dict()
        tracelist = self.pos_tracelist
        negative_tracelist = self.neg_tracelist
        
        positive_pta = self.utility_construct_pta(full_pta, tracelist, False)
        pos_and_neg_pta = self.utility_construct_pta(positive_pta, negative_tracelist, True)
        
        return pos_and_neg_pta

    ### Utility method for constructing a PTA
    def utility_construct_pta(self, full_pta, tracelist, neg_tracelist_bool):
        localStateNum = self.initialState

        # Loop through every trace
        for trace in tracelist:
            localStateNum = 1
            trace_length = len(trace) - 1

            # Loop through every input in trace string
            for index, input in enumerate(trace):
                if index == trace_length and neg_tracelist_bool == True:
                    if str(localStateNum) + KTails.ACCEPT_SUFFIX in full_pta:
                        # If transition already exists for the current state, move on
                        # Else, add a new one and update the state counter
                        if input in full_pta[str(localStateNum) + KTails.ACCEPT_SUFFIX]:
                            original_state_name = full_pta[str(localStateNum) + KTails.ACCEPT_SUFFIX][input]
                            
                            if original_state_name.endswith(KTails.ACCEPT_SUFFIX):
                                new_state_name = original_state_name.replace(KTails.ACCEPT_SUFFIX, '')
                            else:
                                new_state_name = original_state_name
                            
                            full_pta[str(localStateNum) + KTails.ACCEPT_SUFFIX][input] = new_state_name

                            full_pta = {new_state_name if key == original_state_name else key:value for key, value in full_pta.items()}

                            localStateNum+=1
                        else:
                            full_pta[str(localStateNum) + KTails.ACCEPT_SUFFIX][input] = str(self.initialState+1)
                            localStateNum = self.initialState + 1
                            self.initialState+=1

                    elif str(localStateNum) in full_pta:
                        # If transition already exists for the current state, move on
                        # Else, add a new one and update the state counter
                        if input in full_pta[str(localStateNum)]:
                            original_state_name = full_pta[str(localStateNum)][input]

                            if original_state_name.endswith(KTails.ACCEPT_SUFFIX):
                                new_state_name = original_state_name.replace(KTails.ACCEPT_SUFFIX, '')
                            else:
                                new_state_name = original_state_name
                            
                            full_pta[str(localStateNum)][input] = new_state_name

                            full_pta = {new_state_name if key == original_state_name else key:value for key, value in full_pta.items()}

                            localStateNum+=1
                        else:
                            full_pta[str(localStateNum)][input] = str(self.initialState+1)
                            localStateNum = self.initialState + 1
                            self.initialState+=1
                    
                    else:
                        full_pta[str(localStateNum) + KTails.ACCEPT_SUFFIX] = {input:str(localStateNum+1)}
                        localStateNum+=1
                        self.initialState+=1
                else:
                    if str(localStateNum) + KTails.ACCEPT_SUFFIX in full_pta:
                        # If transition already exists for the current state, move on
                        # Else, add a new one and update the state counter
                        if input in full_pta[str(localStateNum) + KTails.ACCEPT_SUFFIX]:
                            localStateNum+=1
                        else:
                            full_pta[str(localStateNum) + KTails.ACCEPT_SUFFIX][input] = str(self.initialState+1) + KTails.ACCEPT_SUFFIX
                            localStateNum = self.initialState + 1
                            self.initialState+=1

                    elif str(localStateNum) in full_pta:
                        # If transition already exists for the current state, move on
                        # Else, add a new one and update the state counter
                        if input in full_pta[str(localStateNum)]:
                            localStateNum+=1
                        else:
                            full_pta[str(localStateNum)][input] = str(self.initialState+1) + KTails.ACCEPT_SUFFIX
                            localStateNum = self.initialState + 1
                            self.initialState+=1
                    else:
                        full_pta[str(localStateNum) + KTails.ACCEPT_SUFFIX] = {input:str(localStateNum+1) + KTails.ACCEPT_SUFFIX}
                        localStateNum+=1
                        self.initialState+=1
        
        return full_pta
    
    ### Method that checks that if a certain input comes before a state, it will be merged with k + 1
    def merge_with_plus_k(self, blue_state, state_machine):
        returned_k = self.ktails
        inverse_dictionary = dict()                 # Inverse dictionary of the blue node's previous transitions

        # Creating an inverse dictionary for the blue node's previous transitions
        for state in state_machine:
            for input, next_state in state_machine[state].items():
                if next_state == blue_state:
                    inverse_dictionary[input] = state
        
        # If any of the labels specified for this improvement is a transition name to the blue state,
        # return k+1
        if len(inverse_dictionary) != 0:
            for label in self.transition_labels:
                if label in inverse_dictionary:
                    returned_k = self.ktails + 1
                    break
        
        return returned_k
    
    ### Method that checks that if a certain input comes before a state, a self loop should not be formed
    def no_self_loop(self, red_state, blue_state, red_states_checked_and_satisfied, red_states_future_states, state_machine):
        self_loop_will_exist = False
        label_precedes = False

        inverse_dictionary = dict()                 # Inverse dictionary of the blue node's previous transitions

        # Creating an inverse dictionary for the blue node's previous transitions
        for state in state_machine:
            for input, next_state in state_machine[state].items():
                if next_state == blue_state:
                    inverse_dictionary[input] = state
        
        # If any of the labels specified for this improvement is a transition name to the blue state,
        # return a red node and red node score for a merge depending on whether a self loop will be formed afterwards or not
        if len(inverse_dictionary) != 0:
            for label in self.transition_labels2:
                if label in inverse_dictionary:
                    label_precedes = True
                    break

        if label_precedes == True:
            if red_state in state_machine:
                for input, next_state in state_machine[red_state].items():
                    if next_state == blue_state:
                        self_loop_will_exist = True
            elif blue_state in state_machine:
                for input, next_state in state_machine[blue_state].items():
                    if next_state == red_state:
                        self_loop_will_exist = True
            
            if self_loop_will_exist == True:
                if len(red_states_checked_and_satisfied) > 0:
                    red_states_checked_and_satisfied.pop(red_state)

                    best_red_node, best_red_node_score, red_states_checked_and_satisfied = self.max_score(red_states_checked_and_satisfied, red_states_future_states)

                    if best_red_node_score != 0:
                        best_red_node, best_red_node_score = self.no_self_loop(best_red_node, blue_state, red_states_checked_and_satisfied, state_machine)
                else:
                    best_red_node = 0
                    best_red_node_score = 0
            else:
                if len(red_states_checked_and_satisfied) != 0:
                    best_red_node = red_state
                    best_red_node_score = red_states_checked_and_satisfied[best_red_node]
                else:
                    best_red_node = 0
                    best_red_node_score = 0
        
        else:
            if len(red_states_checked_and_satisfied) != 0:
                best_red_node = red_state
                best_red_node_score = red_states_checked_and_satisfied[best_red_node]
            else:
                best_red_node = 0
                best_red_node_score = 0

        return best_red_node, best_red_node_score
    
    ### Method for evaluating how accurate the predicted state machine is compared to the true state machine
    def evaluation_score(self, predicted_fsm, true_fsm):
        max_score = 0
        current_score = 0

        # Calculate max score based on true state machine
        for state in true_fsm:
            for input in true_fsm[state]:
                max_score+=1
        
        # If a transition for a particular state in the predicted state machine matches one in the true state machine,
        # increase the current score
        for state in predicted_fsm:
            if state in true_fsm:
                for input in predicted_fsm[state]:
                    if input in true_fsm[state]:
                        current_score+=1
        
        percentage = (current_score / max_score) * 100

        return percentage
    
    # Run the blue_fringe algorithm on the instance's pta
    def run_bluefringe_algorithm(self):
        state_machine = self.construct_pta()
        red_states_checked_score = dict()
        red_states_future_states = dict()
        red_states_ktail_satisfied = dict()
        red_states_checked_and_satisfied = dict()

        # Turn the initial state to a red node and the successive state to a blue node
        state_machine = self.label_state_ends(state_machine)

        redNodesList = self.list_of_blue_or_red_nodes(state_machine, KTails.RED_NODE_NAME)
        blueNodesList = self.list_of_blue_or_red_nodes(state_machine, KTails.BLUE_NODE_NAME)
        
        # Repeat until no blue nodes left
        while len(blueNodesList) != 0:
            blueNode = blueNodesList[0]
            k_number = self.ktails

            # IMPROVEMENT 2: IF ANY SPECIFIED TRANSITION NAMES PRECEDE THE EVALUATED BLUE NODE, MERGE WITH K+1
            if self.improvement2_active == True:
                k_number = self.merge_with_plus_k(blueNode, state_machine)

            for redNode in redNodesList:
                merge_score, candidate_merges, ktail_satisfied = self.compare_ktails(blueNode, redNode, state_machine, k_number)

                # Store the red node name and future states to be merged in a dictionary
                red_states_future_states[redNode] = candidate_merges

                # IMPROVEMENT 1: KHEAD, PREVIOUS TRANSITIONS TAKEN INTO ACCOUNT
                if self.improvement1_active == True:
                    # Score is affected by the previous transitions of a node in question
                    khead_merge_score, khead_satisfied = self.compare_kheads(blueNode, redNode, state_machine, self.kheads)

                    # Store the red node name and score in a dictionary
                    red_states_checked_score[redNode] = merge_score + khead_merge_score

                    # Store whether or not the red node has similar past and future paths of length k with the checked blue node
                    if self.improvement1_enforce_klength == True:
                        if ktail_satisfied == True and khead_satisfied == True:
                            red_states_ktail_satisfied[redNode] = True
                        else:
                            red_states_ktail_satisfied[redNode] = False
                    else:
                        # Store whether or not the red node has a similar future path of length k with the checked blue node
                        red_states_ktail_satisfied[redNode] = ktail_satisfied
                
                else:
                    # Store the red node name and score in a dictionary
                    red_states_checked_score[redNode] = merge_score

                    # Store whether or not the red node has a similar future path of length k with the checked blue node
                    red_states_ktail_satisfied[redNode] = ktail_satisfied
            
            # If a red node has a similar path of length k with the checked blue node, add it to a dictionary of red nodes to consider
            for red_node, truth_val in red_states_ktail_satisfied.items():
                if truth_val == True:
                    red_states_checked_and_satisfied[red_node] = red_states_checked_score[red_node]
            
            best_red_node, best_red_node_score, red_states_checked_and_satisfied = self.max_score(red_states_checked_and_satisfied, red_states_future_states)

            # IMPROVEMENT 3: IF ANY SPECIFIED TRANSITION NAMES PRECEDE THE EVALUATED BLUE NODE, ENSURE NO TRANSITIONS LOOP ON THE STATE CREATED AFTER A MERGE
            if self.improvement3_active == True:
                best_red_node, best_red_node_score = self.no_self_loop(best_red_node, blueNode, red_states_checked_and_satisfied, red_states_future_states, state_machine)

            # If max score is > 0, merge the respective red and blue node
            if best_red_node_score > 0:
                states_to_merge = red_states_future_states[best_red_node]

                for red_state, blue_state in states_to_merge:
                    # Merge any appropriate future nodes
                    state_machine = self.merge_red_and_blue_node(blue_state, red_state, state_machine)

                # Calculate new blue nodes
                state_machine = self.label_state_ends(state_machine)
            else:
                # Turn the blue node into a red node
                temp_node_name = blueNode.replace(KTails.BLUE_NODE_NAME, '')
                blue_to_red_node_name = temp_node_name + KTails.RED_NODE_NAME

                state_machine = self.propagate_state_name_change(state_machine, blueNode, blue_to_red_node_name)

                # Calculate new blue nodes
                state_machine = self.label_state_ends(state_machine)

            # Re-calculate set of red and blue nodes
            redNodesList = []
            blueNodesList = []
            redNodesList = self.list_of_blue_or_red_nodes(state_machine, KTails.RED_NODE_NAME)
            blueNodesList = self.list_of_blue_or_red_nodes(state_machine, KTails.BLUE_NODE_NAME)

            # Clear the dictionary of red states checked
            red_states_checked_score = dict()

            # Clear the dictionary of checked future states of the red states
            red_states_future_states = dict()

            # Clear the dictionary of truth values of red nodes that have a similar path of length k with the checked blue node
            red_states_ktail_satisfied = dict()

            # Clear the dictionary of red node scores that have a similar path of length k with the checked blue node
            red_states_checked_and_satisfied = dict()
            
        # Remove all red node suffixes from the state names in the state machine
        state_machine = self.state_name_cleanup(state_machine)

        return state_machine

    ### Main method for running the KTails algorithm, graphically visualizing the outputted state machine and saving it as a PDF file
    ### in the root directory of the program
    def run_ktails_algorithm(self):
        state_machine = self.run_bluefringe_algorithm()

        state_machine_graph = StateMachineGraph(state_machine, KTails.ACCEPT_SUFFIX, self.filename)
        state_machine_graph.load_state_machine()
    
    # ------------------------------------------------------------------