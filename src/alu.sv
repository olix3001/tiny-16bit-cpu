`default_nettype none

typedef enum logic [3:0] { 
    ADD, SUB, MUL, DIV,
    MOD, SHL, SHR, AND,
    OR , XOR, NOR, POPCNT, 
    CLZ, CTZ, XXX, CMP 
} alu_op_t;

module alu (
    input wire clk,
    input wire reset,

    input alu_op_t op, // TODO: Add bitwise operators, popcnt, trailing/leading zeros, etc...
    input logic [15:0] ra,
    input logic [15:0] rb,

    output logic [15:0] out,
    output logic busy
);
    wire [16:0] diff = {1'b0, ra} - {1'b0, rb}; // This sub is used for both arithmetic and logic.
    wire diff_borrow = diff[16];
    wire diff_zero = diff[15:0] == 0;

    logic div_start;
    logic div_busy;
    logic [15:0] q_out, r_out;

    divider u_divider (
        .clk      (clk),
        .reset    (reset),
        .start    (div_start),
        .dividend (ra),
        .divisor  (rb),
        .quotient (q_out),
        .remainder(r_out),
        .busy     (div_busy)
    );

    assign div_start = ((op == DIV || op == MOD) && !div_busy);
    assign busy = div_busy;

    logic [15:0] alu_reg;

    assign out = (op == DIV) ? q_out : ((op == MOD) ? r_out : alu_reg);

    integer i;

    always_ff @(posedge clk) begin
        if (reset) alu_reg <= 16'b0;

        case (op)
            ADD: alu_reg <= ra + rb;
            SUB: alu_reg <= diff[15:0];
            MUL: alu_reg <= ra * rb;
            DIV: alu_reg <= q_out;
            MOD: alu_reg <= r_out;
            SHL: alu_reg <= ra << rb;
            SHR: alu_reg <= ra >> rb;
            AND: alu_reg <= ra & rb;
            OR : alu_reg <= ra | rb;
            XOR: alu_reg <= ra ^ rb;
            NOR: alu_reg <= ~(ra | rb);
            POPCNT: begin : pop_logic
                logic [4:0] count_temp;
                count_temp = 5'b0;
                for (i = 0; i < 16; i = i + 1)
                    count_temp = count_temp + ra[i];
                alu_reg <= {11'b0, count_temp};
            end
            CLZ: begin : clz_logic
                logic [15:0] val;
                logic [3:0] count;
                val = ra;
                count = 0;
                
                if (val[15:8] == 8'b0) begin count += 8; val <<= 8; end
                if (val[15:12] == 4'b0) begin count += 4; val <<= 4; end
                if (val[15:14] == 2'b0) begin count += 2; val <<= 2; end
                if (val[15] == 1'b0)    begin count += 1; end
                
                alu_reg <= (ra == 0) ? 16 : {12'b0, count};
            end
            CTZ: begin : ctz_logic
                logic [15:0] v;
                logic [3:0] c;
                
                v = ra;
                c = 0;

                if (v[7:0] == 8'b0) begin c += 8; v >>= 8; end
                if (v[3:0] == 4'b0) begin c += 4; v >>= 4; end
                if (v[1:0] == 2'b0) begin c += 2; v >>= 2; end
                if (v[0] == 1'b0)   begin c += 1; end

                alu_reg <= (ra == 16'b0) ? 16'd16 : {12'b0, c};
            end
            XXX: alu_reg <= alu_reg;
            CMP: alu_reg <= {13'b0, (!diff_borrow & !diff_zero), diff_zero, diff_borrow};
        endcase
    end
endmodule

module divider (
    input logic clk,
    input logic reset,
    input logic start,
    input logic [15:0] dividend,
    input logic [15:0] divisor,
    output logic [15:0] quotient,
    output logic [15:0] remainder,
    output logic busy
);
    logic [4:0] count;
    logic [31:0] temp;

    // The divider is busy if the counter is non-zero
    assign busy = (count != 0);
    assign quotient  = temp[15:0];
    assign remainder = temp[31:16];

    always_ff @(posedge clk) begin
        if (reset) begin
            count <= 0;
            temp  <= 0;
        end 
        else if (start && !busy) begin
            // INITIALIZE: This happens on the first cycle of division
            count <= 16;
            temp  <= {16'b0, dividend};
        end 
        else if (busy) begin
            // STEP: The shift-and-subtract loop
            logic [31:0] shifted_temp;
            shifted_temp = {temp[30:0], 1'b0}; // Shift left by 1
            
            if (shifted_temp[31:16] >= divisor) begin
                // Subtract divisor from upper half AND set the LSB to 1
                temp <= {shifted_temp[31:16] - divisor, shifted_temp[15:0] | 16'b1};
            end else begin
                // Just keep the shifted value
                temp <= shifted_temp;
            end
            count <= count - 1;
        end
    end
endmodule