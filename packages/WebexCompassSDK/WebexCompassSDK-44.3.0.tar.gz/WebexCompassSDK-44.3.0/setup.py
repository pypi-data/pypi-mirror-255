from setuptools import setup

setup(
    name="WebexCompassSDK",
    version="44.3.0",
    author="Won Zhou",
    author_email="wanzhou@cisco.com",
    description="A SDK for troubleshooting Webex Meetings",
    py_modules=["WebexCompassSDK/__init__", "WebexCompassSDK/WebexCompassSDK", "WebexCompassSDK/ws"],
    data_files=[("", ["WebexCompassSDK/README.md"])],
    package_dir={'': 'src'}
)
