`default_nettype none

typedef enum logic [3:0] {
    // 0XXX: Memory Operations
    LSU_LW  = 4'h0, // Load Word
    LSU_LBL = 4'h1, // Load Byte Lower
    LSU_LBU = 4'h2, // Load Byte Upper
    LSU_SW  = 4'h4, // Store Word
    LSU_SBL = 4'h5, // Store Byte Lower
    LSU_SBU = 4'h6, // Store Byte Upper
    
    // 1XXX: Register-only Operations
    LSU_MOV  = 4'h8, // rv <= ra
    LSU_XCHG = 4'h9  // ra <=> rv
} lsu_op_t;

typedef enum logic [1:0] {
    LSU_IDLE,
    LSU_BUSY,
    LSU_DONE
} lsu_state_t;

module lsu (
    input wire clk,
    input wire reset,
    input wire enable,
    
    input lsu_op_t op,
    input wire [15:0] mem_page,
    input wire [15:0] ra_val,     // Current value of register RA
    input wire [15:0] rv_val,     // Current value of register RV
    input wire [3:0] ra_idx,     // Address of register RA
    input wire [3:0] rv_idx,     // Address of register RV
    
    input wire [15:0] mem_data_in,
    input wire mem_valid,
    
    output logic [31:0] mem_addr,
    output logic [15:0] mem_data_out,
    output logic [1:0] mem_mask,
    output logic mem_write,
    
    output logic [15:0] reg_wdata, // Data to write to reg file
    output logic [3:0] reg_widx,  // Which register to write to
    output logic reg_write_en,   // Write enable to reg file
    output lsu_state_t state
);
    // Internal buffer for XCHG and other possible future instructions.
    logic [15:0] temp_val;

    always_ff @(posedge clk) begin
        if (reset) begin
            state <= LSU_IDLE;
            reg_write_en <= 1'b0;
            mem_write <= 1'b0;
            mem_addr <= 32'b0;
        end else if (enable) begin
            case (state)
                LSU_IDLE: begin
                    reg_write_en <= 1'b0;
                    if (op[3] == 1) begin
                        // 1XXX: Internal Register Ops
                        if (op == LSU_MOV) begin
                            reg_wdata <= ra_val;
                            reg_widx <= rv_idx;
                            reg_write_en <= 1'b1;
                            state <= LSU_DONE;
                        end else if (op == LSU_XCHG) begin
                            // Start XCHG: Step 1, write RA to RV
                            reg_wdata <= ra_val;
                            reg_widx <= rv_idx;
                            reg_write_en <= 1'b1;
                            temp_val <= rv_val; // Save RV to write to RA next
                            state <= LSU_BUSY; 
                        end
                    end else begin
                        // 0XXX: Memory Ops
                        state <= LSU_BUSY;
                        mem_addr <= {mem_page, ra_val};
                        if (op[2] == 1) begin // Store instructions
                            mem_write <= 1'b1;
                            case (op)
                                LSU_SW: begin 
                                    mem_data_out <= rv_val; 
                                    mem_mask <= 2'b11; 
                                end
                                LSU_SBL: begin 
                                    // Take Lower half of register [7:0]
                                    mem_data_out <= {rv_val[7:0], 8'h00};
                                    mem_mask <= 2'b10;
                                end
                                LSU_SBU: begin 
                                    // Take Upper half of register [15:8]
                                    mem_data_out <= {rv_val[15:8], 8'h00};
                                    mem_mask <= 2'b10;
                                end
                            endcase
                        end
                    end
                end

                LSU_BUSY: begin
                    if (op == LSU_XCHG) begin
                        // XCHG Step 2: Write saved RV to RA
                        reg_wdata <= temp_val;
                        reg_widx  <= ra_idx;
                        reg_write_en <= 1'b1;
                        state <= LSU_DONE;
                    end else if (mem_valid) begin
                        // Memory Operation Completion
                        mem_write <= 1'b0;
                        if (op[2] == 0) begin // Load instructions
                            reg_write_en  <= 1'b1;
                            reg_widx <= rv_idx;
                            case (op)
                                LSU_LW: reg_wdata <= mem_data_in;
                                LSU_LBL: reg_wdata <= {8'h00, mem_data_in[7:0]};
                                LSU_LBU: reg_wdata <= {mem_data_in[7:0], 8'h00};
                            endcase
                        end
                        state <= LSU_DONE;
                    end
                end

                LSU_DONE: begin
                    reg_write_en <= 1'b0;
                    state <= LSU_IDLE;
                end
            endcase
        end
    end
endmodule