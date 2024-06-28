import os, cv2, pytesseract, glob, io, re
import numpy as np
from PIL import Image
from pytesseract import Output
from PyPDF2  import PdfWriter, PdfReader
from pdf2image import convert_from_path
from easyocr import Reader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import units
from bidi import algorithm
Image.LOAD_TRUNCATED_IMAGES = True

def check_make_path(path):
  """
  A function that checks if the path exists, if not, it creates the path.
  """
  if os.path.exists(path):
    pass
  else:
    os.mkdir(path)
  return path

def get_pdf_text_bulk_pdf(pdf_folder_path, output_path, lang_code, ocr_used, lang_rtl, draw_boxes=True):
  """
  A function that is used to recognize and extract text from PDF files in bulk stored in a given folder.

  The function gives the ability to extract text by using either OCRs 'tesseract' or 'easyocr'.
  """
  _ = check_make_path(output_path)
  out_path_bulk, imgs_path = [], []
  for pdf_path, dirs, files in os.walk(pdf_folder_path):
    for z, file in enumerate(files):
      if not file.lower().endswith('.pdf'):
              continue
      file_path = os.path.join(pdf_path, file)
      file_name = os.path.basename(file_path)
      out_path = os.path.join(output_path, file)
      pages = convert_from_path(file_path, 500)
      with open(f'{out_path.replace(".pdf", ".txt")}', 'w') as the_file:  # write mode, coz one time
        for pageNum, imgBlob in enumerate(pages):
            if 'easyocr' in ocr_used:
              img_byte_arr = io.BytesIO()
              imgBlob.save(img_byte_arr, format='PNG')
              img_byte_arr = img_byte_arr.getvalue()
              results, sorted_results, text = extract_text_using_easyocr(img_byte_arr, lang_code, lang_rtl)
            elif 'tesseract' in ocr_used:
              text = pytesseract.image_to_string(imgBlob,lang=lang_code)
            else:
              raise Exception("Inappropriate OCR label used. Use either 'easyocr' or 'tesseract'.")
            if draw_boxes:
              imgs_path.append(draw_bounding_boxes(np.array(imgBlob), output_path, file_name.split('.')[-1], pageNum))
            the_file.write(text)
      out_path_bulk.append(out_path)
  return {'number_of_files': len(out_path_bulk), 'txt_file_path_bulk': out_path_bulk, 'bounding_img_path': imgs_path}

def get_pdf_text(file_pdf, output_path, txt_extract_lang_code, ocr_used, lang_rtl=False, draw_boxes=True):
  """
  A function that is used to recognize and extract text from given PDF file.

  The function gives the ability to extract text by using either OCRs 'tesseract' or 'easyocr'.
  """
  imgs_path = []
  if not file_pdf.lower().endswith('.pdf'):
    raise ValueError('File is not a PDF')
  _ = check_make_path(output_path)
  file_name = os.path.basename(file_pdf)
  out_path = os.path.join(output_path, file_name)
  pages = convert_from_path(file_pdf, 500)
  txt_path = f'{out_path.replace(".pdf", ".txt")}'
  with open(txt_path, 'w') as the_file:  # write mode, coz one time
    for pageNum, imgBlob in enumerate(pages):
        if 'easyocr' in ocr_used:
          img_byte_arr = io.BytesIO()
          imgBlob.save(img_byte_arr, format='PNG')
          img_byte_arr = img_byte_arr.getvalue()
          results, sorted_results, text = extract_text_using_easyocr(img_byte_arr, txt_extract_lang_code, lang_rtl)
        elif 'tesseract' in ocr_used:
          text = pytesseract.image_to_string(imgBlob,lang=txt_extract_lang_code)
        else:
          raise Exception("Inappropriate OCR label used. Use either 'easyocr' or 'tesseract'.")
        if draw_boxes:
          imgs_path.append(draw_bounding_boxes(np.array(imgBlob), output_path, file_name.split('.')[-1], pageNum))
        the_file.write(text)
  return {'bounding_img_path': imgs_path, 'txt_file_path': txt_path}

