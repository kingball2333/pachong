from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import os
import time

def main():
    custom_download_dir = r"D:\Desktop\shiyan1"
    if not os.path.exists(custom_download_dir):
        os.makedirs(custom_download_dir)

    # 配置 Edge 浏览器的选项
    edge_options = webdriver.EdgeOptions()
    prefs = {
        "download.default_directory": custom_download_dir,
        "profile.default_content_settings.popups": 0,
    }
    edge_options.add_experimental_option("prefs", prefs)

    # 初始化 Edge 驱动
    service = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=edge_options)

    # 访问目标网站
    url = r"https://www.agilent.com/en-us/library/usermanuals?N=135"  # 替换为实际的目标网站 URL
    driver.get(url)

    attempt_count = 0
    while True:
        # 关闭弹窗或同意横幅的逻辑（视具体网站而定）
        try:
            accept_button = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable((By.ID, "truste-consent-button"))
            )
            accept_button.click()
            print("成功关闭横幅")
        except Exception as e:
            print("找不到横幅或关闭失败：", str(e))

        # 等待页面加载并获取下载链接
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h.media-heading a"))
        )

        # 获取包含下载链接的元素
        download_links = driver.find_elements(By.CSS_SELECTOR, "h.media-heading a")

        for element in download_links:
            try:
                # 点击标题链接，打开新页面
                element.click()
                WebDriverWait(driver, 3).until(EC.number_of_windows_to_be(2))

                # 切换到新窗口
                new_window = driver.window_handles[-1]
                driver.switch_to.window(new_window)

                # 等待下载按钮出现，并点击下载按钮
                WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "cr-icon-button#download"))
                )
                download_button = driver.find_element(By.CSS_SELECTOR, "cr-icon-button#download")
                driver.execute_script("arguments[0].click();", download_button)

                print(f"成功点击下载按钮: {element.text}")

                # 等待下载完成
                time.sleep(5)  # 可以根据文件大小适当调整等待时间

                # 关闭新窗口并切换回原窗口
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except Exception as e:
                print(f"Error downloading file: {e}")

        # 检查是否存在“下一页”按钮
        try:
            next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.page-forward > a")))
            if next_button.is_displayed():
                print("找到下一页按钮，准备点击...")
                driver.execute_script("arguments[0].click();", next_button)
                print("成功点击下一页按钮，等待页面加载...")

                # 等待页面刷新
                WebDriverWait(driver, 30).until(
                    EC.staleness_of(next_button)
                )
                time.sleep(5)
                attempt_count = 0  # 翻页成功，重置尝试次数
            else:
                print("未找到下一页按钮，爬取结束")
                break
        except Exception as e:
            print(f"未找到下一页按钮或发生错误: {str(e)}，当前尝试次数：{attempt_count}")
            attempt_count += 1
            if attempt_count >= 300:
                print("已到达最后一页或尝试次数过多，结束")
                break

    driver.quit()

if __name__ == "__main__":
    main()
