# hVAE - backbone

This repository contains:
- customizable backbone implementation of hVAE
- reuseable hVAE components such as blocks, layers, losses, etc.
- training, evaluation and analyzation scripts
- checkpoint handling (using  [Weights & Biases](https://wandb.ai/site))


## Installation
```bash
pip install hvae_backbone
```

## Usage
This repository is intended to be used as a backend package.  
Please refer to  [hvae template](https://github.com/lacykaltgr/hvae) repository for usage instructions.


## Project Structure

```
├── hvae_backbone
│   ├── elements
│   │   ├── __init__.py             
│   │   ├── data_preproc.py         # Modules for data preprocessing
│   │   ├── dataset.py              # Base dataset class
│   │   ├── distributions.py        # Distributions, distributions generation
│   │   ├── layers.py               # Layers for building models
│   │   ├── losses.py               # Loss functions
│   │   ├── nets.py                 # Network architectures
│   │   ├── optimizers.py           # Optimizers
│   │   ├── schedules.py            # Schedules e.g. LR, KL weight
│   ├── __init__.py                 # package level scripts
│   ├── analysis.py                 # Analysis tools for trained models
│   ├── block.py                    # Blocks for building hierarchical models
│   ├── checkpoint.py               # Checkpoint handling (save, load)
│   ├── functional.py               # Functional scripts (training, loss, etc.)
│   ├── hvae.py                     # General hVAE class
│   ├── sequence.py                 # General sequential hVAE class
│   ├── utils.py                    # Utility functions
```


# TODO:
- callbacks
- preprocessing
- sample vs rsmaple blokkoknál (SimpleGenBlock)
- weight initialization
