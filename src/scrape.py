import undetected_chromedriver as uc
import time
import random

def run_stealth_browser():
    print("Launching Stealth Browser...")
    options = uc.ChromeOptions()
    
    options.add_argument("--window-size=1920,1080")
    
    driver = uc.Chrome(options=options, headless=False)

    try:
        url = "https://scottsbluff.craigslist.org/search/huntley-wy/mca?lat=41.705&lon=-104.0625&search_distance=1000"
        print(f"Navigating to {url}...")
        
        driver.get(url)

        time.sleep(random.uniform(5, 8))

        if "Access Denied" in driver.title or "Reference #" in driver.page_source:
            print("\n FAILURE: Akamai still detected us.")
        else:
            print(f"\n SUCCESS! Page Title: {driver.title}")
            print("You have successfully bypassed the firewall.")
            
            with open("motorcycles.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Saved page content to 'motorcycles.html'")

        time.sleep(5)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == '__main__':
    run_stealth_browser()