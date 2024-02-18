[PyPI python package](https://pypi.org/project/afipcaeqrdecode/)

# AFIP invoice pdf qr CAE extract and decode

This is a python package that uses [pdf2image](https://pypi.org/project/pdf2image/) to convert the first page of your AFIP invoice with an AFIP CAE QR code to an image, and then run [qreader](https://pypi.org/project/qreader/) on it in order to locate and decode the AFIP CAE QR code in order to extract relevant invoice metadata like: 

- Invoice date
- CUIT of invoice creator
- AFIP electronic invoice point of sale (Punto de venta)
- Invoice number
- Amount
- Currency
- CUIT of inovoice recipient

And other less important properties.

## Why qreader instead of pyzbar

In its inception this library used just [pyzbar](https://pypi.org/project/pyzbar/), however we came upon some QR codes which did not decode succesfully using just [pyzbar](https://pypi.org/project/pyzbar/).

[qreader](https://pypi.org/project/qreader/) depends on [pyzbar](https://pypi.org/project/pyzbar/), but uses a pre-trained AI model to detect and segment QR codes, using information extracted by this AI model, it applies different image preprocessing techniques that heavily increase the decoding rate by [pyzbar](https://pypi.org/project/pyzbar/)

## Example Usage and notes about metadata

Using the included sample files for demonstration (and ran from repository root using included sample file):

```
from afipcaeqrdecode import get_cae_metadata

invoice_metadata = get_cae_metadata('./tests/sample_files/2000005044986390.pdf')
```

Here, invoice metadata will evaluate to:

```python
{
    "ver":1,
    "fecha":"2023-02-10", #I've found this field to be missing in some decodes
    "cuit":30710145764,
    "ptoVta":4,
    "tipoCmp":1,
    "nroCmp":25399,
    "importe":2460,
    "moneda":"PES",
    "ctz":1,
    "tipoDocRec":80,
    "nroDocRec":30717336905,
    "tipoCodAut":"E",
    "codAut":73064176949471
}

#The actual output will not be pretty printed, it will be stripped of all whitespace and formatting characters
```

## Salvaging bad QR code z-indexing on invoices, bad AFIP CAE urls, and bad JSON

Some bad PDFs have other images overlapping on the AFIP CAE QR code, so we implemented a second run codepath that uses [PyMuPDF](https://pypi.org/project/PyMuPDF/) in order to extract all images inside the invoices and then run [qreader](https://pypi.org/project/qreader/) on them.

In cases in which the construction of the AFIP CAE QR url was done incorrectly or have some parts missing, we try to decode anyways.

We came upon many decoded metadatas with bad json that had to be repaired in the consumer application, with this in mind we included [json-repair] (https://pypi.org/project/json-repair/) by and turn it on by default.

## System Dependencies and their installation

This package depends on [qreader](https://pypi.org/project/qreader/), which in turn depends on [pyzbar](https://pypi.org/project/pyzbar/), which in turn depends on the system library zbar [ZBar](https://zbar.sourceforge.net/)

Check your OS documentation on what package to install to get ZBar working with pyzbar.

On Linux (Ubuntu 22.04):

`sudo apt-get install libzbar0`


On Mac OS X:

`brew install zbar`

## Installation using pip

After installing system dependencies, you can install using the [PyPI python package](https://pypi.org/project/afipcaeqrdecode/)

`pip install afipcaeqrdecode`

## First run notice

On first run [qreader](https://pypi.org/project/qreader/) will download the weights to run its QR detector AI model, then it will resume program operation automatically.


## WARNING

This is an experimental package, USE IN PRODUCTION AT YOUR OWN RISK.

It is barely even tested, i'm sharing it so I can actually import it as a PyPI package in another project that consumes it.

## Credits

All the other library authors this package depends on.
Facundo Mainere for helping with JWT decode.

Author: Emiliano Mesquita.

## License

GNU LGPLv3.

