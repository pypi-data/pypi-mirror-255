from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

youtubeLink = "https://www.youtube.com/watch?v=V0Sdgn0_kFM"
rejectXPath = '//*[@id="content"]/div[2]/div[6]/div[1]/ytd-button-renderer[1]/yt-button-shape/button'
transcriptSelector = "#primary-button > ytd-button-renderer > yt-button-shape > button"
    
class Transcript:
    def __init__(self, headless=False):
        self.options = Options()
        self.options.add_experimental_option("detach", True)
        if headless:
            self.options.add_argument('--headless')
        self.browser = Chrome(options=self.options)
        self.waiter = WebDriverWait(self.browser, 20)

    def get_transcript(self):
        print("Opening YouTube...")
        self.browser.get(youtubeLink)

        print("Reject cookies...")
        rejectButton = self.waiter.until(
            EC.element_to_be_clickable((By.XPATH, rejectXPath))
        )
        rejectButton.click()

        print("Expand description...")
        expandButton = self.waiter.until(
            EC.element_to_be_clickable((By.ID, "expand"))
        )
        expandButton.click()

        print("Reveal transcripts...")
        transcriptsButton = self.waiter.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, transcriptSelector))
        )
        transcriptsButton.click()

        print("Grab transcript...")
        transcriptElements = self.waiter.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "segment-text")))
        transcriptLines = [transcriptElement.get_attribute("innerHTML") for transcriptElement in transcriptElements]
        transcriptText = "\n".join(transcriptLines)
        transcriptText.replace("&nbsp","")
        with open("output.txt", "w", encoding="utf-8") as file:
            file.write(transcriptText)

        print("Closing browser...")
        self.browser.quit()
