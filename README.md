# Tiny 16-bit custom RISC CPU architecture
**Disclaimer:** I have absolutely no frickin' idea what I'm doing.

This project aims at desining a custom RISC CPU architecture with the following:
- Hardware division,
- Primitive cache system,
- Built-in programmable interrupt controller,
- Possible future SIMD instructions.

## Current state
- [x] Basic ALU design
- [x] Register file
- [ ] LSU (Load-Store Unit)
- [ ] PC, CSR, Fetcher & Decoder
- [ ] Programmable Interrupt controller
- [ ] Some kind of cache
- [ ] Multi-core design???

# ISA
Instructions (16-bit) are divided into 4-bit parts:
```
0000    0000    0000    0000
Type   Opcode   ARG1    ARG2
```
Instruction's "Type" indicated what kind of operation it does. At the moment available types are:
- I-Type : Integer Type (ALU)
- M-Type : Memory Type (LSU)
- B-Type : Branch Type
- CS-Type : Control/Status Type (CSR)

Some features like plic or peripherals are memory mapped, so are accessed using M-Type or CS-Type instructions.

All currently unused instruction types are reserved for the future, and should be
treated as UB.
One exception to that is type `0000` or NOP-Type, that guarantees to do nothing and is a recomended way of introducing 1-cycle delay.

There are different sets of opcodes for each type:
### I-Type (`0001`)
| Opcode | Description [Notes] | Opcode | Description [Notes] |
| --- | --- | ---| --- |
| `0000` | Addition | `1000` | Bitwise OR | 
| `0001` | Subtraction | `1001` | XOR | 
| `0010` | Multiplication | `1010` | NOR | 
| `0011` | Division [4c] | `1011` | Population Count (counts ones) | 
| `0100` | Modulo [4c] | `1100` | Count Leading Zeros | 
| `0101` | Shift Left | `1101` | Count Trailing Zeros | 
| `0110` | Shift Right | `1110` | *TBD* | 
| `0111` | Bitwise AND | `1111` | Compare [13x0 GT EQ LT] | 

### M-Type (`0010`)
| Opcode | Description [Notes] | Opcode | Description [Notes] |
| --- | --- | ---| --- |
| `0000` | Load Word @ (seg<<4+R) | `1000` | *TBD* | 
| `0001` | Store Word @ ... | `1001` | *TBD* | 
| `0010` | Load Byte @ ... | `1010` | *TBD* | 
| `0011` | Store Byte @ ... | `1011` | *TBD* | 
| `0100` | Move Rt <- Rs | `1100` | *TBD* | 
| `0101` | Exchnge Rt <- Rs; Rs <- Rt | `1101` | *TBD* | 
| `0110` | Load Imm high | `1110` | *TBD* | 
| `0111` | Load Imm low | `1111` | *TBD* | 

### B-Type (`0011`)
| Opcode | Description [Notes] | Opcode | Description [Notes] |
| --- | --- | ---| --- |
| `0000` | Unconditional Jump | `1000` | *TBD* | 
| `0001` | Jump gt [Requires CMP] | `1001` | *TBD* | 
| `0010` | Jump eq [Requires CMP] | `1010` | *TBD* | 
| `0011` | Jump lt [Requires CMP] | `1011` | *TBD* | 
| `0100` | *TBD* | `1100` | *TBD* | 
| `0101` | *TBD* | `1101` | *TBD* | 
| `0110` | *TBD* | `1110` | *TBD* | 
| `0111` | *TBD* | `1111` | *TBD* | 

### CS-Type (`0100`)
| Opcode | Description [Notes] | Opcode | Description [Notes] |
| --- | --- | ---| --- |
| `0000` | Read CSR | `1000` | *TBD* | 
| `0001` | Write CSR [NOP for read-only] | `1001` | *TBD* | 
| `0010` | *TBD* | `1010` | *TBD* | 
| `0011` | *TBD* | `1011` | *TBD* | 
| `0100` | *TBD* | `1100` | *TBD* | 
| `0101` | *TBD* | `1101` | *TBD* | 
| `0110` | *TBD* | `1110` | *TBD* | 
| `0111` | *TBD* | `1111` | *TBD* | 
