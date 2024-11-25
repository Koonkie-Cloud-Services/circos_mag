# Circos for MAGs

This command line tool provides an easy-to-use interface for creating Circos plot for a MAG, SAG, or isolate genome.


## Installation

This package requires [Circos](https://circos.ca), [Prokka](https://github.com/tseemann/prokka), and (optionally, but recommended) [Samtools](https://www.htslib.org) to be installed on your system. The easiest and recommend method for installing Circos and Prokka is to use [Conda](https://docs.conda.io/projects/conda/en/latest/index.html):

```
> conda create -n circos_mag -c bioconda circos prokka
```

This creates a Conda environment named `circos_mag` that must be activate before running this tool:
```
> conda activate circos_mag
```

The Circos MAG tool must be installed into the `circos_mag` Conda environment using:
```
> git clone https://github.com/Koonkie-Cloud-Services/circos_mag.git
> cd circos_mag
> python -m pip install .
```

You can test the installation using the data in the `example` directory:
```
> circos_mag plot --genome_file ./example/GCA_016214285.1_ASM1621428v1_genomic.fna.gz --gff_file ./example/GCA_016214285.1.gff --coverage_file ./example/coverage.tsv.gz --completeness 96.0 --output_dir ~/tmp/test_install
```

You can also (optionally) install Samtools using Conda. This should be installed in its own environment since it has conflicting dependencies with Circos:
```
> conda create -n samtools -c bioconda samtools
```

## Usage

The typical workflow for generating a Circos plot of your MAG is as follows:
 1. Obtain genomic FASTA file for your MAG
 2. Run Prokka on your MAG to identify the 5S, 16S, and 23S rRNA and tRNA genes in your MAG (<i>note</i>: Prokka only accepts uncompressed files):
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
 - `genome_stats.tsv`: plain text file with common statistics about your MAG such as genome size, mean GC, and number of rRNA genes
 - `circos`: directory containing the configuration and data files used by Circos

You can tweak the Circos plot by modifying the data in the `<output_dir>/circos` directory and then regenerating the Circos plots using:
```
> circos --config ./circos/circos.conf
```

## Interpreting the Circos plot

The Circos plot produced by this tool consists of a number of rings that visually indicate the quality of a MAG:
 - __Ring 1__: Displays the contigs comprising a MAG in green. An additional red contig indicates the estimated amount of DNA missing from the MAG as set with the optional `--completeness` parameter. For contigs > 5kb, tick markers are drawn to indicate the length of the contig with units in kilobases.
 - __Ring 2__: Displays the deviation in GC content of 1000 bp windows from the mean GC of the entire MAG. Windows in orange/green have a higher/lower GC than the mean. The background of this ring has 3 positive and negative bands that go from grey to white and each indicate a +/-5% GC deviations. For eample, windows reaching the last band in white have a GC deviation >10% from the mean GC and are rendered in orange. The window size can be changed with `--gc_window_size` parameter. 
 - __Ring 3__: Displays the location of 5S (square), 16S (triangle), and 23S (circle) rRNA genes indentified in the MAG as grey shapes.
 - __Ring 4__: Displays the location of tRNA genes identified in the MAG as dark red rhombi (i.e. diamonds).
 - __Ring 5__: Displays the percent deviation in coverage of 1000 bp windows from the mean coverage of the entire MAG. Windows in orange/green have a higher/lower coverage than the mean. The background of this ring has 3 positive and negative bands that go from grey to white and each indicate a 100% coverage deviations. For eample, windows reaching the last band in white have a coverage that is >200% from the mean coverage and are rendered in orange. The window size can be changed with `--cov_window_size` parameter. 

<p align="center">
<img src="https://github.com/Koonkie-Cloud-Services/circos_mag/blob/main/images/circos.png" width="600">
</p>

## Customizing Circos plot with Command Line Arguements

The Circos plot contains a few optional arguments for customizing the plot:
 - `completeness`: This parameter is used to indicate the estimate completeness of a MAG as determined using a program such as [CheckM](https://github.com/Ecogenomics/CheckM). The amount of DNA estimated to be missing from the MAG is visually indicated by a red contig.
 - `min_contig_len`: MAGs often have a large number of relatively short contigs. Be default, these are all drawn but this can be rather uninformative and add a lot of visual clutter. This parameters allows contigs shorter than a given length to all be drawn as a single grey contig in the outer ring. Note that any rRNA or tRNA genes on these contigs
 will not be shown in the plot.
 - `max_contigs`: This is similar to the above parameter, but simply limits the plot to the specified number of longest contigs.

## Customizing Circos plot with a Custom Style File

The Circos plot can be customized by providing a custom style file to the `--plot_style_file` argument. This file is a simple text file (technically a [TOML](https://toml.io/en/) formatted file) that can be edited in any text editor and allows for a number of visual elements to be modified. An example style file is provided in `example/plot_style.toml`. It is recommended to start with the example style file and modify elements from their default values as required. Documentation for changing value is provided at the top of the example style file.

## Further Customization of SVG Plot

Your Circos plot is also generated as a scalable vector graphics (SVG) file. This file can be modified in SVG editing software such as [Inkscape](https://circos.ca/documentation/tutorials/configuration/svg_output) or Adobe Illustrator. Circos uses a [custom font file](https://circos.ca/documentation/tutorials/configuration/svg_output/), `circossymbols.otf`, for symbols. This is in the `fonts` directory and must be installed on your system for symbols to display as expected. Under Windows, this can be down by double clicking on the `circossymbols.otf` file and then clicking Install. 
 
## Acknowledgements and Citations

If you find this tool please useful, please consider meantioning [Koonkie Inc.](https://www.koonkie.com/) in your Acknowledgements and citing Circos:
 - Krzywinski, M. et al. [Circos: an Information Aesthetic for Comparative Genomics](https://genome.cshlp.org/content/early/2009/06/15/gr.092759.109.abstract). Genome Res (2009) 19:1639-1645
