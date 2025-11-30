# KiCAD Pinout Generator #

The KiCAD Pinout Generator is a Python project intended to create a pinout document for a given component (refdes) in a KiCAD project. (A pinout document is a table of pin numbers, pin names, and the net connected to each pin.)

# 0. Prerequisites #

- The input folder will have a netlist (.net) file.

- This file is in KiCAD 9 format.

# 1. Project Requirements #

## 1.1 Input Validation ##

### 1.1.1 KiCAD Project Folder Path ###

- Validation Criteria:

    - Verify the path exists and is accessible.

    - Check for the presence of a KiCAD netlist file (.net).

    - Check that the netlist is in KiCAD 9 format. The file must contain a line specifying the KiCad version that starts with 9 (e.g., ```tool "Eeschema 9.0.3"```).

- Error Handling:

    - If the path is invalid or contains no valid files, raise an error:

            "Invalid path: '[PATH]'. Please verify the directory contains valid KiCAD netlist files."

    - If the path is a file instead of a directory, raise:

            "Invalid input: '[PATH]' is not a directory. Specify a valid KiCAD project folder."

    - If the version does not start with 9, the tool must exit with an error.

            "Unsupported KiCAD version. Only KiCAD 9 files are accepted."

### 1.1.2 Output Directory Path ###

- Validation Criteria:

     - Ensure the path is valid and writable. If the path does not exist, the tool must attempt to create the directory.

- Error Handling:

    - If the directory is not writable or creation fails, raise:

        "Permission denied: '[PATH]'. Choose a directory with write permissions or adjust file system settings."

    - If the path is invalid or cannot be created, raise an error:

        "Invalid path: '[PATH]'. Please verify that the directory exists and the path is valid."

### 1.1.3 Reference Designator (Refdes) ###

Input: The Refdes will be passed as a mandatory command-line argument to the executable.

- Validation Criteria:

    - Confirm the refdes exists in the netlist.

    - Validate that the refdes is unique across the project.

- Error Handling:

    - If the refdes is invalid or missing:

            "Refdes '[REFDES]' not found in the netlist. Verify the component exists and the refdes is correctly formatted."

    - If multiple components share the same refdes:

            "Duplicate refdes '[REFDES]' found. Fix the netlist before proceeding."
        - Action: Terminate execution immediately.

### 1.1.4 Logging Configuration ###

- Requirement:

    - Implement a logging module to handle user notifications (Errors and Warnings).

    - Complexity: Low (Standard Python logging library).

    - Functionality:

        - Errors: Fatal issues that stop execution (e.g., File not found, Duplicate RefDes).

        - Warnings: Recoverable issues (e.g., Trimming whitespace, Defaulting values).

        - Output logs to console.

# 2. Modules #

## 2.1 Netlist Parser Module ##

### 2.1.2 Error Handling ###

- File Reading Errors:

    - Catch exceptions during file loading (e.g., corrupted files, unsupported formats).

        Raise an error:

            "Error parsing '[FILE]': [EXCEPTION TYPE]."

## 2.2 Component Locator Module ##

### 2.2.1 Functionality ###

- Component Search:

    - Locate components by refdes using parsed netlist data.

    - Apply exclusion rules for specific pin types.

- Configuration: 
    - The exclusion list must be defined as a constant list within the code 
    - Must include the following pin types: 'Power Input', 'Power Output', and 'Unconnected'.

### 2.2.2 Error Handling ###

- Component Not Found:

    Raise an error:

        "Component '[REFDES]' not found in the netlist. Verify the refdes is valid and exists in the project."

- Multiple Refdes Matches:

    Raise an error and terminate:

        "Duplicate refdes '[REFDES]' found. Fix the netlist before proceeding."

## 2.3 Pinout Generation Module ##

### 2.3.1 Functionality ###

- Data Extraction:

    - Extract pin data including: Pin number, name, type (input/output/ etc), and associated net.

    - Component symbol value and part number (trimming leading and trailing whitespaces).

    - Pin Sorting:
        - Numeric pins: Ascending order (e.g., 1, 2, 10).
        - Alphanumeric pins: Sorted by length, then alphabetically, then numerically (e.g., A0, A1... Z9... AA0...).

- Formatting:

    - Save output as CSV.
    
    - Filename convention: `pinout-[PROJECTNAME]-[REFDES].csv`

    - Enclose the data of each cell in the CSV in quotes ("").

- Data Handling: 
    - Handle missing data by logging a Warning (do not terminate).

    - CSV Structure:
        Metadata Headers (Rows 1-5):

    ```text
    Project: [PROJECT]
    Component Refdes: [REFDES]
    Symbol Value: [VALUE]
    Manufacturer Part Number: [MPN]
    Generated on: [DATE_TODAY] [PRESENT_TIME]
    ```

    - Blank Separator Row (Row 6): Add a single empty row to separate metadata from the table.

    - Column Headers (Row 7):

            "Pin Number","Pin Name","Net Name"

### 2.3.2 Edge Case Handling ###

- Empty Symbol Values:

    Log a Warning and proceed:

        "Component '[REFDES]' has an empty symbol value. Defaulted to 'N/A'."

- Missing Symbol Value:

    Log a Warning and proceed:

        "Missing symbol value for component '[REFDES]'. Defaulted to 'N/A'."

- Incomplete Part Numbers:

    Trim whitespace, log a Warning, and proceed:

        "Part number for '[REFDES]' contains trailing/leading spaces. Trimmed to '[TRIMMED]'."

# 3. Error Handling and Edge Cases #

## 3.1 File Parsing Errors##

- Corrupted Files:

    Raise an error:

        "Corrupted file '[FILE]'. Cannot parse."

- Unsupported Formats:

    Raise an error:

        "File '[FILE]' is not a valid KiCAD netlist. Supported formats: KiCAD 9"

## 3.2 Missing netlist file ##

- Raise an error:

        "Missing netlist file '[FILE]'. Verify the project directory contains all required files."

## 3.3 Multiple Components with Same Refdes ##

- Action:

    Raise an error and terminate:

        "Duplicate refdes '[REFDES]' found. Fix the netlist before proceeding."

## 3.4 Other Edge Cases ##

- Empty Pin Data:

    Raise an error:

        "Component '[REFDES]' has no pin data. Excluded from output."

# 4. Packaging Requirements #

- Standalone Executable:

    - The application must be packagable into a single .exe file for Windows.

    - Tool: Use PyInstaller or similar.

    - Dependencies: All Python dependencies must be bundled.

    - Portability: The EXE should run on standard Windows 10/11 systems without requiring a separate Python installation.

# 5. Glossary #

- Refdes: Reference designator (e.g., "U1", "R1") used to identify components in a netlist.

- CSV: Comma-separated values file format for tabular data.

- EXE: Executable file format.