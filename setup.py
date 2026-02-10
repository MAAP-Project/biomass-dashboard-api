"""Setup dashboard_api."""

from setuptools import find_packages, setup

with open("README.md") as f:
    long_description = f.read()

inst_reqs = [
    "fastapi>=0.73",
    "urllib3>=1.26.5",  # earlier versions have DoS vulnerability
    "jinja2~=3.0.1",
    "python-binary-memcached",
    "rio-color",
    "rio-tiler>=3.1,<3.2",
    "email-validator",
    "fiona",
    "shapely",
    "rasterstats",
    "geojson-pydantic",
    "boto3",
    "requests",
    "mercantile",
    "pyyaml~=5.4.0",
    "cachetools",
    "pydantic<2",
]
extra_reqs = {
    "dev": ["pre-commit", "safety", "bandit", "mypy==1.13.0"],
    "server": ["uvicorn", "click==7.0"],
    "deploy": [
        "aws-cdk-lib>=2.0.0",
        "aws-cdk.aws_apigatewayv2_alpha>=2.67.0a0",
        "aws-cdk.aws_apigatewayv2_integrations_alpha>=2.67.0a0",
    ],
    "test": ["moto[iam]", "mock", "pytest", "pytest-cov", "pytest-asyncio", "requests"],
}


setup(
    name="dashboard_api",
    version="0.5.0",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3",
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="",
    author="Development Seed",
    author_email="info@developmentseed.org",
    url="https://github.com/developmentseed/dashboard_api",
    license="MIT",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    package_data={
        "dashboard_api": ["templates/*.html", "templates/*.xml", "db/static/**/*.json"]
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)