def draw_bounding_boxes(img, output_path, file_name, pageNum):
  """
  A function that is used to draw bounding boxes are the text that can be read and extracted from the image by the OCR (Outputs an image with bounding boxes).
  """
  data = pytesseract.image_to_data(img, output_type=Output.DICT)
  n_boxes = len(data["text"])
  for i in range(n_boxes):
    if data["conf"][i] == -1:
        continue
    # Coordinates
    x, y = data["left"][i], data["top"][i]
    w, h = data["width"][i], data["height"][i]

    # Corners
    top_left = (x, y)
    bottom_right = (x + w, y + h)
    # Box params
    green = (0, 255, 0)
    thickness = 3  # pixels

    cv2.rectangle(img=img, pt1=top_left, pt2=bottom_right, color=green, thickness=thickness)
  _ = check_make_path(os.path.join(output_path, 'images_bounding'))
  file_out_folder = os.path.join('images_bounding', file_name+'_bounding_images')
  _ = check_make_path(os.path.join(output_path, file_out_folder))
  output_image_path = "{}/text_with_boxes_{}_{}.jpg".format(file_out_folder, file_name, pageNum)
  out_file = os.path.join(output_path, output_image_path)
  cv2.imwrite(out_file, img)
  return out_file

def get_pages_as_imgs(file_pdf,file_out_path, image_converted_format):
  """
  A function that is used to get PIL images from PDF file.
  """
  pages_img = convert_from_path(file_pdf, output_folder=file_out_path, fmt=image_converted_format)
  return pages_img

def add_custom_font(font_name, font_path):
  """
  A function called to add custom font to the ReportLab canvas.
  """
  pdfmetrics.registerFont(TTFont(font_name, font_path))

def draw_text_at_coords(canva, text, x, y):
  """
  Takes the text that shall be inserted in the document along wit its vertical (y) and horizontal (x) positions.

  """
  reordered_text = algorithm.get_display(text)
  canva.drawString(x, y, reordered_text)
  return canva

def easyocr_result_convert_to_pdf_single_image(file_name, image_path, data, font_name='', font_ttf_path='', font_size=12, non_standard_font=False):
  """
  Takes the desired file_name for the output pdf, the path to the image that is desried to be placed in the base layer (usually the scanned page), and the output of easyocr.

  If non_standard_font is True, it means that it is desired to use non-standard ReportLab font (custom), the font_name, and font_path (to ttf file) are required.
  """
  
  img = Image.open (image_path)
  width, height = img.size
  pdf = canvas.Canvas("{}.pdf".format(file_name))
  pdf.setPageSize((width, height))
  if non_standard_font:
    add_custom_font(font_name, font_ttf_path)
    pdf.setFont(font_name, size=font_size)
  else:
      pdf.setFont('Times-Roman', size=font_size)
  for o in range(0, len(data)):
    coords, text, confidence = data[o]
    x1, y1 = [(pixel_unit) for pixel_unit in coords[0]]  # Top-left corner
    x2, y2 = [(pixel_unit) for pixel_unit in coords[2]]   # Bottom-right corner
    x = (x1 + x2) / 2
    y = (y1 + y2) / 2
    pdf = draw_text_at_coords(pdf, text, x, height-y)
    pdf.drawImage(image_path, x=0, y=0, width=width, height=height)
  pdf.save()

def easyocr_result_convert_to_pdf_bulk_images(file_name, images_path, data, font_name='', font_ttf_path='', font_size=12, non_standard_font=False):
  """
  Takes the desired file_name for the output pdf, the path to the image that is desried to be placed in the base layer (usually the scanned page), and the output of easyocr.

  If non_standard_font is True, it means that it is desired to use non-standard ReportLab font (custom), the font_name, and font_path (to ttf file) are required.
  """
  pdf = canvas.Canvas("{}.pdf".format(file_name)) #, pagesize=(width, height)
  for a, img_file in enumerate(images_path):
    img = Image.open (img_file)
    width, height = img.size
    pdf.setPageSize((width, height))
    print(data[a])
    # Adjust font size and leading as needed
    if non_standard_font:
      add_custom_font(font_name, font_ttf_path)
      pdf.setFont(font_name, size=font_size)
    else:
      pdf.setFont('Times-Roman', size=font_size)
    for o in range(0, len(data[a])):
      coords, text, confidence = data[a][o]
      x1, y1 = [(pixel_unit) for pixel_unit in coords[0]]  # Top-left corner
      x2, y2 = [(pixel_unit) for pixel_unit in coords[2]]   # Bottom-right corner
      x = (x1 + x2) / 2
      y = (y1 + y2) / 2
      #print(x, y, img.size, x1, y1, x2, y2, text, height-y)
      pdf = draw_text_at_coords(pdf, text, x, height-y)
    pdf.drawImage(img_file, x=0, y=0, width=width, height=height)
    if (a+1) < len(images_path):
      pdf.showPage()
  pdf.save()

