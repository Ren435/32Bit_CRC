
module CRC_Checker(
    input [47:0] received_codeword,  // 32-bit received codeword (16-bit dataword + 16-bit CRC remainder)
    output reg accept,               // Output flag to indicate CRC validity
    output reg [15:0] syndrome       // 16-bit syndrome for debugging
);

    parameter [15:0] divisor = 16'b1100000000000001;  // Polynomial x^16 + x^15 + 1
    reg [47:0] temp;
    integer i;  // Temporary register for division

    always @(*) begin
        // Initialize `temp` with `received_codeword` to perform division
        temp = received_codeword;

        // Perform XOR division based on the divisor
        for (i = 47; i >= 16; i = i - 1) begin
            if (temp[i] == 1)
                temp = temp ^ (divisor << (i - 16)); // Apply the divisor using shifting
        end

        // The remainder after division is the 16 least significant bits
        syndrome = temp[15:0];
        // If the syndrome is all zeros, the CRC is valid
        accept = (syndrome == 16'b0);
    end
endmodule
