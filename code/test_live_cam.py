import cv2
from ultralytics import YOLO

model = YOLO('marker_ui_best.pt')
#model = YOLO('best.onnx')

print(model.names)
webcamera = cv2.VideoCapture(0)
# webcamera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
# webcamera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

while True:
    success, frame = webcamera.read()
    
    results = model.track(frame, classes=[0,1,2,3,4,5,6,7,8,9], conf=0.1, imgsz=640, verbose=False)
    cv2.putText(frame, f"Total: {len(results[0].boxes)}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    cv2.imshow("Live Camera", results[0].plot())

    #print (results[0])

    if cv2.waitKey(1) == ord('q'):
        break

webcamera.release()
cv2.destroyAllWindows()