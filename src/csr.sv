`default_nettype none

typedef enum logic [3:0] {
    // Read-Write
    PC,
    MEM_PAGE,

    // Read-Only
    CORE_ID=8,
    PLIC_PAGE,
    PLIC_ADDR
} csr_id_t;

// This module provides 16 (C)ontrol/(S)tatus (R)egisters.
// First 8 are RW registers, while the next 8 are RO (hardcoded).
module csr #(
    parameter CORE_INDEX=0
) (
    input wire clk,
    input wire reset,

    input wire en_read,
    input wire en_write,

    input logic [15:0] data,
    input csr_id_t id,

    output logic [15:0] value,
    output wire mem_page,
);
    logic [15:0] registers[7:0];

    assign mem_page = registers[MEM_PAGE];

    always_ff @(posedge clk) begin
        if (reset) begin
            registers[PC] <= 16'b0;
            registers[MEM_PAGE] <= 16'b0;
            registers[2] <= 16'b0;
            registers[3] <= 16'b0;
            registers[4] <= 16'b0;
            registers[5] <= 16'b0;
            registers[6] <= 16'b0;
            registers[7] <= 16'b0;
        end else begin
            if (en_read) begin
                if (id[3] == 0) value <= registers[id];
                else case (id[2:0])
                    3'b000: value <= CORE_INDEX;
                    3'b001: value <= 0; // PLIC_PAGE
                    3'b010: value <= 0; // PLIC_ADDR
                    default: value <= 16'b0;
                endcase
            end
            if (en_write && id[3] == 0) registers[id] <= data;
        end
    end
endmodule