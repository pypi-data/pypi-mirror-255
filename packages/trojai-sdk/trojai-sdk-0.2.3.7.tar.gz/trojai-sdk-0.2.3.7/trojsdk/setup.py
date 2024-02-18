from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="trojsdk",
    version="0.1",
    packages=find_packages(),
    author="TrojAI",
    author_email="stan.petley@troj.ai",
    description="TrojAI provides the troj Python convenience package to allow users to integrate TrojAI adversarial protections and robustness metrics seamlessly into their AI development pipelines.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://troj.ai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=open("requirements.txt").readlines(),
    python_requires=">=3.6",
    entry_points={"console_scripts": ["trojsdk = trojsdk.cmd:main"]},
)
