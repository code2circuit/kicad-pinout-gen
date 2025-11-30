class ComponentLocator:
    def __init__(self, parsed_data):
        self.parsed_data = parsed_data
        # Exclusion list as per requirements (mapped to KiCad internal names)
        # 'Power Input' -> 'power_in'
        # 'Power Output' -> 'power_out'
        # 'Unconnected' -> 'no_connect'
        self.EXCLUDED_PIN_TYPES = ['power_in', 'power_out', 'no_connect']

    def find_component(self, refdes):
        """
        Finds a component by RefDes and returns its details and pins.
        """
        components = self._get_components()
        target_comp = None
        
        # Search for the component
        for comp in components:
            # comp structure: ['comp', ['ref', 'REFDES'], ...]
            curr_ref = self._get_property(comp, 'ref')
            if curr_ref == refdes:
                if target_comp:
                    raise ValueError(f"Duplicate refdes '{refdes}' found. Fix the netlist before proceeding.")
                target_comp = comp
        
        if not target_comp:
             raise ValueError(f"Component '{refdes}' not found in the netlist. Verify the refdes is valid and exists in the project.")

        # Extract basic info
        value = self._get_property(target_comp, 'value')
        footprint = self._get_property(target_comp, 'footprint')
        
        # Extract MPN from fields or properties
        # In KiCad 9, it might be in (property ...) or (fields (field ...))
        mpn = self._find_mpn(target_comp)
        
        # Find pins for this component
        pins = self._find_pins(refdes)
        
        return {
            'refdes': refdes,
            'value': value,
            'mpn': mpn,
            'pins': pins
        }

    def _get_components(self):
        # Navigate to (export (components ...))
        # self.parsed_data is the root list
        for item in self.parsed_data:
            if isinstance(item, list) and item[0] == 'components':
                return [x for x in item[1:] if isinstance(x, list) and x[0] == 'comp']
        return []

    def _get_property(self, comp_node, prop_name):
        for item in comp_node:
            if isinstance(item, list) and len(item) > 1 and item[0] == prop_name:
                return item[1]
        return None

    def _find_mpn(self, comp_node):
        # Check 'property' tags first (KiCad 6+)
        for item in comp_node:
            if isinstance(item, list) and item[0] == 'property':
                # (property (name "Manufacturer Part Number") (value "Test_SD1"))
                name_node = self._get_property(item, 'name')
                if name_node == "Manufacturer Part Number":
                    return self._get_property(item, 'value')
        
        # Check 'fields' -> 'field'
        for item in comp_node:
            if isinstance(item, list) and item[0] == 'fields':
                for field in item[1:]:
                    if isinstance(field, list) and field[0] == 'field':
                         # (field (name "Manufacturer Part Number") "Test_SD1")
                         name_node = self._get_property(field, 'name')
                         if name_node == "Manufacturer Part Number":
                             # The value is the last element
                             return field[-1]
        return None

    def _find_pins(self, refdes):
        """
        Scans all nets to find pins belonging to this RefDes.
        Returns a list of dicts: {'number': '1', 'name': 'PinName', 'net': 'NetName', 'type': 'Type'}
        """
        pins = []
        nets = self._get_nets()
        
        # We need to iterate over all nets and their nodes
        for net in nets:
            # net structure: ['net', ['code', '1'], ['name', 'NetName'], (node ...), (node ...)]
            net_name = self._get_property(net, 'name')
            
            for item in net:
                if isinstance(item, list) and item[0] == 'node':
                    # (node (ref "MICRO_SD1") (pin "3") (pinfunction "CMD/DI") (pintype "input"))
                    node_ref = self._get_property(item, 'ref')
                    if node_ref == refdes:
                        pin_num = self._get_property(item, 'pin')
                        pin_type = self._get_property(item, 'pintype')
                        pin_func = self._get_property(item, 'pinfunction')
                        
                        # Filter excluded types
                        if pin_type in self.EXCLUDED_PIN_TYPES:
                            continue
                            
                        pins.append({
                            'number': pin_num,
                            'name': pin_func if pin_func else "", # Use pinfunction as pin name if available
                            'net': net_name,
                            'type': pin_type
                        })
        
        # Sort pins by number (numeric first, then alphanumeric)
        def sort_key(p):
            import re
            pin_num = p['number']
            
            # Try pure integer
            try:
                return (0, 0, "", int(pin_num))
            except ValueError:
                pass
            
            # Alphanumeric parsing
            # Split into alpha and numeric parts
            # Example: A1 -> A, 1. AA10 -> AA, 10.
            match = re.match(r"([A-Za-z]+)([0-9]*)", pin_num)
            if match:
                alpha_part = match.group(1)
                num_part_str = match.group(2)
                num_part = int(num_part_str) if num_part_str else 0
                
                # Sort by:
                # 1. Flag (1 for alphanumeric)
                # 2. Length of alpha part (A < AA)
                # 3. Alpha part itself (lexicographical)
                # 4. Numeric part
                return (1, len(alpha_part), alpha_part.upper(), num_part)
            
            # Fallback for completely weird pins
            return (2, 0, pin_num, 0)
        
        pins.sort(key=sort_key)
        return pins

    def _get_nets(self):
        # Navigate to (export (nets ...)) or just find all (net ...) elements at root level?
        # In the example, (net ...) are at the root level of (export ...), after (components ...)
        # Wait, the example structure is:
        # (export 
        #   (version "E")
        #   (design ...)
        #   (components ...)
        #   (libparts ...)
        #   (libraries ...)
        #   (nets 
        #      (net ...)
        #      (net ...)
        #   )
        # )
        # OR are (net ...) directly under export?
        # Let's check the example file again.
        # Line 42: (net (code "34") ...
        # It seems `(net ...)` might be inside `(nets ...)` or directly under `(export ...)` depending on version?
        # In KiCad 6+, it's usually inside `(nets ...)`
        # Let's look at the parser output structure conceptually.
        
        # I'll search for 'nets' list first.
        for item in self.parsed_data:
            if isinstance(item, list) and item[0] == 'nets':
                return [x for x in item[1:] if isinstance(x, list) and x[0] == 'net']
        
        # Fallback: check if 'net' items are direct children (unlikely for KiCad 9 but possible in some exports?)
        return [x for x in self.parsed_data if isinstance(x, list) and x[0] == 'net']
