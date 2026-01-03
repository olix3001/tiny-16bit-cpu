import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_registers_basic(dut):
    """Test basic write and read functionality"""

    # Start the clock (10ns period -> 100MHz)
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # --- Reset Phase ---
    dut.reset.value = 1
    dut.en_read.value = 0
    dut.en_write.value = 0
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk)

    # --- Write Phase ---
    # Note: Your Verilog defines 'data' as [3:0], but registers as [15:0].
    # This test uses values within the 4-bit limit (0-15).
    test_data = [0xA, 0x5, 0xF, 0x1]
    
    for i in range(len(test_data)):
        dut.en_write.value = 1
        dut.rd_addr.value = i
        dut.data.value = test_data[i]
        await RisingEdge(dut.clk)
    
    dut.en_write.value = 0
    await RisingEdge(dut.clk)

    # --- Read Phase ---
    dut.en_read.value = 1
    
    # Read back Register 0 and Register 1
    dut.ra_addr.value = 0
    dut.rb_addr.value = 1
    await RisingEdge(dut.clk) # Data is latched into 'ra' and 'rb' here
    await Timer(1, unit="ns") # Small delay to let signals settle for checking

    assert dut.ra.value == test_data[0], f"Reg0 failed: expected {test_data[0]}, got {dut.ra.value}"
    assert dut.rb.value == test_data[1], f"Reg1 failed: expected {test_data[1]}, got {dut.rb.value}"

    # Read back Register 2 and Register 3
    dut.ra_addr.value = 2
    dut.rb_addr.value = 3
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert dut.ra.value == test_data[2], f"Reg2 failed: expected {test_data[2]}, got {dut.ra.value}"
    assert dut.rb.value == test_data[3], f"Reg3 failed: expected {test_data[3]}, got {dut.rb.value}"

    dut._log.info("Register Write/Read tests passed!")