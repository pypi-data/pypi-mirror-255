# ngs-analysis

Convenient analysis of sequencing reads that span multiple DNA or protein parts. For instance, given a library of protein variants linked to DNA barcodes, this tool can answer questions like:

- How accurate are the variant sequences, at the DNA or protein level?
- How frequently is the same barcode linked to two different variants?
- Which reads contain parts required for function (e.g., a kozak start sequence, or a fused protein tag)?

This kind of analysis often involves parsing raw sequencing reads for DNA and/or protein sub-sequences (parts), then mapping the parts to a reference of anticipated part combinations. Here the workflow is: 

1. Define how to parse reads into parts using plain text expressions (no code)
2. Parse your anticipated DNA sequences to generate a reference
3. Parse a batch of sequencing samples
4. Map the parts found in each read to the reference

It’s been tested with Illumina paired-end reads and Oxford Nanopore long reads. Under the hood it uses [NGmerge](https://github.com/jsh58/NGmerge) to merge paired reads and [MMseqs2](https://github.com/soedinglab/MMseqs2) for sequencing mapping. It is moderately performant: 1 million paired-end reads can be mapped to a reference of 100,000 variant-barcode pairs in ~1 minute.

# Workflow

A cartoon example with two reference sequences, each consisting of a variant linked to a barcode:

<img src="examples/sequences.png" alt="sequences" width="500"/>

Here's the analysis workflow and outputs:

<img src="examples/workflow.png" alt="analysis workflow" width="500"/>

Note that in the last two columns, the parsed variant is mapped to a reference variant defined by the barcode present in the same read, rather than all possible reference variants. Check out the [example notebook for paired end reads](examples/paired_reads/paired_read_example.ipynb) for details.

### **TL;DR**

Run `ngs-analysis --help` to see available commands.

1. Make an empty directory, add `config.yaml` and `samples.csv` based on the example.
2. Add `reference_dna.csv` with anticipated DNA sequences (including adapters).
3. Run `ngs-analysis setup`. Add `--clean` to start the analysis from scratch.
4. Check that `designs.csv` is accurate; if not, fix `config.yaml`.
5. 
    - If you have paired-end data, put it in `0_paired_reads/` and run `ngs-analysis merge_read_pairs <sample>`.
    - If you have single-end data (e.g., nanopore), put it in `1_reads/`.
6. Run `ngs-analysis parse_reads <sample>`. Check that `2_parsed/<sample>.parsed.pq` looks alright (with pandas, use `pd.read_parquet`)
7. Run `ngs-analysis map_parsed_reads <sample>`. Results are in `3_mapped/<sample>.mapped.csv`

# Simulation mode

Debugging complex read structures and experimental layouts can be tricky. For example, your `config.yaml` might parse reference sequences incorrectly, or samples might map to the reference in an unexpected way (e.g., if the same barcode is attached to different variants). 

Before running an analysis (or designing an experiment), you can simulate the results by defining `sample_plan.csv` and running `simulate_single_reads` or `simulate_paired_reads`, which have options to add simple random mutations and variable coverage per subpool.

Here's `sample_plan.csv` from the [paired read example](examples/paired_reads/sample_plan.csv). Note that "source" refers to the optional "source" column in `reference_DNA.csv`.

| sample | source | coverage |
| --- | --- | --- |
|  sample\_A | pool1 | 50 |
|  sample\_B | pool2 | 50 |
|  sample\_C | pool1 | 50 |
|  sample\_C | pool2 | 20 |
|  sample\_D | pool3 | 50 |

To analyze the simulated data, just add the `--simulate` flag to `merge_read_pairs`, `parse_reads`, `map_parsed_reads`, and `plot`. Results will be saved to `{step}/simulate/{sample}` rather than `{step}/{sample}`.


# Install

```bash
pip install ngs-analysis
```

Make sure that the `mmseqs` and `NGmerge` executables are available (NGmerge is only needed for paired reads). 

On Linux and Intel-based MacOS, you can use `conda install -c bioconda -c conda-forge mmseqs2 ngmerge`. On Apple Silicon `mmseqs` can be installed via Homebrew with `brew install mmseqs2`, and NGmerge can be installed [from source](https://github.com/jsh58/NGmerge?tab=readme-ov-file#compile), or via `brew install brewsci/bio/ngmerge`.

Tested on Linux and MacOS (Apple Silicon).

