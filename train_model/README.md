Примеры запуска команд, для обучения, в каждой папке  внутри `runs` есть файл README.md, где команда для запуска модели на обучение
```bash
yolo detect train name=baseline seed=42 workers=20 batch=24 data=shov.yml  epochs=1000 imgsz=1920 device=0,1 model=/home/simba9/pet/shov/runs/detect/baseline2/weights/last.pt

yolo detect train box=10 seed=42 workers=20 optimizer=AdamW batch=24 data=shov.yml  epochs=1000 imgsz=1080 device=0,1


yolo detect train box=9 seed=42 workers=20 optimizer=AdamW batch=24 data=shov_old.yml  epochs=1000 imgsz=1080 device=0,1



CUDA_VISIBLE_DEVICES=0 yolo detect train box=9 seed=42 workers=10 batch=12 optimizer=AdamW data=shov_adj.yml  epochs=1000 imgsz=1920

CUDA_VISIBLE_DEVICES=1 yolo detect train box=9 seed=42 workers=10 batch=12 optimizer=AdamW data=shov_geo.yml  epochs=1000 imgsz=1920



CUDA_VISIBLE_DEVICES=0 yolo detect train box=9 seed=42 workers=10 batch=12 optimizer=AdamW data=shov_int.yml  epochs=1000 imgsz=1920

CUDA_VISIBLE_DEVICES=1 yolo detect train box=9 seed=42 workers=10 batch=12 optimizer=AdamW data=shov_pro.yml  epochs=1000 imgsz=1920

CUDA_VISIBLE_DEVICES=0 yolo detect train box=9 seed=42 workers=10 batch=12 optimizer=AdamW data=shov_non.yml  epochs=1000 imgsz=1920 
```
