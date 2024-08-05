import tkinter as tk
from tkinter import scrolledtext
import sys
from tkinter import ttk
import serial
import threading

class START_COM:
    def __init__(self, arduino_port: str, baud_rate: int):
        self.arduino_port = arduino_port
        self.baud_rate = baud_rate
        self.ser = None
        self.read = 0
        self.arduino_data = ""
        self.reading_thread = None
        self.string=""

    def open_coms(self):
        try:
            self.ser = serial.Serial(self.arduino_port, self.baud_rate, timeout=1)
        except Exception as e:
            print(f"ERROR : unable to open comms on port {self.arduino_port}: \n {e}")

    def start_reading(self, b1, b2, b3, b4, b5, e1, e2, e3):
        self.read = 1
        self.reading_thread = threading.Thread(target=self.read_message, daemon=True, args=[b1, b2, b3, b4, b5, e1, e2, e3])
        self.reading_thread.start()

    def read_message(self, b1, b2, b3, b4, b5, e1, e2, e3) -> None:
        self.string=""
        numbers_ok=False
        while self.read == 1:
            try:
                self.arduino_data = self.ser.readline().decode('utf-8').strip()
                if self.arduino_data:
                    if self.arduino_data.isnumeric():
                        numbers_ok=True
                    if numbers_ok==True:
                        if "Option" in self.arduino_data:
                            self.stop_reading(b1, b2, b3, b4, b5, e1, e2, e3)
                            sys.stdout.flush()
                        else:
                            self.string=self.string + self.arduino_data.strip() + ","  
                            print(f"# RESPONSE # : {self.arduino_data}")         
                            sys.stdout.flush()
            except KeyboardInterrupt:
                print("\nExiting program")
                self.read = 0

    def stop_reading(self, b1, b2, b3, b4, b5, e1, e2, e3) -> None:
        self.read = 0
        self.arduino_data = ""
        insert_entry_data(self.string, b1, b2, b3, b4, b5, e1, e2, e3)

    def send_message(self, message:str):
        self.message=message
        self.sending_thread=threading.Thread(target=self.send, daemon=True)
        self.sending_thread.start()

    def send(self) -> None:
        if self.ser and self.ser.is_open:
            self.ser.write(self.message.encode())
            print(f"\n# COMMAND # : {self.message}\n")
        else:
            print("Serial connection not open. Cannot send message.")

    def close_coms(self) -> None:
        if self.ser and self.ser.is_open:
            self.ser.close()

