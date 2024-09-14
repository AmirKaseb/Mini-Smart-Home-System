import os
from pathlib import Path
import cv2
import face_recognition
import flet as ft
import base64
from io import BytesIO
import asyncio

###################################
# Initialization 

folder_path = Path(r"C:\Users\Administrator\Desktop\Known")  # Default directory
cam = cv2.VideoCapture(0)

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
    
# Load all images in the directory
def load_image(folder_path):
    folder = Path(folder_path)  # Convert to Path object
    known_face_encodings = []
    known_face_names = []

    for image_path in folder.glob('*.jpg'):  # Use Path's glob method
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(encoding)
        known_face_names.append(image_path.stem)  # Use stem for the name

    return known_face_encodings, known_face_names

# Extract the file name without the extension
def name_from_path(image_path):
    base_name = os.path.basename(image_path)
    name = os.path.splitext(base_name)[0]
    return name

def path_from_name(name, folder_path):
    folder = Path(folder_path)  # Convert to Path object
    return folder / f"{name}.jpg"  # Use Path's / operator for joining paths

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
    return False

def get_names_from_folder(folder_path):
    names = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".jpg") or file_name.endswith(".png"):  # Assuming images are stored with these extensions
            name = os.path.splitext(file_name)[0]  # Remove extension to get the name
            names.append(name)
    return names

###################################  
# Choice of running

# Terminal
def processTerminal():
    # Initialize video capture
    cam = cv2.VideoCapture(0)
    
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

        # Initialize `face_detected` to False and set default name to 'Unknown'
        face_detected = False
        name = "Unknown"  # Default name for unidentified faces

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
            if delete_person(name, folder_path):
                known_face_encodings, known_face_names = load_image(folder_path)
                print(f"{name} deleted from database")
            else:
                print(f"{name} doesn't exist in the database")

        # Handle homeowner decisions
        door_opened, homeowner_ask = homeowner_open(face_detected, door_opened, homeowner_ask, key)
        if homeowner_add(door_opened, key, clean_frame, folder_path):
            # Reload the known faces and names as a new person has been added
            known_face_encodings, known_face_names = load_image(folder_path)

            # Reset flags to go back to detecting faces
            door_opened = False
            homeowner_ask = False

# GUI (Flet)

