import tkinter as tk
from tkinter import messagebox
from tkinter.font import Font
from tkinter import Canvas
import subprocess
import threading

result_output="Yes"
# Function to run Verilog simulation in a separate thread
def run_verilog_simulation(binary_input,error=False):
    yes_tb_template =f"""
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
            
            dataword = 32'b{binary_input}; // Random 32-bit dataword
            #10;
            received_codeword = codeword; // Pass codeword to checker
            #10;
            display_result(dataword, codeword, syndrome, accept);

            $finish;
        end
    endmodule
    """

    no_tb_template=f"""
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
                $display("| Input            |   Input Received by Checker   | Remainder     | CRC Valid |");
                $display("| (Dataword)       |    (Codeword)                 | (syndrome)    |           |");
                $display("---------------------------------------------------------------------");
                $display("| %b | %b | %b |    %s     |", dataword, codeword, syndrome, (accept ? "Yes" : "No"));
                $display("---------------------------------------------------------------------");
            end
        endtask

        // Apply test cases
        initial begin
            $display("Running CRC test cases...");
            
            dataword = 32'b{binary_input}; // Random 16-bit dataword
            #10;
            received_codeword = codeword ^ 48'b000000000000000000000000000000000000000000000001; // Pass codeword to checker
            #10;
            display_result(dataword, codeword, syndrome, accept);

            $finish;
        end
    endmodule
"""

    file = open("tb.v", "w")
    if error:
        file.write(no_tb_template)
    else:
        file.write(yes_tb_template)
    file.close()

    def simulate():
        compile_command = ["iverilog", "-o", "CRC_simulation.vvp", "CRC_Generator.v", "CRC_Checker.v", "tb.v"]
        compile_process = subprocess.run(compile_command, capture_output=True, text=True)

        if compile_process.returncode != 0:
            print("Error in Verilog compilation:", compile_process.stderr)
            result_output = None
        else:
            run_command = ["vvp", "crc_simulation.vvp"]
            run_process = subprocess.run(run_command, capture_output=True, text=True)

            if run_process.returncode != 0:
                print("Error in Verilog simulation:", run_process.stderr)
                result_output = None
            else:
                result_output = run_process.stdout

        print(result_output)
        update_result(result_output, binary_input, error)

    thread = threading.Thread(target=simulate)
    thread.start()

def update_result(result_output, binary_input, error=False):
    if result_output:
        
        syndrome = "N/A"  
        crc_valid = "No"  
        received_codeword = "N/A" 
        remainder = "N/A"  

        for line in result_output.splitlines():
            if "|" in line:  
                parts = line.split("|")
                if len(parts) > 3:
                    received_codeword = parts[2].strip()  
                    remainder = parts[3].strip()  
                    crc_valid = parts[4].strip()  

        if crc_valid == "No":
            result_message = (
                f"Error detected in your binary input.\n"
                f"Number inputed: {binary_input}\n"
                f"Received Codeword: {received_codeword}\n"
                f"Remainder (Syndrome): {remainder}\n"
                f"Please check your input."
            )
        else:
            result_message = (
                f"No error detected in your binary input.\n"
                f"Number inputed: {binary_input}\n"
                f"Received Codeword: {received_codeword}\n"
                f"Remainder (Syndrome): {remainder}\n"
            )

        show_notification("Phone", result_message)
    else:
        
        result_message = "Failed to process CRC. Check the console for errors."
        show_notification("Error", result_message)


def hex_to_binary(hex_string):
    """
    Convert a hexadecimal string to its binary representation, padded to 16 bits.
    """
    try:
        binary_representation = format(int(hex_string, 32), 'b')  
        if len(binary_representation) > 32:
            return "Error: Hexadecimal input exceeds 32 bits."
        return binary_representation.zfill(32)  
    except ValueError:
        return "Error: Invalid hexadecimal input."

def word_to_binary(word):
    """
    Convert a word (1-2 alphabets) to its binary representation.
    Each character is represented by its ASCII value in binary.
    If the input has only one alphabet, it pads with a second null character (00000000).
    """
    if len(word) <=3 :
        word += '\0'  
    elif len(word) > 4:
        return "Error: Input must be of maximum 4  alphabets."
    
    binary_representation = ''.join(format(ord(char), '08b') for char in word)
    return binary_representation


def send_message():
    user_input = input_box.get().strip()
    if user_input:
        chat_canvas.config(state=tk.NORMAL)
        chat_canvas.insert(tk.END, f"{user_input}\n")
        chat_canvas.config(state=tk.DISABLED)
        chat_canvas.see(tk.END)
        input_box.delete(0, tk.END)

    if len(user_input) <= 4 and user_input.isalpha():
        
        binary_input = word_to_binary(user_input)
        if "Error" in binary_input:  
            messagebox.showerror("Invalid Input", binary_input)
            return
    elif all(char in '0123456789ABCDEFabcdef' for char in user_input):
    
        binary_input = hex_to_binary(user_input)
        if "Error" in binary_input:  
            messagebox.showerror("Invalid Input", binary_input)
            return
    elif all(bit in '01' for bit in user_input):
       
        if len(user_input) > 32:
            messagebox.showerror("Invalid Input", "Input exceeds 32 bits. Please provide a valid binary input.")
            return
        binary_input = user_input.zfill(32)  
    else:
        
        messagebox.showerror("Invalid Input", "Please enter a valid binary, 4-alphabet word, or hexadecimal input.")
        return

    add_message(binary_input, "user")
   
    input_box.delete(0, tk.END)
    confirm = messagebox.askyesno("Generate Error?", "Do you want to introduce an error in the CRC simulation?")
    
    if confirm:
        
        run_verilog_simulation(binary_input, error=True)
    else:
        
        run_verilog_simulation(binary_input, error=False)

