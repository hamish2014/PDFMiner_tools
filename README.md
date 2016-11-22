# PDFMiner_tools
Quick start tools for PDFMiner https://github.com/euske/pdfminer/

## Getting Started on a Debian Linux system

Create a sandbox directory for the example, and download a sample pdf to analyse

```bash
$ mkdir /tmp/PDFMiner_tools_sandbox
$ cd /tmp/PDFMiner_tools_sandbox
$ wget http://www.analog.com/media/en/technical-documentation/data-sheets/ADXL345.pdf
```

install PDFMiner and clone PDFMiner_tools
```bash
$ sudo apt-get install python-pdfminer
$ git clone https://github.com/hamish2014/PDFMiner_tools
```

### Basic Text Dump Example

```python
> import PDFMiner_tools
> PDFMiner_tools.PDF_text( open('ADXL345.pdf') ) #basic text dump
> PDFMiner_tools.PDF_text_with_locations?
> 

```

### PDF text with locations example

```python
> import PDFMiner_tools
> PDFMiner_tools.PDF_text_with_locations?
> pdf = PDFMiner_tools.PDF_text_with_locations( open('ADXL345.pdf') )
> page = 1
> for t in pdf.text_groups[page]:
      print(t)

> pdf.get(text = "Data Sheet ", page=1)
> pdf.current_page = 1
> pdf.get(text = "Data Sheet ")
> pdf.get(text__startswith = 'F')

> pdf.filter(text__startswith = 'F')
> pdf.filter(text__contains = 'voltage')

> t = pdf.get(text__startswith = "SERIAL ")
> print( t.text )
> t.textblock_above() #returns none, if not textblock or string of characters above
> t.textblock_below(tol=6.0) #increase tol, to make less strict
> t.textblock_right( tol=1.0)
> t.textblocks_same_y( tol=4.2 )

```

### PDF table example

```python
> import PDFMiner_tools
> PDFMiner_tools.PDF_text_with_locations?
> pdf = PDFMiner_tools.PDF_text_with_locations( open('ADXL345.pdf'),  record_rects=True)
> t = pdf.get( page=5, text__startswith ='Parameter' )
not working yet ...
```