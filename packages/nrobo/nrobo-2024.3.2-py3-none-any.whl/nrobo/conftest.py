"""
nrobo conftest.py file.
Doc: https://docs.pytest.org/en/latest/reference/reference.html#request
Doc: https://github.com/SeleniumHQ/seleniumhq.github.io/blob/trunk/examples/python/tests/browsers/test_chrome.py
Doc2: https://docs.pytest.org/en/7.1.x/example/simple.html

Contains fixtures for nrobo framework
"""
import logging
import os
import pathlib
import sys
import time
from datetime import datetime

import allure
import pytest
import pytest_html
from nrobo.cli import STYLE
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

import nrobo.cli.cli_constansts
from nrobo.cli.nglobals import __APP_NAME__, __USERNAME__, __PASSWORD__, __URL__, __BROWSER__, Browsers
from nrobo.util.common import Common
from nrobo.cli.cli_constansts import nCLI as CLI, NREPORT
import os.path as path

from nrobo.util.constants import CONST

global __APP_NAME__, __USERNAME__, __PASSWORD__, __URL__, __BROWSER__


def ensure_logs_dir_exists():
    """checks if driver logs dir exists. if not creates on the fly."""
    from nrobo.cli.cli_constansts import NREPORT
    if not os.path.exists(NREPORT.REPORT_DIR + os.sep + NREPORT.LOG_DIR_DRIVER):
        """ensure driver logs dir"""
        try:
            os.makedirs(NREPORT.REPORT_DIR + os.sep + NREPORT.LOG_DIR_DRIVER)
        except FileExistsError as e:
            pass  # Do nothing

    if not os.path.exists(NREPORT.REPORT_DIR + os.sep + NREPORT.LOG_DIR_TEST):
        """ensure test logs dir"""
        try:
            os.makedirs(NREPORT.REPORT_DIR + os.sep + NREPORT.LOG_DIR_TEST)
        except FileExistsError as e:
            pass  # do nothing

    if not os.path.exists(NREPORT.REPORT_DIR + os.sep + NREPORT.SCREENSHOTS_DIR):
        """ensure test logs dir"""
        try:
            os.makedirs(NREPORT.REPORT_DIR + os.sep + NREPORT.SCREENSHOTS_DIR)
        except FileExistsError as e:
            pass  # do nothing

    if not os.path.exists(NREPORT.ALLURE_REPORT_PATH):
        try:
            os.makedirs(NREPORT.ALLURE_REPORT_PATH)
        except FileExistsError as e:
            pass  # do nothing


def read_browser_config_options(_config_path):
    """
    process browser config options from the <_config_path>
    and return list of those.

    If file not found, then raise exception.

    """
    if not _config_path:
        return []

    if path.exists(_config_path):
        """if path exists"""

        # read file and store it's content in a list
        _config_options = []
        with open(_config_path, "r") as f:
            _config_options.append(str(f.readline()).strip())

        return _config_options
    else:
        raise Exception(f"Chrome config file does not exist at path <{_config_path}>!!!")


def pytest_addoption(parser):
    """
    Pass different values to a test function, depending on command line options

    Doc: https://docs.pytest.org/en/7.1.x/example/simple.html
    :param parser:
    :return:
    """
    group = parser.getgroup("nrobo header options")
    group.addoption(
        f"--{CLI.BROWSER}", help="""
    Target browser name. Default is chrome.
    Options could be:
        chrome | firefox | safari | edge.
        (Only chrome is supported at present.)
    """
    )
    group.addoption(f"--{CLI.APP}", help="Name of your app project under test")
    group.addoption(f"--{CLI.URL}", help="Link of application under test.yaml")
    group.addoption(f"--{CLI.USERNAME}", help="Username for login", default="")
    group.addoption(f"--{CLI.PASSWORD}", help="Password for login", default="")
    group.addoption(f"--{CLI.BROWSER_CONFIG}", help="Browser config file path for setting requested options")
    group.addoption(f"--{CLI.PACKAGES}", help="Browser config file path for setting requested options")
    group.addoption(f"--{CLI.GRID}", help="Url of remote selenium grid server")

    # ini option
    parser.addini(f"{CLI.APP}", type="string",
                  help="Name of your app project under test")
    parser.addini(f"{CLI.URL}", type='string',
                  help="Link of application under test.yaml")
    parser.addini(f"{CLI.USERNAME}", type="string",
                  help="Username for login")
    parser.addini(f"{CLI.PASSWORD}", type='string',
                  help="Password for login")
    parser.addini(f"{CLI.BROWSER_CONFIG}", type='string',
                  help="Browser config file path for setting requested options")
    parser.addini(f"{CLI.BROWSER_CONFIG}", type='string',
                  help="Browser config file path for setting requested options")
    parser.addini(f"{CLI.PACKAGES}", type='string',
                  help="Browser config file path for setting requested options")
    parser.addini(f"--{CLI.GRID}", type='string', help="Url of remote selenium grid server")


