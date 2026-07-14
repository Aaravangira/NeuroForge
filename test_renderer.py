from pdf_renderer import PDFRenderer

renderer = PDFRenderer(dpi=400)

images = renderer.pdf_to_images(
    "uploads/Prachar 082983.pdf",
    "temp"
)

print(images)