[[_TOC_]]

# Description

# Installation

Do:

```
git clone ssh://git@gitlab.cern.ch:7999/acampove/scripts.git

cd scripts

./install.sh
```

to get all the modules and binaries installed (symbolic links will be made). They will go to:

| Type           | Path                  | Environment variable |
|----------------|-----------------------|----------------------|
| Binary         | `$HOME/.local/bin`    | `PATH`               |
| Python modules | `$HOME/.local/python` | `PYTHONPATH`         |
| Config files   | `$HOME/`              | NA                   |

where, for instance, the environment variable needs to be set in `~/.bashrc` as:

```bash
export PATH=$HOME/.local/bin/
```

for the first path.

# Usage

## Python modules

They should be ready to be used as:

```python
import utils
```

for instance.

## Statistics

[Covariance calculator](doc/covariance.md)   
[Negative log likelihood plotter](doc/nll_plt.md)   
## Other utilities

These live in the `zutils/utils.py` module and can be used to:

### Print PDFs

```python
import zutils.utils      as zut

zut.print_pdf(mod_ee, d_const=d_const ,txt_path='./pdf.txt')
```
where `d_const` is a mapping between the name of the parameter and `[mu, error]`.

## File system

[Symbolic link maker](doc/link_files.md)

[Held jobs manager](doc/held_jobs.md)

[Transfer ntuples to LXPLUS from IHEP](doc/tuple_transfer.md)

[TAR directory sctructure with a given type of files](doc/tar_plots.md)

[Check file size](doc/check_size.md)