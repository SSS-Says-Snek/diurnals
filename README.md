<p align="center">
    <img src="data/io.github.sss_says_snek.diurnals.svg" width="200" alt="Diurnals logo">
</p>
<h1 align="center">Diurnals</h1>
<p align="center">Receive a daily popup to notify about upcoming Todoist tasks. Simple and easy to configure</p>
<p align="center">
    <img alt="Static Badge" src="https://img.shields.io/badge/Python-%233776ab?style=for-the-badge&logo=python&logoColor=ffffff">
    <img alt="GitHub License" src="https://img.shields.io/github/license/SSS-Says-Snek/diurnals?style=for-the-badge">
    <img alt="GitHub Release" src="https://img.shields.io/github/v/release/SSS-Says-Snek/diurnals?style=for-the-badge">
    <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/SSS-Says-Snek/diurnals?style=for-the-badge">
    <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/SSS-Says-Snek/diurnals?style=for-the-badge">
</p>

## Installation

[![Get it on Flathub](https://flathub.org/api/badge?svg&locale=en)](https://flathub.org/apps/io.github.sss_says_snek.diurnals)

[![Packaging status](https://repology.org/badge/vertical-allrepos/diurnals.svg)](https://repology.org/project/diurnals/versions)

### Arch Linux (AUR)
You can install Diurnals with any AUR helper like `yay` or `paru`:
```
yay -S diurnals
```

### Manual Installation
To build Diurnals from source, the following dependencies is required:
- Meson (build dependency)
- Python
- Python libraries, whether installed from systemwide packages or from `pip`
    - `PyGObject`
    - `schedule`
    - `todoist_api_python`

Download the source, then run
```
meson setup build
sudo meson install -C build
```
