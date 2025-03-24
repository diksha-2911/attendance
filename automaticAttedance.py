import os
import cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import customtkinter as ctk

# Set appearance and color theme to match main application
ctk.set_appearance_mode("light")  # Options: "light", "dark", "system"
ctk.set_default_color_theme("blue")  # Options: "blue", "dark-blue", "green"

# Paths setup
haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = "TrainingImageLabel/Trainner.yml"
trainimage_path = "TrainingImage"
studentdetail_path = "StudentDetails/studentdetails.csv"
attendance_path = "Attendance"

# Function for choosing subject and filling attendance
def subjectChoose(text_to_speech):
    def FillAttendance():
        sub = subject_entry.get()
        now = time.time()
        future = now + 20
        
        if sub == "":
            t = "Please enter the subject name!"
            text_to_speech(t)
            # Show error notification
            update_notification("Please enter the subject name!", "warning")
        else:
            try:
                recognizer = cv2.face.LBPHFaceRecognizer_create()
                try:
                    recognizer.read(trainimagelabel_path)
                except:
                    e = "Model not found, please train model"
                    update_notification(e, "error")
                    text_to_speech(e)
                    return
                
                facecasCade = cv2.CascadeClassifier(haarcasecade_path)
                df = pd.read_csv(studentdetail_path)
                cam = cv2.VideoCapture(0)
                font = cv2.FONT_HERSHEY_SIMPLEX
                col_names = ["Enrollment", "Name"]
                attendance = pd.DataFrame(columns=col_names)
                
                # Progress bar setup
                progress_label.configure(text="Capturing faces... Please wait")
                progress_bar.set(0)
                progress_bar.pack(pady=(5, 10), padx=20, fill="x")
                progress_frame.pack(fill="x", padx=20, pady=10)
                
                # Update UI
                subject_window.update()
                
                capture_complete = False
                progress_value = 0
                
                while True:
                    ret, im = cam.read()
                    if not ret:
                        update_notification("Camera not accessible", "error")
                        break
                        
                    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                    faces = facecasCade.detectMultiScale(gray, 1.2, 5)
                    
                    for (x, y, w, h) in faces:
                        global Id
                        Id, conf = recognizer.predict(gray[y:y+h, x:x+w])
                        
                        if conf < 70:
                            global Subject, aa, date, timeStamp
                            Subject = sub
                            ts = time.time()
                            date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                            timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                            aa = df.loc[df["Enrollment"] == Id]["Name"].values
                            global tt
                            tt = str(Id) + "-" + str(aa[0]) if len(aa) > 0 else str(Id)
                            
                            # Add to attendance dataframe
                            attendance.loc[len(attendance)] = [Id, aa[0] if len(aa) > 0 else "Unknown"]
                            
                            # Draw green rectangle for recognized faces
                            cv2.rectangle(im, (x, y), (x+w, y+h), (0, 255, 0), 4)
                            cv2.putText(im, str(tt), (x+h, y), font, 1, (255, 255, 0), 2)
                        else:
                            Id = "Unknown"
                            tt = str(Id)
                            # Draw red rectangle for unknown faces
                            cv2.rectangle(im, (x, y), (x+w, y+h), (0, 0, 255), 4)
                            cv2.putText(im, str(tt), (x+h, y), font, 1, (0, 0, 255), 2)
                    
                    # Update progress bar
                    progress_value = min(1.0, (time.time() - now) / (future - now))
                    progress_bar.set(progress_value)
                    subject_window.update_idletasks()
                    
                    if time.time() > future:
                        capture_complete = True
                        break
                    
                    # Remove duplicates
                    attendance = attendance.drop_duplicates(["Enrollment"], keep="first")
                    
                    # Show live feed
                    cv2.imshow("Filling Attendance...", im)
                    key = cv2.waitKey(30) & 0xFF
                    if key == 27:  # ESC key
                        break
                
                # Clean up camera
                cam.release()
                cv2.destroyAllWindows()
                
                if capture_complete:
                    # Process the attendance data
                    ts = time.time()
                    date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                    Hour, Minute, Second = timeStamp.split(":")
                    
                    # Add attendance column
                    attendance[date] = 1
                    
                    # Create directory if not exists
                    path = os.path.join(attendance_path, Subject)
                    if not os.path.exists(path):
                        os.makedirs(path)
                    
                    # Save attendance file
                    fileName = f"{path}/{Subject}_{date}_{Hour}-{Minute}-{Second}.csv"
                    attendance = attendance.drop_duplicates(["Enrollment"], keep="first")
                    attendance.to_csv(fileName, index=False)
                    
                    # Show success message
                    m = f"Attendance filled successfully for {Subject}"
                    update_notification(m, "success")
                    text_to_speech(m)
                    
                    # Hide progress elements
                    progress_frame.pack_forget()
                    
                    # Display attendance
                    showAttendanceWindow(path, fileName, Subject)
                else:
                    update_notification("Attendance capture was interrupted", "warning")
            
            except Exception as e:
                update_notification(f"Error: {str(e)}", "error")
                text_to_speech("An error occurred while capturing attendance")
                cv2.destroyAllWindows()
    
    def update_notification(message, message_type="info"):
        # Configure colors based on message type
        if message_type == "error":
            notification_label.configure(text=message, fg_color="#FFE0E0", text_color="#D32F2F")
        elif message_type == "warning":
            notification_label.configure(text=message, fg_color="#FFF8E1", text_color="#FF8F00")
        elif message_type == "success":
            notification_label.configure(text=message, fg_color="#E8F5E9", text_color="#2E7D32")
        else:  # info
            notification_label.configure(text=message, fg_color="#E3F2FD", text_color="#1976D2")
        
        notification_label.pack(pady=(10, 5), padx=20, fill="x")
        subject_window.update_idletasks()
    
    def check_attendance_sheets():
        sub = subject_entry.get()
        if sub == "":
            text_to_speech("Please enter the subject name!")
            update_notification("Please enter the subject name!", "warning")
        else:
            path = os.path.join(attendance_path, sub)
            if os.path.exists(path):
                os.startfile(path)
            else:
                update_notification(f"No attendance records found for {sub}", "warning")
    
    def showAttendanceWindow(path, filename, subject_name):
        # Create a new window to show attendance
        attendance_window = ctk.CTkToplevel()
        attendance_window.title(f"Attendance for {subject_name}")
        attendance_window.geometry("600x400")
        attendance_window.grab_set()  # Make it modal
        
        # Configure grid
        attendance_window.grid_columnconfigure(0, weight=1)
        attendance_window.grid_rowconfigure(0, weight=0)  # Header
        attendance_window.grid_rowconfigure(1, weight=1)  # Table content
        
        # Header
        header_frame = ctk.CTkFrame(attendance_window)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text=f"Attendance Details - {subject_name} - {datetime.datetime.now().strftime('%Y-%m-%d')}",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold")
        )
        header_label.pack(pady=10)
        
        # Create a frame for the attendance data
        data_frame = ctk.CTkScrollableFrame(attendance_window)
        data_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Read the CSV file and display data
        try:
            df = pd.read_csv(filename)
            
            # Create header row
            for col_idx, col_name in enumerate(df.columns):
                header = ctk.CTkLabel(
                    data_frame,
                    text=col_name,
                    font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
                    corner_radius=4,
                    fg_color="#E3F2FD",
                    text_color="#1976D2"
                )
                header.grid(row=0, column=col_idx, padx=5, pady=(0, 5), sticky="ew")
            
            # Create data rows
            for row_idx, row in df.iterrows():
                for col_idx, col_name in enumerate(df.columns):
                    value = row[col_name]
                    cell = ctk.CTkLabel(
                        data_frame,
                        text=str(value),
                        font=ctk.CTkFont(family="Arial", size=12),
                        corner_radius=4,
                        fg_color="#F5F5F5" if row_idx % 2 == 0 else "#FFFFFF"
                    )
                    cell.grid(row=row_idx+1, column=col_idx, padx=5, pady=2, sticky="ew")
        
        except Exception as e:
            error_label = ctk.CTkLabel(
                data_frame,
                text=f"Error loading attendance data: {str(e)}",
                font=ctk.CTkFont(family="Arial", size=14),
                text_color="#D32F2F"
            )
            error_label.pack(pady=20)
    
    # Create the subject window with CustomTkinter
    subject_window = ctk.CTk()
    subject_window.title("Select Subject")
    subject_window.geometry("600x500")
    subject_window.resizable(True, False)
    
    # Header frame
    header_frame = ctk.CTkFrame(subject_window, corner_radius=0, height=80)
    header_frame.pack(fill="x")
    
    header_label = ctk.CTkLabel(
        header_frame,
        text="Enter the Subject Name",
        font=ctk.CTkFont(family="Arial", size=24, weight="bold")
    )
    header_label.place(relx=0.5, rely=0.5, anchor="center")
    
    # Content frame
    content_frame = ctk.CTkFrame(subject_window)
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Subject input area
    input_frame = ctk.CTkFrame(content_frame)
    input_frame.pack(fill="x", padx=10, pady=20)
    
    subject_label = ctk.CTkLabel(
        input_frame,
        text="Enter Subject:",
        font=ctk.CTkFont(family="Arial", size=16)
    )
    subject_label.pack(side="left", padx=(10, 0))
    
    subject_entry = ctk.CTkEntry(
        input_frame,
        font=ctk.CTkFont(family="Arial", size=16),
        width=300,
        height=40
    )
    subject_entry.pack(side="left", padx=20)
    
    # Buttons frame
    buttons_frame = ctk.CTkFrame(content_frame)
    buttons_frame.pack(fill="x", padx=10, pady=20)
    
    fill_attendance_button = ctk.CTkButton(
        buttons_frame,
        text="Fill Attendance",
        command=FillAttendance,
        font=ctk.CTkFont(family="Arial", size=16),
        width=200,
        height=40,
        corner_radius=8
    )
    fill_attendance_button.pack(side="left", padx=(50, 10))
    
    check_sheets_button = ctk.CTkButton(
        buttons_frame,
        text="Check Sheets",
        command=check_attendance_sheets,
        font=ctk.CTkFont(family="Arial", size=16),
        width=200,
        height=40,
        corner_radius=8
    )
    check_sheets_button.pack(side="right", padx=(10, 50))
    
    # Progress frame (initially hidden)
    progress_frame = ctk.CTkFrame(content_frame)
    
    progress_label = ctk.CTkLabel(
        progress_frame,
        text="",
        font=ctk.CTkFont(family="Arial", size=14)
    )
    progress_label.pack(pady=(10, 0), padx=20, fill="x")
    
    progress_bar = ctk.CTkProgressBar(progress_frame)
    progress_bar.set(0)
    
    # Notification label (initially hidden)
    notification_label = ctk.CTkLabel(
        content_frame,
        text="",
        font=ctk.CTkFont(family="Arial", size=14),
        corner_radius=8,
        height=40
    )
    
    # Instructions frame
    instructions_frame = ctk.CTkFrame(content_frame)
    instructions_frame.pack(fill="x", padx=10, pady=(30, 10))
    
    instructions_label = ctk.CTkLabel(
        instructions_frame,
        text="Instructions:\n"
             "1. Enter the subject name above\n"
             "2. Click 'Fill Attendance' to start face recognition\n"
             "3. The system will capture attendance for 20 seconds\n"
             "4. Press ESC to stop capturing early\n"
             "5. Use 'Check Sheets' to view previous attendance records",
        font=ctk.CTkFont(family="Arial", size=14),
        justify="left"
    )
    instructions_label.pack(pady=10, padx=10, fill="x")
    
    subject_window.mainloop()

