#!/home/lebaoquan/.local/share/pipx/venvs/hermes-agent/bin/python
"""
PDF Parser & Extractor Helper Script
Extracts structured Markdown, tables, and images from PDFs using PyMuPDF (fitz).
"""

import os
import sys
import argparse
import fitz  # PyMuPDF

def extract_pdf(pdf_path: str, output_dir: str = "/tmp/pdf_extracted", extract_images: bool = True) -> dict:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    os.makedirs(output_dir, exist_ok=True)
    img_dir = os.path.join(output_dir, "images")
    if extract_images:
        os.makedirs(img_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    metadata = doc.metadata
    total_pages = len(doc)
    
    pages_text = []
    total_images = 0

    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text("text")
        pages_text.append(f"--- Page {page_num + 1} ---\n{text}")

        if extract_images:
            image_list = page.get_images(full=True)
            for img_idx, img in enumerate(image_list):
                xref = img[0]
                base_img = doc.extract_image(xref)
                image_bytes = base_img["image"]
                image_ext = base_img["ext"]
                image_filename = f"page_{page_num + 1}_img_{img_idx + 1}.{image_ext}"
                image_filepath = os.path.join(img_dir, image_filename)
                with open(image_filepath, "wb") as f:
                    f.write(image_bytes)
                total_images += 1

    markdown_content = "\n\n".join(pages_text)
    md_file = os.path.join(output_dir, "extracted_text.md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    return {
        "title": metadata.get("title") or os.path.basename(pdf_path),
        "author": metadata.get("author") or "Unknown",
        "total_pages": total_pages,
        "markdown_path": md_file,
        "images_extracted": total_images,
        "images_dir": img_dir if extract_images else None
    }

def main():
    parser = argparse.ArgumentParser(description="Extract text and graphs from PDF files.")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--out", "-o", default="/tmp/pdf_extracted", help="Output directory")
    parser.add_argument("--no-images", action="store_true", help="Skip image extraction")
    args = parser.parse_args()

    res = extract_pdf(args.pdf_path, args.out, not args.no_images)
    print(f"✓ PDF Processed: {res['title']}")
    print(f"• Total Pages: {res['total_pages']}")
    print(f"• Text saved to: {res['markdown_path']}")
    if res['images_extracted'] > 0:
        print(f"• Extracted {res['images_extracted']} image(s) to: {res['images_dir']}")
    else:
        print("• No embedded raster images found.")

if __name__ == "__main__":
    main()
