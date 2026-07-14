from pathlib import Path
import fitz


class PDFRenderer:
    def __init__(self, dpi=400):
        self.dpi = dpi

    def pdf_to_images(self, pdf_path, output_dir):
        """
        Convert PDF into high-resolution PNG images.

        Args:
            pdf_path (str | Path): Input PDF
            output_dir (str | Path): Folder to save images

        Returns:
            List[str]: Image paths
        """

        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        output_dir.mkdir(parents=True, exist_ok=True)

        image_paths = []

        try:
            with fitz.open(pdf_path) as doc:

                for page_number in range(len(doc)):

                    page = doc.load_page(page_number)

                    pix = page.get_pixmap(
                        dpi=self.dpi,
                        alpha=False
                    )

                    image_name = f"{pdf_path.stem}_page_{page_number+1}.png"

                    image_path = output_dir / image_name

                    pix.save(image_path)

                    image_paths.append(str(image_path))

            return image_paths

        except Exception as e:
            raise RuntimeError(f"PDF Rendering Failed : {e}")