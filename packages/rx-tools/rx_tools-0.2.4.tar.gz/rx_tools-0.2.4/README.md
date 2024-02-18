# Tools

This project contains the following tools:

[Getter of decay descriptors associated to a given decay file, more details](doc/descriptors.md).

[Getter of $`R_K`$ extracting model constraints](doc/model_constraints.md)

[Apply analysis selection with cluster jobs](doc/apply_selection.md)

[Get partially reconstructed PDFs](doc/prec_pdf.md)

[Get model for fit](doc/fit_model.md)

# Installation

Prepare a virtual environment (here called `tools`) with ROOT and python with:

```bash
mamba create -n tools root=6.28 python=3.9
mamba activate tools
```

and then install the project

```bash
ssh://git@gitlab.cern.ch:7999/r_k/tools.git
cd tools
git fetch 
git checkout dev_pip

pip install -e .
```

