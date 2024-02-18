from .convert_first_page_of_pdf_to_image import convert_first_page_of_pdf_to_image
from .decode_cae_url import decode_cae_url
from .extract_images_from_invoice_pdf import extract_images_from_invoice_pdf

from qreader import QReader
import re

qreader = QReader(model_size='l', min_confidence=0.7)
regex_for_cae_jwt_querystring = re.compile('https:\/\/(?:www\.)?afip\.gob\.ar\/fe\/qr\/?\?p=(.*)')

def get_cae_metadata(filepath, attempt_to_repair_json=True):

    #First attempt convert first page of pdf invoice to image and detect and decode method
    
    first_page_of_invoice_as_image_in_np_array = convert_first_page_of_pdf_to_image(filepath)
    
    for decoded_qr in qreader.detect_and_decode(first_page_of_invoice_as_image_in_np_array):
        if decoded_qr:
            matched = regex_for_cae_jwt_querystring.fullmatch(decoded_qr)
            if matched:
                return decode_cae_url(matched.group(1), attempt_to_repair_json=attempt_to_repair_json)

    #If not successful (no return) attempt extract and decode method

    images_in_invoice_pdf_as_np_arrays = extract_images_from_invoice_pdf(filepath)

    for image_as_np_array in images_in_invoice_pdf_as_np_arrays:
        for decoded_qr in qreader.detect_and_decode(image_as_np_array, is_bgr=True): #cv2 always processes images as BGR
            if decoded_qr:
                matched = regex_for_cae_jwt_querystring.fullmatch(decoded_qr)
                if matched:
                    return decode_cae_url(matched.group(1), attempt_to_repair_json=attempt_to_repair_json)
