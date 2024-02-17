from setuptools import setup

from src.WebexCompassSDK.version import sdk_version

setup(
    name="WebexCompassSDK",
    version=sdk_version,
    author="Won Zhou",
    author_email="wanzhou@cisco.com",
    description="A SDK for troubleshooting Webex Meetings",
    py_modules=["WebexCompassSDK/__init__", "WebexCompassSDK/WebexCompassClient","WebexCompassSDK/version", "WebexCompassSDK/ws"],
    data_files=[("", ["README.md"])],
    package_dir={'': 'src'}
)
