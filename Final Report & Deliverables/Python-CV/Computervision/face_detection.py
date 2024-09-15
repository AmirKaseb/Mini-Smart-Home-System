import os
from pathlib import Path
import cv2
import face_recognition

###################################
# Functions to be used

# Draw rectangular frame around person's face
def draw(face_detected, frame, left, top, right, bottom, name):
    # Set color based on face detection status
    if face_detected:
        color = (0, 255, 0) # Green for recognized
    else:
        color = (0, 0, 255)  # Red for unrecognized

    # Draw rectangle around face
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)

    # Write name below face
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

    return frame

# Extract the file name without the extension
def name_from_path(image_path):
    base_name = os.path.basename(image_path)
    name = os.path.splitext(base_name)[0]
    return name

def path_from_name(name, folder_path):
    path = r"C:\Users\Administrator\Desktop\Known"
    image_path = os.path.join(folder_path, f"{name}.png")
    return image_path
    
# Load all images in the directory
def load_image(folder_path):
    known_face_encodings = []
    known_face_names = []

    for image_path in folder_path.glob("*.png"):
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(name_from_path(image_path))

    return known_face_encodings, known_face_names

# Function to open the door
def homeowner_open(face_detected, door_opened, homeowner_ask, key):
    if not face_detected and not door_opened:
        if not homeowner_ask:
            print("Press 'o' to open the door")
            homeowner_ask = True # This ensures that the message is only printed only once

        if key == ord('o'):
            print("Door opened")
            door_opened = True
            print("Press 'a' to add person to database")

    return door_opened, homeowner_ask

# Function to add person to the database and reload images
def homeowner_add(door_opened, key, clean_frame, folder_path):
    if door_opened and key == ord('a'):
        name = input("Enter the person's name: ")
        cv2.imwrite(path_from_name(name, folder_path), clean_frame)
        print(f"Person added as {name}")

        return True
    return False
    
def delete_person(name, folder_path):
    image_path = path_from_name(name, folder_path)
    
    # Check if person's image exists
    if os.path.exists(image_path):
        # Delete the image
        os.remove(image_path) 
        return True
    
###################################

if __name__ == "__main__":
    # Initialize video capture
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Error: Could not open video capture")
        exit()

    folder_path = Path(r"C:\Users\Administrator\Desktop\Known")  # Default directory

    # Load known faces and their names from the specified directory
    known_face_encodings, known_face_names = load_image(folder_path)

    door_opened = False
    homeowner_ask = False

    while True:
        # Capture frame-by-frame
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Create a clean copy of the frame before drawing in case image will be saved
        clean_frame = frame.copy()

        # Detect face locations and encodings in the current frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        face_detected = False
        name = "Unknown"

        # Compare detected faces with known faces
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                face_detected = True

            # Draw a rectangle around the face
            frame = draw(face_detected, frame, left, top, right, bottom, name)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        # Check for user key press
        key = cv2.waitKey(1) & 0xFF

        # Handle quitting and password reset functionality at any time
        if key == ord('q'):
            print("Quitting...")
            break  # Exit the loop

        if key == ord('r'):
            password = input("New password: ")
            print(f"Password updated to: {password}")
            
        if key == ord('d'):
            name = input("Enter name of person to delete: ")
            if (delete_person(name, folder_path)):
                known_face_encodings, known_face_names = load_image(folder_path)
                print(f"{name} deleted from database")
            else:
                print(f"{name} doesn't exist in database")
        # Handle homeowner decisions
        door_opened, homeowner_ask = homeowner_open(face_detected, door_opened, homeowner_ask, key)
        if homeowner_add(door_opened, key, clean_frame, folder_path):
            # Reload the known faces and names as a new person has been added
            known_face_encodings, known_face_names = load_image(folder_path)

            # Reset flags to go back to detecting faces
            door_opened = False
            homeowner_ask = False

    # Release the capture and close windows
    cam.release()
    cv2.destroyAllWindows()
