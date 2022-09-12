
Test datasets and files for testing the [segmentation gym](https://github.com/Doodleverse/segmentation_gym) program

Dataset consists of a time-series of Landsat-8 images of Cape Hatteras National Seashore, courtesy of the U.S. Geological Survey. Imagery spans the period February 2015 to September 2021.


```{sh}
/Users/Someone/my_segmentation_gym_datasets
                    │   ├── config
                    │   |    └── *.json
                    │   ├── capehatteras_data
                    |   |   ├── fromDoodler
                    |   |   |     ├──images
                    |   │   |       └── *.jpg
                    │   |   |     └──labels
                    |   │   |       └── *.jpg
                    |   |   ├──npzForModel
                    |   │       └── *.npz                    
                    │   |   └──toPredict
                    |   │       └── *.jpg
                    │   └── modelOut
                    │       └── *.png
                    │   └── weights
                    │       └── *.h5

```

Download this file and unzip to your machine, then see [segmentation gym wiki](https://github.com/Doodleverse/segmentation_gym/wiki) for further explanation
