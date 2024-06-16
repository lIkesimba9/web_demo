Model summary (fused): 168 layers, 3006623 parameters, 0 gradients, 8.1 GFLOPs
Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100%|██████████| 15/15 [00:02<00:00,  7.10it/s]
all        148        451      0.937      0.883      0.936      0.607
adj         48        206      0.934      0.883      0.937       0.53
int         41         48      0.852      0.792      0.846      0.508
geo        105        140       0.96      0.871      0.932      0.683
pro         26         40      0.969      0.925      0.972      0.605
non         13         17      0.969      0.941      0.992      0.708


yolo detect train box=9 seed=42 workers=20 optimizer=AdamW batch=10 data=shov_old.yml  epochs=1000 imgsz=1920 device=0,1
