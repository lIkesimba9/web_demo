CUDA_VISIBLE_DEVICES=0 yolo detect train box=9 seed=42 workers=10 batch=12 optimizer=AdamW data=shov_adj.yml  epochs=1000 imgsz=1920

337 epochs completed in 1.281 hours.
Optimizer stripped from runs/detect/train/weights/last.pt, 6.5MB
Optimizer stripped from runs/detect/train/weights/best.pt, 6.5MB

Validating runs/detect/train/weights/best.pt...
Ultralytics YOLOv8.2.31 🚀 Python-3.11.9 torch-2.3.1+cu121 CUDA:0 (NVIDIA GeForce RTX 3090, 24257MiB)
Model summary (fused): 168 layers, 3005843 parameters, 0 gradients, 8.1 GFLOPs
Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100%|
all         37        153      0.808      0.797      0.832      0.365
Speed: 1.0ms preprocess, 4.8ms inference, 0.0ms loss, 1.4ms postprocess per image