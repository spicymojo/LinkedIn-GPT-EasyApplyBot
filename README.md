# LinkedIn Easy Apply Bot
Automatically apply to LinkedIn Easy Apply jobs. This bot answers the application questions as well!

This is a fork of a fork of the original _LinkedIn Easy Apply Bot_, but it is a very special fork of a fork, this one relies on GPT-3 to answer the questions. 



> This is for educational purposes only. I am not responsible if your LinkedIn account gets suspended or for anything else.

This bot is written in Python using Selenium and OpenAI API.

## Fork Notes

The original bot implementation, couldn't handle open questions, just used keywords and predefined answers. Such couldn't complete a lot of the applications, as any open question or weird selector would make the bot unable to answer.  Now that we have LLM, this is an easy problem to solve, just ask the bot to answer the question, and it will do it.

Another great benefit, is that you can provide way more information to the bot, so it can address truthfully the job requirements, and the questions, just as a human would do. 

I did try to tidy the code a bit, but I didn't want to spend too much time on it, as I just wanted to get it working, so there is still a lot of work to do there.

Thank you for everyone that contributed to the original bot, and all the forks, as made my work way easier.

_by Jorge Frías_

### Future updates
- I will keep updating this fork as I use it for my own "educational research".
- I will add features as I find fun applications, or I require them for my "educational research".

## Setup & Startup



## Setup

### OpenAI API Key
First you need to provide your Open AI API key using environment variable `OPEN_AI_API_KEY`.

### Your information
Fill out the `config.yaml` file. This contains the information used to search on LinkedIn and fill in your personal information. Most of this is self-explanatory but if you need explanations please see the end of this `README`.
 > A future update will get rid of most of this and just use the LLM to answer the questions, but for now, you need to provide the information.

You will notice you also have to provide the paths to: 
- `resume in PDF`. Will be uploaded to LinkedIn when applying.
- `plain text resume`. Will be used to answer the questions.
- - `cover letter in PDF` (optional). Will be uploaded to LinkedIn when applying if provided and the job application asks for it.
- `plain text cover letter`. Will be used when the form ask for a cover letter. When the form ask to write a cover letter (not upload it), the bot will adjust the cover letter to the job description.
  - You can use placeholders in your cover letter, a placeholder is defined as `[[placeholder]]`, the LLM will look onto the job description to fill in the placeholders. E.g. `[[company]]` will be replaced by the given company name.
- `personal information`. More information about you, what you want of the job search, work authorization, extended information not covered by the resume, etc. This will be used to answer the questions, and inform other parts of the application. This file doesn't have any structure, will be interpreted by the LLM so fell free to add structure or information as you see fit.

You will find templates for all this files in the `templates` folder.

### Install required libraries
> You should use a `virtual environment` for this, but it is not required.
```bash
pip3 install -r requirements.txt
```

## Execute
To run the bot, run the following in the command line:
```bash
python3 main.py
```


## Config.yaml Explanations
Just fill in your email and password for linkedin.
```yaml
email: email@domain.com
password: yourpassword
```

This prevents your computer from going to sleep so the bot can keep running when you are not using it. Set this to True if you want this disabled.
```yaml
disableAntiLock: False
```

Set this to True if you want to look for remote jobs only.
```yaml
remote: False
```

This is for what level of jobs you want the search to contain. You must choose at least one.
```yaml
experienceLevel:
 internship: False
 entry: True
 associate: False
 mid-senior level: False
 director: False
 executive: False
```

This is for what type of job you are looking for. You must choose at least one.
```yaml
jobTypes:
 full-time: True
 contract: False
 part-time: False
 temporary: False
 internship: False
 other: False
 volunteer: False
```

How far back you want to search. You must choose only one.
```yaml
date:
 all time: True
 month: False
 week: False
 24 hours: False
 ```

A list of positions you want to apply for. You must include at least one.
```yaml
positions:
 #- First position
 #- A second position
 #- A third position
 #- ...
 ```

A list of locations you are applying to. You must include at least one.
```yaml
locations:
 #- First location
 #- A second location
 #- A third location
 #- ...
 - Remote
 ```

How far out of the location you want your search to go. You can only input 0, 5, 10, 25, 50, 100 miles.
```yaml
distance: 25
 ```

This is the directory where all the job application stats will go to.
```yaml
outputFileDirectory: C:\Users\myDirectory\
 ```

A list of companies to not apply to.
```yaml
companyBlacklist:
 #- company
 #- company2
 ```

A list of words that will be used to skip over jobs with any of these words in there.
```yaml
titleBlacklist:
 #- word1
 #- word2
 ```

A path to your resume and cover letter.
```yaml
uploads:
 resume: C:\Users\myDirectory\Resume.pdf
 # Cover letter is optional
 #coverLetter: C:\Users\myDirectory\CoverLettter.pdf
 ```

Input your personal info. Include the state/province in the city name to not get the wrong city when choosing from a dropdown.
The phone country code needs to be exact for the one that is on linkedin.
The website is interchangeable for github/portfolio/website.
> This information should also be provided on `personal_data.md`.
```yaml
# ------------ Additional parameters: personal info ---------------
personalInfo:
 First Name: FirstName
 Last Name: LastName
 Phone Country Code: Canada (+1) # See linkedin for your country code, must be exact according to the international platform, i.e. Italy (+39) not Italia (+39)
 Mobile Phone Number: 1234567890
 Street address: 123 Fake Street
 City: Red Deer, Alberta # Include the state/province as well!
 State: YourState
 Zip: YourZip/Postal
 Linkedin: https://www.linkedin.com/in/my-linkedin-profile
 Website: https://www.my-website.com # github/website is interchangeable here
  ```
This is unused at the moment. For the EEO the bot will try to decline to answer for everything.
```yaml
# ------------ Additional parameters: USA employment crap ---------------
eeo:
 gender: None
 race: None
 vetran: None
 disability: None
 citizenship: yes
 clearance: no
```

## Troubleshooting
The bot will store all answered questions on `unprepared_questions_gpt_answered.csv`, so you can always check what questions were asked, and what answers were provided, and adjust the personal information files accordingly.
```
touch unprepared_questions.csv
```
