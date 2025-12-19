Role: Senior EdTech Developer. Task: Create a "Classroom Hub Auto-Installer" Python script.



Project Requirements:



The Script's Job: When run, this script must programmatically create the following structure:



/templates/index.html (Student Portal)



/templates/admin.html (Teacher Dashboard)



/static/uploads/ (Folder for media)



app.py (The main Flask/Waitress server)



settings.json (Default state: Activity toggles OFF)



Server Specs (app.py):



Use Waitress for multi-threaded local streaming.



Auto-IP Detection: Use socket to find the LAN IP and print a large, clear console banner with the Student URL (e.g., http://192.168.43.101:5000).



Routes: - /: Student view. Shows Group Selection (1-4). Displays PDF/Video ONLY if toggled ON in settings.json.



/admin: Password-protected (default: admin123). Controls toggles and a "Teacher's Announcement" text area.



UI Specs (HTML):



Use Bootstrap 5. (Add a fallback note in the UI: "Requires internet for initial CSS load, or save bootstrap.min.css to /static for 100% offline use").



Responsive design for mobile/tablet student devices.



Video player should be mobile-friendly with playsinline.



Output Format: Provide ONE SINGLE Python script that handles all file creation and includes the full code for the Flask app within it as string variables.

