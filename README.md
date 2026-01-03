# Tiny 16-bit custom RISC CPU architecture
**Disclaimer:** I have absolutely no frickin' idea what I'm doing.

This project aims at desining a custom RISC CPU architecture with the following:
- Hardware division,
- Multi-core design,
- Basic atomic operations (LR, SC, ASWP, AINC, ...),
- Primitive cache system,
- Possible future SIMD instructions.

## Current state
- [x] Basic ALU design
- [x] Register file
- [ ] LSU (Load-Store Unit)
- [ ] PC, CSR, Fetcher & Decoder
- [ ] Interrupt controller between cores?
- [ ] Bus arbiter (Round robin)
- [ ] L2 Cache
- [ ] ACU (Atomic Control Unit)
- [ ] SIMD registers and instructions?