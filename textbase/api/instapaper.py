from pathlib import Path
from time import sleep
from selenium import webdriver
import sys
from .legacy import local_logger



def export_link_list_from_instapaper(
        instapaper_login: dict,
        firefox_dl_dir: Path,
        target: Path
):
    firedriver = config_firefox_driver(download_dir=firefox_dl_dir)
    try:
        download_instapaper_export(
            driver=firedriver,
            instapaper_login=instapaper_login
        )
        while not Path.exists(target):
            sleep(1)
        local_logger.info("Successfully downloaded Instapaper export data in .html format.")
        firedriver.close()
    except Exception as e:
        local_logger.warning(e)
        firedriver.close()


def config_firefox_driver(download_dir: Path):
    try:
        options = webdriver.firefox.options.Options()
        options.headless = True
        options.set_preference(
            "browser.download.folderList", 2
        )
        options.set_preference(
            "browser.download.manager.showWhenStarting", False
        )
        options.set_preference(
            "browser.download.dir", download_dir.as_posix()
        )
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk", "text/html, text/plain, application/octet-stream, application/binary, text/csv, application/csv, application/excel, text/comma-separated-values, text/xml, application/xml"
        )
        options.set_preference(
            "pdfjs.disabled", True
        )
        # driver = webdriver.Firefox(firefox_options=options, service_log_path='../logs/geckodriver.log')
        driver = webdriver.Firefox(firefox_options=options)
        local_logger.info(f'Firefox/Selenium options successfully set')
        return driver
    except Exception as e:
        local_logger.error(f'Unable to set Firefox/Selenium options; returned exception {e}; exiting')
        sys.exit()


def download_instapaper_export(driver: webdriver, instapaper_login: dict):
    driver.get(
        "https://www.instapaper.com/"
    )
    driver.find_element_by_css_selector(
        "a.js_show_hide:nth-child(1)"
    ).click()
    mail_field = driver.find_element_by_css_selector(
        "#sign_in_modal_email"
    )
    mail_field.click()
    mail_field.clear()
    mail_field.send_keys(
        instapaper_login['user']
    )
    pass_field = driver.find_element_by_css_selector(
        "#sign_in_modal_group > form:nth-child(1) > div:nth-child(2) > input:nth-child(2)"
    )
    pass_field.click()
    pass_field.clear()
    pass_field.send_keys(
        instapaper_login['pass']
    )
    driver.find_element_by_css_selector(
        "button.btn-instapaper:nth-child(3)"
    ).click()
    driver.implicitly_wait(
        time_to_wait=20
    )
    driver.find_element_by_css_selector(
        "a.js_popover:nth-child(1)"
    ).click()
    driver.find_element_by_css_selector(
        ".popover-content > ul:nth-child(1) > li:nth-child(11) > a:nth-child(1)"
    ).click()
    driver.implicitly_wait(
        time_to_wait=5
    )
    download_button = driver.find_element_by_css_selector(
        "#download_html_button"
    )
    download_button.click()
    driver.switch_to.alert.accept()
