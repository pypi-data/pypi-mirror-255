import os


class NREPORT:
    HTML = "html"
    ALLURE = "allure"
    REPORT_DIR = "results"
    HTML_REPORT_PATH = REPORT_DIR + os.sep + "report.html"
    LOG_DIR_DRIVER = "driver-logs"
    LOG_EXTENTION = ".log"
    LOG_DIR_TEST = "test-logs"
    SCREENSHOTS_DIR = "screenshots"
    ALLURE_REPORT_PATH = REPORT_DIR + os.sep + ALLURE


class nCLI:
    """
    List of nrobo defined cli options.

    NOTE:
        when you add/remove an option from nCLI class,
        Make sure that the same option is also removed from the
        nCLI.ARGS dictionary too!!!

    """
    INSTALL = "install"
    APP = "app"
    URL = "url"
    USERNAME = "username"
    PASSWORD = "password"
    INSTANCES = "instances"
    RERUNS = "reruns"
    RERUNS_DELAY = "reruns-delay"
    REPORT = "report"
    TESTDIR = "testsdir"
    BROWSER = "browser"
    BROWSER_CONFIG = "browser-config"
    KEY = "key"
    PACKAGES = "packages"
    GRID = "grid"

    ARGS = {
        INSTALL: INSTALL,
        APP: APP,
        URL: URL,
        USERNAME: USERNAME,
        PASSWORD: PASSWORD,
        INSTANCES: INSTANCES,
        RERUNS: RERUNS,
        REPORT: REPORT,
        TESTDIR: TESTDIR,
        BROWSER: BROWSER,
        BROWSER_CONFIG: BROWSER_CONFIG,
        KEY: KEY,
        PACKAGES: PACKAGES,
        GRID: GRID
    }

    DEFAULT_ARGS = {
        '--cache-clear': ['--cache-clear'],
        '--color': ['--color', 'yes'],
        '-r': ['-r', 'fE'],
        '--code-highlight': ['--code-highlight', 'yes'],
        '--junit-xml': ['--junit-xml', NREPORT.REPORT_DIR + os.sep + f"junit-report.xml"]
    }


class PACKAGES:
    NROBO = "nrobo"
    CLI = "cli"
