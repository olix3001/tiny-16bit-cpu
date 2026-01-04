import cocotb
from cocotb.triggers import Timer, FallingEdge, RisingEdge, ReadOnly, ReadWrite
from cocotb.clock import Clock

async def reset_dut(dut):
    dut.reset.value = 1
    dut.en_read.value = 0
    dut.en_write.value = 0
    dut.data.value = 0
    dut.id.value = 0
    await Timer(10, unit="ns")
    await FallingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk)

@cocotb.test()
async def test_csr_rw_and_ro(dut):
    """Test Read/Write capabilities and Read-Only hardcoded values"""
    
    # Start the clock
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    async def test_read(reg, expected):
        dut._log.info("Testing register read: " + str(reg))
        dut.id.value = reg
        dut.en_read.value = 1
        await RisingEdge(dut.clk)
        dut.en_read.value = 0
        await Timer(1, unit="ns") # Small delay to let signals settle for checking
        assert dut.value.value.to_unsigned() == expected, f"{reg} Read failed. Expected {hex(expected)} got {hex(dut.value.value.to_unsigned())}"
    
    async def test_write(reg, value):
        dut._log.info("Writing register: " + str(reg))
        dut.id.value = reg
        dut.data.value = value
        dut.en_write.value = 1
        await RisingEdge(dut.clk)
        dut.en_write.value = 0

    # PC Register (RW)
    await test_read(0, 0)
    await test_write(0, 0xABCD)
    await test_read(0, 0xABCD)

    # CORE_ID Register (RO)
    await test_read(8, 0)
    await test_write(8, 0xABCD)
    await test_read(8, 0)

    # TODO: Add more tests