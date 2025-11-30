# KiCad Pinout Generator

## Overview
The KiCad Pinout Generator is a standalone tool designed to extract pinout information from KiCad 9 netlist files (`.net`) and generate a formatted CSV document. It is useful for documentation and verification of component connections.

## Prerequisites
- **Input**: A valid KiCad 9 project directory containing a `.net` netlist file.
- **System**: Windows 10/11 (for the executable) or Python 3.x (for running from source).

## How to Use

### Using the Executable
Run the tool from the command line:
```powershell
pinout_generator.exe <PROJECT_PATH> <OUTPUT_DIR> <REFDES>
```

**Arguments:**
- `<PROJECT_PATH>`: Path to the KiCad project folder containing the `.net` file.
- `<OUTPUT_DIR>`: Directory where the generated CSV file will be saved.
- `<REFDES>`: Reference Designator of the component (e.g., `U1`, `J1`).

**Example:**
```powershell
pinout_generator.exe "C:\Projects\MyBoard" "C:\Docs" "U1"
```

### Running from Source
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the script:
   ```bash
   python src/main.py "C:\Projects\MyBoard" "C:\Docs" "U1"
   ```

## Output
The tool generates a CSV file named `pinout-[PROJECT_NAME]-[REFDES].csv` containing:
- Project and Component Metadata
- Pin Number, Pin Name, and Net Name
- Pins are sorted numerically, then alphanumerically (e.g., 1, 2, A1, AA1).

## Limitations
- **KiCad Version**: Only supports KiCad 9 netlist files.
- **Pin Filtering**: Automatically excludes pins defined as 'Power Input', 'Power Output', or 'Unconnected'.
- **Input**: Requires a generated `.net` file (does not parse `.kicad_sch` or `.kicad_pcb` directly).
