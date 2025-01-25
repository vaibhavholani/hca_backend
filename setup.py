from setuptools import setup, find_packages

setup(
    name="hca_backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pytesseract>=0.3.10",
        "Pillow>=9.2.0",
        "openai>=1.0.0",
        "opencv-python>=4.6.0.66",
        "flask",
        "flask-cors",
        "python-dotenv",
        "flask_jwt_extended",
        "python-dateutil",
        "psycopg2-binary",
        "pypika",
        "phonenumbers",
        "reportlab",
        "requests",
        "supabase",
        "rapidfuzz",
        "langchain>=0.1.0",
        "langchain-openai>=0.0.2",
        "pydantic>=2.0.0"
    ]
)
