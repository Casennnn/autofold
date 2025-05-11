import os
import time
import random
import winsound
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


def get_user_inputs():
    """Prompts the user for necessary inputs and returns them as a dictionary."""
    filelocation = input("Please enter your chromedriver location e.g. C:/Users/Alex/Downloads\n")
    username = input("\nPlease enter your poker name:(make sure it is unique in your table)\n")
    url = input("\nPlease enter the Pokernow link:\n")
    freq = int(input("\nChecking for the next hand every __ second(s)?  *enter a number in the range of 1 to 5\n"))
    tight = int(input("\nYou wanna fold more(0) or less(1)?\n"))
    buyin_str = input("\nPlease enter your intended buy-in in terms of BB(optional, default is 100BB):\n")
    buyin = 100 if not buyin_str else int(buyin_str)  # Default to 100 if input is empty

    return {
        "filelocation": filelocation,
        "username": username,
        "url": url,
        "freq": freq,
        "tight": tight,
        "buyin": buyin,
    }


def setup_driver(filelocation, url):
    """Sets up the Chrome driver with the given file location and navigates to the specified URL."""
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    os.environ["PATH"] += filelocation
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    return driver


def request_seat(driver, username, buyin):
    """Requests a seat in the Pokernow game and enters the username and intended stack."""
    time.sleep(7)  # Manual cross out ads if any
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sit')]")))
    seatbutton = driver.find_elements(By.XPATH, "//*[contains(text(), 'Sit')]")
    seatbutton[-1].click()

    bb = int(driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[3]/div/div/div[2]/span[2]/span').text)
    namefield = driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]//input[@placeholder="Your Name"]')
    namefield.send_keys(username)
    bbfield = driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]//input[@placeholder="Intended Stack"]')
    bbfield.send_keys(buyin * bb)
    requestbutton = driver.find_element(By.XPATH, "//*[contains(text(), 'Request the Seat')]")
    requestbutton.click()  # Ignore the error for repeated names
    time.sleep(0.5)
    actions = ActionChains(driver)
    actions.send_keys(Keys.ENTER)
    actions.perform()


def wait_for_hand(driver, longwaitingtime):
    """Waits until a hand is dealt to the player."""
    while not driver.find_elements(
        By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]/div[2]/div[3]/div[2]/div/div[2]/span[1]'
    ):
        time.sleep(longwaitingtime + 1.5)
        print("waiting for first hand")  # Comment out later


def extract_hand(driver):
    """Extracts the player's hand from the webpage."""
    myhand = []
    myhand.append(
        driver.find_element(
            By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]/div[2]/div[3]/div[2]/div/div[2]/span[1]'
        ).text
    )
    myhand.append(
        driver.find_element(
            By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]/div[2]/div[3]/div[1]/div/div[2]/span[1]'
        ).text
    )
    onesuit = driver.find_element(
        By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]/div[2]/div[3]/div[2]/div/div[2]/span[2]'
    ).get_attribute("innerHTML")
    secondsuit = driver.find_element(
        By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]/div[2]/div[3]/div[1]/div/div[2]/span[2]'
    ).get_attribute("innerHTML")
    myhand.append("s" if onesuit == secondsuit else "o")
    return myhand


def determine_blind_and_dealer(driver, bb):
    """Determines if the player is the big blind, small blind, or dealer."""
    myblind = driver.find_elements(
        By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]/div[2]/p/span/span[@class="normal-value"]'
    )
    smallblind = False
    if not myblind:
        bigblind = False  # no blinds
    else:
        realpotsize = int(driver.execute_script("return arguments[0].innerHTML;", myblind[0]))
        if int(realpotsize) != bb:
            bigblind = False  # I am small blind
            smallblind = True
        else:
            bigblind = True

    dealerposition = driver.find_elements(By.CLASS_NAME, "dealer-position-1")
    dealer = False if not dealerposition else True

    return bigblind, smallblind, dealer


