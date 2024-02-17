# LinkML formbuilder
&copy; Amsterdam UMC, 2024

This CLI tool converts LinkML models into HTML and PDF forms. It does **not** check for model validity and thus might crash or show errors when used with an invalid model. Use the official LinkML tools to check whether your model is valid. 

This tool was built as part of a larger project by a programmer who is not part of the LinkML development team. Therefore, errors in the interpretation of slots of the modelling language are possible. 

## Installation
Under the hood, this tool uses the python adaptation of [PDFKIT](https://pypi.org/project/pdfkit/). It requires [wkhtmltopdf](https://wkhtmltopdf.org/index.html) to be installed on your system.

Installation steps:
1. Install and add wkhtmltopath
    1. [Download here](https://wkhtmltopdf.org/downloads.html)
    2. Add the /bin to the path variable in your system's environment variables
2. ```pip install linkmlformbuilder```

## Build from source
1. Make sure the working directory contains the pyproject.toml file
2. ```pip install build```
3. ```python -m build```
4. Install the .whl file in the dist folder using ```pip install```

## Usage
### Basic usage
Without additional arguments, the command ```linkmlformbuilder [yamlfile]``` with ```[yamlfile]``` being an absolute or relative path to the LinkML yaml resource you want converted, processes the provided LinkML model and creates two files:
1. An HTML file containing code for PDFKIT to use. This HTML file can be viewed, but will look different than the PDF file. This is due to a missing css file that is added during the PDF conversion
2. A PDF form based on the provided LinkML model

### Advanced usage
```
usage: linkmlformbuilder [-h] [-html] [-dir [OUTPUT_DIRECTORY]] [--name [NAME]]
                    yamlfile

positional arguments:
  yamlfile              The LinkML yaml file for which a form should be built

optional arguments:
  -h, --help            show this help message and exit
  -html, --html_only    This flag is used when the user only wants an HTML
                        file returned, there will be no PDF export
  -dir [OUTPUT_DIRECTORY], --output_directory [OUTPUT_DIRECTORY]
                        Specify an output directory, the current working
                        directory is used when this value not provided or the
                        flag is missing
  --name [NAME]         Specify an alternative file name, do not specify a
                        file extension. By default, the filename of the
                        yamlfile is used for the HTML and optionally PDF files
```

## Changelog
### Version 0.1.6
- Overwrite existing output file(s) instead of throwing fileExists errors
### Version 0.1.5
- Capitalize visible names, values, and descriptions
- Remove spaces in ids and enum names
### Version 0.1.4
- Improve support for inlined enums
- Add support for dynamic enums
### Version 0.1.1 - Version 0.1.3
- Fix entry point
### Version 0.1.0
- Initial commit
