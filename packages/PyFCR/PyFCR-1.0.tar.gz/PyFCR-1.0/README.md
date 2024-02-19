# FRAILTY-BASED COMPETING RISKS MODEL FOR MULTIVARIATE SURVIVAL DATA 
A Python package for frailty-based multivariate survival data analysis with competing risks.

[Danielle Poleg](https://github.com/DaniellePoleg), [Malka Gorfine](https://www.tau.ac.il/~gorfinem/) 2023

[Documentation](https://TODO)  - TODO- add here link to pdf / other documentation 

## Installation
```console
pip install XXXXX - TODO - create a pip install for my project - pyFCRM
```

## Quick Start
This package has 2 options to run:
- "simulation" run to examine the model's performance
- "analysis" run to evaulate the model on an existing data set. If this is the desired option, please add the data files in the data directory, and see the README there. 

```python
from BiometricsModel.Biometrics import BiometricsDataModel, BiometricsRunner, BiometricsMultiRunner

def main(is_simulation=True):
    model = BiometricsDataModel()
    runner = BiometricsRunner(model)
    multi_runner = BiometricsMultiRunner(runner)
    if is_simulation:
        multi_runner.run_multiple_simulations()
        multi_runner.print_summary()
    else:
        runner.run()
        multi_runner.analyze_statistical_results(n_simulations=model.n_bootstrap, empirical_run=True, should_print=True)

if __name__ == '__main__':
    main(True)
```

## Citations
If you found PyDTS software useful to your research, please cite the papers:

```bibtex
@article{
}

```

## How to Contribute
1. Open Github issues to suggest new features or to report bugs\errors
2. Contact Danielle if you want to add a usage example to the documentation 
3. If you want to become a developer (thank you, we appreciate it!) - please contact Danielle for developers' on-boarding 

Danielle Poleg: daniellepoleg@gmail.com