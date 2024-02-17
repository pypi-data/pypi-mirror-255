import neat
import b2sim.engine as b2
from copy import deepcopy as dc
from bisect import bisect_left

def efficientFrontier(eco_sends):
    '''
    Given a list of eco sends, determine which ones belong to the efficient eco frontier
    
    Parameters:
    eco_sends (List[str]): A list containing names of eco sends for consideration

    Returns:
    (List): A list containing names of non-dominated pure eco sends
    '''

    # First, sort the sends based on cost intensity
    eco_sends.sort(key = lambda send_name: b2.eco_send_info[send_name]['Cost Intensity'])

    # Now determine the indices that correspond to eef sends
    i = 0
    eef = []
    while i < len(eco_sends)-1:
        
        #Test remaining eco sends to determine which ones belong on the EEF
        slope = 0
        index = None
        for j in range(i+1,len(eco_sends)):
            test_num = b2.eco_send_info[eco_sends[j]]['Eco Intensity'] - b2.eco_send_info[eco_sends[i]]['Eco Intensity']
            test_den = b2.eco_send_info[eco_sends[j]]['Cost Intensity'] - b2.eco_send_info[eco_sends[i]]['Cost Intensity']
            test_val = test_num/test_den
            #print("Test value for index (" + str(i) + ", " + str(j) + "): " + str(test_val))
            if test_val > slope:
                slope = test_val
                index = j
                
        # When the correct index is discovered, append it to eef
        if index is not None and index > i:
            eef.append(index)
            i = index
        else:
            #It is possible we may run out of eco sends to add to the frontier, in which case...
            break
        
    return [eco_sends[ind] for ind in eef]

def ecoIntensity(intensity: float, eco_sends):
    '''
    Given a desired eco intensity and a list of non-dominated eco_sends of varying intensity, 
    determine the highest intensity eco send among all currently available that does not exceed the given desired eco intensity.

    The eco intensity of an eco send is defined as the eco awarded divided by the amount of time it takes to send.
    The cost intensity of an eco send is defined as the cost to send divided by the amount of time it takes to send.
    
    Parameters:
    intensity (float): The highest desired rate of eco gain (expressed in terms of eco gained per 6 seconds)
    eco_sends (List[str]): A list of non-dominated eco sends to be considered, sorted in order of increasing cost intensity

    Returns:
    eco_send (str): A string which names an eco send and corresponds to an entry in the eco_send_info dictionary
    '''

    try: 
        bisect_left(eco_sends, intensity, key = lambda send_name: b2.eco_send_info[send_name]['Cost Intensity']) - 1
    except:
        eco_sends[0]


# def eval_genomes(genomes, config):
    
#     # Construct the sample simulation that we will evaluate the simulation over
#     rounds = b2.Rounds(0.1)

#     farms = [
#         b2.initFarm(rounds.getTimeFromRound(7), upgrades = [3,2,0])
#     ]

#     initial_state_game = {
#         'Cash': 3000,
#         'Eco': 800,
#         'Eco Send': b2.ecoSend(send_name = 'Zero'),
#         'Rounds': rounds, #Determines the lengths of the rounds in the game state
#         'Farms': farms,
#         'Game Round': 13
#     }

#     target_time = rounds.getTimeFromRound(21)

#     #Evaluate each genome and assign them a fitness score
#     for genome_id, genome in genomes:
#         genome.fitness = 0.0

#         #Create the neural network to be used
#         net = neat.nn.FeedForwardNetwork.create(genome, config)

#         game_state = b2.GameState(initial_state_game)
#         while game_state.current_time < target_time:
#             # Pass the current game info through the genome, giving it the chance to process and spit out an output
#             # We will use the output to determine what to do next in the simulation
#             # QUESTION: How do I influence the inputs and outputs of the neural network?
#             output = net.activate((game_state.cash, game_state.eco, game_state.loan, farm_income))

#             # TODO: Based on the simulator's actions, determine what eco send to use, what farms to buy if any, and so forth

#             # Finally, run the simulation for some time
#             game_state.fastForward(target_time = min(game_state.current_time + 10, target_time))

#         # We will rate the genome based on how much cash it accrued at the end
#         genome.fitness = game_state.cash

#         for xi, xo in zip(xor_inputs, xor_outputs):
#             output = net.activate(xi)
#             genome.fitness -= (output[0] - xo[0]) ** 2