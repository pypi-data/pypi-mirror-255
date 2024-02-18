from setuptools import setup, find_packages

setup(
    name="aisak",
    version="0.2.0",
    author="Mandela Logan",
    author_email="mandelakorilogan@gmail.com",
    description="AISAK, short for Artificially Intelligent Swiss Army Knife, is a state-of-the-art language model designed for text generation tasks. Developed by Mandela Logan, this Large Language Model (LLM) is fine-tuned on extensive datasets to excel in understanding and interpreting your various queries in natural language text.",
    packages=find_packages(),
    install_requires=[
        "accelerate",
        "torch",
		  "transformers",
        # Add more required packages and their versions as needed
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)