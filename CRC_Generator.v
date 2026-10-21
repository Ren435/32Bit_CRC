

module CRC_Generator(
    input [31:0] dataword,        // 16-bit data input
    output wire [47:0] codeword    // 32-bit codeword (16-bit dataword + 16-bit CRC)
);
    parameter [15:0] divisor = 16'b1100000000000001;  // Polynomial x^16 + x^15 + 1
    reg [47:0] temp;
    reg [15:0] remainder;
    
    
    always @(*) begin
        
        // Append 16 zeros to the dataword for CRC calculation
        temp = {dataword, 16'b0};

        // Perform XOR division based on the divisor
        for (integer i = 47; i >= 16; i = i - 1) begin
            if (temp[i] == 1)
                temp = temp ^ (divisor << (i - 16)); // Apply the divisor using shifting
        end
        remainder = temp[15:0];  // Extract 16-bit remainder
    end

    assign codeword = {dataword, remainder};  // Concatenate dataword and CRC remainder
endmodule
