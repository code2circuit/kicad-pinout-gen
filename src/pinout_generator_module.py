import csv
import os
from datetime import datetime

class PinoutGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def generate(self, component_data, project_name):
        refdes = component_data['refdes']
        # Sanitize project name for filename
        safe_project_name = "".join([c for c in project_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        safe_project_name = safe_project_name.replace(' ', '_')
        
        filename = f"pinout-{safe_project_name}-{refdes}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        # Prepare Metadata
        value = component_data.get('value', 'N/A')
        if not value or value.strip() == "":
            print(f"Warning: Component '{refdes}' has an empty symbol value. Defaulted to 'N/A'.")
            value = 'N/A'
            
        mpn = component_data.get('mpn', 'N/A')
        if not mpn:
             print(f"Warning: Missing symbol value for component '{refdes}'. Defaulted to 'N/A'.") # Re-using the warning message style from requirements for missing value, but for MPN? 
             # Requirements say: "Missing Symbol Value" -> Warning. "Incomplete Part Numbers" -> Trim.
             # If MPN is missing, I'll default to N/A.
             mpn = 'N/A'
        else:
            original_mpn = mpn
            mpn = mpn.strip()
            if mpn != original_mpn:
                print(f"Warning: Part number for '{refdes}' contains trailing/leading spaces. Trimmed to '{mpn}'.")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Prepare Rows
        rows = []
        # Metadata
        rows.append(["Project:", project_name if project_name else "Unknown"])
        rows.append(["Component Refdes:", refdes])
        rows.append(["Symbol Value:", value])
        rows.append(["Manufacturer Part Number:", mpn])
        rows.append(["Generated on:", timestamp])
        rows.append([]) # Blank row
        
        # Header
        rows.append(["Pin Number", "Pin Name", "Net Name"])
        
        # Pin Data
        if not component_data['pins']:
             raise ValueError(f"Component '{refdes}' has no pin data. Excluded from output.")

        for pin in component_data['pins']:
            net_name = pin['net']
            # Strip prefix from net name (everything up to last /)
            # Example: /Sheet/SDC0-D2 -> SDC0-D2
            if '/' in net_name:
                net_name = net_name.split('/')[-1]
            
            rows.append([pin['number'], pin['name'], net_name])

        # Write to CSV
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                writer.writerows(rows)
            print(f"Successfully generated pinout for {refdes} at {filepath}")
        except PermissionError:
             raise PermissionError(f"Permission denied: '{self.output_dir}'. Choose a directory with write permissions or adjust file system settings.")
        except Exception as e:
             raise Exception(f"Error writing to file '{filepath}': {e}")