# Pass the camera instance to the add_clicked function
async def process_gui(page: ft.Page):
    global video_container, cap
    global open_button, add_button, delete_button, reset_button
    global open_button_container, add_button_container, delete_button_container, reset_button_container
    
    def show_bottom_sheet(page, message):
        bs = ft.BottomSheet(
            content=ft.Container(
                padding=50,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.Text(value=message),
                        ft.ElevatedButton("OK", on_click=lambda _: page.close(bs)),
                    ],
                ),
            ),
        )
        page.open(bs)
        # Ensure immediate update
        asyncio.run(page.update_async())

    def open_clicked(e):
        # Define the confirmation modal dialog
        def handle_modal_close(e):
            if e.control.text == "Yes":
                # Show a confirmation message in an alert dialog
                confirmation_dlg = ft.AlertDialog(
                    title=ft.Text("Door has been opened."),
                    actions=[
                        ft.TextButton("OK", on_click=lambda _: page.close(confirmation_dlg)),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.open(confirmation_dlg)  # Open the alert dialog
            else:
                # Show a cancellation message in an alert dialog
                confirmation_dlg = ft.AlertDialog(
                    title=ft.Text("Door remains closed."),
                    actions=[
                        ft.TextButton("OK", on_click=lambda _: page.close(confirmation_dlg)),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.open(confirmation_dlg)  # Open the alert dialog
            
            # Close the confirmation modal dialog
            page.close(dlg_modal)

        # Define the confirmation modal dialog
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please confirm"),
            content=ft.Text("Are you sure you want to open the door?"),
            actions=[
                ft.TextButton("Yes", on_click=handle_modal_close),
                ft.TextButton("No", on_click=handle_modal_close),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Open the confirmation modal dialog
        page.open(dlg_modal)

    def add_clicked(e, cap): 
        # Clear all controls before proceeding
        page.controls.clear()

        name_field = ft.TextField(label="Enter Name", width=310)

        def submit_handler(e):
            name = name_field.value
            if name:
                if not cap.isOpened():
                    show_bottom_sheet(page, "Error: Unable to access the webcam.")
                    return

                # Capture the current frame from the existing cap instance
                ret, frame = cap.read()
                if ret:
                    clean_frame = frame.copy()
                    file_path = path_from_name(name, folder_path)
                    cv2.imwrite(file_path, clean_frame)
                    show_bottom_sheet(page, f"Person added as {name}")
                    global known_face_encodings, known_face_names
                    known_face_encodings, known_face_names = load_image(folder_path)
                else:
                    show_bottom_sheet(page, "Error: Unable to capture image.")

                # Re-add the buttons after the process is done
                page.controls.clear()  # Clear all controls again
                # Center the video container and buttons
                button_row1 = ft.Row(
                    controls=[open_button_container, add_button_container],
                    alignment=ft.MainAxisAlignment.CENTER
                )
                button_row2 = ft.Row(
                    controls=[delete_button_container, reset_button_container],
                    alignment=ft.MainAxisAlignment.CENTER
                )
                main_column = ft.Column(
                    controls=[video_container, button_row1, button_row2],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )

                # Add the main column to the page
                page.add(main_column)
                page.update()
            else:
                show_bottom_sheet(page, "Error: No name entered.")

        # Add the input field and submit button to the page
        submit_button = ft.ElevatedButton("Submit", on_click=submit_handler)

        # Create a row for buttons and ensure the row is centered
        button_row = ft.Row(
            controls=[submit_button],
            alignment=ft.MainAxisAlignment.CENTER  # Ensure the button row is centered
        )

        # Organize the video container, dropdown, and button in a centered column
        main_column = ft.Column(
            controls=[video_container, name_field, button_row],
            alignment=ft.MainAxisAlignment.CENTER,  # Center the column vertically
            horizontal_alignment=ft.CrossAxisAlignment.CENTER  # Center the column horizontally
        )

        # Add the main column to the page
        page.add(main_column)
        page.update()  # Update the page to show the new elements        page.update()

    def delete_clicked(e):
        # Clear all buttons before proceeding
        page.controls.clear()  # Clear all controls from the page

        # Load the known face names for the dropdown menu
        known_face_encodings, known_face_names = load_image(folder_path)  # Assuming this function returns face names

        # Create a dropdown with all known face names
        dropdown = ft.Dropdown(
            label="Select Name to Delete",
            width=310,
            options=[ft.dropdown.Option(name) for name in known_face_names]
        )

        # Define the modal dialog
        def handle_modal_close(e):
            name = dropdown.value  # Get the selected name from the dropdown
            if e.control.text == "Yes":
                if delete_person(name, folder_path):  # Function to delete the person
                    known_face_encodings, known_face_names = load_image(folder_path)  # Reload face data
                    show_bottom_sheet(page, f"{name} deleted from the database")  # Show bottom sheet message
                    known_face_encodings, known_face_names
                    known_face_encodings, known_face_names = load_image(folder_path)
            else:
                show_bottom_sheet(page, f"{name} was not deleted from the database")  # Show bottom sheet message

            page.close(dlg_modal)  # Close modal dialog

            # Re-add the buttons after the process is done
            page.controls.clear()  # Clear all controls again
            # Center the video container and buttons
            button_row1 = ft.Row(
                controls=[open_button_container, add_button_container],
                alignment=ft.MainAxisAlignment.CENTER
            )
            button_row2 = ft.Row(
                controls=[delete_button_container, reset_button_container],
                alignment=ft.MainAxisAlignment.CENTER
            )
            main_column = ft.Column(
                controls=[video_container, button_row1, button_row2],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )

            # Add the main column to the page
            page.add(main_column)
            page.update()

        # Define the confirmation modal dialog
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please confirm"),
            content=ft.Text("Are you sure you want to delete this person?"),
            actions=[
                ft.TextButton("Yes", on_click=handle_modal_close),
                ft.TextButton("No", on_click=handle_modal_close),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Handler for the submit button
        def submit_handler(e):
            if dropdown.value:  # Ensure a name is selected from the dropdown
                page.open(dlg_modal)  # Open the modal dialog for confirmation
            else:
                show_bottom_sheet(page, "Please select a person to delete.")  # Show a message if no name is selected

        # Add the dropdown and submit button to the page
        submit_button = ft.ElevatedButton("Submit", on_click=submit_handler)

        # Create a row for buttons and ensure the row is centered
        button_row = ft.Row(
            controls=[submit_button],
            alignment=ft.MainAxisAlignment.CENTER  # Ensure the button row is centered
        )

        # Organize the video container, dropdown, and button in a centered column
        main_column = ft.Column(
            controls=[video_container, dropdown, button_row],
            alignment=ft.MainAxisAlignment.CENTER,  # Center the column vertically
            horizontal_alignment=ft.CrossAxisAlignment.CENTER  # Center the column horizontally
        )

        # Add the main column to the page
        page.add(main_column)
        page.update()  # Update the page to show the new elements

    def reset_clicked(e):
        # Clear all buttons before proceeding
        page.controls.clear()  # Clear all controls

        # Define the modal dialog for password reset confirmation
        def handle_modal_close(e):
            if e.control.text == "Yes":
                new_password = password_field.value
                if new_password:
                    # Show the result in an alert dialog
                    result_dlg = ft.AlertDialog(
                        title=ft.Text("Password has been updated."),
                        actions=[
                            ft.TextButton("OK", on_click=lambda _: page.close(result_dlg)),
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    page.open(result_dlg)  # Open the alert dialog with the success message
                else:
                    # This block should not be reached because we already check for empty password before opening modal
                    result_dlg = ft.AlertDialog(
                        title=ft.Text("Password has not been updated."),
                        actions=[
                            ft.TextButton("OK", on_click=lambda _: page.close(result_dlg)),
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    page.open(result_dlg)  # Open the alert dialog with the failure message
            else:
                # Show the result in an alert dialog
                result_dlg = ft.AlertDialog(
                    title=ft.Text("Password remains the same."),
                    actions=[
                        ft.TextButton("OK", on_click=lambda _: page.close(result_dlg)),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.open(result_dlg)  # Open the alert dialog with the success message
            
            page.close(dlg_modal)

            # Re-add the buttons after the process is done
            page.controls.clear()  # Clear all controls again
            # Center the video container and buttons
            button_row1 = ft.Row(
                controls=[open_button_container, add_button_container],
                alignment=ft.MainAxisAlignment.CENTER
            )
            button_row2 = ft.Row(
                controls=[delete_button_container, reset_button_container],
                alignment=ft.MainAxisAlignment.CENTER
            )
            main_column = ft.Column(
                controls=[video_container, button_row1, button_row2],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )

            # Add the main column to the page
            page.add(main_column)
            page.update()

        # Define the confirmation modal dialog
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please confirm"),
            content=ft.Text("Are you sure you want to reset the password?"),
            actions=[
                ft.TextButton("Yes", on_click=handle_modal_close),
                ft.TextButton("No", on_click=handle_modal_close),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Define the submit handler
        def submit_handler(e):
            new_password = password_field.value
            if new_password:
                # Open the modal dialog if a password is entered
                page.open(dlg_modal)
            else:
                # Show the bottom sheet if no password is entered
                show_bottom_sheet(page, "Please type in a password.")

        # Add the password input field and submit button to the page
        password_field = ft.TextField(label="Enter Password", width=310)
        # Add the dropdown and submit button to the page
        submit_button = ft.ElevatedButton("Submit", on_click=submit_handler)

        # Create a row for buttons and ensure the row is centered
        button_row = ft.Row(
            controls=[submit_button],
            alignment=ft.MainAxisAlignment.CENTER  # Ensure the button row is centered
        )

        # Organize the video container, dropdown, and button in a centered column
        main_column = ft.Column(
            controls=[video_container, password_field, button_row],
            alignment=ft.MainAxisAlignment.CENTER,  # Center the column vertically
            horizontal_alignment=ft.CrossAxisAlignment.CENTER  # Center the column horizontally
        )

        # Add the main column to the page
        page.add(main_column)
        page.update()  # Update the page to show the new elements        page.add(password_field, submit_button)


    button_width = 150
    # Create buttons
    open_button = ft.ElevatedButton(
        text="Open Door",
        on_click=open_clicked,
        bgcolor=ft.colors.RED_300,
        color=ft.colors.WHITE
    )
    add_button = ft.ElevatedButton(
        text="Add",
        on_click=lambda e: add_clicked(e, cap),
        bgcolor=ft.colors.RED_300,
        color=ft.colors.WHITE
    )
    delete_button = ft.ElevatedButton(
        text="Delete",
        on_click=delete_clicked,
        bgcolor=ft.colors.GREEN_300,
        color=ft.colors.WHITE
    )
    reset_button = ft.ElevatedButton(
        text="Reset Password",
        on_click=reset_clicked,
        bgcolor=ft.colors.BLUE_300,
        color=ft.colors.WHITE
    )

    # Create containers for buttons
    open_button_container = ft.Container(open_button, width=button_width)
    add_button_container = ft.Container(add_button, width=button_width)
    delete_button_container = ft.Container(delete_button, width=button_width)
    reset_button_container = ft.Container(reset_button, width=button_width)

    # Create a video container
    global video_container
    video_container = ft.Container(width=310, height=240)

    # Center the video container and buttons
    button_row1 = ft.Row(
        controls=[open_button_container, add_button_container],
        alignment=ft.MainAxisAlignment.CENTER
    )
    button_row2 = ft.Row(
        controls=[delete_button_container, reset_button_container],
        alignment=ft.MainAxisAlignment.CENTER
    )
    main_column = ft.Column(
        controls=[video_container, button_row1, button_row2],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # Add the main column to the page
    page.add(main_column)
    page.update()

    # Start video feed update task
    cap = cv2.VideoCapture(0)  # Initialize camera capture
    await update_frame(video_container, page, cap)

async def update_frame(video_container, page, cap):
    global open_button, add_button
    known_face_encodings, known_face_names = load_image(folder_path)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect faces in the current frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        # Initialize face detection status and name
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
            
        if not face_detected:
            open_button.disabled = False
            add_button.disabled = False
        else:
            open_button.disabled = True
            add_button.disabled = True

        # Convert the frame to an image that Flet can display
        _, buffer = cv2.imencode('.png', frame)
        img_str = base64.b64encode(buffer).decode('utf-8')
        video_container.content = ft.Image(src_base64=img_str)
        
        # Ensure the page updates immediately
        await page.update_async()

        # Wait for a short period to limit the frame rate (adjust for smoother video)
        await asyncio.sleep(0.005)

    cap.release()

###################################  

if __name__ == "__main__":

    runChoice = input("Would you rather Terminal or GUI?\nType in your choice\n")
    if runChoice.lower() == "terminal":
        processTerminal()
    elif runChoice.lower() == "gui":
        ft.app(target=process_gui)
    else:
        print("Please enter a valid choice")
    
    # Release the capture and close windows
    cam.release()
    cv2.destroyAllWindows()
