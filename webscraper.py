import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import sqlite3

#https://stackoverflow.com/questions/75235102/selenium-4-and-webdriver-manager-for-firefox-fails-to-run-in-ubuntu
## make sure to have BOTH selenium and webdriver-manager installed.
### they lie to you that they install together

##parse code sample
# searchVariable = web_driver.find_element(By.ITEM,"enter_text_search")

def indeed_search(web_driver):
    #search for the job title
    Job_title = web_driver.find_element(By.TAG_NAME,"h1")
    # print(Job_title.text)
    #get the job location
    Location = web_driver.find_element(By.CSS_SELECTOR,"div.css-waniwe.eu4oa1w0")
    # print(Location.text)
    #get the company
    Company = web_driver.find_element(By.CSS_SELECTOR,"a.css-1ioi40n.e19afand0")
    # print(Company.text)
    #get the job description
    Description = web_driver.find_element(By.CSS_SELECTOR,"div.jobsearch-jobDescriptionText.jobsearch-JobComponent-description.css-kqe8pq.eu4oa1w0")
    # print(Description.text)

    return Job_title.text,Location.text,Company.text,Description.text

def linkedin_search(web_driver,job_url):

    #login to linken so we have consistenty amongst the pages so we actually load the page when called.
    web_driver.get("https://www.linkedin.com/login") #login page
    user_name = web_driver.find_element(By.ID,"username") #find the username field
    password_entry = web_driver.find_element(By.ID,"password") #find the password field

    #we send the username and the password to the site. We open a "secure" file that is not in the github repo. 
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #make more secure later
    with open("passwd.txt","r") as f:
        user_name_from_file = f.readline()
        password_from_file = f.readline()

    user_name.send_keys(user_name_from_file)
    password_entry.send_keys(password_from_file)
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    #submit the form to login
    web_driver.find_element(By.XPATH,"/html/body/div/main/div[2]/div[1]/form/div[3]/button").click()
    
    #go to the job page, sleep to allow page(s) to load before we scrape
    time.sleep(2)
    web_driver.get(job_url)
    time.sleep(5)
 

    Job_title = web_driver.find_element(By.TAG_NAME,"h1")
    # print(Job_title.text)

    #find the company
    Company = web_driver.find_element(By.XPATH,"/html/body/div[5]/div[3]/div[2]/div/div/main/div/div[1]/div/div[1]/div/div/div[1]/div[3]/div/a")
    # print(Company.text)

    #we grab the entire div as the text is hard to get alone
    #get the location info
    Location = web_driver.find_element(By.CLASS_NAME,"job-details-jobs-unified-top-card__primary-description-without-tagline.mb2")
    #we have to do some fun text cutting
    location_text = Location.text
    location_text = location_text.split("·")
    location_text = location_text[1].strip()
    # print(location_text[1].strip())

    #get the description, we have to click the more button first to allow the full description to load first
    web_driver.find_element(By.CLASS_NAME,"jobs-description__footer-button.t-14.t-black--light.t-bold.artdeco-card__action.artdeco-button.artdeco-button--icon-right.artdeco-button--3.artdeco-button--fluid.artdeco-button--tertiary.ember-view").click()

    Description = web_driver.find_element(By.CLASS_NAME,"jobs-description__container.jobs-description__container--condensed")

    
    return Job_title.text,location_text,Company.text,Description.text
    
