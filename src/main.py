import argparse
import os
import sys
import glob
from netlist_parser import NetlistParser
from component_locator import ComponentLocator
from pinout_generator_module import PinoutGenerator

def main():
    parser = argparse.ArgumentParser(description="KiCad Pinout Generator")
    parser.add_argument("project_path", help="Path to the KiCad project folder")
    parser.add_argument("output_dir", help="Directory to save the generated CSV")
    parser.add_argument("refdes", help="Reference Designator of the component")
    
    args = parser.parse_args()
    
    project_path = args.project_path
    output_dir = args.output_dir
    refdes = args.refdes
    
    # 1. Input Validation
    if not os.path.exists(project_path):
        print(f"Invalid path: '{project_path}'. Please verify the directory contains valid KiCAD netlist files.")
        sys.exit(1)
        
    if not os.path.isdir(project_path):
        print(f"Invalid input: '{project_path}' is not a directory. Specify a valid KiCAD project folder.")
        sys.exit(1)
        
    # Find .net file
    net_files = glob.glob(os.path.join(project_path, "*.net"))
    if not net_files:
        print(f"Invalid path: '{project_path}'. Please verify the directory contains valid KiCAD netlist files.")
        sys.exit(1)
    
    # Use the first found netlist file (or maybe we should ask user if multiple? Requirements imply just checking for presence)
    netlist_file = net_files[0]
    
    # 2. Output Directory Validation
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError:
            print(f"Permission denied: '{output_dir}'. Choose a directory with write permissions or adjust file system settings.")
            sys.exit(1)
    
    if not os.access(output_dir, os.W_OK):
        print(f"Permission denied: '{output_dir}'. Choose a directory with write permissions or adjust file system settings.")
        sys.exit(1)

    try:
        # 3. Parse Netlist
        print(f"Parsing netlist: {netlist_file}")
        net_parser = NetlistParser(netlist_file)
        parsed_data = net_parser.parse()
        project_name = net_parser.get_design_title()
        
        # 4. Locate Component
        print(f"Locating component: {refdes}")
        locator = ComponentLocator(parsed_data)
        component_data = locator.find_component(refdes)
        
        # 5. Generate Pinout
        print(f"Generating pinout for {refdes}...")
        generator = PinoutGenerator(output_dir)
        generator.generate(component_data, project_name)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
