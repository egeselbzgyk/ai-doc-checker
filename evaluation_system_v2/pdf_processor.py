import fitz  # PyMuPDF
from PIL import Image
import io
import os
from typing import List, Tuple
import base64

class PDFImageExtractor:
    """Extract images from PDF files for evaluation"""
    
    def __init__(self, min_image_size: Tuple[int, int] = (100, 100)):
        """
        Initialize PDF extractor
        
        Args:
            min_image_size: Minimum width, height for valid images
        """
        self.min_image_size = min_image_size
    
    def extract_images_from_pdf(self, pdf_path: str, output_dir: str = None) -> List[dict]:
        """
        Extract all images from PDF
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save extracted images (optional)
            
        Returns:
            List of dictionaries with image info:
            [
                {
                    'image_path': str,
                    'image_base64': str,
                    'page_number': int,
                    'image_index': int,
                    'width': int,
                    'height': int
                }
            ]
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        extracted_images = []
        
        try:
            # Open PDF document
            pdf_document = fitz.open(pdf_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    # Get image data
                    xref = img[0]
                    pix = fitz.Pixmap(pdf_document, xref)
                    
                    # Skip if image is too small
                    if pix.width < self.min_image_size[0] or pix.height < self.min_image_size[1]:
                        pix = None
                        continue
                    
                    # Convert to PIL Image
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_data = pix.tobytes("png")
                        pil_image = Image.open(io.BytesIO(img_data))
                    else:  # CMYK: convert to RGB first
                        pix1 = fitz.Pixmap(fitz.csRGB, pix)
                        img_data = pix1.tobytes("png")
                        pil_image = Image.open(io.BytesIO(img_data))
                        pix1 = None
                    
                    # Generate filename
                    filename = f"page_{page_num+1}_img_{img_index+1}.png"
                    
                    # Save to file if output directory provided
                    image_path = None
                    if output_dir:
                        os.makedirs(output_dir, exist_ok=True)
                        image_path = os.path.join(output_dir, filename)
                        pil_image.save(image_path, "PNG")
                    
                    # Convert to base64 for API calls
                    img_buffer = io.BytesIO()
                    pil_image.save(img_buffer, format='PNG')
                    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                    
                    extracted_images.append({
                        'image_path': image_path,
                        'image_base64': img_base64,
                        'page_number': page_num + 1,
                        'image_index': img_index + 1,
                        'width': pix.width,
                        'height': pix.height,
                        'filename': filename
                    })
                    
                    pix = None  # Free memory
            
            pdf_document.close()
            
        except Exception as e:
            raise Exception(f"Error extracting images from PDF: {str(e)}")
        
        return extracted_images
    
    def extract_images_as_base64_only(self, pdf_path: str) -> List[dict]:
        """
        Extract images as base64 only (no file saving)
        Faster method for direct API usage
        
        Returns:
            List with base64 images and metadata
        """
        return self.extract_images_from_pdf(pdf_path, output_dir=None)
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """
        Get basic PDF information
        
        Returns:
            Dictionary with PDF metadata
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            pdf_document = fitz.open(pdf_path)
            
            info = {
                'page_count': len(pdf_document),
                'title': pdf_document.metadata.get('title', ''),
                'author': pdf_document.metadata.get('author', ''),
                'subject': pdf_document.metadata.get('subject', ''),
                'creator': pdf_document.metadata.get('creator', ''),
                'producer': pdf_document.metadata.get('producer', ''),
                'creation_date': pdf_document.metadata.get('creationDate', ''),
                'modification_date': pdf_document.metadata.get('modDate', '')
            }
            
            pdf_document.close()
            return info
            
        except Exception as e:
            raise Exception(f"Error reading PDF info: {str(e)}")

# Example usage function
def process_student_pdf(pdf_path: str, temp_dir: str = "temp_images") -> List[dict]:
    """
    Process student PDF and extract images for evaluation
    
    Args:
        pdf_path: Path to student PDF
        temp_dir: Temporary directory for extracted images
        
    Returns:
        List of extracted image data
    """
    extractor = PDFImageExtractor()
    
    try:
        # Get PDF info
        pdf_info = extractor.get_pdf_info(pdf_path)
        print(f"Processing PDF: {pdf_info['page_count']} pages")
        
        # Extract images
        images = extractor.extract_images_from_pdf(pdf_path, temp_dir)
        print(f"Extracted {len(images)} images")
        
        return images
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return []

if __name__ == "__main__":
    # Test function
    test_pdf = "test_student_submission.pdf"
    if os.path.exists(test_pdf):
        images = process_student_pdf(test_pdf)
        for img in images:
            print(f"Image: {img['filename']}, Size: {img['width']}x{img['height']}") 