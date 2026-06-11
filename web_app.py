import os
import datetime
import pickle
import numpy as np
import cv2
import face_recognition
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import util

app = FastAPI()

# Mount static files
if not os.path.exists("static"):
    os.mkdir("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

db_dir = './db'
if not os.path.exists(db_dir):
    os.mkdir(db_dir)

pending_db_dir = './pending_db'
if not os.path.exists(pending_db_dir):
    os.mkdir(pending_db_dir)

log_path = './log.txt'

def read_imagefile(file) -> np.ndarray:
    nparr = np.frombuffer(file, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image

@app.post("/api/login")
async def login(file: UploadFile = File(...)):
    image = read_imagefile(await file.read())
    
    # Check for faces
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        return JSONResponse(status_code=400, content={"message": "No face found in image", "status": "error"})
    
    name = util.recognize(image, db_dir)
    
    if name in ['unknown_person', 'no_persons_found']:
        return JSONResponse(status_code=401, content={"message": "Authentication Failed. User not verified.", "status": "error"})
    
    with open(log_path, 'a') as f:
        f.write('{},{},in\n'.format(name, datetime.datetime.now()))
        
    return {"message": f"Welcome back, {name}!", "status": "success", "user": name}

@app.post("/api/logout")
async def logout(file: UploadFile = File(...)):
    image = read_imagefile(await file.read())
    
    # Check for faces
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        return JSONResponse(status_code=400, content={"message": "No face found in image", "status": "error"})
    
    name = util.recognize(image, db_dir)
    
    if name in ['unknown_person', 'no_persons_found']:
        return JSONResponse(status_code=401, content={"message": "Authentication Failed. User not verified.", "status": "error"})
    
    with open(log_path, 'a') as f:
        f.write('{},{},out\n'.format(name, datetime.datetime.now()))
        
    return {"message": f"Goodbye, {name}!", "status": "success", "user": name}

@app.post("/api/register")
async def register(name: str = Form(...), file: UploadFile = File(...)):
    image = read_imagefile(await file.read())
    
    embeddings = face_recognition.face_encodings(image)
    if len(embeddings) == 0:
        return JSONResponse(status_code=400, content={"message": "No face found. Please try again.", "status": "error"})
    
    emb = embeddings[0]
    
    # Save pending user
    with open(os.path.join(pending_db_dir, f'{name}.pickle'), 'wb') as f:
        pickle.dump(emb, f)
        
    cv2.imwrite(os.path.join(pending_db_dir, f'{name}.jpg'), image)
    
    return {"message": "User registered! Pending Admin Verification.", "status": "success"}

@app.post("/api/admin/login")
async def admin_login(password: str = Form(...)):
    if password == "admin123":
        return {"status": "success", "message": "Admin logged in"}
    return JSONResponse(status_code=401, content={"message": "Invalid password", "status": "error"})

@app.get("/api/admin/pending")
async def get_pending_users():
    pending_files = os.listdir(pending_db_dir)
    pending_names = [f[:-7] for f in pending_files if f.endswith('.pickle')]
    return {"pending_users": pending_names}

@app.post("/api/admin/verify/{username}")
async def verify_user(username: str):
    pickle_path = os.path.join(pending_db_dir, f"{username}.pickle")
    img_path = os.path.join(pending_db_dir, f"{username}.jpg")
    
    if os.path.exists(pickle_path):
        os.rename(pickle_path, os.path.join(db_dir, f"{username}.pickle"))
    if os.path.exists(img_path):
        os.remove(img_path)
        
    return {"message": f"User {username} verified successfully!", "status": "success"}

@app.post("/api/admin/reject/{username}")
async def reject_user(username: str):
    pickle_path = os.path.join(pending_db_dir, f"{username}.pickle")
    img_path = os.path.join(pending_db_dir, f"{username}.jpg")
    
    if os.path.exists(pickle_path):
        os.remove(pickle_path)
    if os.path.exists(img_path):
        os.remove(img_path)
        
    return {"message": f"User {username} rejected.", "status": "success"}

user_states = {}
user_last_scan = {}

def trigger_door_open(username: str, state: str):
    # Mock IoT Action
    action = "ENTRY" if state == "in" else "EXIT"
    print(f"\n[IoT SYSTEM] -> Triggering physical relay to OPEN door for {action} of user: {username}...\n")
    # Log the automated entry/exit
    with open(log_path, 'a') as f:
        f.write('{},{},auto_{}\n'.format(username, datetime.datetime.now(), state))

@app.post("/api/auto_unlock")
async def auto_unlock(file: UploadFile = File(...)):
    image = read_imagefile(await file.read())
    
    # Check for faces
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        # Silently fail to save bandwidth/logs during auto-scan
        return JSONResponse(status_code=400, content={"message": "No face found", "status": "error"})
    
    name = util.recognize(image, db_dir)
    
    if name in ['unknown_person', 'no_persons_found']:
        return JSONResponse(status_code=401, content={"message": "Not Verified", "status": "error"})
    
    now = datetime.datetime.now()
    
    # Cooldown Check: Ignore same user if scanned within the last 15 seconds
    if name in user_last_scan:
        if (now - user_last_scan[name]).total_seconds() < 15:
            return JSONResponse(status_code=400, content={"message": "Cooldown active", "status": "cooldown"})
            
    # Toggle user state between 'in' and 'out'
    current_state = user_states.get(name, 'out')
    new_state = 'in' if current_state == 'out' else 'out'
    
    user_states[name] = new_state
    user_last_scan[name] = now
    
    # Valid face recognized
    trigger_door_open(name, new_state)
    
    display_message = "DOOR UNLOCKED (LOG IN)" if new_state == "in" else "DOOR UNLOCKED (LOG OUT)"
    
    return {"message": display_message, "status": "success", "user": name, "state": new_state}

# Serve the main index file
from fastapi.responses import FileResponse
@app.get("/")
async def root():
    return FileResponse("static/index.html")

