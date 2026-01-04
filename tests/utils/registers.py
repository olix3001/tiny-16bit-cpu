class Registers:
    def __init__(self, reg_write_en, reg_widx, reg_wdata, initial_values=None):
        self.reg_write_en = reg_write_en
        self.reg_widx = reg_widx
        self.reg_wdata = reg_wdata
        self.storage = {i: 0 for i in range(16)}
        
        if initial_values:
            for idx, val in initial_values.items():
                self.storage[idx] = val

    def tick(self):
        # Defensive check: Only try to convert to int if signals are 0 or 1
        if self.reg_write_en.value.is_resolvable and self.reg_write_en.value == 1:
            if self.reg_widx.value.is_resolvable and self.reg_wdata.value.is_resolvable:
                idx = int(self.reg_widx.value)
                val = int(self.reg_wdata.value)
                self.storage[idx] = val

    def get_val(self, idx):
        """Returns the current value of a register from shadow storage"""
        return self.storage.get(int(idx), 0)

    def set_val(self, idx, val):
        """Forcefully sets a shadow register value (useful for test setup)"""
        self.storage[int(idx)] = val & 0xFFFF