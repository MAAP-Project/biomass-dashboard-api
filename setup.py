"""Setup dashboard_api."""

from setuptools import find_packages, setup

with open("README.md") as f:
    long_description = f.read()

inst_reqs = [
    "fastapi~=0.70.0", # < 0.65.2 has JSON/cookie vulnerability
    "urllib3>=1.26.5", # earlier versions have DoS vulnerability
    "jinja2~=3.0.1",
    "python-binary-memcached",
    "rio-color",
    "rio-tiler==2.0a.11",
    "email-validator",
    "fiona",
    "shapely",
    "rasterio==1.1.8",
    "rasterstats",
    "geojson-pydantic",
    "boto3",
    "requests",
    "mercantile",
    "pyyaml~=5.4.0",
    "cachetools"
]
extra_reqs = {
    "dev": ["pytest", "pytest-cov", "pytest-asyncio", "pre-commit", "safety", "bandit"],
    "server": ["uvicorn", "click==7.0"],
    "deploy": [
        "docker",
        "attrs==20.1.0",
        "aws-cdk.core==1.119.0",
        "aws-cdk.aws_lambda==1.119.0",
        "aws-cdk.aws_apigatewayv2==1.119.0",
        "aws-cdk.aws_apigatewayv2_integrations==1.119.0",
        "aws-cdk.aws_ecs==1.119.0",
        "aws-cdk.aws_ec2==1.119.0",
        "aws-cdk.aws_autoscaling==1.119.0",
        "aws-cdk.aws_ecs_patterns==1.119.0",
        "aws-cdk.aws_iam==1.119.0",
        "aws-cdk.aws_elasticache==1.119.0",
    ],
    "test": ["moto[iam]", "mock", "pytest", "pytest-cov", "pytest-asyncio", "requests"],
}


setup(
    name="dashboard_api",
    version="0.5.0",
    description=u"",
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
    author=u"Development Seed",
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
