import graphviz

class StateMachineGraph:
    def __init__(self, state_machine, accept_suffix, file_name):
        self.state_machine = state_machine
        self.accept_suffix = accept_suffix
        edited_filename = file_name + '.gv'
        self.rendered_state_machine = graphviz.Digraph('finite_state_machine', filename=edited_filename)
        self.rendered_state_machine.attr(rankdir='LR', size='8,5')

    ### Method for loading the state machine provided to the class,
    ### generating a GV file which describes the state machine
    ### and saving a visually rendered version of the state machine as a PDF file in the root directory of the program
    def load_state_machine(self):
        accept_states = []
        edge_tuples = []

        # Get a list of all non-accept states and accept states
        for state in self.state_machine:
            new_state_name = state

            if state.endswith(self.accept_suffix):
                new_state_name = state.replace(self.accept_suffix, '')
                if new_state_name not in accept_states:
                    accept_states.append(new_state_name)
            
            for input, next_state in self.state_machine[state].items():
                new_next_state_name = next_state
                
                if next_state.endswith(self.accept_suffix):
                    new_next_state_name = next_state.replace(self.accept_suffix, '')
                    if new_next_state_name not in accept_states:
                        accept_states.append(new_next_state_name)
                
                # Get a list of tuples in the form (current_state, input, next_state)
                edge_tuples.append((new_state_name, input, new_next_state_name))
        
        # Generate accept state nodes for visualization of state machine
        self.rendered_state_machine.attr('node', shape='doublecircle')
        for state in accept_states:
            self.rendered_state_machine.node(state)
        
        # Generate edges between all nodes for visualization of state machine
        self.rendered_state_machine.attr('node', shape='circle')
        for state, input, next_state in edge_tuples:
            self.rendered_state_machine.edge(state, next_state, label=input)
        
        self.rendered_state_machine.view()