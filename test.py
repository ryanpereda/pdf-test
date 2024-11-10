from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import json
import logging
from contextlib import contextmanager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_text_overlay(data, page_number, page_size):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=page_size)
    # c.setFont()

    field_positions = {
        0: {
            'Name': (105, 700),
            'Date': (99, 0),
            'Question': (118, 666)
        },
        1: {
            "Reason_for_calling": (100, 700)
        },
        2: {
            'Address': (100,700)
        }
    }

    if page_number in field_positions:
        logger.debug(f"Processing page {page_number}")
        for field, position in field_positions[page_number].items():
            field_key = field.replace('_', ' ')
            if field in data:
                logger.debug(f"Adding field {field_key} at position {position}")
                c.drawString(position[0], position[1], str(data[field_key]))

    c.showPage()
    c.save()
    packet.seek(0)
    return packet

def fill_pdf_form(template_path, output_path, form_data):
    try:    
        with open(template_path, 'rb') as template_file:
            reader = PdfReader(template_file)
            writer = PdfWriter()

            for page_number in range(len(reader.pages)):
                logger.debug(f"Processing page {page_number} of {len(reader.pages)}")

                page = reader.pages[page_number]
                page_size = (float(page.mediabox.width), float(page.mediabox.height))

                logger.debug(f"Page size: {page_size}")

                overlay_packet = create_text_overlay(form_data, page_number, page_size)
                overlay_pdf = PdfReader(overlay_packet)

                if len(overlay_pdf.pages) > 0:
                    page.merge_page(overlay_pdf.pages[0])

                writer.add_page(page)
                overlay_packet.close()
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            logger.debug(f"Successfully created {output_path}")

    except Exception as e:
        logger.error(f"Error in fill_pdf_form: {str(e)}")
        raise

if __name__ == "__main__":
    form_data = [
        {
            "Name": "Ryan Pereda",
            "Date": "October 25th, 2025",
            "Question": "Question",
            "Reason for calling": "Product inquiry",
            "Address": "456 Oak Ave, Town, Country"
        }
    ]

    output_path = f"filled_form.pdf"
    try:
        fill_pdf_form('BK - VOLUNTARY PETITION .pdf', output_path, form_data)
        print(f"Created {output_path}")
    except Exception as e:
        print(f"Error processing form: {str(e)}")
        logger.error(f"Detailed error for form: {str(e)}", exc_info=True)

def load_form_data(json_path):
    with open(json_path, 'r') as file:
        return json.load(file)