def calculate_hand_strength(myhand):
    """Calculates the strength of the player's hand based on predefined rules."""
    handstrength = 0
    transformation = {"J": 11, "Q": 12, "K": 13, "s": "s", "o": "o", "A": 14}
    for i in range(2, 11):
        transformation[str(i)] = i

    processedhand = [transformation[i] for i in myhand]

    hsum = processedhand[0] + processedhand[1]
    hdif = abs(processedhand[0] - processedhand[1])

    if processedhand[0] >= 10 and processedhand[1] >= 10:
        handstrength = 4
    elif (processedhand[0] == 14 or processedhand[1] == 14) and myhand[2] == "s":
        handstrength = 4
    elif processedhand[0] >= 8 and processedhand[1] >= 8 and myhand[2] == "s" and hsum > 18:
        handstrength = 4
    elif hdif == 0 and processedhand[0] >= 6:
        handstrength = 4
    elif (processedhand[0] == 14 or processedhand[1] == 14) and hsum >= 22:
        handstrength = 4

    if handstrength == 0:
        if myhand[2] == "s" and (processedhand[0] == 13 or processedhand[1] == 13):
            handstrength = 3
        elif hdif == 0:
            handstrength = 3
        elif myhand[2] == "o" and (processedhand[0] == 14 or processedhand[1] == 14):
            handstrength = 3
        elif myhand[2] == "o" and (processedhand[0] >= 9 and processedhand[1] >= 9):
            handstrength = 3
        elif (
            processedhand[0] == 11 and processedhand[1] == 7 or processedhand[0] == 7 and processedhand[1] == 11
        ) and myhand[2] == "s":
            handstrength = 3
        elif hdif == 1 and hsum >= 13 and myhand[2] == "s":
            handstrength = 3

        if handstrength == 0:
            if processedhand[0] == 13 or processedhand[1] == 13:
                handstrength = 2
            elif processedhand[0] >= 8 and processedhand[1] >= 8:
                handstrength = 2
            elif (processedhand[0] >= 11 or processedhand[1] >= 11) and myhand[2] == "s" and hsum >= 14:
                handstrength = 2
            elif myhand[2] == "s" and (processedhand[0] >= 5 and processedhand[1] >= 5):
                handstrength = 2
            elif (
                myhand[2] == "o"
                and (processedhand[0] >= 11 and processedhand[1] == 7 or processedhand[0] == 7 and processedhand[1] >= 11)
            ):
                handstrength = 2
            elif myhand[2] == "s" and (processedhand[0] == 3 and processedhand[1] == 5 or processedhand[0] == 3 and processedhand[1] == 5):
                handstrength = 2
            elif hdif == 1 and hsum >= 13:
                handstrength = 2
            elif hdif == 1 and hsum >= 7 and myhand[2] == "s":
                handstrength = 2
            else:
                handstrength = 1

    return handstrength


def should_fold(handstrength, bigblind, dealer, smallblind, firstraise, tight, myhand):
    """Determines whether the player should fold based on hand strength, position, and game settings."""
    if tight == 0:  # Fold more
        if not bigblind and not dealer and not smallblind and not firstraise:  # Normal positions or dealer not first raise
            return handstrength < 4
        elif not bigblind and not dealer and not smallblind and firstraise:
            return handstrength < 3
        elif smallblind and not firstraise:
            return handstrength < 3
        elif dealer and firstraise:
            return handstrength < 2
        elif dealer and not firstraise:
            return handstrength < 3
        elif smallblind and firstraise or bigblind:
            return handstrength < 2 and myhand[2] != "s"
        else:
            return False  # Should not happen, but added for completeness
    else:  # tight == 1, fold less
        if not bigblind and not dealer and not smallblind and not firstraise:  # Normal positions
            return handstrength < 3
        elif not bigblind and not dealer and not smallblind and firstraise:
            return handstrength < 2
        elif smallblind and not firstraise:
            return handstrength < 2
        elif dealer:
            return handstrength < 2
        elif smallblind and firstraise or bigblind:
            return handstrength < 2 and myhand[2] != "s"
        else:
            return False  # Should not happen, but added for completeness


def play_hand(driver, handstrength, bigblind):
    """Plays a hand by beeping and bringing the window to the front."""
    print("Playable")
    winsound.Beep(440, 300)
    main_window_handle = driver.current_window_handle
    driver.switch_to.window(main_window_handle)

