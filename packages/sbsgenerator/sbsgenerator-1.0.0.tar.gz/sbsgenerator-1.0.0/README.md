[![Docs](https://img.shields.io/badge/docs-latest-blue.svg)](https://osf.io/t6j7u/wiki/home/) 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# SBSGenerator

SBSGenerator is a comprehensive Python package designed for bioinformaticians and researchers working in the field of genomics. This package offers a robust set of tools for generating, analyzing, and interpreting single base substitutions (SBS) mutations from Variant Call Format (VCF) files. With a focus on ease of use, efficiency, and scalability, SBSGenerator facilitates the detailed study of genomic mutations, aiding in the understanding of their roles in various biological processes and diseases. Uniquely developed using a hybrid of Python and Rust, SBSGenerator leverages the PyO3 library for seamless integration between Python's flexible programming capabilities and Rust's unparalleled performance. This innovative approach ensures that SBSGen is not only user-friendly but also incredibly efficient and capable of handling large-scale genomic data with ease.

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

```bash
$ pip install sbsgenerator
```

## Usage

Create mutliple SBS files. With increasing context.

The sbs.96.txt file contains all of the following the pyrimidine single nucleotide variants, N[{C > A, G, or T} or {T > A, G, or C}]N.
*4 possible starting nucleotides x 6 pyrimidine variants x 4 ending nucleotides = 96 total combinations.*

The sbs.1536.txt file contains all of the following the pyrimidine single nucleotide variants, NN[{C > A, G, or T} or {T > A, G, or C}]NN.
*16 (4x4) possible starting nucleotides x 6 pyrimidine variants x 16 (4x4) possible ending nucleotides = 1536 total combinations.*

The sbs.24576.txt file contains all of the following the pyrimidine single nucleotide variants, NNN[{C > A, G, or T} or {T > A, G, or C}]NNN.
*64 (4x4x4) nucleotides x 6 pyrimidine variants x 64 (4x4x4) possible ending dinucleotides = 24576 total combinations.*

```python
from sbsgenerator import generator
# Context number (must be larger than 3 and uneven)
context_size = 7
# List with all the vcf files
vcf_files = [str(Path(__file__).parent / "files" / "test.vcf")]
# Where the ref genomes will be downloaded to
ref_genome = Path(__file__).parent / "files"
sbsgen = generator.SBSGenerator(
    context=context_size,
    vcf_files=vcf_files,
    ref_genome=Path(__file__).parent / "files"
)
sbsgen.count_mutations()
```

## Contributing

I welcome contributions to SBSGen! If you have suggestions for improvements or bug fixes, please open an issue or submit a pull request.

## License

SBSGen is released under the MIT License. See the LICENSE file for more details.
