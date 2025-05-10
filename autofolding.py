import os, time, random, winsound
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

filelocation = input("Please enter your chromedriver location e.g. C:/Users/Alex/Downloads\n")
username = input("Please enter your poker name:(make sure it is unique in your table)\n")
url= input("Please enter the Pokernow link:\n")
freq = int(input("Checking for the next hand every __ second(s)?  *enter a number in the range of 1 to 5\n"))
tight = int(input("You wanna fold more(0) or less(1)?\n"))



longwaitingtime = random.randint(1, freq)
shortwaitingtime = 0

#chrome setup below
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
os.environ['PATH'] += filelocation
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

#request seat in pokernow and wait for first hand
time.sleep(10)  # manual cross out ads if any
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sit')]"))
)
seatbutton = driver.find_elements(By.XPATH, "//*[contains(text(), 'Sit')]")
# time.sleep(2)
seatbutton[-1].click()


bb = int(driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[3]/div/div/div[2]/span[2]/span').text)
sb = int(driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[3]/div/div/div[2]/span[1]/span').text)
namefield = driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]//input[@placeholder="Your Name"]')
namefield.send_keys(username)
bbfield = driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]//input[@placeholder="Intended Stack"]')
bbfield.send_keys(100 * bb)
requestbutton = driver.find_element(By.XPATH, "//*[contains(text(), 'Request the Seat')]")
requestbutton.click()  #ignore the error for repeated names
time.sleep(0.5)
actions = ActionChains(driver)
actions.send_keys(Keys.ENTER)
actions.perform()

time.sleep(longwaitingtime)

while True:
    while not driver.find_elements(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]/div[2]/div[3]/div[2]/div/div[2]/span[1]'):
        time.sleep(longwaitingtime+1.5)
        print('waiting for first hand') #comment out later

    #hand found
    myhand=[]
    myhand.append(driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]/div[2]/div[3]/div[2]/div/div[2]/span[1]').text)
    #time.sleep(shortwaitingtime)
    myhand.append(driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]/div[2]/div[3]/div[1]/div/div[2]/span[1]').text)
    #time.sleep(shortwaitingtime)
    onesuit     = driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]/div[2]/div[3]/div[2]/div/div[2]/span[2]').get_attribute("innerHTML")
    #time.sleep(shortwaitingtime)
    secondsuit  = driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]/div[2]/div[3]/div[1]/div/div[2]/span[2]').get_attribute("innerHTML")
    if onesuit == secondsuit:
        myhand.append('s')
    else:
        myhand.append('o')

    print('Your hand is '+ str(myhand))




    #check for big blind or not            
    myblind = driver.find_elements(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]/div[2]/p/span/span[@class="normal-value"]')


    #time.sleep(shortwaitingtime)
    smallblind = False
    if myblind == []:
        bigblind = False   #no blinds
    else:

        realpotsize = int(driver.execute_script("return arguments[0].innerHTML;", myblind[0]))
        if int(realpotsize)!=bb:
            bigblind = False   #I am small blind
            smallblind = True
        else:
            bigblind = True
        

    #check for dealer or not
    dealerposition = driver.find_elements(By.CLASS_NAME, 'dealer-position-1')
    #time.sleep(shortwaitingtime)
    if dealerposition==[]:
        dealer = False
    else:
        dealer = True

    
      
    #check hand shift
    dbutton = driver.find_element(By.XPATH, '//*[contains(@class, "dealer-position")]')
    position = dbutton.get_attribute('class')[-1]
    #time.sleep(shortwaitingtime)

    handstrength = 0

    transformation = {'J':11, 'Q':12, 'K':13, 's':'s', 'o':'o', 'A':14}
    for i in range(2,11):
        transformation[str(i)]=i

    processedhand = []
    for i in myhand:
        processedhand.append(transformation[i])
    
    hsum = processedhand[0]+processedhand[1]
    hdif = abs(processedhand[0]-processedhand[1])
    
    if processedhand[0]>=10 and processedhand[1]>=10:
        handstrength=4
    elif (processedhand[0]==14 or processedhand[1]==14) and processedhand[2]=='s':
        handstrength=4
    elif processedhand[0]>=8 and processedhand[1]>=8 and processedhand[2]=='s' and hsum>18:
        handstrength=4
    elif hdif==0 and processedhand[0]>=6:
        handstrength=4
    elif (processedhand[0]==14 or processedhand==14) and hsum>=22:
        handstrength=4
    
    if handstrength==0:
        if processedhand[2]=='s' and (processedhand[0]==13 or processedhand[1]==13):
            handstrength=3
        elif hdif==0:
            handstrength=3
        elif processedhand[2]=='o' and (processedhand[0]==14 or processedhand[1]==14):
            handstrength=3
        elif processedhand[2]=='o' and (processedhand[0]>=9 and processedhand[1]>=9):
            handstrength=3
        elif (processedhand[0]==11 and processedhand[1]==7 or processedhand[0]==7 and processedhand[1]==11) and processedhand[2]=='s':
            handstrength=3
        elif hdif==1 and hsum>=13 and processedhand[2]=='s':
            handstrength=3
        
        if handstrength==0:
            if processedhand[0]==13 or processedhand[1]==13:
                handstrength=2
            elif processedhand[0]>=8 and processedhand[1]>=8:
                handstrength=2
            elif (processedhand[0]>=11 or processedhand[1]>=11) and processedhand[2]=='s' and hsum>=14:
                handstrength=2
            elif processedhand[2]=='s' and (processedhand[0]>=5 and processedhand[1]>=5):
                handstrength=2
            elif processedhand[2]=='o' and (processedhand[0]>=11 and processedhand[1]==7 or processedhand[0]==7 and processedhand[1]>=11):
                handstrength=2
            elif processedhand[2]=='s' and (processedhand[0]==3 and processedhand[1]==5 or processedhand[0]==3 and processedhand[1]==5):
                handstrength=2
            elif hdif==1 and hsum>=13:
                handstrength=2
            elif hdif==1 and hsum>=7 and processedhand[2]=='s':
                handstrength=2
            else:
                handstrength=1
    
    #handstrength=0 #for debug
    print("\n")
    if dealer:
        print('You are the dealer\n')
    if bigblind:
        print('You are the Big blind\n')
    if smallblind:
        print('You are the Small blind\n')
    #print('dealerposition: ' + position)
    print('handstrength: ' + str(handstrength) + '\n')

    #check first raise or not if I am not bigblind, i.e. bigblind will skip this
    #so wont prefold if not bigblind
    myturn = driver.find_elements(By.XPATH, "//*[contains(text(), 'Your Turn')]")
    firstraise = True

