40 epochs completed in 0.761 hours.
Optimizer stripped from runs/detect/train/weights/last.pt, 6.7MB
Optimizer stripped from runs/detect/train/weights/best.pt, 6.7MB

Validating runs/detect/train/weights/best.pt...
Ultralytics YOLOv8.2.31 🚀 Python-3.11.9 torch-2.3.1+cu121 CUDA:0 (NVIDIA GeForce RTX 3090, 24257MiB)
Model summary (fused): 168 layers, 3005843 parameters, 0 gradients, 8.1 GFLOPs
Class     Images  Instances      Box(P          R      mAP50  m
all         16         19      0.878      0.789      0.827      0.555
Speed: 1.0ms preprocess, 4.6ms inference, 0.0ms loss, 0.4ms postprocess per image
Results saved to runs/detect/train
💡 Learn more at https://docs.ultralytics.com/modes/train

CUDA_VISIBLE_DEVICES=0 yolo detect train box=9 seed=42 workers=10 batch=12 optimizer=AdamW data=shov_non.yml  epochs=1000 imgsz=1920