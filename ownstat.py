import os, time, random
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service

filelocation = input("Please enter your chromedriver location e.g. C:/Users/Alex/Downloads\n")
username = input("please enter ur poker name:(make sure it is unique in your table)\n")
url= input("please enter the Pokernow link:\n")
buyin = input("number of BB for buyin:\n")

#chrome setup below
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
#chrome_options.add_argument(r'--profile-directory=Default')
os.environ['PATH'] += filelocation
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

#request seat in pokernow and wait for first hand
time.sleep(10)  # manual cross out ads if any
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sit')]"))
)
seatbutton = driver.find_elements(By.XPATH, "//*[contains(text(), 'Sit')]")
seatbutton[-1].click()

# WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[3]/div/p/span/span[2]/span'))
# )

bb = int(driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[3]/div/div/div[2]/span[2]/span').text)
namefield = driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]//input[@placeholder="Your Name"]')
namefield.send_keys(username)
bbfield = driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]//input[@placeholder="Intended Stack"]')
bbfield.send_keys(int(buyin) * bb)
requestbutton = driver.find_element(By.XPATH, "//*[contains(text(), 'Request the Seat')]")
requestbutton.click()  #ignore the error for repeated names
time.sleep(0.5)
actions = ActionChains(driver)
actions.send_keys(Keys.ENTER)
actions.perform()


listOfStackLv = []
positionNow = 0
vpipcount = 0
pfrcount = 0
firstCommandinThishand = True
debug = False
plt.ion()

while True:
    if debug==False:
        os.system('cls' if os.name == 'nt' else 'clear')
    print("=====================")
    if positionNow!=0:
        #display info
        print("VPIP: ", round(100*vpipcount/len(listOfStackLv),2), "%")
        print("PFR:  ", round(100*pfrcount/len(listOfStackLv),2), "%")

    command = input("Action:\n") #k, c, r30, b, m, i, f
    if positionNow==0:
        dbutton = driver.find_element(By.XPATH, '//*[contains(@class, "dealer-position")]')
        positionNow = dbutton.get_attribute('class')[-1]  #initialise position and stack
        stacklevel = driver.find_element(By.CLASS_NAME, 'table-player-1').find_element(By.CLASS_NAME, 'table-player-stack').find_element(By.CSS_SELECTOR,"span.normal-value").get_attribute('innerText')
        listOfStackLv.append(int(stacklevel))
    
    try:
        dbutton = driver.find_element(By.XPATH, '//*[contains(@class, "dealer-position")]')
    except:
        break  #game end, no button    

    if positionNow != dbutton.get_attribute('class')[-1]:  
        positionNow = dbutton.get_attribute('class')[-1]   #new hand
        stacklevel = driver.find_element(By.CLASS_NAME, 'table-player-1').find_element(By.CLASS_NAME, 'table-player-stack').find_element(By.CSS_SELECTOR,"span.normal-value").get_attribute('innerText')
        listOfStackLv.append(int(stacklevel))
        firstCommandinThishand = True
    char_list =[]
    for char in command:
        char_list.append(char)
    if char_list!=[] and char_list[0]=='q':
        break
    x = [i for i in range(len(listOfStackLv))]
    plt.plot(x,listOfStackLv)
    plt.xlabel("Hands")
    plt.ylabel("Stack Level")
    plt.grid(axis = 'y')
    plt.draw()
    for keyy in char_list:
        actions = ActionChains(driver)
        actions.send_keys(keyy)
        actions.perform()
        #time.sleep(0.1)
    if char_list==[] or char_list[0]=='r' or char_list[0]=='m' :
        actions = ActionChains(driver)
        actions.send_keys(Keys.ENTER)
        actions.perform()

    #cal VPIP here
    if firstCommandinThishand:
        if char_list[0]=='r' or char_list[0]=='c':
            vpipcount+=1
        if char_list[0]=='r':
            pfrcount +=1

    if debug == True:
        print("First action in this hand: ",firstCommandinThishand)

    if char_list != [] and (char_list[0]=='r' or char_list[0]=='k' or char_list[0]=='f' or char_list[0]=='i' or char_list[0]=='c'):
        firstCommandinThishand = False

    if debug == True:
        print("StackLevel: ", stacklevel)
        print("PositionNow: ", positionNow)
        print("List: ", listOfStackLv)





x = [i for i in range(len(listOfStackLv))]
plt.plot(x,listOfStackLv)
plt.xlabel("Hands")
plt.ylabel("Stack Level")
plt.grid(axis = 'y')
plt.show()
wait = input()
    