def add_message(text, sender):
    message_label = tk.Label(
        chat_frame,
        text=text,
        wraplength=250,
        justify="left",
        padx=15,
        pady=10,
        font=("Arial", 12),
    )
    if sender == "user":
       
        message_label.config(bg="#4CAF50", fg="#ffffff", anchor="e", relief="flat", borderwidth=1, bd=5)
        message_label.pack(anchor="e", pady=5, padx=10)
    elif sender == "system":
        
        message_label.config(bg="#333", fg="#ffffff", anchor="w", relief="flat", borderwidth=1, bd=5)
        message_label.pack(anchor="w", pady=5, padx=10)

    
    chat_canvas.yview_moveto(1.0) 
 

def create_rounded_rectangle_mobile(canvas, x1, y1, x2, y2, radius=20, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

root= tk.Tk()
root.title("CSE213 PROJECT")
root.geometry("400x800")
root.configure(bg="#1E1E2E")  


canvas = Canvas(root, bg="#1E1E2E", width=400, height=800, highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)


offset_x = 850  


mobile_screen_bottom = 710  


create_rounded_rectangle_mobile(canvas, 60 + offset_x, 70, 340 + offset_x, mobile_screen_bottom, radius=30, fill="#2B2E38")  # Mobile screen background

create_rounded_rectangle_mobile(canvas, 60 + offset_x, 70, 340 + offset_x, 140, radius=30, fill="#3E424F")  # Header background
header_label = tk.Label(canvas, text="< Laptop", bg="#3E424F", fg="white", font=("Helvetica", 16, "bold"))
header_label.place(x=80 + offset_x, y=95)

chat_canvas = tk.Text(canvas, bg="#2B2E38", fg="white", font=("Helvetica", 12), wrap=tk.WORD, state=tk.DISABLED, bd=0)
chat_canvas.place(x=80 + offset_x, y=150, width=240, height=500)
chat_frame = tk.Frame(chat_canvas, bg="black")

create_rounded_rectangle_mobile(canvas, 60 + offset_x, 650, 340 + offset_x, mobile_screen_bottom, radius=30, fill="#3E424F")  # Input box background

input_box = tk.Entry(canvas, bg="#3E424F", fg="white", font=("Helvetica", 14), bd=0, insertbackground="white")
input_box.place(x=80 + offset_x, y=665, width=180, height=30)


send_button = tk.Button(
    canvas,
    text="➤",  
    font=("Helvetica", 16, "bold"),
    bg="#3E424F",  
    fg="white",
    relief=tk.FLAT,
    command=send_message
)
send_button.place(x=270 + offset_x, y=665, width=50, height=30)

def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, **kwargs):
    """Draw a rounded rectangle using a polygon for smooth edges."""
    points = [
        x1 + radius, y1, x2 - radius, y1, x2 - radius, y1, x2, y1,
        x2, y1 + radius, x2, y2 - radius, x2, y2 - radius, x2, y2,
        x2 - radius, y2, x1 + radius, y2, x1 + radius, y2, x1, y2,
        x1, y2 - radius, x1, y1 + radius, x1, y1 + radius, x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)



def show_notification(title, message):
   
    notification_window = tk.Toplevel()
    notification_window.geometry("600x180+20+20")  # Increased width and height
    notification_window.overrideredirect(True)  # No window borders

    # Canvas for drawing the notification box
    canvas = tk.Canvas(
        notification_window,
        width=600,  # Increased width
        height=180,  # Increased height
        highlightthickness=0
    )
    canvas.pack(fill="both", expand=True)

    
    create_rounded_rectangle(canvas, 10, 10, 590, 170, radius=25, fill="#FFFFFF", outline="")

    
    title_font = Font(family="Helvetica", size=16, weight="bold")
    canvas.create_text(
        20, 30,  
        text=title,
        font=title_font,
        fill="#000000",  
        anchor="nw"
    )

    
    timestamp_font = Font(family="Helvetica", size=12,weight="bold")
    canvas.create_text(
        580, 30,  
        text="now",
        font=timestamp_font,
        fill="#000000",  
        anchor="ne"
    )

   
    canvas.create_line(20, 55, 580, 55, fill="#000000", width=1)  # Black line

    
    message_font = Font(family="Helvetica", size=14)
    canvas.create_text(
        20, 70,  
        text=message,
        font=message_font,
        fill="#000000",  
        anchor="nw",
        width=560  
    )

    
    notification_window.attributes("-alpha", 0.95) 

    
    notification_window.after(30000, notification_window.destroy)
root.mainloop()
