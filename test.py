from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import json

def create_text_overlay(data, page_size):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=page_size)

    field_positions = {
        'Name': (105, 710),
        'Date': (99, 688),
        'Question': (118, 666)
    }

    for field, position in field_positions.items():
        if field in data:
            c.drawString(position[0], position[1], data[field])

    c.save()
    packet.seek(0)
    return packet

def fill_pdf_form(template_path, output_path, form_data):
    reader = PdfReader(template_path)
    writer = PdfWriter()

    page = reader.pages[0]
    page_size = (float(page.mediabox.width), float(page.mediabox.height))

    overlay_packet = create_text_overlay(form_data, page_size)
    overlay_pdf = PdfReader(overlay_packet)
    overlay_page = overlay_pdf.pages[0]

    page.merge_page(overlay_page)
    writer.add_page(page)

    with open(output_path, 'wb') as output_file:
        writer.write(output_file)

if __name__ == "__main__":
    form_data_list = [
        {
            "Name": "Ryan Pereda",
            "Date": "October 25th, 2025",
            "Question": "Question"
        },
        {
            "Name": "Jane Smith",
            "Date": "2023-02-22",
            "Question": "Sample Question 2"
        }
    ]

    for i, form_data in enumerate(form_data_list):
        output_path = f"filled_form_{i+1}.pdf"
        fill_pdf_form('pdf test.pdf', output_path, form_data)
        print(f"Created {output_path}")

def load_form_data(json_path):
    with open(json_path, 'r') as file:
        return json.load(file)