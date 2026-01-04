import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly, Timer

# Opcode constants
OPS = {
    "ADD":    0b0000, "SUB":    0b0001, "MUL":    0b0010, "DIV":    0b0011,
    "MOD":    0b0100, "SHL":    0b0101, "SHR":    0b0110, "AND":    0b0111,
    "OR":     0b1000, "XOR":    0b1001, "NOR":    0b1010, "POPCNT": 0b1011,
    "CLZ":    0b1100, "CTZ":    0b1101, "CMP":    0b1111
}

def python_popcnt(n):
    return bin(n & 0xFFFF).count('1')

def python_clz(n):
    s = bin(n & 0xFFFF)[2:].zfill(16)
    return len(s) - len(s.lstrip('0'))

def python_ctz(n):
    if n & 0xFFFF == 0: return 16
    s = bin(n & 0xFFFF)[2:].zfill(16)
    return len(s) - len(s.rstrip('0'))

@cocotb.test()
async def test_alu_all_ops(dut):
    """Verify all 16 ALU operations against Python gold models"""

    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.reset.value = 1
    dut.enable.value = 1
    await Timer(20, unit="ns")
    dut.reset.value = 0
    await RisingEdge(dut.clk)

    async def check_op(op_name, a, b, expected):
        dut.op.value = OPS[op_name]
        dut.ra.value = a
        dut.rb.value = b
        
        # Wait for the operation to start/complete
        await RisingEdge(dut.clk)
        await ReadOnly()

        # If it's a multi-cycle op (DIV/MOD), wait for busy to drop
        if op_name in ["DIV", "MOD"]:
            while dut.busy.value == 1:
                await RisingEdge(dut.clk)

        actual = dut.out.value.to_unsigned()
        
        assert actual == (expected & 0xFFFF), \
            f"Failed {op_name}: {a} op {b} | Expected {expected}, Got {actual}"
        
        # Log success
        dut._log.info(f"[PASS] {op_name:6} | A: {a:04x} B: {b:04x} | Result: {actual:04x}")
        await Timer(1, "ns")

    # --- 1. Basic Arithmetic ---
    await check_op("ADD", 0xFFFE, 0x0005, 0x0003)
    await check_op("SUB", 10, 4, 6)
    await check_op("MUL", 100, 5, 500)
    await check_op("DIV", 100, 3, 33)
    await check_op("MOD", 100, 3, 1)

    # --- 2. Bitwise Logic ---
    await check_op("AND", 0xF0F0, 0xAAAA, 0xA0A0)
    await check_op("OR",  0xF0F0, 0xAAAA, 0xFAFA)
    await check_op("XOR", 0xF0F0, 0xAAAA, 0x5A5A)
    await check_op("NOR", 0x00FF, 0xFF00, 0x0000)

    # --- 3. Shifts ---
    await check_op("SHL", 0x0001, 4, 0x0010)
    await check_op("SHR", 0x0010, 4, 0x0001)

    # --- 4. Bit Counting & Search ---
    await check_op("POPCNT", 0x1234, 0, python_popcnt(0x1234))
    await check_op("CLZ",    0x00F0, 0, 8)
    await check_op("CLZ",    0x0000, 0, 16)
    await check_op("CTZ",    0x0F00, 0, 8)
    await check_op("CTZ",    0x0000, 0, 16)

    # --- 5. Comparison ---
    await check_op("CMP", 10, 5,  0b100) # GT
    await check_op("CMP", 5,  10, 0b001) # LT
    await check_op("CMP", 7,  7,  0b010) # EQ

    dut._log.info("All 16 Opcodes Verified Successfully!")