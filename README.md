# Multi-Channel Signal Viewer

## Overview

The **Multi-Channel Signal Viewer** is a desktop application developed using **Python** and **Qt**. The application is designed for **real-time visualization** and manipulation of medical signals such as **ECG**, **EMG**, and **EEG**. This project is particularly targeted at environments like **ICUs** where healthcare professionals need to continuously monitor and analyze multiple medical signals from various sources.

The tool provides **multi-port** functionality, allowing multiple signals to be viewed and manipulated simultaneously. It also supports advanced features such as **signal linking**, **real-time playback**, **signal glueing**, and **report generation**.

https://github.com/user-attachments/assets/37e83417-947d-4947-868d-e2aa1467ed8d


---

## Features

### 1. Signal Viewing

- **Load and Display Signals**:
  - Browse and open any signal file from the PC.
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
  - Change signal color and label.
  - Show/hide specific signals.
  - Scroll/Pan in any direction.
  - Zoom in/out for detailed or overview visualization.
  - Pause, play, or rewind signals.

---

### 3. Signal Glue

- Combine parts of two signals using interpolation into a third graph.
- Customize parameters such as window size and gap/overlap.


https://github.com/user-attachments/assets/85b74bab-7972-4fc0-bcdc-b76c3b8f50cd


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

---

## Contributors

<table align="center" width="100%">
  <tr>
    <td align="center" width="33%">
      <a href="https://github.com/Emaaanabdelazeemm">
        <img src="https://github.com/Emaaanabdelazeemm.png?size=100" style="width:80%;" alt="Emaaanabdelazeemm"/>
      </a>
      <br />
      <a href="https://github.com/Emaaanabdelazeemm">Eman Abdelazeem</a>
    </td>
    <td align="center" width="33%">
      <a href="https://github.com/hassnaa11">
        <img src="https://github.com/hassnaa11.png?size=100" style="width:80%;" alt="hassnaa11"/>
      </a>
      <br />
      <a href="https://github.com/hassnaa11">Hassnaa Hossam</a>
    </td>
    <td align="center" width="33%">
      <a href="https://github.com/shahdragab89">
        <img src="https://github.com/shahdragab89.png?size=100" style="width:80%;" alt="shahdragab89"/>
      </a>
      <br />
      <a href="https://github.com/shahdragab89">Shahd Ragab</a>
    </td>
  </tr>
</table>

