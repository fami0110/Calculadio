from customtkinter import set_appearance_mode, set_default_color_theme, CTk, CTkImage, CTkFrame, CTkLabel, CTkButton, CTkEntry, StringVar
from PIL import Image
import speech_recognition as sr
from playsound3 import playsound
from threading import Thread
from string import digits
import re
import sys
import os

def get_asset_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, "assets", relative_path)

class App(CTk):

    def __init__(self):
        super().__init__()
        
        # Prooerty init
        self.isRecording = False
        self.recognizer = sr.Recognizer()

        # Window config
        self.title("Calculadio")
        self.geometry("400x500")
        self.attributes('-alpha', 0.8)
        
        # Icons
        self.icon_mic_on = CTkImage(dark_image=Image.open(get_asset_path('image/on.png')), size=(28, 28))
        self.icon_mic_off = CTkImage(dark_image=Image.open(get_asset_path('image/off.png')), size=(28, 28))
        self.icon_backspace = CTkImage(dark_image=Image.open(get_asset_path('image/backspace.png')), size=(20, 20))
        
        # Sfx
        self.sfx_active = lambda: playsound(get_asset_path('audio/active.wav'))
        self.sfx_success = lambda: playsound(get_asset_path('audio/success.wav'))
        self.sfx_close = lambda: playsound(get_asset_path('audio/close.wav'))
        self.sfx_failed = lambda: playsound(get_asset_path('audio/failed.wav'))

        # Appearance
        set_appearance_mode("dark")
        set_default_color_theme("blue")

        # Build UI
        self.build_equation_frame()
        self.build_result_frame()
        self.build_action_frame()

    def build_equation_frame(self):
        self.equation_frame = CTkFrame(self, fg_color="#212121")
        self.equation_frame.pack(fill="both")
        
        self.equation_var = StringVar()
        self.equation_var.trace_add('write', self.on_input)

        self.equation_entry = CTkEntry(self.equation_frame,
            placeholder_text="0",
            textvariable=self.equation_var,
            font=("Arial", 20),
            fg_color="#212121",
            border_width=0,
            justify="right",
        )
        self.equation_entry.pack(fill="both", padx=8, pady=16)

    def force_cursor_end(self, event=None):
        self.equation_entry.icursor("end")
        return "break"

    def build_result_frame(self):
        self.result_frame = CTkFrame(self, corner_radius=0)
        self.result_frame.pack(fill="both")

        self.equal_label = CTkLabel(self.result_frame,
            text="=",
            font=("Arial", 40),
            anchor="w"
        )
        self.equal_label.pack(fill="x", side="left", anchor="n", padx=12, pady=8)
        
        self.result_label = CTkLabel(self.result_frame,
            text="0",
            font=("Arial", 48, "bold"),
            anchor="e"
        )
        self.result_label.pack(fill="x", side="left", anchor="n", expand=True, padx=8, pady=8)

    def build_action_frame(self):
        self.action_wrapper = CTkFrame(self, corner_radius=0, fg_color="#2B2B2B")
        self.action_wrapper.pack(fill="both", expand=True)
        
        self.action_frame = CTkFrame(self.action_wrapper, corner_radius=0, fg_color="#2B2B2B")
        self.action_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for i in range(4):
            self.action_frame.grid_columnconfigure(i, weight=1)
        
        for i in range(5):
            self.action_frame.grid_rowconfigure(i, weight=1)

        self.buttons = [[None for _ in range(4)] for _ in range(5)]
        buttons_labels = [
            ["REC", "C", "back"],
            ["/", "*", "-", "+"],
            ["1", "2", "3", "("],
            ["4", "5", "6", ")"],
            ["7", "8", "9", "del"],
        ]

        for i, row in enumerate(buttons_labels):
            for j, label in enumerate(row):
                btn = CTkButton(self.action_frame, 
                    text=label,
                    fg_color="#4B6877",
                    hover_color="#37474F",
                    font=('Arial', 18, 'bold'),
                    corner_radius=5,
                    command=lambda x=label: self.action_handler(action=x)
                )
                btn.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
                self.buttons[i][j] = btn

        self.buttons[0][0].configure(fg_color="#D32F2F", hover_color="#aa0000",
            text="",
            image=self.icon_mic_on,
        )
        self.buttons[0][0].grid_configure(columnspan=2)
        self.buttons[0][1].configure(fg_color="#A16100", hover_color="#7A4D08")
        self.buttons[0][1].grid_configure(column=2)
        self.buttons[0][2].configure(fg_color="#A16100", hover_color="#7A4D08", 
            text="🔙", 
            font=('Arial', 28, 'bold')
        )
        self.buttons[0][2].grid_configure(column=3)
        self.buttons[1][0].configure(fg_color="#0288D1", hover_color="#0277BD")
        self.buttons[1][1].configure(fg_color="#0288D1", hover_color="#0277BD", text="x")
        self.buttons[1][2].configure(fg_color="#0288D1", hover_color="#0277BD")
        self.buttons[1][3].configure(fg_color="#0288D1", hover_color="#0277BD")
        self.buttons[2][3].configure(fg_color="#0288D1", hover_color="#0277BD")
        self.buttons[3][3].configure(fg_color="#0288D1", hover_color="#0277BD")
        self.buttons[4][3].configure(fg_color="#A16100", hover_color="#7A4D08", 
            text="", 
            image=self.icon_backspace,
        )
        
    def clear_equation(self):
        self.equation_var.set("")
        self.result_label.configure(text='0')
        
    def check_types(self, value: str):
        if any([c in value for c in digits]):
            return "number"
        elif any([c in value for c in "+-*/()"]):
            return "operator"
        else:
            return False
        
    def sanitize_equation(self, value):
        equations = re.findall(r'\d+|[+\-*/]+|[()]', value)
        
        if len(equations) > 0:    
            # Prevent the first element from being an operator (except '-')
            if self.check_types(equations[0]) == "operator" and  equations[0] not in ['-', '(']:
                equations.pop(0)

            # Sanitize consecutive operators
            sanitized = []
            prev = None
            for token in equations:
                if prev and self.check_types(prev) == "number" and token == "(":
                    continue
                if prev and self.check_types(prev) == "operator" and token == ")":
                    continue
                elif self.check_types(token) == "operator" and len(token) > 1:
                    sanitized.append(token[0])
                else:
                    sanitized.append(token)   
                prev = token
                
            return "".join(sanitized)
            
        return ""
        
    def calculate(self, equation):
        sanitized_equation = self.sanitize_equation(equation)
        self.equation_var.set(sanitized_equation.replace('*', 'x'))
        if sanitized_equation:
            try:
                result = eval(sanitized_equation)
            except:
                result = "Err"
            self.result_label.configure(text=result)
        else:
            self.result_label.configure(text="0")
    
    def on_input(self, var, index, mode):
        equation = self.equation_var.get()
        self.calculate(equation)
        
            
    def action_handler(self, action: str):
        current_equation = self.equation_var.get()
        
        if action == "REC":
            self.toggleRecord()
            return
        elif action == "C":
            self.clear_equation()
            return
        elif action == "back":
            current_equation = "".join(re.findall(r'\d+|[+\-*/]+|[()]', current_equation)[:-1])
        elif action == "del":
            current_equation = current_equation[:-1]
        else:
            current_equation += action
            
        self.calculate(current_equation)
            
            
    def toggleRecord(self):
        if not self.isRecording :
            self.isRecording = True
            Thread(target=self.record, daemon=True).start()
        else:
            self.isRecording = False
        
    def record(self):
        record_btn = self.buttons[0][0]
        
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            
            print('===Recording===')
            record_btn.configure(image=self.icon_mic_off, fg_color="#AA0000")
            self.sfx_active()
            
            while self.isRecording:
                audio = self.recognizer.listen(source)
                try:
                    text = self.recognizer.recognize_google(audio, language="id-ID")
                    self.process_stream(text)
                    print(text)
                except sr.UnknownValueError:
                    print("?")
                    self.sfx_failed()
                except sr.RequestError as e:
                    print(f"⚠️ Error dengan layanan Google Speech: {e}")
                    break
        
        print('\n===Stopped===')
        record_btn.configure(image=self.icon_mic_on, fg_color="#D32F2F")
        self.sfx_close()
        
    def process_stream(self, transcribed: str):
        current_equation = self.equation_var.get()
        words = transcribed.split(" ")
        
        for word in words:
            if word.isdigit():
                current_equation += word
            elif "tambah" in word  or "plus" in word or word == "+":
                current_equation += "+"
            elif "kurang" in word  or "min" in word or word == "-":
                current_equation += "-"
            elif "kali" in word or word == "*":
                current_equation += "*"
            elif "bagi" in word or word == "/":
                current_equation += "/"
            elif "kurung" in word:
                current_equation += "("
            elif "tutup" in word:
                current_equation += ")"
            elif "hapus" in word:
                current_equation = current_equation[:-1]
            elif "salah" in word or "kembali" in word or "back" in word:
                current_equation = "".join(re.findall(r'\d+|[+\-*/]+|[()]', current_equation)[:-1])
            elif "bersih" in word or "clear" in word or "reset" in word:
                self.clear_equation()
                self.sfx_success()
                return
            elif "berhenti" in word or "stop" in word:
                self.isRecording = False
                return
            else:
                continue
            
        self.calculate(current_equation)
        self.sfx_success()

if __name__ == "__main__":
    app = App()
    app.mainloop()
