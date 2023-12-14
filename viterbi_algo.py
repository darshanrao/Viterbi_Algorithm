class TemporalEnvironment:
    def __init__(self):
        self.state_weights = {}  # Dictionary to store state weights
        self.state_observation_weights = {}  # Dictionary to store state-observation weights
        self.state_action_state_weights = {}  # Dictionary to store state-action-state weights
        self.observation_actions = []  # List to store observation-action pairs
        self.resulting_sequence=[]
        self.state_action_state_default_weight=0
        self.state_observation_default_weight=0
        self.unique_states = set()
        self.unique_observations = set()
        self.unique_actions=set()

    def read_state_weights(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            self.state_weights = {}
            
            total_weight = 0  # Initialize total weight to zero

            for line in lines[2:]:  # Skip the first two lines (file type and header)
                parts = line.strip().split(' ')
                state = parts[0].strip('"')
                weight = int(parts[1])

                self.unique_states.add(state)

                self.state_weights[state] = weight
                total_weight += weight  # Accumulate the total weight

            # Calculate and set the probability distribution for each state
            for state, weight in self.state_weights.items():
                probability = weight / total_weight
                self.state_weights[state] = probability


    def read_unique_observations(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            _1,_2,_3,self.state_observation_default_weight=lines[1].strip().split(' ')
            for line in lines[2:]:  # Skip the first two lines (file type and header)
                parts = line.strip().split(' ')
                observation = parts[1].strip('"')
                self.unique_observations.add(observation)

    def read_unique_actions(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            _1,_2,_3,self.state_action_state_default_weight=lines[1].strip().split(' ')
            for line in lines[2:]:  # Skip the first two lines (file type and header)
                parts = line.strip().split(' ')
                action = parts[1].strip('"')
                self.unique_actions.add(action)

    def create_default_weight_dictionaries(self):
        
        for state in self.unique_states:

            self.state_observation_weights[state] = {}
            for observation in self.unique_observations:
                self.state_observation_weights[state][observation]=int(self.state_observation_default_weight)
                
            self.state_action_state_weights[state]={}
            for action in self.unique_actions:
                self.state_action_state_weights[state][action]={}
                for next_state in self.unique_states:
                     self.state_action_state_weights[state][action][next_state]=int(self.state_action_state_default_weight)
                

                
    def read_state_observation_weights(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            state_total_weights = {}  # Track the total weights for each state
            
            for line in lines[2:]:  # Skip the first two lines (file type and header)
                parts = line.strip().split(' ')
                state = parts[0].strip('"')
                observation = parts[1].strip('"')
                weight = int(parts[2])  # Corrected the missing parenthesis
                state_total_weights[state] = 0

                # Accumulate the observation weights for the state
                self.state_observation_weights[state][observation] = weight

                # print(self.state_observation_weights)
            
            for state, observation_weights in self.state_observation_weights.items():
                for observation, weight in observation_weights.items():
                    state_total_weights[state] += self.state_observation_weights[state][observation]
            # print(state_total_weights)
            # Calculate and set the probability distribution for each state based on observation weights
            for state, observation_weights in self.state_observation_weights.items():
                total_weight = state_total_weights[state]
                for observation, weight in observation_weights.items():
                    probability = weight / total_weight
                    self.state_observation_weights[state][observation] = probability

    def read_state_action_state_weights(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            
            state_action_total_weights = {}  # Track the total weights for each state and action

            
            for line in lines[2:]:  # Skip the first two lines (file type and header)
                parts = line.strip().split(' ')
                state = parts[0].strip('"')
                action = parts[1].strip('"')
                next_state = parts[2].strip('"')
                weight = int(parts[3])
                self.state_action_state_weights[state][action][next_state] = weight
            
            for state, action_weights in self.state_action_state_weights.items():
                state_action_total_weights[state] = {}
                for action, next_state_weights in action_weights.items():
                    state_action_total_weights[state][action] = 0
                    for next_state, weight in next_state_weights.items():
                        state_action_total_weights[state][action]+=self.state_action_state_weights[state][action][next_state]

 
            for state, action_weights in self.state_action_state_weights.items():
                for action, next_state_weights in action_weights.items():
                    total_weight = state_action_total_weights[state][action]
                    for next_state, weight in next_state_weights.items():
                        probability = weight / total_weight
                        self.state_action_state_weights[state][action][next_state] = probability

    def read_observation_actions(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            self.observation_actions = []
            for line in lines[2:]:
                parts = line.strip().split(' ')
                if len(parts) == 1:
                    observation = parts[0].strip('"')
                    self.observation_actions.append([observation, None])
                elif len(parts) == 2:
                    observation = parts[0].strip('"')
                    action = parts[1].strip('"')
                    self.observation_actions.append([observation, action])
                else:
                    # Handle invalid input format or other error conditions
                    print(f"Invalid input format: {line}")



# Create an instance of the TemporalEnvironment class
temporal_env = TemporalEnvironment()

# Use the methods to read input data
# filepath="little_prince/test_case_3/"

filepath="speech_recognition/test_case_4/"

temporal_env.read_state_weights(filepath+'state_weights.txt')

temporal_env.read_unique_observations(filepath+'state_observation_weights.txt')
temporal_env.read_unique_actions(filepath+'state_action_state_weights.txt')


temporal_env.create_default_weight_dictionaries()
temporal_env.read_state_observation_weights(filepath+'state_observation_weights.txt')
temporal_env.read_state_action_state_weights(filepath+'state_action_state_weights.txt')
temporal_env.read_observation_actions(filepath+'observation_actions.txt')







def viterbi(obs_actions, initial_prob, trans_prob, emit_prob):
    states = list(initial_prob.keys())
    V = [{}]

    obs, action = obs_actions[0]
    for state in states:
        V[0][state] = {
            "prob": initial_prob[state] * emit_prob[state].get(obs, 1) ,
            "prev": None
        }

    for t in range(1, len(obs_actions)):
        V.append({})
        obs, action = obs_actions[t][0],obs_actions[t-1][1]
        for state in states:
            if action is not None:
                max_trans_prob = max(V[t - 1][prev_state]["prob"] * trans_prob[prev_state][action].get(state, 1) for prev_state in states)
                max_prob = max_trans_prob * emit_prob[state].get(obs, 1)
                V[t][state] = {"prob": max_prob, "prev": max((prev_state for prev_state in states if V[t - 1][prev_state]["prob"] * trans_prob[prev_state][action].get(state, 1) == max_trans_prob), key=lambda x: V[t - 1][x]["prob"])}
    optimal_path = []
    max_prob = max(value["prob"] for value in V[-1].values())
    previous_state = None

    for state, data in V[-1].items():
        if data["prob"] == max_prob:
            optimal_path.append(state)
            previous_state = state
            break

    for t in range(len(V) - 2, -1, -1):
        optimal_path.insert(0, V[t + 1][previous_state]["prev"])
        previous_state = V[t + 1][previous_state]["prev"]
    # print(V)
    print(optimal_path)
    return optimal_path

seq=viterbi(temporal_env.observation_actions,temporal_env.state_weights,temporal_env.state_action_state_weights,temporal_env.state_observation_weights)


def create_states_file(sequence):
        string_list=sequence
        size = len(string_list)
        filename="states.txt"
        with open(filename, 'w') as file:
            file.write("states\n")
            file.write(f"{size}\n")
            for item in string_list:
                file.write(f'"{item}"\n')

        print(f'File "{filename}" created successfully.')

create_states_file(sequence=seq)