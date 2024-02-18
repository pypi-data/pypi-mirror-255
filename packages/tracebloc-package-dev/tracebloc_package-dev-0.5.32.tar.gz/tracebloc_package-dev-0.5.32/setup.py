import setuptools

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="tracebloc_package-dev",
    version="0.5.32",
    description="Package required to run Tracebloc jupyter notebook to create experiment",
    url="https://gitlab.com/tracebloc/tracebloc-py-package/-/tree/dev",
    license="MIT",
    python_requires=">=3",
    packages=["tracebloc_package"],
    author="Tracebloc",
    author_email="info@tracebloc.io",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "requests==2.31.0",
        "termcolor==2.3.0",
        "rich==13.7.0",
        "tqdm==4.66.1",
        "tensorflow_datasets==4.9.3",
        "dill==0.3.7",
        "silence_tensorflow==1.2.1",
        "torch==2.1.0",
        "torchvision==0.16.0",
        "torchlightning==0.0.0",
        "torchmetrics==1.2.0",
        "timm==0.9.10",
        "transformers==4.35.2",
    ],
    zip_safe=False,
)
