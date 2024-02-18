# SMAP - Stack Mapping Anchor Points
![pipepeline status badge](https://gitlab.com/truttink/smap/badges/master/pipeline.svg)
[![coverage report](https://gitlab.com/truttink/smap/badges/master/coverage.svg)](https://gitlab.com/truttink/smap/-/commits/master)

* SMAP delineate analyses read mapping distributions for GBS read mapping QC, defines read mapping polymorphisms within loci and across samples, and selects high quality loci across the sample set for downstream analyses.
* SMAP sliding-frames defines loci covering SNPs and/or structural variants to run **SMAP haplotype-sites**.
* SMAP compare identifies the overlap between two sets of loci (e.g. common loci across two runs of SMAP delineate).
* SMAP haplotype-sites performs read-backed haplotyping using a priori known polymorphic SNP sites, and creates "ShortHaps".
As a special case, SMAP haplotype-sites also captures GBS read mapping polymorphisms (here called "SMAPs") as a novel genetic diversity marker type, and integrates those with SNPs for ShortHap haplotyping.
* SMAP target-selection creates input files for SMAP design.
* SMAP design creates highly multiplex amplicon sequencing (HiPlex) primers and/or gRNA panels for genotyping CRISPR/Cas-induced or natural variation in a genepool.
* SMAP haplotype-window works independent of prior knowledge of polymorphisms, groups reads by locus, defines a window enclosed between two custom border sequences, and retains the entire corresponding DNA sequence as haplotype.
* SMAP effect-prediction is designed to provide biological interpretation of the haplotype call tables created by SMAP haplotype-window.
* SMAP grm creates a similarity/distance matrix by converting a SMAP haplotype-site genotype call table based on GBS or amplicon sequencing data.

## Documentation

An extensive manual of the SMAP package can be found on [Read the Docs](https://ngs-smap.readthedocs.io/) including detailed explanations and illustrations.

## Citation

If you use SMAP, please cite "Schaumont et al., (2022). Stack Mapping Anchor Points (SMAP): a versatile suite of tools for read-backed haplotyping. https://doi.org/10.1101/2022.03.10.483555". Source code is available online at https://gitlab.ilvo.be/genomics/smap-package/smap.

## License

SMAP is available under the GNU Affero General Public License v3.0 ([GNU AGPLv3](https://gitlab.ilvo.be/genomics/smap-package/smap/-/blob/master/LICENSE).

## Building and installing

SMAP is being developed and tested on Linux.
Additionally, some dependencies are only developed on Linux.

https://ngs-smap.readthedocs.io/en/latest/quickstart/quickstart.html#smapinstallationquickstart describes the installation guidelines.

## Contributions

* The Ghent University 2019 and 2021 Computational Biology class under supervision of prof. Dr. Peter Dawyndt and Felix Van der Jeugt has made contributions to reduce memory usage and to speed up haplotype calculations.

## Links
* [Documentation](https://ngs-smap.readthedocs.io/)
* [Source Code](https://gitlab.ilvo.be/genomics/smap-package/smap)
* [Report an issue](https://gitlab.ilvo.be/genomics/smap-package/smap/-/issues)
* [GbprocesS: extraction of genomic inserts from NGS data for GBS experiments](https://gitlab.com/ilvo/GBprocesS)
* [SMAP on pypi](https://pypi.org/project/ngs-smap/)
* [ILVO (Flanders Research Institute for Agriculture, Fisheries and Food)](https://ilvo.vlaanderen.be/en/)
