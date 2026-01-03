`default_nettype none

// This module provides 16 GP registers.
module registers (
    input wire clk,
    input wire reset,

    input wire en_read,
    input wire en_write,

    input wire [3:0] ra_addr,
    input wire [3:0] rb_addr,

    input logic [15:0] data,
    input wire [3:0] rd_addr,

    output logic [15:0] ra,
    output logic [15:0] rb
);
    logic [15:0] registers[15:0];

    always_ff @(posedge clk) begin
        if (reset) begin
            registers[0] <= 8'b0;
            registers[1] <= 8'b0;
            registers[2] <= 8'b0;
            registers[3] <= 8'b0;
            registers[4] <= 8'b0;
            registers[5] <= 8'b0;
            registers[6] <= 8'b0;
            registers[7] <= 8'b0;
            registers[8] <= 8'b0;
            registers[9] <= 8'b0;
            registers[10] <= 8'b0;
            registers[11] <= 8'b0;
            registers[12] <= 8'b0;
            registers[13] <= 8'b0;
            registers[14] <= 8'b0;
            registers[15] <= 8'b0;
        end else begin
            if (en_read) begin
                ra <= registers[ra_addr];
                rb <= registers[rb_addr];
            end

            if (en_write)
                registers[rd_addr] <= data;
        end
    end
endmodule