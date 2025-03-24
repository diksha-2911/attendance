import os
import cv2
import shutil
import csv
import numpy as np
import pandas as pd
import datetime
import time
import pyttsx3
from PIL import ImageTk, Image
import customtkinter as ctk

# Set appearance and color theme
ctk.set_appearance_mode("light")  # Options: "light", "dark", "system"
ctk.set_default_color_theme("blue")  # Options: "blue", "dark-blue", "green"

# project module imports
import show_attendance
import takeImage
import trainImage
import automaticAttedance

def text_to_speech(user_text):
    engine = pyttsx3.init()
    engine.say(user_text)
    engine.runAndWait()

# Paths setup
haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = "./TrainingImageLabel/Trainner.yml"
trainimage_path = "./TrainingImage"
if not os.path.exists(trainimage_path):
    os.makedirs(trainimage_path)

studentdetail_path = "./StudentDetails/studentdetails.csv"
attendance_path = "Attendance"

# Main window setup
class FaceRecognizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Class Vision - Face Recognition Attendance")
        self.geometry("1280x720")
        self.minsize(1000, 600)  # Set minimum window size for responsiveness
        
        # Create responsive grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(2, weight=0)  # Buttons
        self.grid_rowconfigure(3, weight=0)  # Exit button
        
        # Header frame
        self.header_frame = ctk.CTkFrame(self, corner_radius=0)
        self.header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=(20, 0))
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Logo setup (using CTkImage)
        self.logo_img = ctk.CTkImage(light_image=Image.open("UI_Image/0001.png"), size=(50, 47))
        self.logo_label = ctk.CTkLabel(self.header_frame, image=self.logo_img, text="")
        self.logo_label.grid(row=0, column=0, padx=10, pady=10)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="CLASS VISION",
            font=ctk.CTkFont(family="Verdana", size=27, weight="bold")
        )
        self.title_label.grid(row=0, column=1, padx=10, pady=10)
        
        # Welcome message
        self.welcome_label = ctk.CTkLabel(
            self,
            text="Welcome to CLASS VISION",
            font=ctk.CTkFont(family="Verdana", size=32, weight="bold")
        )
        self.welcome_label.grid(row=1, column=0, columnspan=3, padx=20, pady=20)
        
        # Feature frames with images
        # Register frame
        self.register_frame = ctk.CTkFrame(self)
        self.register_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        
        # Load and resize image
        reg_img = Image.open("UI_Image/1.png")
        self.reg_ctk_img = ctk.CTkImage(light_image=reg_img, size=(120, 120))
        
        # Image label
        self.reg_img_label = ctk.CTkLabel(self.register_frame, image=self.reg_ctk_img, text="")
        self.reg_img_label.pack(pady=20)
        
        # Button
        self.register_button = ctk.CTkButton(
            self.register_frame,
            text="Register a new student",
            command=self.open_registration,
            font=ctk.CTkFont(family="Verdana", size=16),
            height=50
        )
        self.register_button.pack(pady=20, padx=20, fill="x")
        
        # Verify frame
        self.verify_frame = ctk.CTkFrame(self)
        self.verify_frame.grid(row=2, column=1, padx=20, pady=20, sticky="nsew")
        
        verify_img = Image.open("UI_Image/3.png")
        self.verify_ctk_img = ctk.CTkImage(light_image=verify_img, size=(120, 120))
        
        self.verify_img_label = ctk.CTkLabel(self.verify_frame, image=self.verify_ctk_img, text="")
        self.verify_img_label.pack(pady=20)
        
        self.take_attendance_button = ctk.CTkButton(
            self.verify_frame,
            text="Take Attendance",
            command=self.take_attendance,
            font=ctk.CTkFont(family="Verdana", size=16),
            height=50
        )
        self.take_attendance_button.pack(pady=20, padx=20, fill="x")
        
        # Attendance frame
        self.attendance_frame = ctk.CTkFrame(self)
        self.attendance_frame.grid(row=2, column=2, padx=20, pady=20, sticky="nsew")
        
        attend_img = Image.open("UI_Image/2.png")
        self.attend_ctk_img = ctk.CTkImage(light_image=attend_img, size=(120, 120))
        
        self.attend_img_label = ctk.CTkLabel(self.attendance_frame, image=self.attend_ctk_img, text="")
        self.attend_img_label.pack(pady=20)
        
        self.view_attendance_button = ctk.CTkButton(
            self.attendance_frame,
            text="View Attendance",
            command=self.view_attendance,
            font=ctk.CTkFont(family="Verdana", size=16),
            height=50
        )
        self.view_attendance_button.pack(pady=20, padx=20, fill="x")
        
        # Exit button
        self.exit_button = ctk.CTkButton(
            self,
            text="EXIT",
            command=self.quit,
            font=ctk.CTkFont(family="Verdana", size=16),
            fg_color="#FF5252",  # Red color for exit button
            hover_color="#FF1A1A",
            height=50
        )
        self.exit_button.grid(row=3, column=0, columnspan=3, padx=300, pady=30, sticky="ew")
    
    def open_registration(self):
        self.registration_window = RegistrationWindow()
        self.registration_window.grab_set()  # Make the window modal
    
    def take_attendance(self):
        automaticAttedance.subjectChoose(text_to_speech)
    
    def view_attendance(self):
        show_attendance.subjectchoose(text_to_speech)