def usaJobs_search(web_driver):
    #get the job title
    Job_title = web_driver.find_element(By.TAG_NAME,"h1")
    #get the location, this selector also works for jobs with a single location, as it still shows as a list
    Location_array = []
    #get the locations div
    Location_unordered_list = web_driver.find_element(By.CLASS_NAME,"usajobs-multiple-locations-list") 



    #get a list of elements in the locations
    Location_list_item = Location_unordered_list.find_elements(By.TAG_NAME,"li")
    for each in Location_list_item:
        #each item is a link to a map location
        #currentLocation//a element//div element second one in list
        try:
            #if the link does not have a div, we move onto the next element
            Location_link = each.find_element(By.XPATH,".//a//div[2]")
            # print(Location_link.tag_name)
        except:
            print("ran into a problem, most likely there exists a button in the list to expand the view of the list for users.")
            continue

        #use this method from GUY for any spans that will not use the .text 
        #https://stackoverflow.com/questions/39608637/selenium-text-not-working
        #find the span element with the street address 
        #get the first span in the div
        location_street = Location_link.find_element(By.XPATH,".//span[1]")
        # print("location_street: ",location_street.get_attribute("innerText").strip())

        #find the span element with the city and state information
        #get the second span in the list
        location_city = Location_link.find_element(By.XPATH,".//span[2]")
        # print("location_city: ",location_city.get_attribute("textContent").strip())

        #concat the location to street address and city/state
        location_string = location_street.get_attribute("innerText").strip()+" "+location_city.get_attribute("innerText").strip()
        #if there is multiple we append it to a list
        Location_array.append(location_string)

    #get the company
    Department = web_driver.find_element(By.CLASS_NAME,"usajobs-joa-banner__dept")
    Agency = web_driver.find_element(By.CLASS_NAME,"usajobs-joa-banner__agency.usajobs-joa-banner--v1-3__agency")
    Company = Department.text+", "+Agency.text
    
    #get the description
    Duties = web_driver.find_element(By.ID,"duties")
    Requirements = web_driver.find_element(By.ID,"requirements")

    Description = Duties.text + Requirements.text

    return Job_title.text,Location_array,Company,Description

def manual_entry():
    Job_title = input("Enter job title: ")

    Location = input("Enter location: ")

    Company = input("Enter company: ")

    Description = input("Enter description: ")

    return Job_title,Location,Company,Description



def main():
    #get arguments which will be a web link
    parser = argparse.ArgumentParser(
        prog="webscrapper.py",
        description="web scrapper")
    parser.add_argument("web_link")
    args = parser.parse_args()
    #save website to variable
    website = args.web_link



    if("indeed.com" in website.lower()):
        #selenium open firefox
        driver=webdriver.Firefox()
        #gets the website
        driver.get(website)
        ##wait a bit to have website fully load
        time.sleep(5) # sleep for 5 seconds
        Job_title,Location,Company,Description=indeed_search(driver)
        #close the web driver
        driver.close()
    elif("linkedin.com" in website.lower()):
        #selenium open firefox
        driver=webdriver.Firefox()
        driver.get(website)
        ##wait a bit to have website fully load
        time.sleep(5) # sleep for 5 seconds
        Job_title,Location,Company,Description=linkedin_search(driver,website)
        driver.close()
    elif("usajobs.gov" in website.lower()):
        #selenium open firefox
        driver=webdriver.Firefox()
        driver.get(website)
        ##wait a bit to have website fully load
        time.sleep(5) # sleep for 5 seconds
        Job_title,Location,Company,Description=usaJobs_search(driver)
        driver.close()
    else:
        Job_title,Location,Company,Description=manual_entry()


    # #print the information gathered
    # print(Job_title)
    # print(Location)
    # print(Company)
    # print(Description)

    #database connection, if it does not exist creates it
    connect = sqlite3.connect('job_search.db')
    #allows us to do SQL queries
    cursor = connect.cursor()



    #create the table Jobs if it does not exist already
    cursor.execute('''CREATE TABLE IF NOT EXISTS job_search
                (id INTEGER PRIMARY KEY,
                job_url TEXT, 
                job_title TEXT,
                company TEXT,
                location TEXT,
                description TEXT,
                applied BOOLEAN,
                date_applied DATE,
                application_status INTEGER,
                interview BOOLEAN,
                interview_date DATE);''')

    applied = 0
    date_applied = 0
    application_status = 0
    interview = 0
    interview_date = 0

    #if we have a list of locations, mainly coming in from usajobs.com, we put them to a string
    if(type(Location) == list):
        location_string = ''
        for item in Location:
            location_string += item+":::"
        Location = location_string

    #insert the item to the database
    cursor.execute("INSERT INTO job_search (job_url, job_title, company, location, description, applied, date_applied,application_status, interview,interview_date) VALUES (?,?,?,?,?,?,?,?,?,?);",(website,Job_title,Company,Location,Description,applied,date_applied,application_status,interview,interview_date))
    #save the input to the database
    connect.commit()
    #close the connection tothe database
    connect.close()
    

 


if __name__ == '__main__':
    main()