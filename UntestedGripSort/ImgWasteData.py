from ultralytics import YOLO
import numpy as np
import cv2

def TakePicture():
    webcamera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    #Take a picture
    success, captured_img = webcamera.read()
        
    return captured_img


def GetMVData(frame):
    #Function takes image input and outputs type_posi array for segregation section
    
    model = YOLO('best.pt')
    print(model.names)
    #0 for Battery
    #1 for E_Devices
    #2 for Alu_Can (Smart dustbin with Alu can segregation?)


    #Sample Frame
    


    results = model.predict(frame, classes=[0, 1, 2], conf=0.8, imgsz=640)

    print(results)

    # print(len(results[0].boxes)) A way to get total detected items

    #Sample of printing out data of detected boxes, tensor conversion needed
    #ID, coordinates and confidence level
    # print("ID", results[0].boxes[0].cls[0].item())
    # print("Coordinates", results[0].boxes[0].xyxy[0].tolist()) #x1, y1, x2, y2 format
    # print("Confidence:", results[0].boxes[0].conf.item()) #Confidence may become a feature to improve accuracy

    waste_type = [] #Store the waste types
    for current_box in results[0].boxes:
        waste_type.append(results[0].names[current_box.cls[0].item()]) #Translate ID into an English string
        
    print(waste_type) #For verification


    #Create type_posi array

    waste_symbol = []

    for waste in  waste_type:
        if waste == 'Battery':
            waste_symbol.append("B")
        elif waste == 'E_Devices':
            waste_symbol.append("E")
        elif waste == 'Alu_Can':
            waste_symbol.append("M")
        


    i = 0
    cen_x = []
    cen_y = []
    
    box_area = []
    
    for box in results[0].boxes:
        
        x_y = results[0].boxes[i].xyxy[0].tolist()
        
        # Calculate the center coordinates
        x1 = x_y[0]
        y1 = x_y[1]
        x2 = x_y[2]
        y2 = x_y[3]
        
        print("\n")
        print(f"Individual box for {results[0].names[box.cls[0].item()]}")
        print("x1", x_y[0])
        print("y1", x_y[1])
        print("x2", x_y[2])
        print("y2", x_y[3])
        print("\n")
        
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        
        #Calculate the area
        detected_area = int((x2 - x1)*(y2 - y1))

        cen_x.append(center_x)
        cen_y.append(center_y)
           
        box_area.append(detected_area)
        
        i += 1


    print("cen_x = ", cen_x)
    print("cen_y = ", cen_y)

    type_posi = np.vstack((waste_symbol, cen_x, cen_y, box_area))

    print("The resulting type_posi array")
    print(type_posi)

    return type_posi



#print(GetMVData(TakePicture()))