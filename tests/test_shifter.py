import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly, Timer, FallingEdge
import random

@cocotb.test()
async def test_shifter_flow(dut):
    """Test shifter using ReadOnly without causing phase errors"""

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.reset.value = 1
    await Timer(20, unit="ns")
    dut.reset.value = 0
    
    expected_values = [0, 0, 0, 0]

    for i in range(20):
        # 1. Drive data (Phase: Active)
        new_val = random.randint(0, 255)
        dut.data_in.value = new_val
        
        # 2. Wait for the clock to trigger the hardware (Phase: Active -> NBA)
        await RisingEdge(dut.clk)
        
        # 3. Enter ReadOnly to verify (Phase: ReadOnly)
        # Signals are locked here.
        await ReadOnly()

        expected_values.insert(0, new_val)
        expected_values.pop()

        current_state = dut.q_all.value.to_unsigned()

        for reg_index in range(4):
            actual_reg_val = (current_state >> (reg_index * 8)) & 0xFF
            expected_reg_val = expected_values[reg_index]
            assert actual_reg_val == expected_reg_val, \
                f"Reg[{reg_index}] Mismatch! Expected {hex(expected_reg_val)}, got {hex(actual_reg_val)}"

        # 4. EXIT the ReadOnly phase.
        # We wait for the FallingEdge (or just a small timer) to move 
        # the simulation back into an 'Active' phase where writing is allowed.
        await FallingEdge(dut.clk)
        
    dut._log.info("SUCCESS: All cycles verified!")