class RegistrationWindow(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Register New Student")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Create responsive grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Register Your Face",
            font=ctk.CTkFont(family="Verdana", size=28, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10))
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Enter the details",
            font=ctk.CTkFont(family="Verdana", size=20)
        )
        self.subtitle_label.grid(row=1, column=0, columnspan=2, padx=20, pady=10)
        
        # Enrollment No
        self.enrollment_label = ctk.CTkLabel(
            self,
            text="Enrollment No:",
            font=ctk.CTkFont(family="Verdana", size=16)
        )
        self.enrollment_label.grid(row=2, column=0, padx=20, pady=10, sticky="e")
        
        # Only numbers validation
        def validate_number(text):
            if text.isdigit() or text == "":
                return True
            return False
        
        validate_cmd = (self.register(validate_number), '%P')
        
        self.enrollment_entry = ctk.CTkEntry(
            self,
            font=ctk.CTkFont(family="Verdana", size=16),
            validate="key",
            validatecommand=validate_cmd,
            width=250
        )
        self.enrollment_entry.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        
        # Name
        self.name_label = ctk.CTkLabel(
            self,
            text="Name:",
            font=ctk.CTkFont(family="Verdana", size=16)
        )
        self.name_label.grid(row=3, column=0, padx=20, pady=10, sticky="e")
        
        self.name_entry = ctk.CTkEntry(
            self,
            font=ctk.CTkFont(family="Verdana", size=16),
            width=250
        )
        self.name_entry.grid(row=3, column=1, padx=20, pady=10, sticky="w")
        
        # Notification area
        self.notification_label = ctk.CTkLabel(
            self,
            text="Notification:",
            font=ctk.CTkFont(family="Verdana", size=16)
        )
        self.notification_label.grid(row=4, column=0, padx=20, pady=10, sticky="e")
        
        self.message_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Verdana", size=16),
            width=250,
            height=50,
            corner_radius=8,
            fg_color=("#EAEAEA", "#2B2B2B"),  # Light/dark mode colors
            anchor="center"
        )
        self.message_label.grid(row=4, column=1, padx=20, pady=10, sticky="w")
        
        # Button frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=20)
        
        # Take Image button
        self.take_img_button = ctk.CTkButton(
            self.button_frame,
            text="Take Image",
            command=self.take_image,
            font=ctk.CTkFont(family="Verdana", size=16),
            width=180,
            height=40
        )
        self.take_img_button.grid(row=0, column=0, padx=20, pady=20)
        
        # Train Image button
        self.train_img_button = ctk.CTkButton(
            self.button_frame,
            text="Train Image",
            command=self.train_image,
            font=ctk.CTkFont(family="Verdana", size=16),
            width=180,
            height=40
        )
        self.train_img_button.grid(row=0, column=1, padx=20, pady=20)
    
    def show_error(self):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Warning!")
        error_window.geometry("400x150")
        error_window.resizable(False, False)
        
        # Center the error message
        error_window.grid_columnconfigure(0, weight=1)
        error_window.grid_rowconfigure(0, weight=1)
        error_window.grid_rowconfigure(1, weight=1)
        
        error_label = ctk.CTkLabel(
            error_window,
            text="Enrollment & Name required!!!",
            font=ctk.CTkFont(family="Verdana", size=16, weight="bold")
        )
        error_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        ok_button = ctk.CTkButton(
            error_window,
            text="OK",
            command=error_window.destroy,
            font=ctk.CTkFont(family="Verdana", size=16),
            width=100
        )
        ok_button.grid(row=1, column=0, padx=20, pady=(10, 20))
        
        # Make the window modal
        error_window.grab_set()
        error_window.focus_set()
    
    def take_image(self):
        l1 = self.enrollment_entry.get()
        l2 = self.name_entry.get()
        
        takeImage.TakeImage(
            l1,
            l2,
            haarcasecade_path,
            trainimage_path,
            self.message_label,
            self.show_error,
            text_to_speech,
        )
        
        self.enrollment_entry.delete(0, "end")
        self.name_entry.delete(0, "end")
    
    def train_image(self):
        trainImage.TrainImage(
            haarcasecade_path,
            trainimage_path,
            trainimagelabel_path,
            self.message_label,
            text_to_speech,
        )


if __name__ == "__main__":
    app = FaceRecognizerApp()
    app.mainloop()