@pytest.fixture()
def url(request):
    # Global fixture returning app url
    # Access pytest command line options
    # Doc: https://docs.pytest.org/en/7.1.x/example/simple.html
    return request.config.getoption(f"--{CLI.URL}")


@pytest.fixture()
def app(request):
    # Global fixture returning app name
    # Access pytest command line options
    # Doc: https://docs.pytest.org/en/7.1.x/example/simple.html
    return request.config.getoption(f"--{CLI.APP}")


@pytest.fixture()
def username(request):
    # Global fixture returning admin username
    # Access pytest command line options
    # Doc: https://docs.pytest.org/en/7.1.x/example/simple.html
    return request.config.getoption(f"--{CLI.USERNAME}")


@pytest.fixture()
def password(request):
    # Global fixture returning admin password
    # Access pytest command line options
    # Doc: https://docs.pytest.org/en/7.1.x/example/simple.html
    return request.config.getoption(f"--{CLI.PASSWORD}")


@pytest.fixture(autouse=True, scope='function')
def driver(request):
    """
    Fixture for instantiating driver for given browser.
    Doc: https://github.com/SeleniumHQ/seleniumhq.github.io/blob/trunk/examples/python/tests/browsers/test_chrome.py
    Doc2: https://docs.pytest.org/en/7.1.x/example/simple.html

    """
    # Access pytest command line options
    # Doc: https://docs.pytest.org/en/7.1.x/example/simple.html
    browser = request.config.getoption(f"--{CLI.BROWSER}")
    global __URL__
    __URL__ = request.config.getoption(f"--{CLI.URL}")
    _grid_server_url = request.config.getoption(f"--{CLI.GRID}")

    # initialize driver with None
    _driver = None

    # Set driver log name
    # current test function name
    # Doc: https://docs.pytest.org/en/latest/reference/reference.html#request
    test_method_name = request.node.name
    from nrobo.cli.cli_constansts import NREPORT
    ensure_logs_dir_exists()
    _driver_log_path = NREPORT.REPORT_DIR + os.sep + \
                       NREPORT.LOG_DIR_DRIVER + os.sep + \
                       test_method_name + NREPORT.LOG_EXTENTION

    if browser == Browsers.CHROME:
        """if browser requested is chrome"""

        # Chrome Flags for Tooling
        # Doc: https://github.com/GoogleChrome/chrome-launcher/blob/main/docs/chrome-flags-for-tools.md
        # Command line switches
        # Doc: https://peter.sh/experiments/chromium-command-line-switches/
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # enable/disable chrome options from a file
        _browser_options = read_browser_config_options(request.config.getoption(f"--{CLI.BROWSER_CONFIG}"))
        # apply chrome options
        [options.add_argument(_option) for _option in _browser_options]

        # Replace with ChromeDriverManager
        # service = webdriver.ChromeService(log_output=_driver_log_path)
        # Doc for webdriver manager: https://pypi.org/project/webdriver-manager/
        if _grid_server_url:
            """Get instance of remote webdriver"""
            _driver = webdriver.Remote(_grid_server_url,
                                       options=options)
        else:
            """Get instance of local chrom driver"""
            _driver = webdriver.Chrome(options=options,
                                       service=ChromeService(
                                           ChromeDriverManager().install(),
                                           log_output=_driver_log_path))
    elif browser == Browsers.CHROME_HEADLESS:
        """if browser requested is chrome"""

        # Chrome Flags for Tooling
        # Doc: https://github.com/GoogleChrome/chrome-launcher/blob/main/docs/chrome-flags-for-tools.md
        # Command line switches
        # Doc: https://peter.sh/experiments/chromium-command-line-switches/
        # Doc: https://github.com/SeleniumHQ/seleniumhq.github.io/blob/trunk/examples/python/tests/browsers/test_chrome.py
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')

        # enable/disable chrome options from a file
        _browser_options = read_browser_config_options(
            request.config.getoption(f"--{CLI.BROWSER_CONFIG}"))
        # apply chrome options
        [options.add_argument(_option) for _option in _browser_options]

        # Replace with ChromeDriverManager
        # service = webdriver.ChromeService(log_output=_driver_log_path)
        # Doc for webdriver manager: https://pypi.org/project/webdriver-manager/
        if _grid_server_url:
            """Get instance of remote webdriver"""
            _driver = webdriver.Remote(_grid_server_url,
                                       options=options)
        else:
            """Get instance of local chrom driver"""
            _driver = webdriver.Chrome(options=options,
                                       service=ChromeService(
                                           ChromeDriverManager().install(),
                                           log_output=_driver_log_path))
    elif browser == Browsers.SAFARI:
        """if browser requested is safari"""

        options = webdriver.SafariOptions()
        options.add_argument("ShowOverlayStatusBar=YES")

        # enable/disable chrome options from a file
        _browser_options = read_browser_config_options(
            request.config.getoption(f"--{CLI.BROWSER_CONFIG}"))
        # apply Safari options
        [options.add_argument(_option) for _option in _browser_options]

        if _grid_server_url:
            """Get instance of remote webdriver"""
            _driver = webdriver.Remote(_grid_server_url,
                                       options=options)
        else:
            """Get instance of local chrom driver"""
            _service = webdriver.SafariService(service_args=["--diagnose"])
            _driver = webdriver.Safari(options=options, service=_service)

    elif browser in [Browsers.FIREFOX, Browsers.FIREFOX_HEADLESS]:
        """if browser requested is firefox"""

        options = webdriver.FirefoxOptions()

        if browser == Browsers.FIREFOX_HEADLESS:
            options.add_argument("-headless")

        # enable/disable chrome options from a file
        _browser_options = read_browser_config_options(
            request.config.getoption(f"--{CLI.BROWSER_CONFIG}"))
        # apply Safari options
        [options.add_argument(_option) for _option in _browser_options]

        if _grid_server_url:
            """Get instance of remote webdriver"""
            _driver = webdriver.Remote(_grid_server_url,
                                       options=options)
        else:
            """Get instance of local firefox driver"""
            _service = webdriver.FirefoxService(log_output=_driver_log_path, service_args=['--log', 'debug'])
            _driver = webdriver.Firefox(options=options, service=_service)
    elif browser == Browsers.EDGE:
        """if browser requested is microsoft edge"""

        options = webdriver.EdgeOptions()

        # enable/disable chrome options from a file
        _browser_options = read_browser_config_options(
            request.config.getoption(f"--{CLI.BROWSER_CONFIG}"))
        # apply Safari options
        [options.add_argument(_option) for _option in _browser_options]

        if _grid_server_url:
            """Get instance of remote webdriver"""
            _driver = webdriver.Remote(_grid_server_url, options=options)
        else:
            """Get instance of local firefox driver"""
            _service = webdriver.EdgeService(log_output=_driver_log_path)
            _driver = webdriver.Edge(options=options, service=_service)
    elif browser == Browsers.IE:
        """if browser requested is microsoft internet explorer"""

        if sys.platform != "win32":
            """No need to proceed"""
            from nrobo.cli.tools import console
            console.rule("IE support available on WIN32 platform only! Quiting test run.")
            console.print("""Please note that the Internet Explorer (IE) 11 desktop application ended support for certain operating systems on June 15, 2022. Customers are encouraged to move to Microsoft Edge with IE mode.""")
            exit(1)

        options = webdriver.IeOptions()

        # enable/disable chrome options from a file
        _browser_options = read_browser_config_options(
            request.config.getoption(f"--{CLI.BROWSER_CONFIG}"))
        # apply Safari options
        [options.add_argument(_option) for _option in _browser_options]

        if _grid_server_url:
            """Get instance of remote webdriver"""
            _driver = webdriver.Remote(_grid_server_url, options=options)
        else:
            """Get instance of local firefox driver"""
            _service = webdriver.IeService(log_output=_driver_log_path)
            _driver = webdriver.Ie(options=options)
    else:
        from nrobo.cli.tools import console
        console.rule(f"[{STYLE.HLRed}]DriverNotConfigured Error!")
        console.print(f"[{STYLE.HLRed}]Driver not configured in nrobo for browser <{browser}>")
        exit(1)

    # store web driver ref in request
    request.node.funcargs['driver'] = _driver
    # yield driver instance to calling test method
    yield _driver

    # quit the browser
    _driver.quit()


