import os.path
import datetime
import pickle

import tkinter as tk
import cv2
from PIL import Image, ImageTk
import face_recognition

import util
# from test import test


class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")
        self.main_window.configure(bg="#1E1E1E")

        self.login_button_main_window = util.get_button(self.main_window, 'login', 'green', self.login)
        self.login_button_main_window.place(x=750, y=200)

        self.logout_button_main_window = util.get_button(self.main_window, 'logout', 'red', self.logout)
        self.logout_button_main_window.place(x=750, y=300)

        self.register_new_user_button_main_window = util.get_button(self.main_window, 'register new user', 'gray',
                                                                    self.register_new_user, fg='black')
        self.register_new_user_button_main_window.place(x=750, y=400)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)

        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.pending_db_dir = './pending_db'
        if not os.path.exists(self.pending_db_dir):
            os.mkdir(self.pending_db_dir)

        self.admin_panel_button_main_window = util.get_button(self.main_window, 'Admin Panel', 'gray', self.open_admin_panel, fg='black')
        self.admin_panel_button_main_window.place(x=750, y=100)

        self.log_path = './log.txt'

    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        if not ret:
            self._label.after(20, self.process_webcam)
            return

        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)

    def show_feedback_window(self, img_to_show, title_text, btn_color="red"):
        feedback_window = tk.Toplevel(self.main_window)
        feedback_window.geometry("720x600+370+120")
        feedback_window.title(title_text)
        feedback_window.configure(bg="#1E1E1E")
        
        img_ = cv2.cvtColor(img_to_show, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=img_pil)
        
        img_label = tk.Label(feedback_window)
        img_label.place(x=10, y=10, width=700, height=500)
        img_label.imgtk = imgtk
        img_label.configure(image=imgtk)
        
        btn = util.get_button(feedback_window, 'Continue', btn_color, feedback_window.destroy)
        btn.place(x=200, y=520)

    def login(self):

        # label = test(
        #         image=self.most_recent_capture_arr,
        #         model_dir='/home/phillip/Desktop/todays_tutorial/27_face_recognition_spoofing/code/face-attendance-system/Silent-Face-Anti-Spoofing/resources/anti_spoof_models',
        #         device_id=0
        #         )
        label = 1

        if label == 1:

            name = util.recognize(self.most_recent_capture_arr, self.db_dir)
            img_to_show = self.most_recent_capture_arr.copy()
            face_locations = face_recognition.face_locations(img_to_show)

            if name in ['unknown_person', 'no_persons_found']:
                if name == 'unknown_person' and face_locations:
                    top, right, bottom, left = face_locations[0]
                    cv2.rectangle(img_to_show, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(img_to_show, "Not Verified", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                self.show_feedback_window(img_to_show, "Authentication Failed", "red")
            else:
                if face_locations:
                    top, right, bottom, left = face_locations[0]
                    cv2.rectangle(img_to_show, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(img_to_show, f"Welcome, {name}", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                self.show_feedback_window(img_to_show, "Authentication Success", "green")
                
                with open(self.log_path, 'a') as f:
                    f.write('{},{},in\n'.format(name, datetime.datetime.now()))
                    f.close()

        else:
            img_to_show = self.most_recent_capture_arr.copy()
            face_locations = face_recognition.face_locations(img_to_show)
            if face_locations:
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(img_to_show, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(img_to_show, "Spoofer!", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            self.show_feedback_window(img_to_show, "Spoofer Detected!", "red")

    def logout(self):

        # label = test(
        #         image=self.most_recent_capture_arr,
        #         model_dir='/home/phillip/Desktop/todays_tutorial/27_face_recognition_spoofing/code/face-attendance-system/Silent-Face-Anti-Spoofing/resources/anti_spoof_models',
        #         device_id=0
        #         )
        label = 1

        if label == 1:

            name = util.recognize(self.most_recent_capture_arr, self.db_dir)
            img_to_show = self.most_recent_capture_arr.copy()
            face_locations = face_recognition.face_locations(img_to_show)

            if name in ['unknown_person', 'no_persons_found']:
                if name == 'unknown_person' and face_locations:
                    top, right, bottom, left = face_locations[0]
                    cv2.rectangle(img_to_show, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(img_to_show, "Not Verified", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                self.show_feedback_window(img_to_show, "Authentication Failed", "red")
            else:
                if face_locations:
                    top, right, bottom, left = face_locations[0]
                    cv2.rectangle(img_to_show, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(img_to_show, f"Goodbye, {name}", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                self.show_feedback_window(img_to_show, "Logout Success", "green")
                
                with open(self.log_path, 'a') as f:
                    f.write('{},{},out\n'.format(name, datetime.datetime.now()))
                    f.close()

        else:
            img_to_show = self.most_recent_capture_arr.copy()
            face_locations = face_recognition.face_locations(img_to_show)
            if face_locations:
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(img_to_show, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(img_to_show, "Spoofer!", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            self.show_feedback_window(img_to_show, "Spoofer Detected!", "red")


    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+370+120")
        self.register_new_user_window.configure(bg="#1E1E1E")

        self.accept_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Accept', 'green', self.accept_register_new_user)
        self.accept_button_register_new_user_window.place(x=750, y=300)

        self.try_again_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Try again', 'red', self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=750, y=400)

        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        self.entry_text_register_new_user = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=750, y=150)

        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 'Please, \ninput username:')
        self.text_label_register_new_user.place(x=750, y=70)

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def start(self):
        self.main_window.mainloop()

    def open_admin_panel(self):
        # 1. Try Face Recognition
        name = util.recognize(self.most_recent_capture_arr, self.db_dir)
        
        if name == "admin":
            util.msg_box('Admin Access', 'Welcome back, Admin!')
            self.launch_admin_panel_ui()
            return
            
        # 2. Fallback to Password
        password_window = tk.Toplevel(self.main_window)
        password_window.geometry("400x250+550+250")
        password_window.title("Admin Authentication")
        password_window.configure(bg="#1E1E1E")
        
        lbl = util.get_text_label(password_window, "Enter Admin Password:")
        lbl.pack(pady=20)
        
        pwd_entry = tk.Entry(password_window, show="*", font=("Segoe UI", 20), bg="#333333", fg="white", relief=tk.FLAT, justify="center")
        pwd_entry.pack(pady=10)
        pwd_entry.focus()
        
        def check_password(event=None):
            pwd = pwd_entry.get()
            if pwd == "admin123":
                password_window.destroy()
                self.launch_admin_panel_ui()
            else:
                util.msg_box('Access Denied', 'Incorrect Password!')
                
        pwd_entry.bind('<Return>', check_password)
        
        btn = util.get_button(password_window, 'Submit', 'green', check_password)
        btn.pack(pady=10)

    def launch_admin_panel_ui(self):
        admin_window = tk.Toplevel(self.main_window)
        admin_window.geometry("900x700+370+120")
        admin_window.title("Admin Panel - Pending Users")
        admin_window.configure(bg="#1E1E1E")
        
        pending_files = os.listdir(self.pending_db_dir)
        pending_names = [f[:-7] for f in pending_files if f.endswith('.pickle')]
        
        if not pending_names:
            lbl = util.get_text_label(admin_window, "No pending users.")
            lbl.pack(pady=50)
            return

        # Setup scrollable Canvas
        canvas = tk.Canvas(admin_window, bg="#1E1E1E", highlightthickness=0)
        scrollbar = tk.Scrollbar(admin_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1E1E1E")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Header
        header_frame = tk.Frame(scrollable_frame, bg="#333333")
        header_frame.pack(fill="x", pady=(0, 10))
        tk.Label(header_frame, text="Photo", font=("Segoe UI", 16, "bold"), bg="#333333", fg="white", width=15).grid(row=0, column=0, padx=10, pady=5)
        tk.Label(header_frame, text="Name", font=("Segoe UI", 16, "bold"), bg="#333333", fg="white", width=20).grid(row=0, column=1, padx=10, pady=5)
        tk.Label(header_frame, text="Action", font=("Segoe UI", 16, "bold"), bg="#333333", fg="white", width=20).grid(row=0, column=2, padx=10, pady=5)

        # Store references to PhotoImages to prevent garbage collection
        admin_window.image_refs = []

        def verify_user(name, row_frame):
            os.rename(os.path.join(self.pending_db_dir, f"{name}.pickle"), 
                      os.path.join(self.db_dir, f"{name}.pickle"))
            img_path = os.path.join(self.pending_db_dir, f"{name}.jpg")
            if os.path.exists(img_path):
                os.remove(img_path)
            row_frame.destroy()
            util.msg_box("Verified", f"User {name} verified successfully!")
            
        def reject_user(name, row_frame):
            pickle_path = os.path.join(self.pending_db_dir, f"{name}.pickle")
            if os.path.exists(pickle_path):
                os.remove(pickle_path)
            img_path = os.path.join(self.pending_db_dir, f"{name}.jpg")
            if os.path.exists(img_path):
                os.remove(img_path)
            row_frame.destroy()
            util.msg_box("Rejected", f"User {name} rejected.")

        for name in pending_names:
            row_frame = tk.Frame(scrollable_frame, bg="#1E1E1E", highlightbackground="#333333", highlightthickness=1)
            row_frame.pack(fill="x", pady=5)
            
            # 1. Photo
            img_label = tk.Label(row_frame, bg="#1E1E1E")
            img_path = os.path.join(self.pending_db_dir, f"{name}.jpg")
            if os.path.exists(img_path):
                img = cv2.imread(img_path)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(img)
                img_pil = img_pil.resize((120, 90))
                imgtk = ImageTk.PhotoImage(image=img_pil)
                admin_window.image_refs.append(imgtk)
                img_label.configure(image=imgtk)
            img_label.grid(row=0, column=0, padx=10, pady=10)
            
            # 2. Name
            name_lbl = tk.Label(row_frame, text=name, font=("Segoe UI", 16), bg="#1E1E1E", fg="white", width=20)
            name_lbl.grid(row=0, column=1, padx=10, pady=10)
            
            # 3. Actions
            action_frame = tk.Frame(row_frame, bg="#1E1E1E")
            action_frame.grid(row=0, column=2, padx=10, pady=10)
            
            btn_verify = tk.Button(action_frame, text="Verify", bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold"), relief=tk.FLAT, width=8, command=lambda n=name, rf=row_frame: verify_user(n, rf))
            btn_verify.pack(side="left", padx=5)
            
            btn_reject = tk.Button(action_frame, text="Reject", bg="#F44336", fg="white", font=("Segoe UI", 12, "bold"), relief=tk.FLAT, width=8, command=lambda n=name, rf=row_frame: reject_user(n, rf))
            btn_reject.pack(side="left", padx=5)

    def accept_register_new_user(self):
        name = self.entry_text_register_new_user.get(1.0, "end-1c")

        embeddings = face_recognition.face_encodings(self.register_new_user_capture)[0]

        file = open(os.path.join(self.pending_db_dir, '{}.pickle'.format(name)), 'wb')
        pickle.dump(embeddings, file)
        file.close()
        
        cv2.imwrite(os.path.join(self.pending_db_dir, '{}.jpg'.format(name)), self.register_new_user_capture)

        util.msg_box('Success!', 'User registered! Pending Admin Verification.')

        self.register_new_user_window.destroy()


if __name__ == "__main__":
    app = App()
    app.start()
