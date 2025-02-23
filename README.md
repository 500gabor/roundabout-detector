# Roundabout Detector

A modular program which is designed to
- Read certain sqlite databases
- Read certain binary files
- Process the given data based on the requirements
- Calculate potential roundabouts
- Optionally visualize the input data


## Prerequisites
- Ensure you have Python 3.11 installed.
- Install Dependencies, use pip install -r requirements.txt

## Arguments
- db_path: The path to the database file. **mandatory**
- binary_path: The path to the binary file. **mandatory**
- visualize: Provide to get a folium visualization of the data. **optional**

## Running the Script
### Basic Usage
Navigate to the src directory and execute:

python main.py --db_path [Database Path] --binary_path [Bin file path] --visualize

### Windows Users
If Python is not in your system's **PATH**, use the full path to the Python interpreter, example:

C:\Python311\python.exe main.py --db_path [Database Path] --binary_path [Bin file path] --visualize

### Running the Script using PyCharm

Run the main.py file, providing the arguments in the Run/Debug configurations.