class Button_loading_type(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.args=kwargs
        if "text" in self.args:
            self.display_text=self.args["text"]
        self.char_list=["-", "\\", "/"]
        self.cycler=self.character_cycler()
        self.ongoing=False
        self.__timer_id = ''
        self.__stop_request = True

    def character_cycler(self):
        while True:
            for char in self.char_list:
                yield char

    def display_animation(self):
        if self.ongoing==True:
            self.config(text=f"{self.display_text} {next(self.cycler)}")
            self.id=self.after(200, self.display_animation)

    def start_loading(self):
        self["state"]=tk.DISABLED
        self.ongoing=True
        self.display_animation()

    def stop_loading(self):
        self["state"]=tk.NORMAL
        self.ongoing=False
        self.config(text=self.display_text)
        self.after_cancel(self.id)

class Logger(scrolledtext.ScrolledText):
    def __init__(self, log:scrolledtext.ScrolledText):
        self.stdout=sys.stdout
        sys.stdout = self
        self.log=log

    def write(self, text):
        self.log.configure(state='normal')
        self.log.insert(tk.END, text)
        self.log.configure(state='disabled')
        self.log.yview(tk.END)

    def flush(self):
        self.stdout.flush()

def insert_entry_data(data:str, b1, b2, b3, b4, b5, e1:tk.Entry, e2, e3):
    b1["state"]=tk.NORMAL
    b4["state"]=tk.NORMAL
    b5.stop_loading()
    good_data=data.split(",")
    good_data=good_data[1:-1]
    print(f"Retreived correct data: {good_data}")
    summs=0
    for i in good_data:
        summs=summs+int(i)
    rmp=(summs/10)*60
    e1.delete(0, tk.END)
    e1.insert(tk.END, round(rmp, 2))

    e2.delete(0, tk.END)
    e2.insert(tk.END, summs/10)

    e3.delete(0, tk.END)
    e3.insert(tk.END, good_data)

class Init_first_frame(tk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.init_comms_btn=Button_loading_type(self, text="Init port comunication", command=self.update_progress)
        self.init_comms_btn.pack(anchor="center", padx=10, pady=10, ipadx=10, ipady=10)

        self.progress = ttk.Progressbar(self, length=200, mode='determinate')
        self.progress.pack(pady=20)
    
    def update_progress(self):
        if self.progress["value"]==0:
            self.init_comms_btn.start_loading()
            COMMS.open_coms()
        self.progress['value'] += 20
        if self.progress['value'] < 100:
            self.master.after(1000, self.update_progress)
        else:
            self.destroy()
        
class Init_seccond_frame(tk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure([0, 1, 2], weight=1)
        self.grid_rowconfigure(0, weight=1)

        ##############################
        self.frame_2_left=tk.LabelFrame(self, text="Read RMK3B values")
        self.frame_2_left.grid(row=0, column=0, sticky="nsew")
        self.frame_2_left.grid_columnconfigure([0,1], weight=1)
        self.frame_2_left.grid_rowconfigure([0, 1, 2, 3], weight=1)

        ##############################
        self.frame_2_mid=tk.LabelFrame(self, text="Stroboscope control")
        self.frame_2_mid.grid(row=0, column=1, sticky="nsew")

        ##############################
        self.frame_2_right=tk.LabelFrame(self, text="Control motor speed")
        self.frame_2_right.grid(row=0, column=2, sticky="nsew")

        ##############################frameside1##############################
        self.rpm_label=tk.Label(self.frame_2_left, text="RPM:")
        self.rpm_label.grid(column=0, row=0, sticky="e")

        self.rpm_entry=tk.Entry(self.frame_2_left)
        self.rpm_entry.grid(column=1, row=0, sticky="w")

        self.current_read_value_label=tk.Label(self.frame_2_left, text="Current value considered (rot/sec for stroboscope) :")
        self.current_read_value_label.grid(column=0, row=1, sticky="e")

        self.current_read_value_entry=tk.Entry(self.frame_2_left)
        self.current_read_value_entry.grid(column=1, row=1, sticky="w")

        self.actual_read_value_label=tk.Label(self.frame_2_left, text="Serial received list of values (rot/s) :")
        self.actual_read_value_label.grid(column=0, row=2, sticky="e")

        self.actual_read_value_entry=tk.Entry(self.frame_2_left)
        self.actual_read_value_entry.grid(column=1, row=2, sticky="w")

        self.read_values_button=Button_loading_type(self.frame_2_left, text="Read values", pady=10, command=lambda: self.read_rmk3b_values())
        self.read_values_button.grid(row=3, column=0, columnspan=2, ipadx=5, ipady=5, padx=10, pady=10)

        ##############################frameside2##############################
        self.start_strobo_button=Button_loading_type(self.frame_2_mid, text="Start stroboscoope", pady=10, command=lambda: self.start_stroboscope_msg())
        self.start_strobo_button.pack(pady=15)

        self.scale = tk.Scale(self.frame_2_mid, from_=1, to=60, orient=tk.HORIZONTAL, bigincrement=0.1, resolution=0.1, length=500, command=self.on_scale_move)
        self.scale.pack()

        self.label_value = tk.Label(self.frame_2_mid, text="Value: 0")
        self.label_value.pack()

        self.send_values_button=Button_loading_type(self.frame_2_mid, text="Send value", pady=10, command=lambda: self.send_strob_value())
        self.send_values_button.pack(pady=15)
        
        self.stop_button=Button_loading_type(self.frame_2_mid, text="Stop stroboscope", pady=10, command=lambda: self.send_strob_stop())
        self.stop_button.pack(pady=15)

        self.strobo_sent_value_to_rmp=tk.Label(self.frame_2_mid, text="Sent value (rot/sec) to rpm (rot/min)")
        self.strobo_sent_value_to_rmp.pack(pady=35)

        self.strobo_sent_value_to_rmp_entry=tk.Entry(self.frame_2_mid)
        self.strobo_sent_value_to_rmp_entry.pack()

        self.send_values_button["state"]=tk.DISABLED
        self.stop_button["state"]=tk.DISABLED

        ##############################frameside2##############################
        self.scale_speed = tk.Scale(self.frame_2_right, from_=0, to=4, orient=tk.HORIZONTAL, length=200, command=self.on_speed_scale_move)
        self.scale_speed.pack(pady=20)

        self.label_value_speed = tk.Label(self.frame_2_right, text="Value: 0")
        self.label_value_speed.pack()

        self.start_mottor=Button_loading_type(self.frame_2_right, text="Send value", pady=10, command=lambda: self.send_speed_value())
        self.start_mottor.pack(pady=15)

        self.current_speed_label=tk.Label(self.frame_2_right, text="Current motor speed :")
        self.current_speed_label.pack(pady=35)

        self.current_speed_entry=tk.Entry(self.frame_2_right)
        self.current_speed_entry.pack()

    def start_stroboscope_msg(self):
        self.read_values_button["state"]=tk.DISABLED
        self.start_mottor["state"]=tk.DISABLED
        COMMS.send_message("start_s")
        print("Stroboscope started with freq 11;")
        self.send_values_button["state"]=tk.NORMAL
        self.stop_button["state"]=tk.NORMAL
        self.start_strobo_button.start_loading()

    def read_rmk3b_values(self):
        self.read_values_button.start_loading()
        print("Reading values...")
        self.start_strobo_button["state"]=tk.DISABLED
        self.send_values_button["state"]=tk.DISABLED
        self.stop_button["state"]=tk.DISABLED
        self.start_mottor["state"]=tk.DISABLED
        COMMS.send_message("measure")
        COMMS.start_reading(self.start_strobo_button, self.send_values_button, self.stop_button, self.start_mottor, self.read_values_button,
                            self.rpm_entry, self.current_read_value_entry, self.actual_read_value_entry)
        
    def on_scale_move(self, value):
        self.label_value.config(text=f"Value: {value}")

    def on_speed_scale_move(self, value):
        self.label_value_speed.config(text=f"Value: {value}")

    def send_strob_value(self):
        value=""
        a=self.label_value["text"][-4]
        b=self.label_value["text"][-3]
        c=self.label_value["text"][-2]
        d=self.label_value["text"][-1]
        if a.isnumeric():
            value+=a
        if b.isnumeric():
            value+=b
        if c==".":
            value+=c
        if d.isnumeric():
            value+=d  
        print(f"Setting Stroboscope frequency to {value}...")
        COMMS.send_message(f"{value}")
        self.strobo_sent_value_to_rmp_entry.delete(0, tk.END)
        self.strobo_sent_value_to_rmp_entry.insert(tk.END, round(float(value)*60, 2))

    def send_strob_stop(self):
        self.read_values_button["state"]=tk.NORMAL
        self.start_mottor["state"]=tk.NORMAL
        COMMS.send_message("s")
        self.send_values_button["state"]=tk.DISABLED
        self.stop_button["state"]=tk.DISABLED
        self.start_strobo_button.stop_loading()
        print("Stroboscope stopped successfully")

    def send_speed_value(self):
        print(f"Setting motor to speed {self.label_value_speed["text"][-1]}...")
        COMMS.send_message(f"speed{self.label_value_speed["text"][-1]}")
        self.current_speed_entry.delete(0, tk.END)
        self.current_speed_entry.insert(tk.END, self.label_value_speed["text"][-1])

class GUI:
    def __init__(self):
        self.root=tk.Tk()
        self.root.title("Masurarea turatiei")
        self.root.state("zoomed")
        self.root.resizable(width=False, height=False)
        
        self.root.grid_columnconfigure(0, weight=1, pad=10)
        self.root.grid_rowconfigure(0, weight=2, pad=10)
        self.root.grid_rowconfigure(1, weight=1, pad=10)

        self.work_frame=Init_seccond_frame(self.root, text="Work space")
        self.work_frame.grid(column=0, row=0, sticky="nsew")

        self.work_frame=Init_first_frame(self.root)
        self.work_frame.grid(column=0, row=0, sticky="nsew")

        self.log_frame=tk.LabelFrame(self.root, text="Log")
        self.log_frame.grid(column=0, row=1, sticky="nsew")

        self.log=scrolledtext.ScrolledText(self.log_frame)
        self.log.pack(expand=True, fill=tk.BOTH)

        logger=Logger(self.log)
        
        self.root.mainloop()

if __name__=="__main__":
    #("COM5", 115200)
    COMMS=START_COM("COM5", 115200)
    window=GUI()
    COMMS.close_coms()