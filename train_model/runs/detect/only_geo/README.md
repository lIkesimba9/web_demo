CUDA_VISIBLE_DEVICES=1 yolo detect train box=9 seed=42 workers=10 batch=12 optimizer=AdamW data=shov_geo.yml  epochs=1000 imgsz=1920

Validating runs/detect/train2/weights/best.pt...
Ultralytics YOLOv8.2.31 🚀 Python-3.11.9 torch-2.3.1+cu121 CUDA:0 (NVIDIA GeForce RTX 3090, 24260MiB)
Model summary (fused): 168 layers, 3005843 parameters, 0 gradients, 8.1 GFLOPs
Class     Images  Instances      Box(P          R      mAP50  m
all         83        105      0.967      0.895      0.946      0.537
Speed: 0.7ms preprocess, 4.4ms inference, 0.0ms loss, 0.5ms postprocess per image