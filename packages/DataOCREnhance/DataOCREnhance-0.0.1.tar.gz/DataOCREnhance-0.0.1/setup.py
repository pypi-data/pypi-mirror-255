from setuptools import setup, find_packages

setup(
    name='DataOCREnhance',
    version='0.0.1',
    author='IoT Noob Talha Khalid',
    author_email='zjohndavid88@gmail.com',
    description='A toolkit for performing OCR (Optical Character Recognition) tasks',
    long_description=open('README.md').read(),  # Assuming you have a README.md file
    long_description_content_type='text/markdown',
    url='https://github.com/your_username/ocr_toolkit',  # Link to your package's repository
    packages=find_packages(),  # Automatically find and include all packages in the package directory
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'Pillow',  # Python Imaging Library fork
        'pytesseract',  # Python wrapper for Google Tesseract-OCR Engine
        'opencv-python',  # OpenCV (Open Source Computer Vision Library)
        'numpy',  # NumPy
        'nltk',  # Natural Language Toolkit
    ],
)
