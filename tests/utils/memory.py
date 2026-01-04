class FlashMemory:
    def __init__(self, addr_sig, data_out_sig, mask_sig, write_sig, flash_data=None):
        self.addr_sig = addr_sig
        self.data_out_sig = data_out_sig
        self.mask_sig = mask_sig
        self.write_sig = write_sig
        self.storage = flash_data if flash_data is not None else {}

    def get_outputs(self):
        # If address is 'X', return 0 and valid=0
        if not self.addr_sig.value.is_resolvable:
            return (0, 0)
        
        addr = int(self.addr_sig.value)
        low = self.storage.get(addr, 0x00)
        high = self.storage.get(addr + 1, 0x00)
        return ((high << 8) | low, 1)

    def tick(self):
        # Safety check: if write_en is X/Z or not 1, exit
        if not self.write_sig.value.is_resolvable: return
        if int(self.write_sig.value) != 1: return
        
        # Safety check: if address or data contain X, we can't write to storage
        if not self.addr_sig.value.is_resolvable: return
        if not self.data_out_sig.value.is_resolvable: return

        addr = int(self.addr_sig.value)
        mask = int(self.mask_sig.value) if self.mask_sig.value.is_resolvable else 0
        data = int(self.data_out_sig.value)

        if mask == 0b11: # SW
            self.storage[addr] = data & 0xFF
            self.storage[addr + 1] = (data >> 8) & 0xFF
        elif mask == 0b10: # SBL/SBU (targets high lane in your Verilog)
            self.storage[addr] = (data >> 8) & 0xFF