def scanned_pdf_to_text_searchable_pdf(file_pdf, output_folder_path_img, output_path, lang_code, ocr_used, ocr_used_txt_extraction, txt_extract_lang_code, font_name='', font_ttf_path='', font_size=12, lang_rtl=False, non_standard_font=False, image_converted_format="png", get_text=True, draw_boxes=False):
  """
  Convert scanned PDF to searchable PDF.

  Takes the path to a pdf file as an input along with other variable names specified.
  """
  _ = check_make_path(output_path)
  output_folder_path = os.path.join(output_path, output_folder_path_img)
  _ = check_make_path(output_folder_path)
  file_name = os.path.basename(file_pdf).split('.')[0]
  file_out_path = os.path.join(output_folder_path, file_name+'_images')
  _ = check_make_path(file_out_path)
  pages = get_pages_as_imgs(file_pdf,file_out_path, image_converted_format)
  if not pages:
    raise Exception('Error prasing the file, plese make sure the input file is not corrupted or is readable and available.')
  pdf_searchable_file = os.path.join(output_path, "searchable_pdf_{}.pdf".format(file_name))
  files = glob.glob(os.path.join(file_out_path, "*.{}".format(image_converted_format))) #os.listdir(file_out_path)
  files.sort()
  if 'easyocr' in ocr_used:
    ocr_sorted_result = []
    for img_file in files:
      results, sorted_results, extracted_text = extract_text_using_easyocr(img_file, lang_code, lang_rtl)
      ocr_sorted_result.append(sorted_results)
    easyocr_result_convert_to_pdf_bulk_images(pdf_searchable_file, files, ocr_sorted_result, font_name, font_ttf_path, font_size, non_standard_font)
  elif 'tesseract' in ocr_used:
    c = open(pdf_searchable_file, "w+b")
    c.close()
    f = open(pdf_searchable_file, "a+b")
    raw_pdf = [pytesseract.image_to_pdf_or_hocr(img_file, lang=lang_code) for img_file in files]
    pdf_writer = PdfWriter()
    for z, pg in enumerate(raw_pdf):
      pdf = PdfReader(io.BytesIO(pg))
      pdf_writer.add_page(pdf.pages[0])
    pdf_writer.write(f)
    f.close()
  else:
    raise Exception("Inappropriate OCR label used. Use either 'easyocr' or 'tesseract'.")
  text_file = None
  if get_text:
    text_file = get_pdf_text(file_pdf, output_path, txt_extract_lang_code, ocr_used_txt_extraction, draw_boxes=draw_boxes)
  return {'file_name':file_name,'img_path': file_out_path, 'pdf_path': pdf_searchable_file, 'number_of_pages':len(files), 'text_file': text_file}

def scanned_pdf_to_text_searchable_pdf_bulk(pdf_folder_path, output_folder_path_img, output_path, lang_code, ocr_used, ocr_used_txt_extraction, txt_extract_lang_code, font_name='', font_ttf_path='', font_size=12, lang_rtl=False, non_standard_font=False, image_converted_format="png", get_text=True, draw_boxes=False):
  """
  Convert mutliple scanned PDFs to searchable PDFs.

  Takes a pth to folder than contains the PDF files as input along with other variable names specified.
  """
  list_files = []
  for pdf_path, dirs, files in os.walk(pdf_folder_path):
    for z, file in enumerate(files):
      if not file.lower().endswith('.pdf'):
              continue
      file_pdf = os.path.join(pdf_path, file)
      list_files.append(scanned_pdf_to_text_searchable_pdf(file_pdf, output_folder_path_img, output_path, lang_code, ocr_used, ocr_used_txt_extraction, txt_extract_lang_code, font_name, font_ttf_path, font_size, lang_rtl, non_standard_font, image_converted_format, get_text, draw_boxes))
  return {'number_files_converted': len(list_files), 'files_details': list_files}