@pytest.fixture(scope='function')
def logger(request):
    """
    Fixer that instantiate logger instance for each test

    Doc: https://github.com/SeleniumHQ/seleniumhq.github.io/blob/trunk/examples/python/tests/troubleshooting/test_logging.py
    """
    # Set driver log name
    # current test function name
    # Doc: https://docs.pytest.org/en/latest/reference/reference.html#request
    test_method_name = request.node.name
    from nrobo.cli.cli_constansts import NREPORT
    ensure_logs_dir_exists()

    # Setup logger for tests
    logger = logging.getLogger('selenium')
    logger.setLevel(logging.DEBUG)
    _test_logs_path = NREPORT.REPORT_DIR + os.sep + \
                      NREPORT.LOG_DIR_TEST + os.sep + \
                      test_method_name + NREPORT.LOG_EXTENTION
    handler = logging.FileHandler(_test_logs_path)
    logger.addHandler(handler)
    logging.getLogger('selenium.webdriver.remote').setLevel(logging.WARN)
    logging.getLogger('selenium.webdriver.common').setLevel(logging.DEBUG)

    # yield logger instance to calling test method
    yield logger


def pytest_report_header(config):
    """
    Session-scoped fixture that returns the session’s pytest.Config object.

    Doc: https://docs.pytest.org/en/7.1.x/reference/reference.html#pytestconfig

    :param config:
    :return:
    """
    # if not config.getoption(f"--{CLI.APP}") and not config.getini(f"{CLI.APP}"):
    #     return
    #
    # app_name_option = config.getoption(f"{CLI.APP}")
    # app_name_ini = config.getini(f"{CLI.APP}")
    #
    # header = ""
    # if app_name_option is not None:
    #     if isinstance(app_name_option, str):
    #         header = repr(app_name_option)
    #
    # elif app_name_ini is not None:
    #     if isinstance(app_name_ini, str):
    #         header = repr(app_name_ini)

    return f"test summary".title()