def showAttendanceRecord(filename, subject):
    """Function to display attendance record - can be called from outside"""
    window = ctk.CTk()
    window.title(f"Attendance Record - {subject}")
    window.geometry("800x600")
    
    # Create scrollable frame
    frame = ctk.CTkScrollableFrame(window)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Read CSV file
    try:
        with open(filename, newline="") as file:
            reader = csv.reader(file)
            rows = list(reader)
            
            # Configure grid columns based on data width
            for col_idx in range(len(rows[0]) if rows else 0):
                frame.grid_columnconfigure(col_idx, weight=1, uniform="column")
            
            # Create table
            for row_idx, row_data in enumerate(rows):
                for col_idx, cell_data in enumerate(row_data):
                    # Style headers differently
                    if row_idx == 0:
                        cell = ctk.CTkLabel(
                            frame,
                            text=cell_data,
                            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
                            corner_radius=4,
                            fg_color="#E3F2FD",
                            text_color="#1976D2"
                        )
                    else:
                        cell = ctk.CTkLabel(
                            frame,
                            text=cell_data,
                            font=ctk.CTkFont(family="Arial", size=12),
                            corner_radius=4,
                            fg_color="#F5F5F5" if row_idx % 2 == 0 else "#FFFFFF"
                        )
                    cell.grid(row=row_idx, column=col_idx, padx=5, pady=2, sticky="ew")
    
    except Exception as e:
        error_label = ctk.CTkLabel(
            frame,
            text=f"Error loading file: {str(e)}",
            font=ctk.CTkFont(family="Arial", size=16),
            text_color="#D32F2F"
        )
        error_label.pack(pady=50)
    
    window.mainloop()