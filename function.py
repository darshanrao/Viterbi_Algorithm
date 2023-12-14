def read_state_observation_weights_from_file(filename):
    state_observation_weights = {}
    observation_total_weights = {}  # Track the total weights for each observation

    with open(filename, 'r') as file:
        lines = file.readlines()

        for line in lines[2:]:  # Skip the first two lines (file type and header)
            parts = line.strip().split(' ')
            state = parts[0].strip('"')
            observation = parts[1].strip('"')
            weight = int(parts[2])  # Corrected the missing parenthesis

            # Initialize the state observation weights if not already present
            if observation not in state_observation_weights:
                state_observation_weights[observation] = {}
                observation_total_weights[observation] = 0

            # Accumulate the observation weights for the state
            state_observation_weights[observation][state] = weight
            observation_total_weights[observation] += weight

    # Calculate and set the probability distribution for each observation based on state weights
    for observation, state_weights in state_observation_weights.items():
        total_weight = observation_total_weights[observation]
        for state, weight in state_weights.items():
            probability = weight / total_weight
            state_observation_weights[observation][state] = probability

    return state_observation_weights

# # Example usage:
# filename = "your_file.txt"  # Replace with the actual file path
# result = read_state_observation_weights_from_file(filename)
# print(result)

# Example usage:
filename = "little_prince/test_case_1/state_observation_weights.txt" 
result = read_state_observation_weights_from_file(filename)
print(result)