def handle_blinds(driver, bigblind, myblind, bb, sb):
    """Handles the logic for playing as the big or small blind."""
    if not bigblind:
        actions = ActionChains(driver)
        actions.send_keys("f")
        actions.perform()
        print("AutoFolded")
    else:
        # If big blind, checkfold
        actions = ActionChains(driver)
        actions.send_keys("i")
        actions.perform()
        print("AutoCheckFolded")

        # Handle the case where checkfold but see flop
        # Wait until blind disappear, then see potsize, if not zero, it means see flop, if zero, it means next hand
        while myblind:
            time.sleep(1)
            myblind = driver.find_elements(
                By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]/div[2]/p/span/span'
            )
        ele = driver.find_element(
            By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[2]/div[1]/span/span[@class="normal-value"]'
        )
        realpotsize = int(driver.execute_script("return arguments[0].innerHTML;", ele))

        # Find folding hands
        time.sleep(0.5)
        foldinghands = driver.find_elements(
            By.XPATH, "//*[@id='canvas']/div[1]/div[3]/div[4]/div[4]/div[2]//div[contains(@class, 'hide')]"
        )
        if realpotsize != 0 and not foldinghands:
            print("Check around and see the flop")
            winsound.Beep(240, 300)


def wait_for_next_hand(driver, position, longwaitingtime):
    """Waits for the next hand to be dealt by monitoring the dealer button position."""
    time.sleep(longwaitingtime + 5)
    dbutton = driver.find_element(By.XPATH, '//*[contains(@class, "dealer-position")]')
    newposition = dbutton.get_attribute("class")[-1]

    while position == newposition:
        time.sleep(longwaitingtime + 1.5)
        dbutton = driver.find_element(By.XPATH, '//*[contains(@class, "dealer-position")]')
        newposition = dbutton.get_attribute("class")[-1]


def check_first_raise(driver, sb, bb):
    """Checks if there has been a raise before the player's turn."""
    myturn = driver.find_elements(By.XPATH, "//*[contains(text(), 'Your Turn')]")
    firstraise = True
    ele = driver.find_element(
        By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[2]/div[2]/p/span/span[@class="normal-value"]'
    )
    potsize = int(driver.execute_script("return arguments[0].innerHTML;", ele))
    while not myturn and potsize == (sb + bb):
        time.sleep(1)
        myturn = driver.find_elements(By.XPATH, "//*[contains(text(), 'Your Turn')]")
        potsize = int(driver.execute_script("return arguments[0].innerHTML;", ele))
    potsize = int(driver.execute_script("return arguments[0].innerHTML;", ele))
    if potsize == (sb + bb):
        firstraise = True
    else:
        firstraise = False
    return firstraise


def main():
    """Main function to run the poker bot."""
    inputs = get_user_inputs()
    filelocation = inputs["filelocation"]
    username = inputs["username"]
    url = inputs["url"]
    freq = inputs["freq"]
    tight = inputs["tight"]
    buyin = inputs['buyin']

    longwaitingtime = random.randint(1, freq)
    shortwaitingtime = 0

    driver = setup_driver(filelocation, url)
    request_seat(driver, username, buyin)

    bb = int(driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[3]/div/div/div[2]/span[2]/span').text)
    sb = int(driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[3]/div/div/div[2]/span[1]/span').text)

    time.sleep(longwaitingtime)

    while True:
        wait_for_hand(driver, longwaitingtime)

        # Hand found
        myhand = extract_hand(driver)
        print("Your hand is " + str(myhand))

        # Check for big blind or not
        bigblind, smallblind, dealer = determine_blind_and_dealer(driver, bb)

        # Check hand shift
        dbutton = driver.find_element(By.XPATH, '//*[contains(@class, "dealer-position")]')
        position = dbutton.get_attribute("class")[-1]

        handstrength = calculate_hand_strength(myhand)

        print("\n")
        if dealer:
            print("You are the dealer\n")
        if bigblind:
            print("You are the Big blind\n")
        if smallblind:
            print("You are the Small blind\n")
        print("handstrength: " + str(handstrength) + "\n")

        # Check first raise or not if I am not bigblind, i.e. bigblind will skip this
        # so wont prefold if not bigblind
        firstraise = True
        if not bigblind:
            firstraise = check_first_raise(driver, sb, bb)

        if should_fold(handstrength, bigblind, dealer, smallblind, firstraise, tight, myhand):
            if not bigblind:
                # Just fold
                actions = ActionChains(driver)
                actions.send_keys("f")
                actions.perform()
                print("AutoFolded")
            else:
                myblind = driver.find_elements(
                    By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]/div[2]/p/span/span'
                )
                handle_blinds(driver, bigblind, myblind, bb, sb)

        else:
            play_hand(driver, handstrength, bigblind)

        # Detect next hand or not
        # Use shift of dealer button position to judge, ignore the case where ppl leaving the table making the dealer button position unchange, if thats the case, pokernow will autofold for u after timeout
        wait_for_next_hand(driver, position, longwaitingtime)

        print("===================================")


if __name__ == "__main__":
    main()