<img width=112 height=112 align="left" src="assets/logo.png" />
<h1>
    <div>NerfBaselines</div>

[![PyPI - Version](https://img.shields.io/pypi/v/nerfbaselines)](https://pypi.org/project/nerfbaselines/)
[![GitHub License](https://img.shields.io/badge/license-MIT-%2397ca00)](https://github.com/jkulhanek/nerfbaselines/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/nerfbaselines)](https://pepy.tech/project/nerfbaselines)
</h1>

NerfBaselines is a framework for **evaluating and comparing existing NeRF methods**. Currently, most official implementations use different dataset loaders, evaluation protocols, and metrics, which renders the comparison of methods difficult. Therefore, this project aims to provide a **unified interface** for running and evaluating methods on different datasets in a consistent way using the same metrics. But instead of reimplementing the methods, **we use the official implementations** and wrap them so that they can be run easily using the same interface.

Please visit the <a href="https://jkulhanek.com/nerfbaselines">project page to see the results</a> of implemented methods on dataset benchmarks.<br/>

### [Project Page + Results](https://jkulhanek.com/nerfbaselines)

## Getting started
Start by installing the `nerfbaselines` pip package on your host system.
```bash
pip install nerfbaselines
```
Now you can use the `nerfbaselines` cli to interact with NerfBaselines.

WARNING: the default installation only installs the core nerfbaselines package which does not depend on either PyTorch or JAX.
However, the LPIPS metric requires PyTorch to be installed and will be disabled otherwise. Similarly, if you install JAX and
have a GPU available, the dataloading and evaluation will be faster as some parts of the pipeline will be moved to GPU.
Therefore, we recommend installing the `extras` package by following the **Advanced installation** section.

The next step is to choose the backend which will be used to install different methods. At the moment there are the following backends implemented:
- **docker**: Offers good isolation, requires `docker` to be installed and the user to have access to it (being in the docker user group).
- **apptainer**: Similar level of isolation as `docker`, but does not require the user to have privileged access.
- **conda** (not recommended): Does not require docker/apptainer to be installed, but does not offer the same level of isolation and some methods require additional
dependencies to be installed. Also, some methods are not implemented for this backend because they rely on dependencies not found on `conda`.
- **python** (not recommended): Will run everything directly in the current environment. Everything needs to be installed in the environment for this backend to work.

The backend can be set as the `--backend <backend>` argument or using the `NERFBASELINES_BACKEND` environment variable.

## Advanced installation
The LPIPS metric requires PyTorch to be installed and will be disabled otherwise. Similarly, if you install JAX and
have a GPU available, the dataloading and evaluation will be faster as some parts of the pipeline will be moved to GPU.
In this section we describe how to install the packages required for LPIPS and accelerated dataloading.
We recommend this as the default installation (unless there is a reason for not installing PyTorch or JAX).
Select one of the following configurations:
- CPU-only install
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install jax[cpu]
pip install 'nerfbaselines[extras]'
```
- CUDA 11.8 install
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install jax[cuda11_pip]
pip install 'nerfbaselines[extras]'
```
- CUDA 12.1 install
```bash
pip install torch torchvision torchaudio
pip install jax[cuda12_pip]
pip install 'nerfbaselines[extras]'
```

## Downloading data
For some datasets, e.g. Mip-NeRF 360 or NerfStudio, the datasets can be downloaded automatically. You can specify the argument `--data external://dataset/scene` during training
or download the dataset beforehand by running `nerfbaselines download-dataset dataset/scene`.
Examples:
```bash
# Downloads the garden scene to the cache folder.
nerfbaselines download-dataset mipnerf360/garden

# Downloads all nerfstudio scenes to the cache folder.
nerfbaselines download-dataset nerfstudio

# Downloads kithen scene to folder kitchen
nerfbaselines download-dataset mipnerf360/kitchen -o kitchen
```

## Training
To start the training, use the `nerfbaselines train --method <method> --data <data>` command. Use `--help` argument to learn about all implemented methods and supported features.

## Rendering
The `nerfbaselines render --checkpoint <checkpoint>` command can be used to render images from a trained checkpoint. Again, use `--help` to learn about the arguments.

## Interactive viewer
Given a trained checkpoint, the interactive viewer can be launched as follows:
```bash
nerfbaselines viewer --checkpoint <checkpoin> --data <dataset>
```
Even though the argument `--data <dataset>` is optional, it is recommended, as the camera poses
are used to perform gravity alignment and rescaling for a better viewing experience.
Again, you can use the `--backend <backend>` flag or `NS_BACKEND=<backend>` environment variable to change the backend.

## Results
In this section, we present results of implemented methods on standard benchmark datasets. For detailed results, visit the project page:
[https://jkulhanek.com/nerfbaselines](https://jkulhanek.com/nerfbaselines)

### Mip-NeRF 360
Mip-NeRF 360 is a collection of four indoor and five outdoor object-centric scenes. The camera trajectory is an orbit around the object with fixed elevation and radius. The test set takes each n-th frame of the trajectory as test views.
Detailed results are available on the project page: [https://jkulhanek.com/nerfbaselines/mipnerf360](https://jkulhanek.com/nerfbaselines/mipnerf360)

| Method                                                                         |       PSNR |      SSIM |     LPIPS |        Time |   GPU mem. |
|:-------------------------------------------------------------------------------|-----------:|----------:|----------:|------------:|-----------:|
| [Zip-NeRF](https://jkulhanek.com/nerfbaselines/m-zipnerf)                      | **28.516** | **0.828** | **0.138** |  5h 30m 49s |    26.2 GB |
| [Mip-NeRF 360](https://jkulhanek.com/nerfbaselines/m-mipnerf360)               |   *27.670* |     0.792 |     0.196 |  7h 29m 42s |   127.0 GB |
| [Gaussian Splatting](https://jkulhanek.com/nerfbaselines/m-gaussian-splatting) |     27.439 |   *0.814* |   *0.180* |     22m 45s |    11.1 GB |
| [NerfStudio](https://jkulhanek.com/nerfbaselines/m-nerfacto)                   |     26.348 |     0.730 |     0.257 |   *19m 50s* | **3.8 GB** |
| [Tetra-NeRF](https://jkulhanek.com/nerfbaselines/m-tetra-nerf)                 |     25.468 |     0.670 |     0.352 | 17h 32m 35s |    13.4 GB |
| [Instant NGP](https://jkulhanek.com/nerfbaselines/m-instant-ngp)               |     24.899 |     0.673 |     0.355 |  **4m 16s** |   *5.6 GB* |


### Blender
Blender (nerf-synthetic) is a synthetic dataset used to benchmark NeRF methods. It consists of 8 scenes of an object placed on a white background. Cameras are placed on a semi-sphere around the object.
Detailed results are available on the project page: [https://jkulhanek.com/nerfbaselines/blender](https://jkulhanek.com/nerfbaselines/blender)

| Method                                                                         |       PSNR |      SSIM |     LPIPS |       Time |   GPU mem. |
|:-------------------------------------------------------------------------------|-----------:|----------:|----------:|-----------:|-----------:|
| [Zip-NeRF](https://jkulhanek.com/nerfbaselines/m-zipnerf)                      | **33.670** | **0.973** | **0.020** | 5h 21m 57s |    26.2 GB |
| [Gaussian Splatting](https://jkulhanek.com/nerfbaselines/m-gaussian-splatting) |   *33.308* |   *0.969* |   *0.023* |    *6m 6s* |   *3.1 GB* |
| [Instant NGP](https://jkulhanek.com/nerfbaselines/m-instant-ngp)               |     32.191 |     0.959 |     0.031 | **2m 23s** | **2.6 GB** |
| [Tetra-NeRF](https://jkulhanek.com/nerfbaselines/m-tetra-nerf)                 |     31.951 |     0.957 |     0.031 | 6h 53m 20s |    29.6 GB |
| [Mip-NeRF 360](https://jkulhanek.com/nerfbaselines/m-mipnerf360)               |     30.345 |     0.951 |     0.038 | 3h 29m 39s |   114.8 GB |
| [NerfStudio](https://jkulhanek.com/nerfbaselines/m-nerfacto)                   |     29.191 |     0.941 |     0.049 |     9m 38s |     3.6 GB |


### Nerfstudio
Nerfstudio Dataset includes 10 in-the-wild captures obtained using either a mobile phone or a mirror-less camera with a fisheye lens. We processed the data using either COLMAP or the Polycam app to obtain camera poses and intrinsic parameters.
Detailed results are available on the project page: [https://jkulhanek.com/nerfbaselines/nerfstudio](https://jkulhanek.com/nerfbaselines/nerfstudio)

| Method                                                                         |       PSNR |      SSIM |     LPIPS |       Time |   GPU mem. |
|:-------------------------------------------------------------------------------|-----------:|----------:|----------:|-----------:|-----------:|
| [Zip-NeRF](https://jkulhanek.com/nerfbaselines/m-zipnerf)                      | **24.815** | **0.798** | **0.178** | 5h 21m 41s |    26.2 GB |
| [Instant NGP](https://jkulhanek.com/nerfbaselines/m-instant-ngp)               |   *20.653* |     0.601 |     0.452 | **4m 33s** | **4.2 GB** |
| [NerfStudio](https://jkulhanek.com/nerfbaselines/m-nerfacto)                   |     20.064 |   *0.617* |   *0.353* |  *13m 30s* |   *4.8 GB* |
| [Gaussian Splatting](https://jkulhanek.com/nerfbaselines/m-gaussian-splatting) |          - |         - |         - |          - |          - |


## Implementation status
Methods:
- [x] Nerfacto
- [x] Instant-NGP
- [x] Gaussian Splatting
- [x] Mip-Splatting
- [x] Tetra-NeRF
- [x] Mip-NeRF 360
- [x] Zip-NeRF
- [x] CamP
- [x] TensoRF (Blender, LLFF datasets)
- [ ] Mip-NeRF
- [ ] NeRF

Datasets/features:
- [x] Mip-NeRF 360 dataset
- [x] Blender dataset
- [x] any COLMAP dataset
- [x] any NerfStudio dataset
- [x] automatic dataset download
- [x] interactive viewer
- [x] undistorting images for methods that do not support complex camera models (Gaussian Splatting)
- [x] logging to tensorboard, wandb
- [x] LLFF dataset (only supported in TensoRF now)
- [ ] Tanks and Temples
- [ ] HDR images support
- [ ] RAW images support
- [ ] handling large datasets
- [ ] loading/creating camera trajectories in the interactive viewer

## Contributing
Contributions are very much welcome. Please open a PR with a dataset/method/feature that you want to contribute. The goal of this project is to slowly expand by implementing more and more methods.

## License
This project is licensed under the MIT license.

## Thanks
A big thanks to the authors of all implemented methods for the great work they have done.
