import os
from pathlib import Path
import cv2
import face_recognition

###################################
# Functions to be used

# Extract the file name without the extension
def extract_name(image_path):
    base_name = os.path.basename(image_path)
    name = os.path.splitext(base_name)[0]
    return name


# Function to ask user to state directory if needed


# Loads all images in directory
def load_image():
    # Specify the directory containing known face images
    folder_dir = Path(r"C:\Users\Administrator\Desktop\Known")  # Default directory
    
    known_face_encodings = []
    known_face_names = []

    # Iterate through all image files in the directory
    for image_path in folder_dir.glob("*.png"):
        # Load the image file
        image = face_recognition.load_image_file(image_path)

        # Encode the face found in the image
        face_encoding = face_recognition.face_encodings(image)[0]
        
        # Append the face encoding
        known_face_encodings.append(face_encoding)

        # Extract the name from the image file name and append it
        name = extract_name(image_path)
        known_face_names.append(name)

    return known_face_encodings, known_face_names

###################################

video_capture = cv2.VideoCapture(0)

# Load known faces and their names from the specified directory
known_face_encodings, known_face_names = load_image()

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    # Initialize face_detected variable
    face_detected = 0
    name = "Unknown"

    # Process each detected face
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            face_detected = 1  # Set face_detected to 1 if a face is recognized

            # Draw green rectangle around recognized face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)

        else:
            # Draw red rectangle around unrecognized face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)

        # Write name below face
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

    # Output the face_detected flag to the console
    print("Face Detected:", face_detected)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
video_capture.release()
cv2.destroyAllWindows()
