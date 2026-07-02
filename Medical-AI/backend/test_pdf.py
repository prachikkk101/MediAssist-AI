from app.utils.pdf_reader import extract_text_from_pdf

text = extract_text_from_pdf("uploads/Prior Art.pdf")

print(text)