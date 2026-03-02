# คู่มือการติดตั้ง SAX-NeRF Web Application (ฉบับสมบูรณ์สำหรับ Windows 11)

> **สำหรับสเปค:** Intel Core i9-13900F | RAM 64GB | RTX 4070 12GB | SSD 1TB + HDD 9TB  

โครงสร้างโปรเจค AI มักถูกเขียนมาเพื่อทำงานบน **Linux** (มีไฟล์ `Makefile`, `setup.sh`, `HashEncoder` ที่ต้องใช้ C++ Compiler) ดังนั้น **วิธีที่เสถียร สเถียร และทรงพลังที่สุดในการรันโปรเจคนี้บน Windows 11 คือ การใช้ "WSL 2" (Windows Subsystem for Linux)** ครับ 

สเปคเครื่องคุณ **ระดับ Hi-End** รันงานนี้ได้ราบรื่นมากครับ! นี่คือขั้นตอนแบบจับมือทำ:

---

## 🛠️ Phase 1: เตรียมความพร้อมบน Windows (ฝั่งคนขับ)

### 1.1 อัปเดต NVIDIA Driver
- ให้แน่ใจว่าติดตั้ง **NVIDIA GeForce Game Ready Driver** หรือ **Studio Driver** เวอร์ชั่นล่าสุดบน Windows 11 แล้ว (ไม่ต้องติดตั้งอะไรเกี่ยวกับ NVIDIA ฝั่ง Linux เดี๋ยว Windows จัดการเชื่อมการ์ดจอ RTX 4070 เข้าระบบให้เอง)

### 1.2 ติดตั้ง WSL 2 (จำลอง Linux)
1. กดปุ่ม `Win` พิมพ์ `cmd` คลิกขวาที่ **Command Prompt** เลือก **Run as administrator**
2. พิมพ์คำสั่งนี้แล้วกด Enter:
   ```cmd
   wsl --install
   ```
3. รอจนเสร็จ แล้ว **Restart คอมพิวเตอร์** 1 ครั้ง
4. เมื่อเปิดขึ้นมา มันจะให้ตั้ง **Username** และ **Password** สำหรับระบบ Ubuntu (ตั้งสั้นๆ จำง่ายๆ เช่น User: `admin`, Pass: `1234` เพราะจะพิมพ์บ่อย)

### 1.3 การบริหารพื้นที่ (SSD 1TB vs HDD 9TB)
เนื่องจาก Model NeRF ต้องอ่านเขียนข้อมูลเร็วมาก:
- **ตัวโปรเจค โค้ด และ WSL2:** จะถูกเก็บอยู่บน **SSD 1TB** อัตโนมัติ (ดีที่สุด)
- **ไฟล์ .pickle และ .tar (รวมๆ ประมาณ 5-10GB):** ควรเก็บไว้ที่โฟลเดอร์ `data/` และ `pretrained/` ภายในโปรเจค (บน SSD) จะทำให้เปิดดูและรัน Inference ได้ทันที ไม่กระตุก
- **เก็บสำรอง (Backup):** ถ้าใช้เสร็จแล้วค่อยย้ายไฟล์ใหญ่ๆ ไปวางพักก้อนแช่ไว้ใน **HDD 9TB** 

---

## 🚀 Phase 2: เริ่มลุยฝั่ง Linux (ผ่าน WSL)

### 2.1 เปิดหน้าต่างรันงาน
1. กดปุ่ม `Win` พิมพ์ `Ubuntu` แล้วกดเปิดแอปพลิเคชัน
2. คุณจะเข้ามาสู่หน้าจอดำๆ ของเซิร์ฟเวอร์ (นี่คือระบบที่ RTX 4070 และ RAM 64GB ของคุณจะถูกดึงมาใช้แบบเต็มสูบ)

### 2.2 ติดตั้งระบบพื้นฐาน (Conda)
พิมพ์ทีละบรรทัดในหน้าต่าง Ubuntu:
```bash
# 1. โหลดตัวติดตั้ง
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# 2. เริ่มติดตั้ง (ให้กด Enter รัวๆ เพื่ออ่านข้อตกลง แล้วพิมพ์ 'yes' แล้ว Enter อีก)
bash Miniconda3-latest-Linux-x86_64.sh

# 3. รีเฟรชระบบให้รู้จักคำสั่ง conda
source ~/.bashrc
```

