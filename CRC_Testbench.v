


module CRC_Testbench;
    reg [31:0] dataword;                  // 16-bit dataword input
    wire [47:0] codeword;                 // 32-bit codeword (dataword + 16-bit CRC)
    reg [47:0] received_codeword;         // 32-bit received codeword for checking
    wire accept;                          // Output flag to indicate CRC validity
    wire [15:0] syndrome;                 // Syndrome for debugging

    // Instantiate the CRC Generator and Checker modules
    CRC_Generator crc_gen(
        .dataword(dataword),
        .codeword(codeword)
    );

    CRC_Checker crc_check(
        .received_codeword(received_codeword),
        .accept(accept),
        .syndrome(syndrome) // Expose syndrome for debugging
    );

    // Task to display results in a table format
    task display_result;
        input [31:0] dataword;
        input [47:0] codeword;
        input [15:0] syndrome;
        input accept;
        
        begin
            $display("---------------------------------------------------------------------");
            $display("| Dataword        | Codeword                      | Syndrome        | CRC Valid |");
            $display("---------------------------------------------------------------------");
            $display("| %b | %b | %b |    %s     |", dataword, codeword, syndrome, (accept ? "Yes" : "No"));
            $display("---------------------------------------------------------------------");
        end
    endtask

    // Apply test cases
    initial begin
        $display("Running CRC test cases...");
        
        // Test Case 1: No error
        dataword = 32'b1101010111010101; // Random 16-bit dataword
        #10;
        received_codeword = codeword; // Pass codeword to checker
        #10;
        display_result(dataword, codeword, syndrome, accept);

        // Test Case 2: No error
        dataword = 32'b0110101010101010; // Another random 16-bit dataword
        #10;
        received_codeword = codeword;
        #10;
        display_result(dataword, codeword, syndrome, accept);

        // Test Case 3: With error (flip one bit in received_codeword)
        dataword = 32'b1111111111111111; // Random 16-bit dataword
        #10;
        received_codeword = codeword ^ 48'b000000000000000000000000000000000000000000000001; // Introduce an error by flipping the last bit
        #10;
        display_result(dataword, codeword, syndrome, accept);

        // Test Case 4: No error
        dataword = 32'b0000000000000000; // All zeros dataword
        #10;
        received_codeword = codeword;
        #10;
        display_result(dataword, codeword, syndrome, accept);

        $finish;
    end
endmodule
