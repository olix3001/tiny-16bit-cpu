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
            registers[0] <= 16'b0;
            registers[1] <= 16'b0;
            registers[2] <= 16'b0;
            registers[3] <= 16'b0;
            registers[4] <= 16'b0;
            registers[5] <= 16'b0;
            registers[6] <= 16'b0;
            registers[7] <= 16'b0;
            registers[8] <= 16'b0;
            registers[9] <= 16'b0;
            registers[10] <= 16'b0;
            registers[11] <= 16'b0;
            registers[12] <= 16'b0;
            registers[13] <= 16'b0;
            registers[14] <= 16'b0;
            registers[15] <= 16'b0;
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