### 2.3 ติดตั้ง Git และ Build Tools พื้นฐาน
```bash
sudo apt update
sudo apt install -y git make build-essential
```

---

## 💻 Phase 3: ติดตั้งโปรเจค SAX-NeRF โฉมใหม่

### 3.1 Clone Project
```bash
# ดาวน์โหลดโปรเจคจาก GitHub ของคุณ
git clone https://github.com/Eakkachad/xray_to_3d.git

# เข้าไปในโฟลเดอร์โปรเจค
cd xray_to_3d
```

### 3.2 สั่งเสกโปรเจค 1 คลิก (Setup.sh)
มาถึงความดีงามของโครงสร้างใหม่ที่คุณเพิ่งอัปโหลด วันนี้คุณ**แค่สั่งรันคำสั่งเดียว** โค้ดจะจัดการสร้าง Environment, โหลด PyTorch 1.11, ติดตั้ง Node.js (pnpm) และลงทุกอย่างให้หมด:
```bash
bash setup.sh
```
> *(ขั้นตอนนี้อาจใช้เวลาสักพัก 5-10 นาที เพราะต้องโหลด Library เยอะมาก ปล่อยให้มันไหลไป)*

---

## 💾 Phase 4: เติม "สมอง" และ "ข้อมูล" (ดาวน์โหลดไฟล์ขนาดใหญ่)

ตัวโปรเจคโหลดมาทาง Git จะไม่มีไฟล์โมเดลที่ฝึกมาแล้ว (ไฟล์มันใหญ่มาก) คุณต้องโหลดมาใส่ด้วยตัวเอง

1. **โหลด Data (ไฟล์ `.pickle`)**
   - ไปที่: [Google Drive (Data)](https://drive.google.com/drive/folders/1SlneuSGkhk0nvwPjxxnpBCO59XhjGGJX)
   - โหลดมาแล้ว ใน Windows ให้เปิด File Explorer
   - ช่อง Address Bar พิมพ์ `\\wsl$\Ubuntu\home\ชื่อuserของคุณ\xray_to_3d\data`
   - ลากไฟล์ `.pickle` ทั้งหมด (เช่น chest_50.pickle) เข้าไปวาง

2. **โหลด Pretrained Models (ไฟล์ `.tar`)**
   - ไปที่: [Google Drive (Pretrained)](https://drive.google.com/drive/folders/1wlDrZQRbQENcfW1Pjrr1gasFQ8v6znHV)
   - เปิดโฟลเดอร์ใน Windows ไปที่ `\\wsl$\Ubuntu\home\ชื่อuserของคุณ\xray_to_3d\pretrained`
   - ลากไฟล์ `.tar` เข้าไปวาง

---

## 🎬 Phase 5: รัน Web App (ของจริงเริ่มแล้ว)

ทุกครั้งที่คุณต้องการเปิดเว็บนี้ให้คนอื่นดู ให้ทำตามนี้ครับ:

1. เปิดแอป **Ubuntu**
2. เข้าไปในโฟลเดอร์โปรเจค และปลุก environment ของเราขึ้นมา:
   ```bash
   cd xray_to_3d
   conda activate sax_nerf
   ```
3. สั่งรัน Backend (FastAPI) และ Frontend (React) พร้อมกัน:
   ```bash
   make dev
   ```

**เสร็จแล้ว! 🎉**
เปิดบราวเซอร์ใน Windows (Chrome / Edge) ของคุณ พิมพ์ Address:
👉 **[http://localhost:5173](http://localhost:5173)**

คุณจะเจอหน้าเว็บที่เพิ่งทำเสร็จ สามารถเลือกไขสันหลัง ปอด ซี่โครง มาลอง Reconstruction ด้วย i9 และ RTX 4070 ของคุณได้เลยครับ ผลลัพธ์ที่ได้จะไปปรากฎอยู่ในโฟลเดอร์ `output/web_cache` อัตโนมัติ (ครั้งแรกอาจใช้เวลาดึงแบบจำลองสักพัก แต่ครั้งต่อไปจะกดดูปุ๊บขึ้นปั๊บเลยครับ)