def sort_extracted_text_based_on_x_position(results):
  """
  Read easyocr output and reposition the output recognized vertically (y) axis based on the bounding box position the bottom right specifically.
  """
  list_words_tr, list_words_br, list_words, list_bbox, list_prob = [], [], [], [], []
  for bbox, text, prob in results:
    (tl, tr, br, bl) = bbox
    tl = (int(tl[0]), int(tl[1]))
    tr = (int(tr[0]), int(tr[1]))
    br = (int(br[0]), int(br[1]))
    bl = (int(bl[0]), int(bl[1]))
    list_words_tr.append(tr[1])
    list_words_br.append(br[1])
    list_words.append(text)
    list_bbox.append(bbox)
    list_prob.append(prob)

  sorted_list_words_br = sorted(list_words_br)

  sorted_list_words, sorted_list_bbox, sorted_list_prob, sorted_results = [], [], [], []
  for cord_br in sorted_list_words_br:
    original_position = list_words_br.index(cord_br)
    sorted_list_words.append(list_words[original_position])
    sorted_list_bbox.append(list_bbox[original_position])
    sorted_list_prob.append(list_prob[original_position])
    sorted_results.append([list_bbox[original_position], list_words[original_position], list_prob[original_position]])
  return sorted_results

def get_raw_text(result, lang_rtl=False):
  """
  Process easyocr output and get the text in a single variable.
  """
  lines_dict = get_lines(result)
  arranged_lines_dict = arrange_words_in_line(lines_dict, lang_rtl)
  text_list = []
  for i in range(len(arranged_lines_dict.keys())):
    for j in range (len(arranged_lines_dict[i])):
      line_text = arranged_lines_dict[i][j][1]
      text_list.append(line_text)
    text_list.append('\n')
    raw_text = ' '.join(text_list)
    raw_text = replace_en_num(raw_text)
  return raw_text

def arrange_words_in_line(lines_dict, lang_rtl=False):
  """
  Arrange the words used in recognized in one line in the appropriate order considering (Right-To-Left and Left-To-Right Languages)
  """
  if isinstance(lines_dict, dict):
    arranged_dict = {}
    for key, values in lines_dict.items():
      line = lines_dict[key]
      sorted_line = sorted(line,key=lambda x:x[0][0], reverse=lang_rtl)
      arranged_dict[key] = sorted_line
    return arranged_dict
  else:
    raise TypeError("The arg must be dict of lines")

def get_lines(result):
  lines_dict = {}
  l=0
  lines_dict[0]=[]
  cord = result[0][0]
  print([int(min(idx)) for idx in zip(*cord)])
  x_min, y_min = [int(min(idx)) for idx in zip(*cord)]
  x_max, y_max = [int(max(idx)) for idx in zip(*cord)]
  lines_dict[0].append([[x_max, y_min], result[0][1]])
  y_min_prev = lines_dict[0][0][0][1]
  for i in range(1, len(result)):
    cord = result[i][0]
    x_min, y_min = [int(min(idx)) for idx in zip(*cord)]
    x_max, y_max = [int(max(idx)) for idx in zip(*cord)]
    if y_min-y_min_prev<18:
      lines_dict[l].append([[x_max, y_min], result[i][1]])
      y_min_prev = y_min
    else:
      l= l+1
      lines_dict[l]=[]
      lines_dict[l].append([[x_max, y_min], result[i][1]])
      y_min_prev = y_max
  return lines_dict

def replace_en_num(text):
  """
  Replace the digits used in numbers to the one used in arabic  modernly language.
  """
  text = re.sub("0", "\u0660", text)
  text = re.sub("1", "\u0661", text)
  text = re.sub("2", "\u0662", text)
  text = re.sub("3", "\u0663", text)
  text = re.sub("4", "\u0664", text)
  text = re.sub("5", "\u0665", text)
  text = re.sub("6", "\u0666", text)
  text = re.sub("6", "\u0667", text)
  text = re.sub("8", "\u0668", text)
  text = re.sub("9", "\u0669", text)
  return text

def extract_text_using_easyocr(image, langs, lang_rtl=False):
  """
  A function that calls easyocr reader, sort the extracted text in-order vertically (x-axis), and considers RTL/LTR languages.

  langs: list of languages to be used, language codes can be found in the official easyocr documentation.

  Outputs tha raw result from easyocr, the sorted results and the extracted text.
  """
  reader = Reader(langs, gpu=-1 > 0)
  results = reader.readtext(image)
  sorted_results = sort_extracted_text_based_on_x_position(results)
  raw_text = get_raw_text(sorted_results, lang_rtl)
  return results, sorted_results, raw_text