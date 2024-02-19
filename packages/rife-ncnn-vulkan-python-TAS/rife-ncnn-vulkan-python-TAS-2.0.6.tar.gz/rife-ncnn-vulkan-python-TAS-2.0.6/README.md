This is but a minimalist version of rife-ncnn-vulkan with updated models for my script.
it will contain the latest models + rife4.6 for speedy inference, head to releases to download the wheels.
Windows only cuz I cba to figure out why Mac and Linux won't build.

Credit to the creators and maintainers

Install through pypi
```bash
pip install rife-ncnn-vulkan-python-TAS
```

## Introduction
[rife-ncnn-vulkan](https://github.com/nihui/rife-ncnn-vulkan) is nihui's ncnn implementation of Real-Time Intermediate Flow Estimation for Video Frame Interpolation.

rife-ncnn-vulkan-python wraps [rife-ncnn-vulkan project](https://github.com/nihui/rife-ncnn-vulkan) by SWIG to make it easier to integrate rife-ncnn-vulkan with existing python projects.

## Original RIFE Project

- https://github.com/hzwer/arXiv2020-RIFE

## Other Open-Source Code Used

- https://github.com/Tencent/ncnn for fast neural network inference on ALL PLATFORMS
- https://github.com/webmproject/libwebp for encoding and decoding Webp images on ALL PLATFORMS
- https://github.com/nothings/stb for decoding and encoding image on Linux / MacOS
- https://github.com/tronkko/dirent for listing files in directory on Windows
- https://github.com/nihui/rife-ncnn-vulkan the original rife-ncnn-vulkan project
