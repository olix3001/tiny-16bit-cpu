module shifter (
    input  logic        clk,
    input  logic        reset,
    input  logic [7:0]  data_in,
    output logic [31:0] q_all    // {reg3, reg2, reg1, reg0}
);
    logic [3:0][7:0] regs;

    always_ff @(posedge clk) begin
        if (reset) begin
            regs <= '0;
        end else begin
            regs <= {regs[2:0], data_in};
        end
    end

    assign q_all = regs;

endmodule