import cv2
import cv2.aruco as aruco
import numpy as np
import serial
import time
ser = serial.Serial(port='COM4', baudrate=250000, timeout=.1)           #ใส่ address port ให้ถูก วิธีดู port ใน raspi คือ lsusb ดูว่าอันไหน Arduino ใส่เเทนตรงคำว่า COM4

# เปิดกล้อง (ใช้กล้องหลัก)
cap = cv2.VideoCapture(0)  # 0 หมายถึงกล้องตัวแรก ถ้าต้องการใช้กล้องตัวอื่นสามารถเปลี่ยนหมายเลขได้

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# กำหนด dictionary ของ ArUco marker ที่จะใช้
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters()

# สร้างอินสแตนซ์ของ ArucoDetector
detector = aruco.ArucoDetector(aruco_dict, parameters)

# กำหนดขนาดและตำแหน่งของกรอบที่ใช้ตรวจจับ (เช่น กำหนดกรอบไว้กลางภาพ)
frame_width = 640
frame_height = 480
bounding_box = (0, 100, 640, 100)  # (x, y, width, height)

# ตัวแปรนับจำนวน markers ID 1 ที่อยู่ในกรอบ
id_0_count_in_box = 0
id_1_count_in_box = 0
id_2_count_in_box = 0
total_id = 0
seen_ids = set()  # เซ็ตเก็บ id ที่เคยตรวจพบแล้ว

while True:
    # อ่านภาพจากกล้อง
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    # วาดกรอบที่ต้องการตรวจจับ
    cv2.rectangle(frame, (bounding_box[0], bounding_box[1]),
                  (bounding_box[0] + bounding_box[2], bounding_box[1] + bounding_box[3]), (0, 0, 255), 2)

    # ตรวจจับ markers
    marker_corners, marker_ids, rejected_candidates = detector.detectMarkers(frame)

    # ถ้าไม่เจอ ID 1 ในเฟรมนี้ ให้รีเซ็ตการนับ
    if marker_ids is None or 1 not in marker_ids:
        seen_ids.discard(1)

    # กำหนดสีกรอบ (เช่น สีแดง)
    border_color = (0, 0, 255)  # สีแดงใน BGR format

    # วาดกรอบที่ตรวจจับได้ด้วยสีที่กำหนด
    frame_markers = aruco.drawDetectedMarkers(frame, marker_corners, marker_ids, borderColor=border_color)

    # ตรวจสอบว่า ArUco marker ID 1 อยู่ภายในกรอบที่วาดหรือไม่
    if marker_ids is not None:
        for i in range(len(marker_corners)):
            # ตรวจสอบว่า marker อยู่ในกรอบที่กำหนดหรือไม่
            marker_center = np.mean(marker_corners[i], axis=0)  # หาจุดกึ่งกลางของ marker
            x, y = int(marker_center[0][0]), int(marker_center[0][1])

            # เช็คว่า (x, y) ของ marker อยู่ในกรอบหรือไม่
            if bounding_box[0] <= x <= bounding_box[0] + bounding_box[2] and bounding_box[1] <= y <= bounding_box[1] + bounding_box[3]:
                # ตรวจสอบว่า ID ของ marker เป็น 1 หรือไม่
                for marker_id in marker_ids.flatten():  # แปลงเป็น 1D array
                    if marker_id == 0 and marker_id not in seen_ids:
                        command="1"
                        ser.write(command.encode())  # ส่งข้อมูลไปยัง Arduino
                        seen_ids.add(marker_id)
                        id_0_count_in_box += 1  # เพิ่มจำนวนเมื่อเจอ ID 1 ใหม่
                        cv2.putText(frame_markers, f"ID {marker_id} inside box", (x - 50, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    if marker_id == 1 and marker_id not in seen_ids:
                        command = "2"
                        ser.write(command.encode())  # ส่งข้อมูลไปยัง Arduino
                        seen_ids.add(marker_id)
                        id_1_count_in_box += 1  # เพิ่มจำนวนเมื่อเจอ ID 1 ใหม่
                        cv2.putText(frame_markers, f"ID {marker_id} inside box", (x - 50, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    if marker_id == 2 and marker_id not in seen_ids:
                        command = "3"
                        ser.write(command.encode())  # ส่งข้อมูลไปยัง Arduino
                        seen_ids.add(marker_id)
                        id_2_count_in_box += 1  # เพิ่มจำนวนเมื่อเจอ ID 1 ใหม่
                        cv2.putText(frame_markers, f"ID {marker_id} inside box", (x - 50, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # แสดงจำนวน markers ID 1 ที่อยู่ในกรอบ
    text = f"Markers ID 0 in box: {id_0_count_in_box}"
    cv2.putText(frame_markers, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 255, 0), 1, cv2.LINE_AA)
    text = f"Markers ID 1 in box: {id_1_count_in_box}"
    cv2.putText(frame_markers, text, (10, 45), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 255, 0), 1, cv2.LINE_AA)
    text = f"Markers ID 2 in box: {id_2_count_in_box}"
    cv2.putText(frame_markers, text, (10, 55), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 255, 0), 1, cv2.LINE_AA)
    text = f"Totalx: {total_id}"
    cv2.putText(frame_markers, text, (10, 65), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 255, 0), 1, cv2.LINE_AA)

    # แสดงผลภาพ
    cv2.imshow('Detected ArUco Markers - Camera', frame_markers)

    # ออกจากลูปเมื่อกดปุ่ม 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ปิดการใช้งานกล้องและหน้าต่าง
cap.release()
cv2.destroyAllWindows()
