# 📡 Local File Transfer Tool

This is a simple Python-based tool for sending and receiving files over a **local network** (LAN). The tool can operate in two modes: **sender** or **receiver**. Devices automatically scan the network for available peers and establish direct TCP connections.

---

## ✨ Features

- 🔍 Auto-discovers devices on the same local network.
- 📁 Send files of any size using chunked transfer.
- 🔒 Confirms file transfers before downloading.
- 📊 Displays real-time progress bars with time estimates.
- 🎨 Colorized terminal output using `colorama`.

---

## 📷 Screenshots

### 🖥️ Receiver Waiting for Files  

<img width="800" alt="image" src="https://github.com/user-attachments/assets/3d21d50c-be43-47d7-9be6-fb2386438452" />

---

### 📤 Sending a File  

<img width="800" alt="image" src="https://github.com/user-attachments/assets/1b6bc2ae-a2f0-4113-95f6-7ccddcb699d6" />


---

## 🚀 How to Use

### 1. Install Requirements

```bash
pip install colorama
