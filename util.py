import os
import pickle

import tkinter as tk
from tkinter import messagebox
import face_recognition


def get_button(window, text, color, command, fg='white'):
    color_map = {
        'green': '#4CAF50',
        'red': '#F44336',
        'gray': '#607D8B'
    }
    hex_color = color_map.get(color, color)

    button = tk.Button(
                        window,
                        text=text.upper(),
                        activebackground="#333333",
                        activeforeground="white",
                        fg=fg if color != 'gray' else 'white',
                        bg=hex_color,
                        command=command,
                        height=2,
                        width=20,
                        font=('Segoe UI', 12, 'bold'),
                        relief=tk.FLAT,
                        cursor="hand2"
                    )

    return button


def get_img_label(window):
    label = tk.Label(window, bg="#1E1E1E")
    label.grid(row=0, column=0)
    return label


def get_text_label(window, text):
    label = tk.Label(window, text=text)
    label.config(font=("Segoe UI", 16, "bold"), justify="left", bg="#1E1E1E", fg="#FFFFFF")
    return label


def get_entry_text(window):
    inputtxt = tk.Text(window,
                       height=1,
                       width=15, font=("Segoe UI", 24),
                       bg="#333333", fg="#FFFFFF",
                       insertbackground="#FFFFFF",
                       relief=tk.FLAT,
                       padx=10, pady=10)
    return inputtxt


def msg_box(title, description):
    messagebox.showinfo(title, description)


def recognize(img, db_path):
    # it is assumed there will be at most 1 match in the db

    embeddings_unknown = face_recognition.face_encodings(img)
    if len(embeddings_unknown) == 0:
        return 'no_persons_found'
    else:
        embeddings_unknown = embeddings_unknown[0]

    db_dir = sorted(os.listdir(db_path))

    match = False
    j = 0
    while not match and j < len(db_dir):
        path_ = os.path.join(db_path, db_dir[j])

        file = open(path_, 'rb')
        embeddings = pickle.load(file)

        match = face_recognition.compare_faces([embeddings], embeddings_unknown)[0]
        j += 1

    if match:
        return db_dir[j - 1][:-7]
    else:
        return 'unknown_person'

