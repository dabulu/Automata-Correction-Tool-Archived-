#========================================================
# Importing
from ktails import KTails

#========================================================
# MAIN
if __name__ == '__main__':
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------
    # VARIABLE DESCRIPTION SECTION
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    k_number = 2                                                                    # length k to be used in the algorithm
    
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------
    algorithm_improvement1_setting = 0                                              # Can be 0 (Turn off improvement)
                                                                                    # or 1 (Don't check if a state's previous transitions are of length k - 1)
                                                                                    # or 2 (Check if a state's previous transitions are of length k - 1)
    
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    algorithm_improvement2_setting = 0                                              # Can be 0 (Turn off improvement)
                                                                                    # or 1 (If any of the specified labels precede a state, temporarily set k to k+1)
    
    if algorithm_improvement2_setting == 1:
        specified_labels1 = input("Please enter a transition label for improvement 2 (separate labels by commas if multiple; ex: \"a,b,c\"): ")
    else:
        specified_labels1 = ""
    algorithm_improvement2_tuple = (specified_labels1, algorithm_improvement2_setting)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    algorithm_improvement3_setting = 0                                              # Can be 0 (Turn off improvement)
                                                                                    # or 1 (If any of the specified labels precede a state, temporarily set k to k+1)
    
    if algorithm_improvement3_setting == 1:
        specified_labels2 = input("Please enter a transition label for improvement 3 (separate labels by commas if multiple; ex: \"a,b,c\"): ")
    else:
        specified_labels2 = ""
    algorithm_improvement3_tuple = (specified_labels2, algorithm_improvement3_setting)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------
    # TESTING AND DEMO SECTION
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Test Automaton 1: Sets of 2 Positive and 2 Negative Traces
    automaton1_trace1_pos = ['a', 'b', 'e', 'f']
    automaton1_trace2_pos = ['a', 'b', 'e', 'f', 'e', 'f']
    automaton1_tracelist1_pos = [automaton1_trace1_pos, automaton1_trace2_pos]      # List of positive traces

    automaton1_trace1_neg = ['a', 'b', 'e']
    automaton1_trace2_neg = ['a', 'b', 'e', 'f', 'e']
    automaton1_tracelist1_neg = [automaton1_trace1_neg, automaton1_trace2_neg]      # List of negative traces

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    # Test Automaton 2: Sets of 3 Positive and 3 Negative Traces
    automaton2_trace1_pos = ['g', 'b', 'a']
    automaton2_trace2_pos = ['g', 'b', 'a', 'a', 's']
    automaton2_tracelist1_pos = [automaton2_trace1_pos, automaton2_trace2_pos]      # List of positive traces

    automaton2_trace1_neg = ['g']
    automaton2_trace2_neg = ['g', 'b', 'a', 'a']
    automaton2_tracelist1_neg = [automaton2_trace1_neg, automaton2_trace2_neg]      # List of negative traces

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    # Test Automaton 3: Sets of 2 Positive and Negative Traces
    automaton3_trace1_pos = ['a','b','c','b','d']
    automaton3_trace2_pos = ['a','b','b','d']
    automaton3_tracelist1_pos = [automaton3_trace1_pos, automaton3_trace2_pos]      # List of positive traces

    automaton3_trace1_neg = []
    automaton3_tracelist1_neg = [automaton3_trace1_neg]                             # List of negative traces

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    # Variable to control which automaton to test on (to demonstrate improvements)
    test_automaton_selection = 0                                                    # Demo Test Automaton 1 with Improvement 1
                                                                                    # Demo Test Automaton 2 with Improvement 2
                                                                                    # Demo Test Automaton 3 with Improvement 3

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------

    if test_automaton_selection == 1:
        ktails_algorithm = KTails(automaton1_tracelist1_pos, automaton1_tracelist1_neg, k_number, algorithm_improvement1_setting, algorithm_improvement2_tuple, algorithm_improvement3_tuple, 'automaton1_beforeimprov')
        ktails_algorithm.run_ktails_algorithm()

        algorithm_improvement1_setting = 2
        ktails_algorithm = KTails(automaton1_tracelist1_pos, automaton1_tracelist1_neg, k_number, algorithm_improvement1_setting, algorithm_improvement2_tuple, algorithm_improvement3_tuple, 'automaton1_afterimprov')
        ktails_algorithm.run_ktails_algorithm()
    
    elif test_automaton_selection == 2:
        k_number = 1

        ktails_algorithm = KTails(automaton2_tracelist1_pos, automaton2_tracelist1_neg, k_number, algorithm_improvement1_setting, algorithm_improvement2_tuple, algorithm_improvement3_tuple, 'automaton2_beforeimprov')
        ktails_algorithm.run_ktails_algorithm()

        algorithm_improvement2_setting = 1
        if algorithm_improvement2_setting == 1:
            specified_labels1 = input("Please enter a transition label for improvement 2 (separate labels by commas if multiple; ex: \"a,b,c\"): ")
        else:
            specified_labels1 = ""
        algorithm_improvement2_tuple = (specified_labels1, algorithm_improvement2_setting)

        ktails_algorithm = KTails(automaton2_tracelist1_pos, automaton2_tracelist1_neg, k_number, algorithm_improvement1_setting, algorithm_improvement2_tuple, algorithm_improvement3_tuple, 'automaton2_afterimprov')
        ktails_algorithm.run_ktails_algorithm()
    
    elif test_automaton_selection == 3:
        ktails_algorithm = KTails(automaton3_tracelist1_pos, automaton3_tracelist1_neg, k_number, algorithm_improvement1_setting, algorithm_improvement2_tuple, algorithm_improvement3_tuple, 'automaton3_beforeimprov')
        ktails_algorithm.run_ktails_algorithm()

        algorithm_improvement3_setting = 1
        if algorithm_improvement3_setting == 1:
            specified_labels2 = input("Please enter a transition label for improvement 3 (separate labels by commas if multiple; ex: \"a,b,c\"): ")
        else:
            specified_labels2 = ""
        algorithm_improvement3_tuple = (specified_labels2, algorithm_improvement3_setting)

        ktails_algorithm = KTails(automaton3_tracelist1_pos, automaton3_tracelist1_neg, k_number, algorithm_improvement1_setting, algorithm_improvement2_tuple, algorithm_improvement3_tuple, 'automaton3_afterimprov')
        ktails_algorithm.run_ktails_algorithm()


    # ------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ACTUAL USE SECTION
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Create set of positive and negative traces to use, Example:
    # user_tracelist = [
    #     ['a', 'c', 'g']
    #     ['v', 'c', 'g']
    # ]
    
    user_positive_tracelist = [
        
    ]

    user_negative_tracelist = [
        
    ]

    # Set variables to your preference (see VARIABLE DESCRIPTION SECTION for details on the variables)
    # Set the variable 'user_use' to '1' when wanting to use the program, otherwise set to '0'

    user_use = 0

    if user_use == 1:
        k_number = 2
        algorithm_improvement1_setting = 0

        algorithm_improvement2_setting = 0
        if algorithm_improvement2_setting == 1:
            specified_labels1 = input("Please enter a transition label for improvement 2 (separate labels by commas if multiple; ex: \"a,b,c\"): ")
        else:
            specified_labels1 = ""
        algorithm_improvement2_tuple = (specified_labels1, algorithm_improvement2_setting)
        
        algorithm_improvement3_setting = 0
        if algorithm_improvement3_setting == 1:
            specified_labels2 = input("Please enter a transition label for improvement 3 (separate labels by commas if multiple; ex: \"a,b,c\"): ")
        else:
            specified_labels2 = ""
        algorithm_improvement3_tuple = (specified_labels2, algorithm_improvement3_setting)

        # Parameter descriptions: KTails(list_of_positive_traces, list_of_negative_traces, value_of_k, improvement1_setting, improvement2_setting, improvement3_setting, filename)
        user_ktails_algorithm = KTails(user_positive_tracelist, user_negative_tracelist, k_number, algorithm_improvement1_setting, algorithm_improvement2_tuple, algorithm_improvement3_tuple, 'predicted_automaton')
        user_ktails_algorithm.run_ktails_algorithm()
