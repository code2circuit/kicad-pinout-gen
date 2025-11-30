import re

class NetlistParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.content = ""
        self.parsed_data = None

    def load_file(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Missing netlist file '{self.file_path}'. Verify the project directory contains all required files.")
        except Exception as e:
            raise Exception(f"Error parsing '{self.file_path}': {type(e).__name__}.")

    def validate_version(self):
        # Look for (tool "Eeschema 9.x.x")
        match = re.search(r'\(tool\s+"Eeschema\s+(9\.[^"]+)"\)', self.content)
        if not match:
            # Check if it's a valid KiCad file at all but wrong version
            if '(tool "Eeschema' in self.content:
                 raise ValueError("Unsupported KiCAD version. Only KiCAD 9 files are accepted.")
            else:
                 raise ValueError(f"File '{self.file_path}' is not a valid KiCAD netlist. Supported formats: KiCAD 9")
        return match.group(1)

    def parse(self):
        self.load_file()
        self.validate_version()
        self.parsed_data = self._parse_sexp(self.content)
        return self.parsed_data

    def _parse_sexp(self, sexp_string):
        """
        A simple recursive descent parser for S-expressions.
        Returns a nested list structure.
        """
        sexp_string = sexp_string.strip()
        if not sexp_string:
            return []

        # Tokenize: add spaces around parens and split
        # We need to be careful with strings that might contain parens
        # This simple regex approach works for standard KiCad netlists where strings are quoted
        
        tokens = []
        token = ""
        in_string = False
        escape = False
        
        for char in sexp_string:
            if in_string:
                if escape:
                    token += char
                    escape = False
                elif char == '\\':
                    token += char
                    escape = True
                elif char == '"':
                    token += char
                    in_string = False
                    tokens.append(token)
                    token = ""
                else:
                    token += char
            else:
                if char == '(':
                    if token.strip():
                        tokens.append(token.strip())
                    tokens.append('(')
                    token = ""
                elif char == ')':
                    if token.strip():
                        tokens.append(token.strip())
                    tokens.append(')')
                    token = ""
                elif char.isspace():
                    if token.strip():
                        tokens.append(token.strip())
                    token = ""
                elif char == '"':
                    token += char
                    in_string = True
                else:
                    token += char
        
        if token.strip():
            tokens.append(token.strip())

        # Build hierarchy
        stack = [[]]
        for token in tokens:
            if token == '(':
                sub_list = []
                stack[-1].append(sub_list)
                stack.append(sub_list)
            elif token == ')':
                if len(stack) > 1:
                    stack.pop()
                else:
                    raise ValueError(f"Corrupted file '{self.file_path}'. Cannot parse.")
            else:
                # Clean quotes from strings if needed, or keep them
                # KiCad strings are usually quoted. We keep them as is for now or strip?
                # The requirements say "Enclose the data ... in quotes", but that's for CSV output.
                # For internal representation, stripping outer quotes is usually better.
                if token.startswith('"') and token.endswith('"'):
                    token = token[1:-1]
                stack[-1].append(token)
        
        if len(stack) != 1:
             raise ValueError(f"Corrupted file '{self.file_path}'. Cannot parse.")
             
        return stack[0][0] if stack[0] else []

    def get_design_title(self):
        """Extracts project title from (design (sheet (title_block (title ...))))"""
        # Navigate the parsed data structure
        # (export (version "E") (design ... ) ... )
        if not self.parsed_data:
            return None
        
        # Helper to find node by name
        def find_node(data, name):
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, list) and len(item) > 0 and item[0] == name:
                        return item
            return None

        design = find_node(self.parsed_data, 'design')
        if design:
            sheet = find_node(design, 'sheet') # Note: KiCad 9 might have multiple sheets or different structure?
            # In the example: (design ... (sheet (number "1") ... (title_block (title "A64..."))))
            # Actually, `sheet` might be a list of sheets. But usually title block is in the first one or root?
            # Let's look at the example netlist structure again.
            # (design ... (sheet (number "1") ... (title_block (title "A64-OLinuXino") ... ) ... ))
            
            if sheet:
                title_block = find_node(sheet, 'title_block')
                if title_block:
                    title_node = find_node(title_block, 'title')
                    if title_node and len(title_node) > 1:
                        return title_node[1]
        return None

