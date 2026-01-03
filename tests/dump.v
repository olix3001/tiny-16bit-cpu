module dump();
    initial begin
        $dumpfile("dump.vcd");
        $dumpvars(0);
    end
endmodule