from PIL import Image, ImageEnhance, ImageFilter
import os

class LinkedinPhotoEnhancer:
    def __init__(self):
        pass

    def enhance_photo(self, input_image_path, output_image_path):
        # Open an image file
        image = Image.open(input_image_path)

        # Enhance brightness
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.2)

        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.3)

        # Blur background slightly for professional look
        image = image.filter(ImageFilter.GaussianBlur(radius=1))

        # Save enhanced image
        image.save(output_image_path)

        return output_image_path


# Define a simple test image path
# input_image_path = '/media/upload/Bishar - Copy.jpg'
# output_image_path = '/media/upload/enhanced_Bishar.jpg'

# input_image_path = r'C:\SSMC Documents\Python Scripts\Django\myproject\media\upload\Bishar - Copy.jpg'
# output_image_path = r'C:\SSMC Documents\Python Scripts\Django\myproject\media\upload\enhanced_image.jpg'


# # Instantiate and use the LinkedinPhotoEnhancer class provided
# enhancer = LinkedinPhotoEnhancer()
# enhancer.enhance_photo(input_image_path, output_image_path)

# # Load and display the enhanced image
# enhanced_image = Image.open(output_image_path)
# enhanced_image.show()