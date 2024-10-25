# Circos for MAGs

This command line tool provides and easy-to-use interface for creating Circos plot for a MAG.


## Installation

This package requires [Circos](https://circos.ca), [Prokka](https://github.com/tseemann/prokka), and (optionally, be recommended) [Samtools](https://www.htslib.org) to be installed on your system. The easiest and recommend method for installing Circos and Prokka is to use [Conda](https://docs.conda.io/projects/conda/en/latest/index.html):

```
> conda create -n circos_mag -c bioconda circos prokka
```

This creates a Conda environment named `circos_mag` that must be activate before running this tool:
```
> conda activate circos_mag
```

You can also (optionally) install Samtools using Conda. This should be installed in its own environment since it has conflicting dependencies with Circos:
```
> conda create -n samtools -c bioconda samtools
```

This tool can be installed by downloading and uncompressing the software as follows:
```
> wget https://github.com/Koonkie-Cloud-Services/circos_mag/archive/refs/tags/1.0.0.tar.gz
> tar -xvzf 1.0.0.tar.gz
```

You can test the installation using the data in the `example` directory:
```
> cd circos_mag-1.0.0
> ./bin/circos_mag plot --genome_file ./example/GCA_016214285.1_ASM1621428v1_genomic.fna.gz --gff_file ./example/GCA_016214285.1.gff --coverage_file ./example/coverage.tsv.gz --completeness 96.0 --output_dir ~/tmp/test_install
```

## Usage

The typical workflow for generating a Circos plot of your MAG is as follows:
 1. Get the genomic FASTA file for your MAG
 2. Run Prokka on your MAG to identify the 5S/16S/23S rRNA and tRNA genes in your MAG (<i>note</i>: Prokka only accepts uncompressed files):
 ```
> conda activate circos_mag
> prokka --outdir prokka --prefix example_name example_mag.fna
 ```
 4. Run samtools to get coverage information from the BAM file produced while recoverying your MAG (optional, but recommended):
 ```
> conda activate samtools
> samtools depth -a example.bam > coverage.tsv
 ```
 5. Generate the Circos plot:
 ```
> conda activate circos_mag
> ./bin/circos_mag plot --genome_file example_mag.fna --gff_file ./prokka/example_name.gff --coverage_file coverage.tsv --completeness <estimate for your MAG> --output_dir <out_dir>
 ```

## Output files

This tools produces the following output files:
 - `circos.png`: raster PNG file of the Circos plot
 - `circos.svg`: vector SVG file of the Circos plot
 - `genome_stats.tsv`: plain text file with common statistics about your MAG
 - `circos`: directory containing the configuration and data files used by Circos

You can tweak the Circos plot by modifying the data in the `circos` directory and then regenerating the Circos plots using:
```
> circos --config ./circos/circos.conf
```

## Interpreting the Circos plot

The Circos plot produced by this tool consists of a number of rings that visually indicate the quality of a MAG:
 - __Ring 1__: Displays the contigs comprising a MAG in green. An additional red contig indicates the estimated amount of DNA missing from the MAG as set with the optional `--completeness` parameter. For contigs > 5kb, tick markers are drawn to indicate the length of the contig with units in kilobases.
 - __Ring 2__: Displays the deviation in GC content of 1000 bp windows from the mean GC of the entire MAG. This background of this ring has 3 positive and negative bands that go from grey to white and each indicate a +/-5% GC deviations. For eample, windows reaching the last band in white have a GC deviation >10% from the mean GC. The window size can be changed with `--gc_window_size` parameter. 
 - __Ring 3__: Displays the location of 5S (square), 16S (triangle), and 23S (circle) rRNA genes indentified in the MAG as grey shapes.
 - __Ring 4__: Displays the location of tRNA genes identified in the MAG as dark red rhombi (i.e. diamonds).
 - __Ring 5__: Displays the deviation in coverage of 1000 bp windows from the mean coverage of the entire MAG. This background of this ring has 3 positive and negative bands that go from grey to white and each indicate a 100% coverage deviations. For eample, windows reaching the last band in white have a coverage that is >200% from the mean coverage. The window size can be changed with `--cov_window_size` parameter. 

<p align="center">
<img src="https://github.com/Koonkie-Cloud-Services/circos_mag/blob/main/images/circos.png" width="600">
</p>

## Acknowledgements and Citations

If you find this tool please useful, please consider meantioning [Koonkie Inc.](https://www.koonkie.com/) in your Acknowledgements and citing Circos:
 - Krzywinski, M. et al. [Circos: an Information Aesthetic for Comparative Genomics](https://genome.cshlp.org/content/early/2009/06/15/gr.092759.109.abstract). Genome Res (2009) 19:1639-1645
