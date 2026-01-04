import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from utils.memory import FlashMemory
from utils.registers import Registers

async def run_lsu_op(dut, regs, flash):
    dut.enable.value = 1
    # Loop while state is not LSU_DONE (2)
    while True:
        # Provide inputs to DUT
        d, v = flash.get_outputs()
        dut.mem_data_in.value = d
        dut.mem_valid.value = v and dut.state.value.to_unsigned() == 1
        
        await RisingEdge(dut.clk)
        
        # Capture outputs FROM DUT
        flash.tick()
        regs.tick()
        
        if int(dut.state.value) == 2:
            break
            
    dut.enable.value = 0
    await RisingEdge(dut.clk)
    regs.tick()

@cocotb.test()
async def test_lsu_all_ops(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    
    # 1. Hardware Reset
    dut.reset.value = 1
    dut.enable.value = 0
    dut.op.value = 0xF
    dut.mem_page.value = 0
    await Timer(20, unit="ns")
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.clk) # Wait one more cycle for signals to stabilize

    # 2. Setup
    regs = Registers(dut.reg_write_en, dut.reg_widx, dut.reg_wdata, {3: 0xAABB})
    flash = FlashMemory(dut.mem_addr, dut.mem_data_out, dut.mem_mask, dut.mem_write)

    # --- SBL ---
    dut._log.info("Testing SBL: Mem[0x1000] = R3[7:0]")
    dut.op.value = 0x5 
    dut.ra_val.value = 0x1000
    dut.rv_val.value = 0xAABB
    await run_lsu_op(dut, regs, flash)
    assert flash.storage.get(0x1000) == 0xBB

    # --- SBU ---
    dut._log.info("Testing SBU: Mem[0x1001] = R3[15:8]")
    dut.op.value = 0x6
    dut.ra_val.value = 0x1001
    dut.rv_val.value = 0xAABB
    await run_lsu_op(dut, regs, flash)
    assert flash.storage.get(0x1001) == 0xAA

    # --- SW ---
    dut._log.info("Testing SW: Mem[0x2000] = 0x1234")
    dut.op.value = 0x4
    dut.ra_val.value = 0x2000
    dut.rv_val.value = 0x1234
    await run_lsu_op(dut, regs, flash)
    assert flash.storage.get(0x2000) == 0x34
    assert flash.storage.get(0x2001) == 0x12

    # --- LW ---
    dut._log.info("Testing LW: R10 <= Mem[0x1000]")
    dut.op.value = 0x0
    dut.ra_val.value = 0x1000
    dut.rv_idx.value = 10
    await run_lsu_op(dut, regs, flash)
    assert regs.get_val(10) == 0xAABB

    # --- LBL/LBU ---
    dut._log.info("Testing LBL/LBU extraction")
    # LBL: R11 gets Mem[0x1000] in low byte
    dut.op.value = 0x1
    dut.ra_val.value = 0x1000
    dut.rv_idx.value = 11
    await run_lsu_op(dut, regs, flash)
    assert regs.get_val(11) == 0x00BB

    # LBU: R12 gets Mem[0x1001] in high byte
    dut.op.value = 0x2
    dut.ra_val.value = 0x1001
    dut.rv_idx.value = 12
    await run_lsu_op(dut, regs, flash)
    assert regs.get_val(12) == 0xAA00

    dut._log.info("All tests passed with X-protection!")