# //*[@id="canvas"]/div[1]/div[3]/div[4]/div[2]/div[1]/span/span
# //*[@id="canvas"]/div[1]/div[3]/div[4]/div[2]/div[2]/p/span/span

# //*[@id="canvas"]/div[1]/div[3]/div[4]/div[2]/div[2]/p/span/span[2]
    if not bigblind:
        ele = driver.find_element(By.XPATH,'//*[@id="canvas"]/div[1]/div[3]/div[4]/div[2]/div[2]/p/span/span[@class="normal-value"]')
        potsize = int(driver.execute_script("return arguments[0].innerHTML;", ele))
        while not myturn and potsize==(sb+bb):
            time.sleep(1)
            myturn = driver.find_elements(By.XPATH, "//*[contains(text(), 'Your Turn')]")
            potsize = int(driver.execute_script("return arguments[0].innerHTML;", ele))
        potsize = int(driver.execute_script("return arguments[0].innerHTML;", ele))
        if potsize==(sb+bb):
            firstraise=True
        else:
            firstraise=False



    if tight==0:  
        #fold more
        if not bigblind and not dealer and not smallblind and not firstraise: #normal positions or dealer not first raise

            #play 4
            if handstrength==4:
                print('Playable')
                winsound.Beep(440, 300)
                #add alert 
            else:
                #just fold
                actions = ActionChains(driver)
                actions.send_keys('f')
                actions.perform()
                print("AutoFolded")

        elif not bigblind and not dealer and not smallblind and firstraise:

            #play 4 3 
            if handstrength>=3:
                print('Playable')
                winsound.Beep(440, 300)
                #add alert 
            else:
                #just fold
                actions = ActionChains(driver)
                actions.send_keys('f')
                actions.perform()
                print("AutoFolded")



        elif smallblind and not firstraise:

            #play 4 3
            if handstrength>=3:
                print('Playable')
                winsound.Beep(440, 300)
                #add alert 
            else:
                #just fold
                actions = ActionChains(driver)
                actions.send_keys('f')
                actions.perform()
                print("AutoFolded")
        

        elif dealer and firstraise:
            # first raise as dealer
            #play 4 3 2 
            if handstrength>=2:
                print('Playable')
                winsound.Beep(440, 300)
                #add alert 
            else:
                #just fold
                actions = ActionChains(driver)
                actions.send_keys('f')
                actions.perform()
                print("AutoFolded")

        elif dealer and not firstraise:
            # first raise as dealer
            #play 4 3
            if handstrength>=3:
                print('Playable')
                winsound.Beep(440, 300)
                #add alert 
            else:
                #just fold
                actions = ActionChains(driver)
                actions.send_keys('f')
                actions.perform()
                print("AutoFolded")

        elif smallblind and firstraise or bigblind:
            #play 4 3 2 + s
            if handstrength>=2 or myhand[2]=='s':
                print('Playable')
                winsound.Beep(440, 300)
                #add alert 
            else:
                #just fold
                if not bigblind:
                    actions = ActionChains(driver)
                    actions.send_keys('f')
                    actions.perform()
                    print("AutoFolded")
                else:
                    #if big blinfd, checkfold
                    actions = ActionChains(driver)
                    actions.send_keys('i')
                    actions.perform()
                    print("AutoCheckFolded")
                    #handle the case where checkfold but see flop
                    #wait until blind disappear, then see potsize, if not zero, it means see flop, if zero, it means next hand
                    #deal with fold and other see flop
                    while myblind !=[]:
                        time.sleep(1)
                        myblind = driver.find_elements(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]/div[2]/p/span/span')
                    ele = driver.find_element(By.XPATH,'//*[@id="canvas"]/div[1]/div[3]/div[4]/div[2]/div[1]/span/span[@class="normal-value"]')
                    realpotsize = int(driver.execute_script("return arguments[0].innerHTML;", ele))


                
                    #find folding hands
                    time.sleep(0.5)
                    foldinghands = driver.find_elements(By.XPATH, "//*[@id='canvas']/div[1]/div[3]/div[4]/div[4]/div[2]//div[contains(@class, 'hide')]")
                    if realpotsize!=0 and foldinghands==[]:
                        print('Check around and see the flop')
                        winsound.Beep(240, 300)
                    
                    


    else:
        #tight is 1, fold less
        if not bigblind and not dealer and not smallblind and not firstraise: #normal positions 

            #play 4 3
            if handstrength>=3:
                print('Playable')
                winsound.Beep(440, 300)
                #add alert 
            else:
                #just fold
                actions = ActionChains(driver)
                actions.send_keys('f')
                actions.perform()
                print("AutoFolded")

            

        
        elif not bigblind and not dealer and not smallblind and firstraise:
            #play 4 3 2
            if handstrength>=2:
                print('Playable')
                winsound.Beep(440, 300)
                #add alert 
            else:
                #just fold
                actions = ActionChains(driver)
                actions.send_keys('f')
                actions.perform()
                print("AutoFolded")

        elif smallblind and not firstraise:

            #play 4 3 2
            if handstrength>=2:
                print('Playable')
                winsound.Beep(440, 300)
                #add alert 
            else:
                #just fold
                actions = ActionChains(driver)
                actions.send_keys('f')
                actions.perform()
                print("AutoFolded")
            
            

        elif dealer:
            #dealer
            #play 4 3 2 
            if handstrength>=2:
                print('Playable')
                winsound.Beep(440, 300)
                #add alert 
            else:
                #just fold
                actions = ActionChains(driver)
                actions.send_keys('f')
                actions.perform()
                print("AutoFolded")

        elif smallblind and firstraise or bigblind:
            #play 4 3 2 + s
            if handstrength>=2 or myhand[2]=='s':
                print('Playable')
                winsound.Beep(440, 300)
                #add alert 
            else:
                if not bigblind:
                    #just fold
                    actions = ActionChains(driver)
                    actions.send_keys('f')
                    actions.perform()
                    print("AutoFolded")
                else:
                    #if big blind, checkfold
                    actions = ActionChains(driver)
                    actions.send_keys('i')
                    actions.perform()
                    print("AutoCheckFolded")
                    #handle the case where checkfold but see flop
                    #wait until blind disappear, then see potsize, if not zero, it means see flop, if zero, it means next hand
                    while myblind !=[]:
                        time.sleep(1)
                        myblind = driver.find_elements(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[4]/div[2]/p/span/span')
                    # realpotsize = int(driver.find_element(By.XPATH, '//*[@id="canvas"]/div[1]/div[3]/div[4]/div[2]/div[1]/span/span[@class="normal-value"]').text)
                    ele = driver.find_element(By.XPATH,'//*[@id="canvas"]/div[1]/div[3]/div[4]/div[2]/div[1]/span/span[@class="normal-value"]')
                    realpotsize = int(driver.execute_script("return arguments[0].innerHTML;", ele))
                    
                    #find folding hands
                    time.sleep(0.5)
                    foldinghands = driver.find_elements(By.XPATH, "//*[@id='canvas']/div[1]/div[3]/div[4]/div[4]/div[2]//div[contains(@class, 'hide')]")
                    if realpotsize!=0 and foldinghands==[]:
                        print('Check around and see the flop')
                        winsound.Beep(240, 300)



        




    #detect next hand or not
    #use shift of dealer button position to judge, ignore the case where ppl leaving the table making the dealer button position unchange, if thats the case, pokernow will autofold for u after timeout
    time.sleep(longwaitingtime+5)
    dbutton = driver.find_element(By.XPATH, '//*[contains(@class, "dealer-position")]')
    newposition = dbutton.get_attribute('class')[-1]

    while position == newposition:
        #print('checking for next hand...')  #comment out later
        time.sleep(longwaitingtime+1.5)
        dbutton = driver.find_element(By.XPATH, '//*[contains(@class, "dealer-position")]')
        newposition = dbutton.get_attribute('class')[-1]
        #maybe some func here allow user to terminate prog if they want

    #time.sleep(shortwaitingtime)
    print("===================================")
    
    




