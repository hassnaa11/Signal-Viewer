# Multi-Channel Signal Viewer

This project involves developing a **desktop application** using Python and Qt to visualize and manipulate multi-port, multi-channel medical signals. The application is tailored for ICU environments, offering real-time interaction, advanced signal manipulation, and reporting features.


https://github.com/user-attachments/assets/37e83417-947d-4947-868d-e2aa1467ed8d


---

## Features

### 1. Signal Viewing

- **Load and Display Signals**:
  - Browse and open any signal file from the PC.
  - Support for various signal types (e.g., ECG, EMG, EEG) with examples of normal and abnormal signals.
  - Ability to connect to a website that streams real-time signals for plotting.
  

https://github.com/user-attachments/assets/88527858-7eb5-452d-8d95-401ef17a8f44


- **Two Main Graphs**:
  - Open different signals in two separate graphs with independent controls.
  - Link graphs for synchronized zooming, panning, and playback.

- **Non-Rectangular Graph**:
  - Supports non-rectangular signals displayed in cine mode.
  - The used data is for global temperature anomalies from 1850 to 2024.
  
  <p align="center">
    <img src="https://github.com/user-attachments/assets/e1477f87-40a2-4ba4-80d3-bb47b17fa762" width="65%" />
  </p>

---

### 2. Signal Playback and Manipulation

- **Cine Mode**: Real-time signal playback similar to ICU monitors.
- **User Controls**:
  - Change signal color.
  - Add labels or titles.
  - Show/hide specific signals.
  - Scroll/Pan in any direction.
  - Zoom in/out for detailed or overview visualization.
  - Pause, play, or rewind signals.

- **Drag and Drop**: Move signals between graphs seamlessly.

---

### 3. Signal Glue

- Combine parts of two signals using interpolation into a third graph.
- Customize parameters such as window size and gap/overlap.

---

### 4. Exporting & Reporting

- Generate snapshots and reports with statistics (mean, std, duration, min, max).
- Export reports as PDFs using programmatically generated content.
<p align="center">
  <img src="https://github.com/user-attachments/assets/f9918e12-27da-495b-b84f-ff926ae81e76" width="30%" />
  <img src="https://github.com/user-attachments/assets/8070bdad-d2cb-448c-a1e9-430428ef57cb" width="30%" />
  <img src="https://github.com/user-attachments/assets/2717d968-dde1-4430-b899-7a0757379e18" width="30%" />
</p>

---

## Usage
1. Install requirments:
```bash
pip install -r requirements.txt
```
2. Clone the repo:
```bash
git clone https://github.com/hassnaa11/Signal-Viewer.git
```
4. Run the program:
```bash
python program.py
``` 

