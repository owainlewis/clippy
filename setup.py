from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="clippy-video",
    version="0.1.0",
    author="Owain Lewis",
    author_email="owain@owainlewis.com",
    description="A Python tool for extracting and processing video clips to create engaging, social media-ready content",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/owainlewis/clippy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "yt-dlp>=2023.11.16",
        "openai-whisper>=20231117",
        "torch>=2.0.0",
        "pysrt>=1.1.2",
        "ffmpeg-python>=0.2.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "python-multipart>=0.0.6",
        "aiofiles>=23.2.0",
    ],
    entry_points={
        "console_scripts": [
            "clippy=clippy.cli:main",
            "clippy-server=clippy.server:main",
        ],
    },
)
