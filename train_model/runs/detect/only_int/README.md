233 epochs completed in 0.718 hours.
Optimizer stripped from runs/detect/train/weights/last.pt, 6.5MB
Optimizer stripped from runs/detect/train/weights/best.pt, 6.5MB

Validating runs/detect/train/weights/best.pt...
Ultralytics YOLOv8.2.31 🚀 Python-3.11.9 torch-2.3.1+cu121 CUDA:0 (NVIDIA GeForce RTX 3090, 24257MiB)
Model summary (fused): 168 layers, 3005843 parameters, 0 gradients, 8.1 GFLOPs
Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100%|
all         31         45      0.931      0.598      0.768      0.361
Speed: 1.0ms preprocess, 4.3ms inference, 0.0ms loss, 0.7ms postprocess per image
Results saved to runs/detect/train
💡 Learn more at https://docs.ultralytics.com/modes/train

CUDA_VISIBLE_DEVICES=0 yolo detect train box=9 seed=42 workers=10 batch=12 optimizer=AdamW data=shov_int.yml  epochs=1000 imgsz=1920