# si_md5_file

Python module to create MD5 files for digital deliveries.

A project of the Digitization Program Office, OCIO, Smithsonian.

https://dpo.si.edu/

## Installation

To install:

```bash
python3 -m pip install simd5
```

To upgrade add `-U`:

```bash
python3 -m pip install -U simd5
```

## Usage

To create a MD5 file with the filenames and hashes:

```python
from simd5 import simd5

simd5.md5_file(folder="files", fileformat="m f", workers=4)
```

The command can take these arguments:

 * `folder`: Which folder to run in. Will ignore subfolders.
 * `fileformat`: What format to use when creating the MD5 file:
   ** `m f`: `[MD5 hash] [filename]` (space-separated)
   ** `f m`: `[filename] [MD5 hash]` (space-separated)
   ** `m,f`: `[MD5 hash],[filename]` (comma-separated)
   ** `f,m`: `[filename],[MD5 hash]` (comma-separated)
 * `workers`: How many parallel processes to use. By default, it will use the number of cores found in the system.

## License

Available under the Apache License 2.0. Consult the [LICENSE](LICENSE) file for details.
