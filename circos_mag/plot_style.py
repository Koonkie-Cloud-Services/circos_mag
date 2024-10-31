"""
Set plot style for attributes defined in data files.
"""

import tomllib
from dataclasses import dataclass

import circos_mag.defaults as Defaults


@dataclass
class PlotStyle:
    contig_color: str = "green"
    contig_filtered_color: str = "grey"
    contig_missing_color: str = "red"

    gc_pos_deviation_color: str = "dorange"
    gc_neg_deviation_color: str = "dblue"
    gc_thickness: str = "1p"
    gc_min: float = -15
    gc_max: float = 15
    gc_show: str = "data"
    gc_window_size: int = Defaults.GC_WINDOW_SIZE

    rrna_label_size: str = "32p"
    rrna_5S_symbol: str = "C"
    rrna_5S_symbol_color: str = "dgrey"
    rrna_16S_symbol: str = "I"
    rrna_16S_symbol_color: str = "dgrey"
    rrna_23S_symbol: str = "O"
    rrna_23S_symbol_color: str = "dgrey"
    rrna_show: str = "yes"

    trna_label_size: str = "32p"
    trna_symbol_color: str = "dred"
    trna_symbol: str = "F"
    trna_show: str = "yes"

    cov_pos_deviation_color: str = "dorange"
    cov_neg_deviation_color: str = "dblue"
    cov_thickness: str = "1p"
    cov_min: float = -300
    cov_max: float = 300
    cov_show: str = "data"
    cov_window_size: int = Defaults.COV_WINDOW_SIZE

    def from_toml_file(self, plot_style_file: str) -> None:
        """Set plot style based on fields in TOML file."""

        with open(plot_style_file, 'rb') as f:
            style = tomllib.load(f)

        self.contig_color = style['contigs']['color']
        self.contig_filtered_color = style['contigs']['filtered_color']
        self.contig_missing_color = style['contigs']['missing_color']

        self.gc_pos_deviation_color = style['gc']['pos_deviation_color']
        self.gc_neg_deviation_color = style['gc']['neg_deviation_color']
        self.gc_thickness = style['gc']['thickness']
        self.gc_min = style['gc']['min']
        self.gc_max = style['gc']['max']
        self.gc_show = style['gc']['show_background']
        self.gc_window_size = style['gc']['window_size']

        self.rrna_label_size = style['rrna']['size']
        self.rrna_5S_symbol = style['rrna']['5S_symbol']
        self.rrna_5S_symbol_color = style['rrna']['5S_color']
        self.rrna_16S_symbol = style['rrna']['16S_symbol']
        self.rrna_16S_symbol_color = style['rrna']['16S_color']
        self.rrna_23S_symbol = style['rrna']['23S_symbol']
        self.rrna_23S_symbol_color = style['rrna']['23S_color']
        self.rrna_show = style['rrna']['show_background']

        self.trna_label_size = style['trna']['size']
        self.trna_symbol_color = style['trna']['color']
        self.trna_symbol = style['trna']['symbol']
        self.trna_show = style['trna']['show_background']

        self.cov_pos_deviation_color = style['coverage']['pos_deviation_color']
        self.cov_neg_deviation_color = style['coverage']['neg_deviation_color']
        self.cov_thickness = style['coverage']['thickness']
        self.cov_min = style['coverage']['min']
        self.cov_max = style['coverage']['max']
        self.cov_show = style['coverage']['show_background']
        self.cov_window_size = style['coverage']['window_size']
