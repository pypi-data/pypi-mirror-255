#!/bin/bash

#git init
git add README.md example_numpy.py example_torch.py src tests requirements.txt
git rm src/cell_data_loader/slice_images_out.py src/cell_data_loader/cell_segmenter.py
git commit -m "First commit"
git branch -M main
git remote add origin https://github.com/mleming/CellDataLoader.git
git push -u origin main
