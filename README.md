# handle_scanned_pdf
A wrapper on top of python-OCR tools such as pytesseract and easyocr, to recognize and extract text embedded in images.

Source code can be accessed here [sxaxmz/handdle_scanned_pdf](https://github.com/sxaxmz/handle_scanned_pdf)

Install the package using:
```console
$ pip install handle-scanned-pdf
```
[![Downloads](https://static.pepy.tech/badge/handle_scanned_pdf)](https://pepy.tech/project/handle_scanned_pdf) [![Downloads](https://static.pepy.tech/badge/handle_scanned_pdf/week)](https://pepy.tech/project/handle_scanned_pdf)

---

Features:
- Convert scanned-PDFs to text searchable PDFs (end-to-end).
- Extract text from scanned PDFs and images.
- Draw bounding boxes around the text that can be extracted on scanned PDFs and images.

Usage:
- Make scanned documents searchable and parsable.
- Helpful in digitizing archives.
- Make use of scanned documents and images when it's intended to be used for RAG applications.

---

##### Tesseract-OCR supports:
- Various image types including (but not limited to) jpeg, png, gif, bmp, tiff.
- Wide range of languages [list of languages](https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html)
- Supports reading more than 1 language at a time.

Server Installation
```console
$ apt install tesseract-ocr
$ apt-get install poppler-utils
```

Only if required set the below path to Tesseract executable:
```python
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract/tesseract.exe'
```

##### EasyOCR supports:
- Does not require server installation.
- Supports reading more than 1 language at a time.
- Performes faster on a GPU.
- List of [supported language code](https://www.jaided.ai/easyocr/).


##### Language Support

###### Tesseract
- Ensure to download the right Tesseract-OCR for the language needed to be used.

Installation on Linux:
```
$ apt install tesseract-ocr-<language-code>
```

Download for Windows (set path to the downloaded OCR):
- [Download language files](https://github.com/tesseract-ocr/tessdata/tree/3.04.00)
- Add the folder that contains the downloaded files into the System Path Variables as TESSDATA_PREFIX

Defining the language codes for Tesseract:
```Python
lang_code = "eng+ara"
txt_extract_lang_code = "eng+ara"
```

###### EasyOCR
Defining the language codes for EasyOCR:
```Python
lang_code = ["en","ar"]
txt_extract_lang_code = ["en","ar"]
```

##### Packages Required (src: requirements.txt):
```bash
pytesseract===0.3.10
pdf2image===1.17.0
PyPDF2===3.0.1
opencv-python
```


## Easy-to-Use:

- Straightforward functions.
- Customizable process.
- JSON output.

#### Draw bounding boxes on the text that can be extracted from PDF
```python
from handle_scanned_pdf import draw_bounding_boxes

img_path = 'sample__images/3ba4c1f1-775f-4e05-ab48-a40617087a57-1.png'
img = np.array(cv2.imread(img_path)) # Read image and convert to numpy array
output_path = 'output'
file_name = os.path.basename(img_path).split('.')[0]
pageNum = 0
draw_bounding_boxes(img, output_path, file_name, pageNum)
```

###### Output:
```console
output/images_bounding/3ba4c1f1-775f-4e05-ab48-a40617087a57-1_bounding_images/text_with_boxes_3ba4c1f1-775f-4e05-ab48-a40617087a57-1_0.jpg
```

#### Get text in Bulk from Multiple PDF files
```python
from handle_scanned_pdf import get_pdf_text_bulk_pdf

pdf_folder_path = 'pdf_files'
output_path = 'output'
draw_boxes = True
lang_code = ['en'] # 'eng'
ocr_used = 'easyocr' # 'tesseract'
lang_rtl = True
get_pdf_text_bulk_pdf(pdf_folder_path, output_path, lang_code, ocr_used, lang_rtl, draw_boxes)

```

###### Output:
```console
{'number_of_files': 1,
 'txt_file_path_bulk': ['output/sample_.pdf'],
 'bounding_img_path': ['output/images_bounding/text_with_boxes_3ba4c1f1-775f-4e05-ab48-a40617087a57-1_0.jpg',
  'output/images_bounding/text_with_boxes_3ba4c1f1-775f-4e05-ab48-a40617087a57-1_1.jpg',
  'output/images_bounding/text_with_boxes_3ba4c1f1-775f-4e05-ab48-a40617087a57-1_2.jpg',
  'output/images_bounding/text_with_boxes_3ba4c1f1-775f-4e05-ab48-a40617087a57-1_3.jpg',
  'output/images_bounding/text_with_boxes_3ba4c1f1-775f-4e05-ab48-a40617087a57-1_4.jpg']}
```

#### Get text from a single PDF file
```python
from handle_scanned_pdf import get_pdf_text

pdf_path_ = 'pdf_files/sample_.pdf'
output_path = 'output'
draw_boxes = True
lang_code = ['ar', 'en'] # 'ara+eng'
ocr_used = 'easyocr' # 'tesseract'
lang_rtl = True
get_pdf_text(pdf_path_, output_path, lang_code, ocr_used, lang_rtl, draw_boxes)

```

###### Output:
```console
{'bounding_img_path': ['output/images_bounding/pdf_bounding_images/text_with_boxes_pdf_0.jpg',
  'output/images_bounding/pdf_bounding_images/text_with_boxes_pdf_1.jpg',
  'output/images_bounding/pdf_bounding_images/text_with_boxes_pdf_2.jpg',
  'output/images_bounding/pdf_bounding_images/text_with_boxes_pdf_3.jpg',
  'output/images_bounding/pdf_bounding_images/text_with_boxes_pdf_4.jpg'],
 'txt_file_path': 'output/sample_.txt'}
```

#### Extract text, draw bounding boxes, and convert PDF file to text searchable PDF
```python
from handle_scanned_pdf import scanned_pdf_to_text_searchable_pdf

file_pdf = 'sample_.pdf'
output_folder_path_img = 'img'
output_path = 'output'
lang_code = ['ar', 'en'] #'ara+eng'
image_converted_format = 'png'
ocr_used = 'easyocr' # 'tesseract'
ocr_used_txt_extraction = 'easyocr' # 'tesseract'
txt_extract_lang_code = ['ar', 'en'] #'ara+eng'
font_name = 'Scheherazade'
font_ttf_path = 'ScheherazadeNew-Regular.ttf'
font_size = 12
lang_rtl = True
non_standard_font = True
get_text=False
draw_boxes=False
scanned_pdf_to_text_searchable_pdf(file_pdf, output_folder_path_img, output_path, lang_code, ocr_used, ocr_used_txt_extraction, txt_extract_lang_code, font_name, font_ttf_path, font_size, lang_rtl, non_standard_font, image_converted_format, get_text, draw_boxes)

```

###### Output:
```console
{'file_name': 'sample_',
 'img_path': 'output/img/sample__images',
 'pdf_path': 'output/searchable_pdf_sample_.pdf',
 'number_of_pages': 5,
 'text_file': {'bounding_img_path': [],
  'txt_file_path': 'output/sample_.txt'}}
```

#### Extract text, draw bounding boxes, and convert PDF file to text searchable PDF in Bulk
```python
from handle_scanned_pdf import scanned_pdf_to_text_searchable_pdf_bulk

pdf_folder_path = 'pdf_files'
output_folder_path_img = 'img'
output_path = 'output'
lang_code = ['ar', 'en'] #'ara+eng'
image_converted_format = 'png'
ocr_used = 'easyocr' # 'tesseract'
ocr_used_txt_extraction = 'easyocr' # 'tesseract'
txt_extract_lang_code = ['ar', 'en'] #'ara+eng'
font_name = 'Scheherazade'
font_path = 'ScheherazadeNew-Regular.ttf'
font_size = 12
lang_rtl = True
non_standard_font = True
get_text=True
draw_boxes=False
scanned_pdf_to_text_searchable_pdf_bulk(pdf_folder_path, output_folder_path_img, output_path, lang_code, ocr_used_txt_extraction, txt_extract_lang_code, font_name, font_ttf_path, font_size, lang_rtl, non_standard_font, image_converted_format, get_text, draw_boxes)

```

###### Output:
```console
{'number_files_converted': 1,
 'files_details': [{'file_name': 'sample_',
   'img_path': 'output/img/sample__images',
   'pdf_path': 'output/searchable_pdf_sample_.pdf',
   'number_of_pages': 5,
   'text_file': {'bounding_img_path': [],
    'txt_file_path': 'output/sample_.txt'}}]}
```


## References:
- [pytesseract package](https://pypi.org/project/pytesseract/)
- [tesseract-ocr](https://tesseract-ocr.github.io)
- [Data Camp Pytesseract Guide](https://www.datacamp.com/tutorial/optical-character-recognition-ocr-in-python-with-pytesseract)
- [Support Other Languages On Windows](https://stackoverflow.com/a/46145156/7316214)
- [EasyOCR](https://www.jaided.ai/easyocr/documentation/)
- [ReportLab](https://docs.reportlab.com/)


