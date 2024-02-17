# HEA Server Framework
[Research Informatics Shared Resource](https://risr.hci.utah.edu), [Huntsman Cancer Institute](https://healthcare.utah.edu/huntsmancancerinstitute/), Salt Lake City, UT

The HEA Server Framework contains shared code for creating HEA microservices.

## Version 1.0.6
* Prevent hang while getting HEA object content when the client connection goes away.

## Version 1.0.5
* Backed out boto connections issue.

## Version 1.0.4
* Don't crash when getting the user's AWS account list includes an account that doesn't exist.
* Fixed exceptions while unarchiving objects.
* Better error messaging when trying to move archived files.
* Allow copying and moving unarchived files.

## Version 1.0.3
* Added heaserver.service.response.status_generic_error() function.
* Made heaserver.service.db.awsservicelib.handle_client_error always return an HTTP response object that can be raised
  as an exception.

## Version 1.0.2
* Improved performance of heaserver.service.activity.DesktopObjectActionLifecycle context manager.
* Removed unused properties from heaserver.service.activity.DesktopObjectActionLifecycle.
* Implemented input validation for heaserver.service.db.awsservicelib.archive_object().

## Version 1.0.1
* Fixed caching bug affecting mongodb paginated queries.
* Fixed passing one desktop object dict to heaserver.service.wstl.RuntimeWeSTLDocumentBuilder().

## Version 1
Initial release.

## Runtime requirements
* Python 3.10 or 3.11.

## Development environment

### Build requirements
* Any development environment is fine.
* On Windows, you also will need:
    * Build Tools for Visual Studio 2019, found at https://visualstudio.microsoft.com/downloads/. Select the C++ tools.
    * git, found at https://git-scm.com/download/win.
* On Mac, Xcode or the command line developer tools is required, found in the Apple Store app.
* Python 3.10 or 3.11: Download and install Python 3.10 from https://www.python.org, and select the options to install
for all users and add Python to your environment variables. The install for all users option will help keep you from
accidentally installing packages into your Python installation's site-packages directory instead of to your virtualenv
environment, described below.
* Create a virtualenv environment using the `python -m venv <venv_directory>` command, substituting `<venv_directory>`
with the directory name of your virtual environment. Run `source <venv_directory>/bin/activate` (or `<venv_directory>/Scripts/activate` on Windows) to activate the virtual
environment. You will need to activate the virtualenv every time before starting work, or your IDE may be able to do
this for you automatically. **Note that PyCharm will do this for you, but you have to create a new Terminal panel
after you newly configure a project with your virtualenv.**
* From the project's root directory, and using the activated virtualenv, run `pip install wheel` followed by
  `pip install -r requirements_dev.txt`. **Do NOT run `python setup.py develop`. It will break your environment.**

### Running tests
Run tests with the `pytest` command from the project root directory. To improve performance, run tests in multiple
processes with `pytest -n auto`.

### Running integration tests
* Install Docker
* On Windows, install pywin32 version >= 223 from https://github.com/mhammond/pywin32/releases. In your venv, make sure that
`include-system-site-packages` is set to `true`.

### Packaging and releasing this project
See the [RELEASING.md](RELEASING.md) file for details.
