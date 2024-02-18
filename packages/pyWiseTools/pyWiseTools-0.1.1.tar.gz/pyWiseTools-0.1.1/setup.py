from setuptools import setup, find_packages

setup(
    name="pyWiseTools",
    version="0.1.1",  # Update with your package version
    description="A description of your package",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/coralexbadea/pyWiseTools",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pytesseract",
        "pyautogui",
        "opencv-python"
        # Add other dependencies here
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
