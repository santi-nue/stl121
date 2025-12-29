import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from urllib.parse import urljoin, urlparse
from webdriver_manager.chrome import ChromeDriverManager
import time


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

stealth(
    driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)




try:
    url = "https://www.ure.es/examenes/electricidad-y-radioelectricidad/"
    driver.get(url)
    time.sleep(5)

    # wait until consent button
    # consent_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'p.fc-button-label')))
    # consent_button.click()
	
    # wait until at least one checkbox label is present
    wait = WebDriverWait(driver, 15)
    labels = wait.until(
    	EC.presence_of_all_elements_located(
    		(By.CSS_SELECTOR, ".ari-checkbox-label.quiz-question-answer-ctrl-lbl")
    	)
    )
    
    print("Found", len(labels), "checkbox labels")
    
    for lbl in labels:
    	try:
    		# ensure it is clickable (in view and enabled)
    		wait.until(EC.element_to_be_clickable(lbl))
    		driver.execute_script("arguments[0].scrollIntoView({block:'center'});", lbl)
    		lbl.click()
    	except Exception as e:
    		print("Could not click one label:", e)	
 	
    # Save entire page HTML after interactions
    #full_html = driver.page_source
    
    #with open("full_page_after_checkboxes.html", "w", encoding="utf-8") as f:
    #	f.write(full_html)
 
    correct_divs_title = driver.find_elements(By.CSS_SELECTOR, ".quiz-question-title")
    
    correct_divs = driver.find_elements(By.CSS_SELECTOR, ".quiz-question-answer.quiz-question-answer-correct")
	
    completed_divs = driver.find_elements(By.CSS_SELECTOR, ".quiz-question.question-answered.question-completed")

    main_container = driver.find_element(By.CSS_SELECTOR, ".main-container.clearfix")	

    resultsTitles = []
    resultsIds = []

    for i, div in enumerate(correct_divs_title, 1):
        resultsTitles.append(div.text)

    for i, div in enumerate(completed_divs, 1):
        # Get the data-question-id attribute
        question_id = div.get_attribute("data-question-id")
        resultsIds.append(question_id)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"eleyrad_{timestamp}.html"
    dir_name = "eleyrad"
    os.makedirs(dir_name, exist_ok=True)
    path = os.path.join(dir_name, file_name)
	
    html_content = main_container.find_elements(By.CSS_SELECTOR, ".site-content.page-wrap")
	
    with open(path, "w", encoding="utf-8") as f:
        f.write("<html><head><style>.quiz-question-title { text-decoration: underline; padding: 20px; font-weight: bold;}</style>\n\n")
        f.write("<style>.quiz-question-result {display: none;}</style><style>.quiz-result-template {display: none;}</style>\n\n")
        f.write("<style>.quiz-result-wrapper {display: none;}</style><style>.quiz-description {display: none;}</style>\n\n")
		
        f.write("<style>.quiz-question-answer-correct { border: 3px solid green; padding: 2px;}</style>\n\n")
        f.write("<style>.asq-image.skip-lazy {width: auto; height: 100% !important; max-height: 480px !important; }</style></head><body>\n\n")

        f.write("<h1>Conocimientos de electricidad y radioelectricidad</h1>\n\n")		
		
        for cont in html_content:
            # if "Correcto" not in cont.text:		
                f.write(cont.get_attribute("innerHTML") + "\n")

        f.write("<br>")
				
        for item1, item2 in zip(resultsIds, resultsTitles):
            f.write(f"<p>{item1}\t{item2}</p>")				
				
        f.write("</body></html>")	

    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
        print(len(data))

finally:
    driver.quit()


