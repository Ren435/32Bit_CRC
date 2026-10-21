
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
                $display("| Input       | Input Received by Checker      | Remainder        | CRC Valid |");
                $display("| (Dataword)  | (Codeword)                     |       | CRC Valid |");
               
                $display("---------------------------------------------------------------------");
                $display("| %b | %b | %b |    %s     |", dataword, codeword, syndrome, (accept ? "Yes" : "No"));
                $display("---------------------------------------------------------------------");
            end
        endtask

        // Apply test cases
        initial begin
            $display("Running CRC test cases...");
            
            dataword = 32'b00000000000000001000100001100100; // Random 32-bit dataword
            #10;
            received_codeword = codeword; // Pass codeword to checker
            #10;
            display_result(dataword, codeword, syndrome, accept);

            $finish;
        end
    endmodule
    