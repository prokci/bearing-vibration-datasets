
# Bearing vibration datasets

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/) [![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A high-performance pipeline for loading, aggregating, normalizing, and splitting bearing vibration benchmark datasets with multi-label stratification.**

---

## Table of Contents
- [Features](#features)
- [Supported Datasets](#supported-datasets)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage & CLI Arguments](#usage--cli-arguments)
- [Docker Support](#docker-support)
- [Repository Structure](#repository-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Features
- **Callback-based Data Aggregation**: Automatic RPM filtering and bearing physical parameter mapping using domain-specific configurations.
- **Balanced Stratification**: Multi-label stratified group K-fold splitting (via `iterative-stratification`) that preserves fault and source distributions without data leakage.
- **Chunked Dataset Serialization**: Memory-efficient partitioned DataFrame pickles structured into train, validation, and test subsets.
- **Extensible Architecture**: Easily add new dataset parsers via the modular `Source/Source_aggregate/Bearing/Architectures` directory.

## Supported Datasets
The pipeline natively supports raw vibration data from the following benchmark repositories:
- **[CWRU](https://engineering.case.edu/bearingdatacenter/download-data-file)** (Case Western Reserve University)
- **[fm6xzxnf36-2](https://data.mendeley.com/datasets/fm6xzxnf36/2)**
- **[HUST](https://bmcresnotes.biomedcentral.com/articles/10.1186/s13104-023-06400-4)** (Huazhong University of Science and Technology)
- **[JNU](https://bmcresnotes.biomedcentral.com/articles/10.1186/s13104-023-06400-4)** (Jiangnan University)
- **[KAt](https://groups.uni-paderborn.de/kat/BearingDataCenter/)** (Paderborn University)
- **[MFPT](https://www.mfpt.org/fault-data-sets/)** (Machinery Failure Prevention Technology)
- **[Multi-domain](https://www.sciencedirect.com/science/article/pii/S235234092400903X)**
- **[SCA](https://data.mendeley.com/datasets/tdn96mkkpt/2)**
- **[hitwzc](https://github.com/hitwzc/Bearing-datasets)**
- **[XJTU-SY](https://biaowang.tech/xjtu-sy-bearing-datasets/)** (Xi'an Jiaotong University)

---

## Quick Start

Get up and running in under a minute using Docker:

```bash
# Clone the repository
git clone https://github.com/yourusername/bearing-vibration-datasets.git
cd bearing-vibration-datasets

# Build and run the pipeline with default settings
docker compose up --build
```

---

## Installation

### Prerequisites
- **Python 3.12+**
- **UnRAR tool**: Required for extracting `.rar` archives (e.g., KAt dataset). 
  - **Windows**: Install WinRAR and add the absolute path for `UnRAR.exe` in a `.env` file.
  - **Linux**: Install via package manager (`sudo apt-get install unrar`).

### Local Setup

1. Clone the repository and navigate to the project directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```
3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env to set UNRAR_TOOL
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage & CLI Arguments

You can run the download and preparation steps together or separately.

### Combined Execution
```bash
python download_and_prepare_bearing_data.py
```

### Separate Execution
```bash
# 1. Download raw datasets
python download_bearing_data.py --datasets CWRU HUST KAt

# 2. Process, stratify, and split
python prepare_bearing_data.py --datasets CWRU HUST KAt --n_chunks 5
```

### Available Arguments

| Argument                                | Default                 | Description                                                                                                                                                     |
| :-------------------------------------- | :---------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--datasets`                            | `['CWRU', 'HUST', ...]` | List of datasets to include from the supported list.                                                                                                            |
| `--n_chunks`                            | `5`                     | Number of balanced stratification chunks.                                                                                                                       |
| `--rng`                                 | `42`                    | Random seed for reproducible splitting.                                                                                                                         |
| `--n_signals_per_chunk_with_disbalance` | `200`                   | The stack size during the raw data aggregation phase. It must be smaller than `n_signals_per_chunk`, since signal lengths can vary significantly at this stage. |
| `--n_signals_per_chunk`                 | `5000`                  | Signals per stack during final split creation.                                                                                                                  |
| `--need_params`                         | `['zT', 'dT', ...]`     | Physical bearing parameters to calculate/map.                                                                                                                   |
| `--split_proportion`                    | `3 1 1`                 | Proportions for data splits (Train/Val/Test).                                                                                                                   |
| `--split_names`                         | `train validate test`   | Output folder names for the respective splits.                                                                                                                  |

#### Need params

| Parameter | Description | Type / Unit | Possible Values |
| :--- | :--- | :--- | :--- |
| **`dT`** | Diameter of the rolling element (ball or roller). | `float` (mm) | e.g., `7.94` |
| **`d0`** | Pitch circle diameter (diameter of the circle passing through the center of the rolling elements). | `float` (mm) | e.g., `38.5` |
| **`mT`** | Mass of a single ball or rolling body. | `float` (kg) | e.g., `0.0014` |
| **`zT`** | Total number of rolling elements (balls or rollers) in the bearing. | `int` | e.g., `8`, `9` |
| **`di`** | Inner race diameter (bore diameter). | `float` (mm) | e.g., `25.0` |
| **`de`** | Outer race diameter (outside diameter). | `float` (mm) | e.g., `52.0` |
| **`b`** | Contact angle between the rolling element and the raceway. | `float` (degrees) | e.g., `0.0`, `13.0` |
| **`rotation`** | Specifies which race is rotating relative to the load. | `str` | `internal`, `external` |
| **`rolling_body`** | The geometric type of the rolling element. | `str` | `ball`, `rolling` |
| **`type`** | The fundamental operating principle of the bearing. | `str` | `rolling`, `sliding` |
| **`accuracy`** | Indicates whether the parameter values are exact (from manufacturer specs) or mathematically approximated. | `bool` | `true`, `false` |
| **`slippage`** | Indicates whether the rolling element experiences slip during operation (affects fault frequency calculations). | `bool` | `true`, `false` |

#### Usage Example in CLI:
You can pass these parameters as a space-separated list to the `--need_params` argument when running the script:

```bash
python download_and_prepare_bearing_data.py --need_params dT d0 mT zT di de b rotation rolling_body type accuracy slippage
```
*(Note: The default value in the script is `['zT', 'dT', 'd0', 'rotation', 'rolling_body']`, so you only need to specify this argument if you want to override the defaults or add the extra metadata fields like `accuracy` and `slippage`.)*

---

## Docker Support

The project includes a fully configured `Dockerfile` and `docker-compose.yml` to ensure consistent environments, especially for handling system-level dependencies like `unrar` and `gcc`.

**Run with default settings:**
```bash
docker compose up --build
```

**Pass custom arguments:**
```bash
docker compose run --rm download_and_prepare_bearing_data --n_chunks 6 --split_proportion 4 1 1 --datasets CWRU MFPT
```
*Note: The `./data` directory is mounted as a volume, so your downloaded raw files and processed pickles will persist on your host machine.*

---

## Repository Structure

```text
├── download_and_prepare_bearing_data.py  # Main CLI entry point
├── prepare_bearing_data.py               # Data processing and stratification logic
├── Source/
│   ├── Download/                         # Dataset downloaders & HTML scrapers
│   ├── Source_aggregate/                 # Dataset architecture parsers & aggregator
│   │   ├── Bearing/Architectures/        # Specific parsers (CWRU, KAt, MFPT, etc.)
│   │   └── Callbacks/                    # RPM filtering & physical param mapping
│   └── Utils/                            # Multi-label stratification & chunk runners
├── DefectParamsDistribution/             # Bearing physical configs & metadata mapping
├── Lib_classes/                          # Stack builders, file architectures, logging
├── MyMath/                               # Signal processing & physical unit conversions
└── data/                                 # Raw external datasets & output serialized pickles
```

---

## Contributing

Contributions are welcome! If you want to add support for a new bearing dataset:
1. Fork the repository.
2. Create a new parser in `Source/Source_aggregate/Bearing/Architectures/`.
3. Create a new loader in `Source/Download` if there isn't a suitable one.
4. Register those in `Source/Source_aggregate/Bearing/BindClasses.py` and `Source/Download/download_spec.py`.
5. Submit a Pull Request.


---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.