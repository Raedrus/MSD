
file_path = '/home/msd/smartdustbin/waste_counts.txt'
def update_values( values):
    with open(file_path, 'w') as file:
        for category, count in values.items():
            file.write(f"{category}:{count}\n")
            
def read_values():
    values = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                category, count = line.strip().split(':')
                values[category] = int(count)
    except FileNotFoundError:
        # If the file does not exist, initialize with zero counts
        values = {'battery': 0, 'e_device': 0, 'metal': 0, 'general_waste': 0}
    return values
    

def reset():
	# Initialize values or read existing values
	waste_counts = read_values()
	print("Previous counts:", waste_counts)

	# Update the counts (example values)
	waste_counts['battery'] =0
	waste_counts['e_device'] = 0
	waste_counts['metal'] =0
	waste_counts['general_waste'] =0

	# Write updated counts back to the file
	update_values( waste_counts)

	# Read back the updated values
	updated_counts = read_values()
	print("Updated counts:", updated_counts)
	
	
def test():
	# Initialize values or read existing values
	waste_counts = read_values()
	print("Initial counts:", waste_counts)

	# Update the counts (example values)
	waste_counts['battery'] += 1
	waste_counts['e_device'] += 2
	waste_counts['metal'] += 3
	waste_counts['general_waste'] += 4

	# Write updated counts back to the file
	update_values( waste_counts)

	# Read back the updated values
	updated_counts = read_values()
	print("Updated counts:", updated_counts)



waste_counts = read_values()
print (waste_counts)



#main()
