from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import requests
import os
import time
import re

def download_file(url, filename, download_dir, headers, cookies):
    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()
        with open(os.path.join(download_dir, filename), 'wb') as f:
            f.write(response.content)
        print(f"成功下载文件: {filename}")
    except Exception as e:
        log_error(filename, str(e))

def sanitize_filename(title):
    return re.sub(r'[:\\/*?"<>|]', '', title)

def get_download_links(driver):
    download_links = []
    # 获取包含下载链接的标题链接元素
    elements = driver.find_elements(By.CSS_SELECTOR, 'h.media-heading a')
    for element in elements:
        title = element.text
        href = element.get_attribute('href')
        download_links.append((element, title, href))
        # print(title)

    return download_links

def log_error(title, error_message):
    print(f"Error downloading {title}: {error_message}")

def click_element(driver, element):
    try:
        driver.execute_script("arguments[0].click();", element)
    except Exception as e:
        log_error(element.text, str(e))

def is_direct_download(url):
    # 简单判断链接是否直接指向文件
    return re.search(r'\.(pdf|zip|exe)$', url, re.IGNORECASE) is not None

def get_session_cookies(driver):
    cookies = driver.get_cookies()
    cookie_dict = {}
    for cookie in cookies:
        cookie_dict[cookie['name']] = cookie['value']
    return cookie_dict

def wait_for_downloads(download_dir, timeout=60):
    """
    等待下载目录中所有下载任务完成。
    """
    seconds = 0
    while True:
        time.sleep(1)
        downloading = False
        for filename in os.listdir(download_dir):
            if filename.endswith('.crdownload') or filename.endswith('.part'):
                downloading = True
                break
        if not downloading:
            break
        if seconds > timeout:
            print("下载超时")
            break
        seconds += 1





def main():
    custom_download_dir = r"D:\Desktop\shiyan"

    if not os.path.exists(custom_download_dir):
        os.makedirs(custom_download_dir)

    url = r"https://www.agilent.com/en-us/library/usermanuals?N=135"

    chrome_options = webdriver.ChromeOptions()
    # 指定Chrome浏览器的可执行文件路径
    chrome_options.binary_location = r"C:\Users\jj_gu\AppData\Local\Google\Chrome\Application\chrome.exe"

    # 配置浏览器下载行为
    prefs = {
        "download.default_directory": custom_download_dir,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_settings.popups": 1,
        "directory_upgrade": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--disable-popup-blocking")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)

    attempt_count = 0
    page_number = 1

    main_window = driver.current_window_handle  # 保存主窗口句柄

    while True:
        print(f"正在处理第 {page_number} 页...")

        # 等待下载链接元素加载完成
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h.media-heading a"))
        )

        # 获取当前页面的下载链接并处理下载逻辑
        download_links = get_download_links(driver)
        for element, title, href in download_links:
            try:
                filename = sanitize_filename(title)
                # 检查文件是否已经存在
                existing_files = os.listdir(custom_download_dir)
                expected_files = [f"{filename}.pdf", f"{filename}.zip", f"{filename}.exe", f"{filename}.xlsx"]
                if any(f in existing_files for f in expected_files):
                    print(f"文件 '{filename}' 已存在，跳过下载。")
                    continue

                # 检查链接是否直接指向文件
                if is_direct_download(href):
                    print(f"链接直接指向文件，使用requests下载: {filename}")
                    # 获取浏览器的User-Agent和Cookies
                    headers = {
                        "User-Agent": driver.execute_script("return navigator.userAgent;")
                    }
                    cookies = get_session_cookies(driver)
                    ext = os.path.splitext(href)[1]
                    new_name = f"{filename}{ext}"
                    download_file(href, new_name, custom_download_dir, headers, cookies)
                else:
                    # 点击标题链接
                    before_click_windows = driver.window_handles
                    before_download = os.listdir(custom_download_dir)
                    click_element(driver, element)
                    time.sleep(2)  # 等待页面反应

                    after_click_windows = driver.window_handles

                    if len(after_click_windows) > len(before_click_windows):
                        # 新窗口已打开
                        new_window = [w for w in after_click_windows if w not in before_click_windows][0]
                        driver.switch_to.window(new_window)
                        download_url = driver.current_url

                        if is_direct_download(download_url):
                            print(f"新窗口URL指向文件，使用requests下载: {filename}")
                            headers = {
                                "User-Agent": driver.execute_script("return navigator.userAgent;")
                            }
                            cookies = get_session_cookies(driver)
                            ext = os.path.splitext(download_url)[1]
                            new_name = f"{filename}{ext}"
                            download_file(download_url, new_name, custom_download_dir, headers, cookies)
                        else:
                            print(f"在新窗口中处理下载: {filename}")
                            # 这里可以添加处理新窗口内容的逻辑

                        # **关闭新窗口并切换回主窗口**
                        driver.close()
                        driver.switch_to.window(before_click_windows[0])
                    else:
                        # 没有新窗口，可能直接触发了下载
                        print(f"链接直接触发下载，等待下载完成: {filename}")
                        wait_for_downloads(custom_download_dir, timeout=120)
                        time.sleep(2)  # 额外等待确保文件稳定

                        after_download = os.listdir(custom_download_dir)
                        new_files = list(set(after_download) - set(before_download))

                        if not new_files:
                            print(f"未检测到新下载的文件: {filename}")
                        else:
                            # 重命名新下载的文件
                            downloaded_file = new_files[0]
                            ext = os.path.splitext(downloaded_file)[1]
                            new_name = f"{filename}{ext}"
                            os.rename(
                                os.path.join(custom_download_dir, downloaded_file),
                                os.path.join(custom_download_dir, new_name)
                            )
                            print(f"成功下载并重命名文件: {new_name}")

            except Exception as e:
                log_error(title, str(e))

        # 尝试点击“下一页”按钮
        try:
            next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.page-forward > a")))
            if next_button.is_displayed():
                print("找到下一页按钮，准备点击...")

                # 记录当前URL
                current_url = driver.current_url

                driver.execute_script("arguments[0].click();", next_button)
                print("成功点击下一页按钮，等待页面加载...")

                # 等待URL变化或页面刷新
                WebDriverWait(driver, 30).until(EC.url_changes(current_url))

                # 等待新页面的标题元素加载完成
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h.media-heading a"))
                )

                time.sleep(2)
                attempt_count = 0  # 翻页成功，重置尝试次数
                page_number += 1
            else:
                print("未找到下一页按钮，爬取结束")
                break
        except Exception as e:
            print(f"未找到下一页按钮或发生错误: {str(e)}，当前尝试次数：{attempt_count}")
            attempt_count += 1
            if attempt_count >= 30:
                print("已到达最后一页或尝试次数过多，结束")
                break

    driver.quit()

if __name__ == "__main__":
    main()
