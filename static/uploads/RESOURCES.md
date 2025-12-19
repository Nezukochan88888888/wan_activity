![](/static/uploads/wallpaperflare.com_wallpaper.jpg)
![](/static/uploads/WIN_20251204_07_24_52_Pro.mp4)

# **Local Classroom Activity Hub — Summary Plan**

## **1️⃣ Purpose / Goal**

- Create a **lightweight, offline-first classroom activity server**.
    
- Host PDFs, images, short videos, and instructions.
    
- Teacher controls which activities are active; students access via local Wi-Fi.
    
- Enable **group-based, paperless learning** without internet.
    

---

## **2️⃣ Devices & Network Setup**





|Device|Role|
|---|---|
|**Tecno Camon 30 Pro**|Wi-Fi hotspot (LAN access point)|
|**Laptop**|Runs Flask + Waitress server, serves static files|
|**4 Group Devices**|Students access activities via browser|

**Key points:**

- All devices must connect to the same hotspot.
    
- Server IP auto-detect and printed in console (e.g., `http://192.168.43.101:5000`).
    
- Only **4 groups**, so network traffic is very light.
    

---

## **3️⃣ Technology Stack**

- **Backend:** Python + Flask
    
- **Server:** Waitress (production-grade WSGI server)
    
- **Frontend:** HTML5 + Bootstrap (responsive UI)
    
- **State Management:** JSON or Python dictionaries (no heavy DB)
    
- **Static Resources:** `/static` folder for PDFs, images, short videos
    
- **Networking:** Local IP hosting over phone hotspot
    

---

## **4️⃣ Functional Features**

### **Teacher/Admin Dashboard (/admin)**

- Password-protected
    
- Activity Management:
    
    - Toggle activities ON/OFF
        
    - Optional group-specific instructions
        
- File Upload:
    
    - PDFs, images, videos
        
    - Stored in `/static`
        
- Status Monitor:
    
    - See which groups are connected (simple JSON / timestamp tracking)
        

### **Student/Group Interface**

- Zero-login: select “Group Number” from dropdown
    
- View only **active tasks**
    
- Access resources:
    
    - PDFs, images, short videos
        
    - Fast local loading (LAN)
        
- Optional group-specific content
    

---

## **5️⃣ Video & File Guidelines**

- Videos: MP4 (H.264 + AAC), 480p–720p, short (≤3 min), 10–50 MB
    
- PDFs/images: high-resolution, optimized for quick local loading
    
- Preload videos for smooth playback
    
- Avoid large / long files to prevent hotspot overload
    

---

## **6️⃣ Server / Performance Considerations**

- **Waitress > Werkzeug**:
    
    - Handles multiple concurrent requests
        
    - Prevents blocking when multiple devices load content simultaneously
        
- Only 4 clients → very low load
    
- Phone hotspot can easily support 4–5 devices
    
- Keep phone plugged in, disable hotspot auto-off
    

---

## **7️⃣ Recommended Development Workflow**

1. Start with **simple Flask starter** repo
    
2. Add:
    
    - `/admin` route + password
        
    - File upload UI
        
    - JSON-based state for activities and connected groups
        
    - Student group selection
        
3. Serve static files from `/static` (PDFs, images, short videos)
    
4. Run via **Waitress**:
    
    `waitress-serve --host=0.0.0.0 --port=5000 app:app`
    
5. Test over your hotspot:
    
    - Connect laptop + 4 devices
        
    - Open the server URL on student devices
        
    - Confirm activity toggle and media playback work smoothly
        

---

## **8️⃣ Backup / Contingency**

- Print or display IP URL in case a student mistypes it
    
- Optional fallback:
    
    - GIFs or images instead of videos for critical instructions
        
    - PDFs as backup if video fails
        

---

## **9️⃣ Next Steps**

- Build **minimal Flask + Waitress starter project**
    
- Implement admin dashboard + group logic
    
- Test short video playback with 4 devices over phone hotspot
    
- Optionally compress videos for speed
    
- Deploy in classroom
    

---

If you want, I can **also draft a ready-to-run Flask + Waitress starter code** for this exact setup, with:

- Admin dashboard
    
- Group selection
    
- File serving (PDF/image/video)
    
- Activity toggle