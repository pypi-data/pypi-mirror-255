import pdf2image
import numpy as np
import cv2

def convert_first_page_of_pdf_to_image(filepath):
    images_from_file = pdf2image.convert_from_path(filepath, first_page=1, last_page=1) #Returns image in RGB color space
    return np.array(images_from_file[0]) #Return as numpy array for QReader ingestion