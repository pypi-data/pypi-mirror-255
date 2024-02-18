import fitz
import numpy as np
import cv2

def extract_images_from_invoice_pdf(filepath):
    
    images_as_list_of_numpy_array = []

    with fitz.open(filepath) as pdf_file:
        pdf_extracted_images = pdf_file[0].get_images()
        
        for extracted_image in pdf_extracted_images:

            xref = extracted_image[0]
            base_image = pdf_file.extract_image(xref)

            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            images_as_list_of_numpy_array.append(cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)) #cv2.imdecode expects numpy array, not bytes class buffer

    return images_as_list_of_numpy_array