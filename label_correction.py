import os

# Root directory of the dataset
dataset_root_dir = r'C:\Users\dingy\OneDrive\Desktop\MSD_YOLO'


# Directory containing label files for training images
label_train_dir = os.path.join(dataset_root_dir, 'data/label_cor_test')

# Valid class range based on your dataset configuration
valid_class_ids = [0, 1, 2]


def correct_and_sort_labels(label_dir):
    # Iterate over all label files in the directory
    for filename in os.listdir(label_dir):
        if filename.endswith('.txt'):
            filepath = os.path.join(label_dir, filename)

            with open(filepath, 'r') as file:
                lines = file.readlines()

            new_lines = []
            for line in lines:
                parts = line.strip().split()
                class_id = int(parts[0])

                # Check if class_id is within the valid range
                if class_id not in valid_class_ids:
                    print(f'Invalid class_id {class_id} in file {filename}, correcting to 0.')
                    class_id = 0  # Change to a valid class id as needed

                new_line = f"{class_id} {' '.join(parts[1:])}\n"
                new_lines.append(new_line)

            # Sort lines by class_id
            new_lines.sort(key=lambda x: int(x.split()[0]))

            # Write corrected and sorted lines back to the file
            with open(filepath, 'w') as file:
                file.writelines(new_lines)


# Correct and sort labels in the train directory
correct_and_sort_labels(label_train_dir)

print('Label correction and sorting completed.')