# set up a hook to be able to check if a test has failed
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Doc: https://stackoverflow.com/questions/70761764/pytest-html-not-displaying-image
    Doc: https://github.com/pytest-dev/pytest/blob/main/doc/en/how-to/writing_hook_functions.rst#hookwrapper-executing-around-other-hooks

    Doc: https://pytest-html.readthedocs.io/en/latest/
    Doc: https://pytest-html.readthedocs.io/en/latest/deprecations.html

    :param item:
    :param call:
    :return:
    """
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, 'extras', [])
    if report.when == 'call':
        xfail = hasattr(report, 'wasxfail')
        if (report.failed and not xfail) \
                    or (report.passed and not xfail):
            # Get test method identifier
            node_id = item.nodeid
            # Get reference to test method
            feature_request = item.funcargs['request']
            # Get driver reference from test method by calling driver(request) fixture
            driver = feature_request.getfixturevalue('driver')

            # replace unwanted chars from node id, datetime and prepare a good name for screenshot file
            screenshot_filename = f'{node_id}_{datetime.today().strftime("%Y-%m-%d_%H:%M")}_{Common.generate_random_numbers(1000, 9999)}.png' \
                .replace(CONST.FORWARD_SLASH, CONST.UNDERSCORE) \
                .replace(CONST.SCOPE_RESOLUTION_OPERATOR, CONST.UNDERSCORE) \
                .replace(CONST.COLON, CONST.EMPTY).replace('.py', CONST.EMPTY)

            # Attach screenshot to allure report
            allure.attach(
                # Not working. Still work in progress...
                driver.get_screenshot_as_png(),
                name='screenshot',
                attachment_type=allure.attachment_type.PNG
            )

            # Attach screenshot to html report
            screenshot_filepath = NREPORT.REPORT_DIR + os.sep + NREPORT.SCREENSHOTS_DIR + os.sep + screenshot_filename
            screenshot_relative_path = NREPORT.SCREENSHOTS_DIR + os.sep + screenshot_filename

            # Create and save screenshot at <screenshot_filepath>
            driver.save_screenshot(screenshot_filepath)

            # get base64 screenshot
            # failure_screen_shot = driver.get_screenshot_as_base64()

            # attach screenshot with html report. Use relative path to report directory
            extras.append(pytest_html.extras.image(screenshot_relative_path))
            # add relative path to screenshot in the html report
            extras.append(pytest_html.extras.url(screenshot_relative_path))

        # update the report.extras
        report.extras = extras
