# PokerNow Automation Scripts

This repository contains two Python scripts, `autofolding.py` and `ownstat.py`, designed to automate actions on the PokerNow website.

## Files

- **autofolding.py**: Automates the folding of hands that are not playable.
- **ownstat.py**: Records your actions and calculates VPIP (Voluntarily Put Money In Pot) and PFR (Pre-Flop Raise).

## Prerequisites

1. **Chrome Driver**: 
   - Download the compatible Chrome Driver for your version of Chrome.
   - Store the path to the Chrome Driver.

2. **Python and Selenium**:
   - Ensure you have Python installed.
   - Install the Selenium module if not already installed:
     ```bash
     pip install selenium
     ```

## Usage

### autofolding.py

1. Run the script:
   ```bash
   python autofolding.py
   
2. Enter the required details when prompted.

3. Manually cross out any ads on PokerNow.

4. The program will start running within 10 seconds:
   - It will automatically fill in details.
   - It will auto-fold hands that are not playable.
   - Alerts will be given for playable hands.

### ownstat.py

1. Run the script:
   ```bash
   python autofolding.py

2. Manually cross out any ads on PokerNow.

3. Enter your commands through the terminal to record your actions and calculate VPIP and PFR.



   
