from ultralytics import YOLO

model = YOLO("Soft-Eng---Robot-/ball_tracking.pt")

# Export to ONNX with pinned opset and static input dimensions
model.export(format="onnx", imgsz=640, opset=12, dynamic=False, simplify=True)