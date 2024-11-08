import os
import csv
import re

from db import Database
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

    current_date = datetime.now()
    datetime_string = current_date.strftime("%Y-%m-%d %H:%M:%S")

def getOrCreateConstituentID(email):
    username = email.split("@")[0]

    firstname = ""
    surname = ""
    if "." in username:
        firstname = username.split(".")[0].capitalize()
        surname = username.split(".")[1].capitalize()
    else:
        surname = username.capitalize()

    db = Database(os.getenv('SUPPORT_DB_NAME'))
    db.query("INSERT INTO `constituents` (firstname, surname, email) SELECT %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM `constituents` WHERE `email` = %s);", [firstname, surname, email, email])
    result = db.query("SELECT `ID` FROM `constituents` where `email` = %s", [email])
    if result != None:
        constituentID = result[0]["ID"]

        db.query("INSERT INTO `contactDetails` (`id`, `constituentID`, `type`, `value`, `primary`, `source`, `accuracy`, `status`, `deleted`, `created_at`, `updated_at`) SELECT NULL, %s, '4', %s, '1', 'import', '0', '', '0', %s, NULL WHERE NOT EXISTS (SELECT 1 FROM `contactDetails` where `value` = %s);", [constituentID, email, datetime_string, email,])

        db.close()
        return constituentID
    else:  
        db.close()
        return result

def getOrCreateCase(constituentID):
    summaryString = 'Imported from new user sign up'

    db = Database(os.getenv('SUPPORT_DB_NAME'))
    result = db.query("INSERT INTO `cases` (`enquirytypeID`, `constituentID`, `casetypeID`, `summary`, `statusID`, `CaseworkerID`, `createdbyID`, `categoryID`, `CMITSoutcome`, `created`) SELECT '8', %s, '19', %s, '1', '28', '1', '1', %s, %s WHERE NOT EXISTS ( SELECT 1 FROM `cases` WHERE `cases`.`constituentID` = %s AND `CMITSoutcome` = %s);", [constituentID, summaryString, summaryString, datetime_string, constituentID, summaryString])

    result = db.query("SELECT cases.caseID FROM `cases` WHERE `cases`.`constituentID` = %s AND `cases`.`CMITSoutcome` = %s;", [constituentID, summaryString])
    db.close()

    if result != None:
        return result[0]["caseID"]

def getOrCreateTagIDs():
    year, week_number = current_date.isocalendar()[0], current_date.isocalendar()[1]
    db = Database(os.getenv('SUPPORT_DB_NAME'))

    weekTagText = f"New User: {year}, Week {week_number}"

    results = []
    for tagText in [weekTagText, "Training", "Prospect"]:
        db.query("INSERT INTO `tags` (`tag`) SELECT %s WHERE NOT EXISTS ( SELECT 1 FROM `tags` WHERE `tag` = %s);", [tagText, tagText])
        result = db.query("SELECT `tagID` FROM `tags` where `tag` = %s", [tagText])
        if result != None:
            results.append(result[0]["tagID"])
        
    db.close()
    return results

def createTaggedIfNotExist(caseID, tagIDs):
    db = Database(os.getenv('SUPPORT_DB_NAME'))
    for tagID in tagIDs:
        db.query("INSERT INTO `tagged` (`tagID`, `caseID`) SELECT %s, %s WHERE NOT EXISTS ( SELECT 1 FROM `tagged` WHERE `tagID` = %s AND `caseID` = %s);", [tagID, caseID, tagID, caseID])

    db.close()

def createPermissionIfNotExist(caseID):
    db = Database(os.getenv('SUPPORT_DB_NAME'))
    db.query("INSERT INTO `restrictions` (`entity_id`, `entity_type`, `caseworker_id`, `group_id`, `view`, `edit`, `delete`, `manage`, `deleted`, `created_by`) SELECT %s, 'cases', '0', '1', '1', '1', '1', '1', '0', '1' WHERE NOT EXISTS ( SELECT 1 FROM `restrictions` WHERE `entity_type` = 'cases' AND `entity_id` = %s);", [caseID, caseID])
    db.close()


def is_valid_email(email):
    # Regular expression pattern for validating an email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email):
        return True
    return False

if __name__ == "__main__":
    count = 0

    with open("data.csv", mode="r", newline="") as file:
        reader = csv.reader(file)

        for [email] in reader:
            if is_valid_email(email):
                count = count + 1
                constituentID = getOrCreateConstituentID(email)
                tagIDs = getOrCreateTagIDs()
                caseID = getOrCreateCase(constituentID)
                createTaggedIfNotExist(caseID, tagIDs)
                createPermissionIfNotExist(caseID)

    print(f"\nImported {count} row(s).")
                
                    
            



# names lowercase but capitalise first letter

# find all .au cases, close and add au.gov

    