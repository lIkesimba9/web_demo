yolo detect train box=9 seed=42 workers=20 optimizer=AdamW batch=24 data=shov_old.yml  epochs=1000 imgsz=1080 device=0,1

Model summary (fused): 168 layers, 3006623 parameters, 0 gradients, 8.1 GFLOPs
Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100%|██████████| 7/7 [00:01<00:00,  5.43it/s]
all        148        451      0.941       0.88      0.935       0.59
adj         48        206      0.929      0.888      0.923      0.492
int         41         48      0.927      0.812      0.859      0.522
geo        105        140       0.96      0.861      0.939      0.669
pro         26         40       0.92        0.9      0.964      0.516
non         13         17      0.969      0.941      0.992      0.748


6	15.06.2024, 14:17 +03:00	0.8648825873387556