import numpy as np

# Existing array
original_array = np.array([1, 2, 3])

# Element(s) to insert
new_elements = np.array([4, 5])

# Insert values at index 1
new_array = np.insert(original_array, 1, new_elements)

print(new_array)