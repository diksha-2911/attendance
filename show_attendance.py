import os
import pandas as pd
from glob import glob
import csv
import customtkinter as ctk
from PIL import Image


def subjectchoose(text_to_speech):
    def calculate_attendance():
        Subject = subject_entry.get()
        if Subject == "":
            t = 'Please enter the subject name.'
            text_to_speech(t)
            return

        filenames = glob(f"Attendance\\{Subject}\\{Subject}*.csv")
        if not filenames:
            message_label.configure(text=f"No attendance records found for {Subject}")
            return
            
        df = [pd.read_csv(f) for f in filenames]
        newdf = df[0]
        for i in range(1, len(df)):
            newdf = newdf.merge(df[i], how="outer")
        newdf.fillna(0, inplace=True)
        newdf["Attendance"] = 0
        for i in range(len(newdf)):
            newdf["Attendance"].iloc[i] = str(int(round(newdf.iloc[i, 2:-1].mean() * 100))) + '%'
        
        newdf.to_csv(f"Attendance\\{Subject}\\attendance.csv", index=False)
        
        # Open attendance in a new window
        attendance_window = ctk.CTkToplevel()
        attendance_window.title(f"Attendance of {Subject}")
        attendance_window.geometry("800x600")
        
        # Create a frame for the data
        data_frame = ctk.CTkScrollableFrame(attendance_window)
        data_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid
        cs = f"Attendance\\{Subject}\\attendance.csv"
        with open(cs) as file:
            reader = csv.reader(file)
            data = list(reader)
            
            # Create header row with special formatting
            for c, col_name in enumerate(data[0]):
                header_label = ctk.CTkLabel(
                    data_frame,
                    text=col_name,
                    font=ctk.CTkFont(family="Verdana", size=16, weight="bold"),
                    width=100,
                    height=35,
                    corner_radius=8,
                    fg_color="#1f538d",  # Blue header
                )
                header_label.grid(row=0, column=c, padx=5, pady=5, sticky="nsew")
            
            # Create data rows
            for r in range(1, len(data)):
                for c, cell_value in enumerate(data[r]):
                    cell_label = ctk.CTkLabel(
                        data_frame,
                        text=cell_value,
                        font=ctk.CTkFont(family="Verdana", size=14),
                        width=100,
                        height=30,
                        corner_radius=8,
                        fg_color=("#EAEAEA", "#2B2B2B"),  # Light/dark mode colors
                    )
                    cell_label.grid(row=r, column=c, padx=5, pady=2, sticky="nsew")

    def open_attendance_folder():
        sub = subject_entry.get()
        if sub == "":
            t = "Please enter the subject name!!!"
            text_to_speech(t)
        else:
            folder_path = f"Attendance\\{sub}"
            if os.path.exists(folder_path):
                os.startfile(folder_path)
            else:
                message_label.configure(text=f"Folder not found: {folder_path}")

    # Create main window
    subject_window = ctk.CTk()
    subject_window.title("View Attendance")
    subject_window.geometry("800x500")
    subject_window.minsize(700, 450)
    
    # Configure responsive grid layout
    subject_window.grid_columnconfigure(0, weight=1)
    subject_window.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
    
    # Header
    header_frame = ctk.CTkFrame(subject_window, corner_radius=0)
    header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
    header_frame.grid_columnconfigure(0, weight=1)
    
    # Title
    title_label = ctk.CTkLabel(
        header_frame,
        text="View Subject Attendance",
        font=ctk.CTkFont(family="Verdana", size=28, weight="bold")
    )
    title_label.grid(row=0, column=0, padx=20, pady=20)
    
    # Try to load and display an image (if available)
    try:
        attendance_img = Image.open("UI_Image/attendance.png")
        attendance_ctk_img = ctk.CTkImage(light_image=attendance_img, size=(80, 80))
        img_label = ctk.CTkLabel(subject_window, image=attendance_ctk_img, text="")
        img_label.grid(row=1, column=0, padx=20, pady=10)
    except:
        pass  # Skip image if not available
    
    # Subject entry section
    entry_frame = ctk.CTkFrame(subject_window)
    entry_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
    entry_frame.grid_columnconfigure(0, weight=1)
    entry_frame.grid_columnconfigure(1, weight=3)
    
    # Subject label
    subject_label = ctk.CTkLabel(
        entry_frame,
        text="Enter Subject:",
        font=ctk.CTkFont(family="Verdana", size=16)
    )
    subject_label.grid(row=0, column=0, padx=20, pady=20, sticky="e")
    
    # Subject entry
    subject_entry = ctk.CTkEntry(
        entry_frame,
        font=ctk.CTkFont(family="Verdana", size=18),
        width=250,
        height=40
    )
    subject_entry.grid(row=0, column=1, padx=20, pady=20, sticky="w")
    
    # Message display
    message_label = ctk.CTkLabel(
        subject_window,
        text="",
        font=ctk.CTkFont(family="Verdana", size=14),
        corner_radius=8,
        fg_color=("#EAEAEA", "#2B2B2B"),  # Light/dark mode colors
        height=30
    )
    message_label.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
    
    # Button frame
    button_frame = ctk.CTkFrame(subject_window)
    button_frame.grid(row=4, column=0, padx=20, pady=20, sticky="ew")
    button_frame.grid_columnconfigure((0, 1), weight=1)
    
    # View Attendance button
    view_button = ctk.CTkButton(
        button_frame,
        text="View Attendance",
        command=calculate_attendance,
        font=ctk.CTkFont(family="Verdana", size=16),
        height=50,
        width=200
    )
    view_button.grid(row=0, column=0, padx=20, pady=20)
    
    # Check Sheets button
    sheets_button = ctk.CTkButton(
        button_frame,
        text="Check Sheets",
        command=open_attendance_folder,
        font=ctk.CTkFont(family="Verdana", size=16),
        height=50,
        width=200
    )
    sheets_button.grid(row=0, column=1, padx=20, pady=20)
    
    # Start the main loop
    subject_window.mainloop()