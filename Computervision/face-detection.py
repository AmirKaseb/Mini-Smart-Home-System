import cv2
import face_recognition

video_capture = cv2.VideoCapture(0)

known_face_encodings = []
known_face_names = []

# Load known face image
image = face_recognition.load_image_file("amir.png")
known_face_encodings.append(face_recognition.face_encodings(image)[0])
known_face_names.append("Amir Kasseb")

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    # Initialize face_detected variable
    face_detected = 0

    # Process each detected face
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            face_detected = 1  # Set face_detected to 1 if a face is recognized

        # Draw rectangle around face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
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
