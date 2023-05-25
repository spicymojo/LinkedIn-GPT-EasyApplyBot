import time, random, csv, pyautogui, pdb, traceback, sys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import date
from itertools import product
from gpt import GPTAnswerer


class LinkedinEasyApply:
    def __init__(self, parameters, driver):
        self.browser = driver
        self.email = parameters['email']
        self.password = parameters['password']
        self.disable_lock = parameters['disableAntiLock']
        self.company_blacklist = parameters.get('companyBlacklist', []) or []
        self.title_blacklist = parameters.get('titleBlacklist', []) or []
        self.poster_blacklist = parameters.get('posterBlacklist', []) or []
        self.positions = parameters.get('positions', [])
        self.locations = parameters.get('locations', [])
        self.base_search_url = self.get_base_search_url(parameters)
        self.seen_jobs = []
        self.file_name = "output"
        self.unprepared_questions_file_name = "unprepared_questions"
        self.unprepared_questions_gpt_file_name = "unprepared_questions_gpt_answered"
        self.output_file_directory = parameters['outputFileDirectory']

        self.resume_dir = parameters['uploads']['resume']
        if 'coverLetter' in parameters['uploads']:
            self.cover_letter_dir = parameters['uploads']['coverLetter']
        else:
            self.cover_letter_dir = ''

        self.personal_info = parameters.get('personalInfo', [])
        self.eeo = parameters.get('eeo', [])

        # Data to fill in the application using GPT
        # - Plain text resume
        plain_text_resume_path = parameters['uploads']['plainTextResume']
        file = open(plain_text_resume_path, "r")            # Read the file
        plain_text_resume: str = file.read()
        # - Plain text personal data
        plain_text_personal_data_path = parameters['uploads']['plainTextPersonalData']
        file = open(plain_text_personal_data_path, "r")     # Read the file
        plain_text_personal_data: str = file.read()
        # - Plain text cover letter
        plain_text_cover_letter_path = parameters['uploads']['plainTextCoverLetter']
        file = open(plain_text_cover_letter_path, "r")      # Read the file
        plain_text_cover_letter: str = file.read()
        # - Build the GPT answerer using the plain text data
        self.gpt_answerer = GPTAnswerer(plain_text_resume, plain_text_personal_data, plain_text_cover_letter)

    def login(self):
        try:
            self.browser.get("https://www.linkedin.com/login")
            time.sleep(random.uniform(5, 10))
            self.browser.find_element(By.ID, "username").send_keys(self.email)
            self.browser.find_element(By.ID, "password").send_keys(self.password)
            self.browser.find_element(By.CSS_SELECTOR, ".btn__primary--large").click()
            time.sleep(random.uniform(5, 10))
        except TimeoutException:
            raise Exception("Could not login!")

    def security_check(self):
        current_url = self.browser.current_url
        page_source = self.browser.page_source

        if '/checkpoint/challenge/' in current_url or 'security check' in page_source:
            input("Please complete the security check and press enter in this console when it is done.")
            time.sleep(random.uniform(5.5, 10.5))

    def start_applying(self):
        searches = list(product(self.positions, self.locations))
        random.shuffle(searches)

        page_sleep = 0
        minimum_time = 60*15
        minimum_page_time = time.time() + minimum_time

        for (position, location) in searches:
            location_url = "&location=" + location
            job_page_number = -1

            print("Starting the search for " + position + " in " + location + ".")

            try:
                while True:
                    page_sleep += 1
                    job_page_number += 1
                    print("Going to job page " + str(job_page_number))
                    self.next_job_page(position, location_url, job_page_number)
                    time.sleep(random.uniform(1.5, 3.5))
                    print("Starting the application process for this page...")
                    self.apply_jobs(location)
                    print("Applying to jobs on this page has been completed!")

                    # Sleep for a random amount of time between 5 and 15 minutes.
                    time_left = minimum_page_time - time.time()
                    if time_left > 0:
                        print("Sleeping for " + str(time_left) + " seconds.")
                        time.sleep(time_left)
                        minimum_page_time = time.time() + minimum_time
                    if page_sleep % 5 == 0:
                        sleep_time = random.randint(500, 900)
                        print("Sleeping for " + str(sleep_time/60) + " minutes.")
                        time.sleep(sleep_time)
                        page_sleep += 1
            except:
                traceback.print_exc()
                pass

            time_left = minimum_page_time - time.time()
            if time_left > 0:
                print("Sleeping for " + str(time_left) + " seconds.")
                time.sleep(time_left)
                minimum_page_time = time.time() + minimum_time
            if page_sleep % 5 == 0:
                sleep_time = random.randint(500, 900)
                print("Sleeping for " + str(sleep_time/60) + " minutes.")
                time.sleep(sleep_time)
                page_sleep += 1

    def apply_jobs(self, location):
        no_jobs_text = ""
        try:
            no_jobs_element = self.browser.find_element(By.CLASS_NAME, 'jobs-search-two-pane__no-results-banner--expand')
            no_jobs_text = no_jobs_element.text
        except:
            pass

        if 'No matching jobs found' in no_jobs_text:
            raise Exception("No more jobs on this page")

        if 'unfortunately, things aren' in self.browser.page_source.lower():
            raise Exception("No more jobs on this page")

        try:
            job_results = self.browser.find_element(By.CLASS_NAME, "jobs-search-results-list")
            self.scroll_slow(job_results)
            self.scroll_slow(job_results, step=300, reverse=True)

            job_list = self.browser.find_elements(By.CLASS_NAME, 'scaffold-layout__list-container')[0].find_elements(By.CLASS_NAME, 'jobs-search-results__list-item')
            if len(job_list) == 0:
                raise Exception("No job class elements found in page")
        except:
            raise Exception("No more jobs on this page")

        if len(job_list) == 0:
            raise Exception("No more jobs on this page")

        # Iterate through each job on the page
        for job_tile in job_list:
            # Extract the job information from the Tile
            job_title, company, job_location, link, poster, apply_method = self.extract_job_information_from_tile(job_tile)
            # Check if the job is blacklisted
            is_blacklisted = self.is_blacklisted(job_title, company, poster, link)
            # Remember the job
            self.seen_jobs += link

            if is_blacklisted:
                print("Job contains blacklisted keyword or company or poster name! Skipping...")
                continue

            try:
                # Click on the job
                job_el = job_tile.find_element(By.CLASS_NAME, 'job-card-list__title')
                job_el.click()
            except:
                traceback.print_exc()
                print("Could not apply to the job!")
                pass

            time.sleep(random.uniform(3, 5))        # Small human-like pause

            try:
                # Apply to the job
                if not self.apply_to_job():         # Returns True if successful, false if already applied, raises exception if failed
                    continue                        # If already applied, next job
            except:
                self.record_failed_application(company, job_location, job_title, link, location)
                continue                            # If failed, next job

            # Record the successful application
            self.record_successful_application(company, job_location, job_title, link, location)

    def record_successful_application(self, company, job_location, job_title, link, location):
        """
        Records the successful application to the job in the csv file.
        """
        try:
            self.write_to_file(company, job_title, link, job_location, location)
        except Exception:
            print("Could not write the job to the file! No special characters in the job title/company is allowed!")
            traceback.print_exc()

    def record_failed_application(self, company, job_location, job_title, link, location):
        """
        Records the failed application to the job in the csv file.
        """
        temp = self.file_name
        self.file_name = "failed"
        print("Failed to apply to job! Please submit a bug report with this link: " + link)
        print("Writing to the failed csv file...")
        try:
            self.write_to_file(company, job_title, link, job_location, location)
        except:
            pass
        self.file_name = temp

    def extract_job_information_from_tile(self, job_tile):
        """
        Extracts the job information from the job tile.
        :param job_tile: The job tile element.
        :return: job_title, company, job_location, link, poster, apply_method
        """
        job_title, company, poster, job_location, apply_method, link = "", "", "", "", "", ""

        try:
            job_title = job_tile.find_element(By.CLASS_NAME, 'job-card-list__title').text
            link = job_tile.find_element(By.CLASS_NAME, 'job-card-list__title').get_attribute('href').split('?')[0]
            company = job_tile.find_element(By.CLASS_NAME, 'job-card-container__company-name').text
        except:
            pass
        try:
            # get the name of the person who posted for the position, if any is listed
            hiring_line = job_tile.find_element(By.XPATH, '//span[contains(.,\' is hiring for this\')]')
            hiring_line_text = hiring_line.text
            name_terminating_index = hiring_line_text.find(' is hiring for this')
            if name_terminating_index != -1:
                poster = hiring_line_text[:name_terminating_index]
        except:
            pass
        try:
            job_location = job_tile.find_element(By.CLASS_NAME, 'job-card-container__metadata-item').text
        except:
            pass
        try:
            apply_method = job_tile.find_element(By.CLASS_NAME, 'job-card-container__apply-method').text
        except:
            pass

        return job_title, company, job_location, link, poster, apply_method

    def is_blacklisted(self, job_title, company, poster, link):
        """
        Checks if the job is blacklisted.

        :param job_title:
        :param company:
        :param poster:
        :param link:
        :return: True if the job is blacklisted, False otherwise.
        """
        # TODO: Use GPT to blacklist jobs, it's more accurate than the current method.

        if job_title.lower().split(' ') in [word.lower() for word in self.title_blacklist]:
            return True

        if company.lower() in [word.lower() for word in self.company_blacklist]:
            return True

        if poster.lower() in [word.lower() for word in self.poster_blacklist]:
            return True

        if link in self.seen_jobs:
            return True

        return False

    def extract_job_information_from_opened_job(self):
        job_title, company, job_location, description = "", "", "", ""

        try:
            # Job panel element
            job_element = self.browser.find_elements(By.CLASS_NAME, 'jobs-search__job-details--container')[0]
            # Individual information
            job_title = job_element.find_element(By.CLASS_NAME, 'jobs-unified-top-card__job-title').text
            company = job_element.find_element(By.CLASS_NAME, 'jobs-unified-top-card__company-name').text
            job_location = job_element.find_elements(By.CLASS_NAME, 'jobs-unified-top-card__bullet')[0].text + " | " + job_element.find_elements(By.CLASS_NAME, 'jobs-unified-top-card__workplace-type')[0].text
            description = job_element.find_element(By.CLASS_NAME, 'jobs-description-content__text').text
        except Exception as e:
            Exception(f"Could not extract job information from the opened job! {e}")

        return job_title, company, job_location, description

    def formatted_job_information(self, job_title: str, company: str, job_location: str, description: str):
        """
        Formats the job information as a markdown string.
        """
        job_information = f"""
        # Job Description
        ## Job Information 
        - Position: {job_title}
        - At: {company}
        - Location: {job_location}
        
        ## Description
        {description}
        """
        return job_information

    def apply_to_job(self):
        """
        Applies to the job, opened in the browser.
        :return: True if successful, False if already applied, raises exception if failed.
        """
        easy_apply_button = None

        try:
            easy_apply_button = self.browser.find_element(By.CLASS_NAME, 'jobs-apply-button')
        except:
            # If the easy apply button is not found, is because is disabled. Supposedly is because the job is already applied.
            # There is a pre-filtering before to only search easy apply jobs.
            return False

        try:
            # Scroll down to the job description like a human reading the whole job description
            job_description_area = self.browser.find_element(By.CLASS_NAME, "jobs-search__job-details--container")
            self.scroll_slow(job_description_area, end=1600)
            self.scroll_slow(job_description_area, end=1600, step=400, reverse=True)
        except:
            pass

        # Load the Job description in the answerer
        job_title, job_company, job_location, job_description = self.extract_job_information_from_opened_job()
        formatted_description = self.formatted_job_information(job_title, job_company, job_location, job_description)
        # Provide the job description to the answerer as context
        self.gpt_answerer.job_description = formatted_description

        # Start the application process
        print("Applying to the job....")
        easy_apply_button.click()           # Click the easy apply button
        submitted_application = False       # Flag to check if the application was submitted successfully
        while not submitted_application:    # Iterate filling up fields until the submit application button is found
            try:
                self.fill_up()              # Fill up the fields
                submitted_application = self.apply_to_job_form_next_step()  # Click the next button after filling up the fields
            except:
                # On any error, close the application window, save the job for later and raise a final exception.
                traceback.print_exc()
                self.browser.find_element(By.CLASS_NAME, 'artdeco-modal__dismiss').click()
                time.sleep(random.uniform(3, 5))
                self.browser.find_elements(By.CLASS_NAME, 'artdeco-modal__confirm-dialog-btn')[1].click()
                time.sleep(random.uniform(3, 5))
                raise Exception("Failed to apply to job!")

        # Successfully applied to the job, close the confirmation window.
        self.apply_to_job_form_close_confirmation_modal()

        # Return True if the job was successfully applied to.
        return True

    def apply_to_job_form_close_confirmation_modal(self):
        closed_notification = False
        time.sleep(random.uniform(3, 5))
        try:
            self.browser.find_element(By.CLASS_NAME, 'artdeco-modal__dismiss').click()
            closed_notification = True
        except:
            pass
        try:
            self.browser.find_element(By.CLASS_NAME, 'artdeco-toast-item__dismiss').click()
            closed_notification = True
        except:
            pass
        time.sleep(random.uniform(3, 5))
        if closed_notification is False:
            raise Exception("Could not close the applied confirmation window!")

    def apply_to_job_form_next_step(self):
        """
        Clicks the next button in the application form / clicks the submit application button.
        :param submit_application_text:
        :return: True if the application was submitted, False otherwise.
        """
        submit_application_text = 'submit application'

        # Find the next button
        next_button = self.browser.find_element(By.CLASS_NAME, "artdeco-button--primary")
        button_text = next_button.text.lower()

        # When the submit application button is found, there is an option to follow the company feed that needs to be unchecked.
        if submit_application_text in button_text:
            self.unfollow()

        # Click continuation button
        # - Next step in the application process
        # - Submit. This action will also submit the application, if the primary button is the submit application button.
        time.sleep(random.uniform(1.5, 2.5))
        next_button.click()
        time.sleep(random.uniform(3.0, 5.0))

        # There are errors in the current fields
        if 'please enter a valid answer' in self.browser.page_source.lower() or 'file is required' in self.browser.page_source.lower():
            # TODO: Provide this feedback to GPT, so it can modify the answers.
            raise Exception("Failed answering required questions or uploading required files.")

        if submit_application_text in button_text.lower():
            return True

        return False

    def home_address(self, element):
        try:
            groups = element.find_elements(By.CLASS_NAME, 'jobs-easy-apply-form-section__grouping')
            if len(groups) > 0:
                for group in groups:
                    lb = group.find_element(By.TAG_NAME, 'label').text.lower()
                    input_field = group.find_element(By.TAG_NAME, 'input')
                    if 'street' in lb:
                        self.enter_text(input_field, self.personal_info['Street address'])
                    elif 'city' in lb:
                        self.enter_text(input_field, self.personal_info['City'])
                        time.sleep(3)
                        input_field.send_keys(Keys.DOWN)
                        input_field.send_keys(Keys.RETURN)
                    elif 'zip' in lb or 'postal' in lb:
                        self.enter_text(input_field, self.personal_info['Zip'])
                    elif 'state' in lb or 'province' in lb:
                        self.enter_text(input_field, self.personal_info['State'])
                    else:
                        pass
        except:
            pass

    def get_answer(self, question):
        """
        Sees if the key `question` is in the dictionary `checkboxes` and returns "yes" is true and "no" if false
        """
        # TODO: This should be a boolean test, why is it a string?
        if self.checkboxes[question]:
            return 'yes'
        else:
            return 'no'

    def get_checkbox_answer(self, question_key):
        """
        Sees if the key `question` is in the dictionary `checkboxes` and returns True if true and False if false.
        :param question_key: The question to check for in the dictionary.
        """
        if self.checkboxes[question_key]:
            return True
        else:
            return False

    # MARK: Additional Questions
    def additional_questions(self):
        frm_el = self.browser.find_elements(By.CLASS_NAME, 'jobs-easy-apply-form-section__grouping')
        if len(frm_el) > 0:
            for el in frm_el:
                # Each call will try to do its job, if they can't, they will return early

                # Radio check
                try:
                    # self.additional_questions_radio(el)
                    self.additional_questions_radio_gpt(el)
                except Exception as e:
                    pass

                # Questions check
                try:
                    # self.additional_questions_textbox(el)
                    self.additional_questions_textbox_gpt(el)
                except Exception as e:
                    pass

                # Date Check
                try:
                    # Works just fine without GPT
                    self.additional_questions_date(el)
                except Exception as e:
                    pass

                # Dropdown check
                try:
                    # self.additional_questions_drop_down(el)
                    self.additional_questions_drop_down_gpt(el)
                except Exception as e:
                    pass

                # Checkbox check for agreeing to terms and service
                try:
                    # Works just fine without GPT
                    self.additional_questions_agree_terms_of_service(el)
                except Exception as e:
                    pass

    def additional_questions_agree_terms_of_service(self, el):
        question = el.find_element(By.CLASS_NAME, 'jobs-easy-apply-form-element')
        clickable_checkbox = question.find_element(By.TAG_NAME, 'label')
        clickable_checkbox.click()

    def additional_questions_drop_down_gpt(self, el):
        question = el.find_element(By.CLASS_NAME, 'jobs-easy-apply-form-element')
        question_text = question.find_element(By.TAG_NAME, 'label').text.lower()
        dropdown_field = question.find_element(By.TAG_NAME, 'select')

        select = Select(dropdown_field)
        options = [options.text for options in select.options]

        # Hardcoded answers
        if 'email' in question_text:
            return  # assume email address is filled in properly by default

        # Answer any other the question
        choice = self.gpt_answerer.answer_question_from_options(question_text, options)
        self.select_dropdown(dropdown_field, choice)
        self.record_gpt_answer("dropdown", question_text, choice)

    def additional_questions_drop_down(self, el):
        question = el.find_element(By.CLASS_NAME, 'jobs-easy-apply-form-element')
        question_text = question.find_element(By.TAG_NAME, 'label').text.lower()
        dropdown_field = question.find_element(By.TAG_NAME, 'select')

        select = Select(dropdown_field)
        options = [options.text for options in select.options]

        # - Language questions
        if 'proficiency' in question_text:
            proficiency = "Conversational"

            for language in self.languages:
                if language.lower() in question_text:
                    proficiency = self.languages[language]
                    break

            self.select_dropdown(dropdown_field, proficiency)

        elif 'country code' in question_text:
            self.select_dropdown(dropdown_field, self.personal_info['Phone Country Code'])

        # - YES or NO questions. Options can be answered with yes or no. Dumb check for yes or no.
        elif 'yes' in options or 'no' in options:
            if 'assessment' in question_text:
                answer = self.get_checkbox_answer('assessment')
                self.select_dropdown_using_answer_boolean(answer, dropdown_field, options, question_text)

            elif 'commut' in question_text:
                answer = self.get_checkbox_answer('commute')
                self.select_dropdown_using_answer_boolean(answer, dropdown_field, options, question_text)

            elif 'north korea' in question_text:
                self.select_dropdown_no(dropdown_field, options)    # Nothing to do with North Korea

            elif 'previously employed' in question_text or 'previous employment' in question_text:
                self.select_dropdown_no(dropdown_field, options)    # Nothing to do with the company previously

            elif 'sponsor' in question_text:
                answer = self.get_checkbox_answer('requireVisa')
                self.select_dropdown_using_answer_boolean(answer, dropdown_field, options, question_text)

            elif 'authorized' in question_text or 'authorised' in question_text:
                answer = self.get_checkbox_answer('legallyAuthorized')
                self.select_dropdown_using_answer_boolean(answer, dropdown_field, options, question_text)

            elif 'citizenship' in question_text:
                answer = self.get_checkbox_answer('legallyAuthorized')
                self.select_dropdown_using_answer_boolean(answer, dropdown_field, options, question_text)

            elif 'clearance' in question_text:
                answer = self.get_checkbox_answer('clearance')
                self.select_dropdown_using_answer_boolean(answer, dropdown_field, options, question_text)

            elif 'experience' in question_text or 'understanding' in question_text or 'familiar' in question_text or 'comfortable' in question_text or 'able to' in question_text:
                answer = 'no'
                for experience in self.experience:
                    if experience.lower() in question_text and self.experience[experience] > 0:
                        answer = 'yes'
                        break
                if answer == 'no':
                    # Ask GPT for an answer, as the resume might reflect the experience
                    answer = self.gpt_answerer.answer_question_from_options(question_text, options)
                    # Record unlisted experience as unprepared questions
                    self.record_gpt_answer("dropdown", question_text, answer)

                self.select_dropdown_using_answer(answer, dropdown_field, options)

        # - Questions that have a specific answer, US employment equality bullshit
        elif 'gender' in question_text or 'veteran' in question_text or 'race' in question_text or 'disability' in question_text or 'latino' in question_text:
            choice = ""
            for option in options:
                if 'prefer' in option.lower() or 'decline' in option.lower() or 'don\'t' in option.lower() or 'specified' in option.lower() or 'none' in option.lower():
                    choice = option
            if choice == "":
                choice = options[len(options) - 1]
            self.select_dropdown(dropdown_field, choice)

        elif 'email' in question_text:
            return  # assume email address is filled in properly by default

        # - Couldn't infer the question's answer, fallback
        else:
            # Let's use GPT to answer the question
            choice = self.gpt_answerer.answer_question_from_options(question_text, options)
            self.select_dropdown(dropdown_field, choice)
            self.record_gpt_answer("dropdown", question_text, choice)

    def select_dropdown_no(self, dropdown_field, options):
        choice = ""
        for option in options:
            if 'no' in option.lower():
                choice = option
        if choice == "":
            choice = options[len(options) - 1]
        self.select_dropdown(dropdown_field, choice)

    def select_dropdown_using_answer(self, answer: str, dropdown_field, options):
        """
        Selects the dropdown option that contains the answer, oly works for yes/no answers.
        :param answer: 'yes' or 'no'
        :param dropdown_field: The dropdown field
        :param options: The options in the dropdown field
        """
        # Select the option that contains the answer
        choice = ""

        for option in options:
            if answer == 'yes' and 'yes' in option.lower():
                choice = option
            if answer == 'no' and 'no' in option.lower():
                choice = option
        if choice == "":
            # If no option contains the answer, select the last option, this is stupid...
            # TODO: Ask GPT, but it will need the question text
            choice = options[len(options) - 1]

        self.select_dropdown(dropdown_field, choice)

    def select_dropdown_using_answer_boolean(self, answer: bool, dropdown_field, options, question: str):
        """
        Selects the dropdown option that contains the answer, oly works for yes/no answers.
        :param answer: 'yes' or 'no'
        :param dropdown_field: The dropdown field
        :param options: The options in the dropdown field
        :param question: The question text
        """
        # Select the option that contains the answer
        choice = ""

        for option in options:
            if answer and 'yes' in option.lower():
                choice = option
            if not answer and 'no' in option.lower():
                choice = option
        if choice == "":
            # If no option contains the answer, select the last option, this is stupid...
            # TODO: Ask GPT, but it will need the question text
            choice = options[len(options) - 1]

        self.select_dropdown(dropdown_field, choice)

    def additional_questions_date(self, el):
        date_picker = el.find_element(By.CLASS_NAME, 'artdeco-datepicker__input ')
        date_picker.clear()
        date_picker.send_keys(date.today().strftime("%m/%d/%y"))
        time.sleep(3)
        date_picker.send_keys(Keys.RETURN)
        time.sleep(2)

    def additional_questions_textbox_gpt(self, el):
        # Question information
        question = el.find_element(By.CLASS_NAME, 'jobs-easy-apply-form-element')
        question_text = question.find_element(By.TAG_NAME, 'label').text.lower()
        try:
            txt_field = question.find_element(By.TAG_NAME, 'input')
        except:
            try:
                txt_field = question.find_element(By.TAG_NAME, 'textarea')  # TODO: Test textarea
            except:
                raise Exception("Could not find textarea or input tag for question")

        # Field type
        text_field_type = txt_field.get_attribute('type').lower()
        if 'numeric' in text_field_type:                                    # TODO: test numeric type
            text_field_type = 'numeric'
        elif 'text' in text_field_type:
            text_field_type = 'text'
        else:
            return      # This function doesn't support other types, just return

        # Use GPT to answer the question
        to_enter = ''
        if text_field_type == 'numeric':
            to_enter = self.gpt_answerer.answer_question_numeric(question_text)
        else:
            to_enter = self.gpt_answerer.answer_question_textual_wide_range(question_text)

        # Record the answer
        self.record_gpt_answer(text_field_type, question_text, to_enter)

        # Enter the answer
        self.enter_text(txt_field, to_enter)

    def additional_questions_textbox(self, el):
        question = el.find_element(By.CLASS_NAME, 'jobs-easy-apply-form-element')
        question_text = question.find_element(By.TAG_NAME, 'label').text.lower()

        txt_field_visible = False
        try:
            txt_field = question.find_element(By.TAG_NAME, 'input')
            txt_field_visible = True
        except:
            try:
                txt_field = question.find_element(By.TAG_NAME, 'textarea')  # TODO: Test textarea
                txt_field_visible = True
            except:
                raise Exception("Could not find textarea or input tag for question")

        # - Field type
        text_field_type = txt_field.get_attribute('type').lower()
        if 'numeric' in text_field_type:  # TODO: test numeric type
            text_field_type = 'numeric'
        elif 'text' in text_field_type:
            text_field_type = 'text'
        else:
            # Unsupported field type
            return

        # - Field value predefined response
        to_enter = ''
        if 'experience' in question_text:
            no_of_years = None
            for experience in self.experience:
                if experience.lower() in question_text:
                    no_of_years = self.experience[experience]
                    break
            if no_of_years is None:
                # 1. Ask GPT for answer
                no_of_years = self.gpt_answerer.answer_question_numeric(question_text, default_experience=self.experience_default)
                self.record_gpt_answer(text_field_type, question_text, no_of_years)
            to_enter = no_of_years

        elif 'grade point average' in question_text:
            to_enter = self.university_gpa
        elif 'first name' in question_text:
            to_enter = self.personal_info['First Name']
        elif 'last name' in question_text:
            to_enter = self.personal_info['Last Name']
        elif 'name' in question_text:
            to_enter = self.personal_info['First Name'] + " " + self.personal_info['Last Name']
        elif 'pronouns' in question_text:
            to_enter = self.personal_info['Pronouns']
        elif 'phone' in question_text:
            to_enter = self.personal_info['Mobile Phone Number']
        elif 'linkedin' in question_text:
            to_enter = self.personal_info['Linkedin']
        elif 'website' in question_text or 'github' in question_text or 'portfolio' in question_text:
            to_enter = self.personal_info['Website']
        elif 'salary' in question_text:
            if text_field_type == 'numeric':
                to_enter = self.salary_minimum
            else:
                to_enter = "$" + self.salary_minimum + "+"

        # - Field value not predefined
        else:
            # There is no predicate for this question, so we ask GPT
            if text_field_type == 'numeric':
                to_enter = self.gpt_answerer.answer_question_numeric(question_text)
            else:
                to_enter = self.gpt_answerer.answer_question_textual_wide_range(question_text)
                # to_enter = " ‏‏‎ "
            self.record_gpt_answer(text_field_type, question_text, to_enter)

        # - Final check
        # TODO: Try to parse the string to a number if it is numeric
        if text_field_type == 'numeric':
            if not isinstance(to_enter, (int, float)):
                to_enter = 0
        elif to_enter == '':
            to_enter = " ‏‏‎ "      # Why these characters? So the answer is not empty?

        # - Enter the answer
        self.enter_text(txt_field, to_enter)

    def additional_questions_radio_gpt(self, el):
        """
        This function handles radio buttons
        :param el: The element containing the radio buttons
        """
        # Question information
        question = el.find_element(By.CLASS_NAME, 'jobs-easy-apply-form-element')
        radios = question.find_elements(By.CLASS_NAME, 'fb-text-selectable__option')
        if len(radios) == 0:
            raise Exception("No radio found in element")

        radio_text = el.text.lower()
        radio_options = [text.text.lower() for text in radios]

        # Ask gpt for the most likely answer
        answer = "yes"
        answer = self.gpt_answerer.answer_question_from_options(radio_text, radio_options)
        self.record_gpt_answer("radio", radio_text, answer)

        # Select the radio that matches the answer
        to_select = None
        for radio in radios:
            if answer in radio.text.lower():
                to_select = radio

        # Fallback to the last radio if no answer was found
        if to_select is None:
            to_select = radios[-1]

        # Select the chosen radio
        self.radio_select_simplified(to_select)

    def additional_questions_radio(self, el):
        """
        This function handles radio buttons
        :param el: The element containing the radio buttons
        :return:
        """
        question = el.find_element(By.CLASS_NAME, 'jobs-easy-apply-form-element')
        radios = question.find_elements(By.CLASS_NAME, 'fb-text-selectable__option')
        if len(radios) == 0:
            raise Exception("No radio found in element")

        radio_text = el.text.lower()
        radio_options = [text.text.lower() for text in radios]
        answer = "yes"

        if 'driver\'s licence' in radio_text or 'driver\'s license' in radio_text:
            answer = self.get_answer('driversLicence')
        elif 'gender' in radio_text or 'veteran' in radio_text or 'race' in radio_text or 'disability' in radio_text or 'latino' in radio_text:
            answer = ""
            for option in radio_options:
                if 'prefer' in option.lower() or 'decline' in option.lower() or 'don\'t' in option.lower() or 'specified' in option.lower() or 'none' in option.lower():
                    answer = option

            if answer == "":
                answer = radio_options[len(radio_options) - 1]
        elif 'assessment' in radio_text:
            answer = self.get_answer("assessment")
        elif 'north korea' in radio_text:
            answer = 'no'
        elif 'previously employ' in radio_text or 'previous employ' in radio_text:
            answer = 'no'
        elif 'authorized' in radio_text or 'authorised' in radio_text or 'legally' in radio_text:
            answer = self.get_answer('legallyAuthorized')
        elif 'urgent' in radio_text:
            answer = self.get_answer('urgentFill')
        elif 'commut' in radio_text:
            answer = self.get_answer('commute')
        elif 'remote' in radio_text:
            answer = self.get_answer('remote')
        elif 'background check' in radio_text:
            answer = self.get_answer('backgroundCheck')
        elif 'drug test' in radio_text:
            answer = self.get_answer('drugTest')
        elif 'level of education' in radio_text:
            for degree in self.checkboxes['degreeCompleted']:
                if degree.lower() in radio_text:
                    answer = "yes"
                    break
        elif 'experience' in radio_text:
            for experience in self.experience:
                if experience.lower() in radio_text:
                    answer = "yes"
                    break
        elif 'data retention' in radio_text:
            answer = 'no'
        elif 'sponsor' in radio_text:
            answer = self.get_answer('requireVisa')
        else:
            # Ask gpt for the most likely answer
            answer = self.gpt_answerer.answer_question_from_options(radio_text, radio_options)
            self.record_gpt_answer("radio", radio_text, answer)
            # Old way to do it
            # answer = radio_options[len(radio_options) - 1]
            # self.record_unprepared_question("radio", radio_text)

        i = 0
        to_select = None
        for radio in radios:
            if answer in radio.text.lower():
                to_select = radios[i]
            i += 1

        if to_select is None:
            to_select = radios[len(radios) - 1]

        self.radio_select(to_select, answer, len(radios) > 2)

        if radios:
            return

    # MARK: - Helper Methods
    def unfollow(self):
        try:
            follow_checkbox = self.browser.find_element(By.XPATH, "//label[contains(.,\'to stay up to date with their page.\')]").click()
            follow_checkbox.click()
        except:
            print("Failed to unfollow company!")

    def send_resume(self):
        # TODO: send_resume() is not working
        try:
            file_upload_elements = (By.CSS_SELECTOR, "input[name='file']")
            if len(self.browser.find_elements(file_upload_elements[0], file_upload_elements[1])) > 0:
                input_buttons = self.browser.find_elements(file_upload_elements[0], file_upload_elements[1])
                if len(input_buttons) == 0:
                    raise Exception("No input elements found in element")
                for upload_button in input_buttons:
                    upload_type = upload_button.find_element(By.XPATH, "..").find_element(By.XPATH, "preceding-sibling::*")
                    if 'resume' in upload_type.text.lower():
                        upload_button.send_keys(self.resume_dir)
                    elif 'cover' in upload_type.text.lower():
                        if self.cover_letter_dir != '':
                            upload_button.send_keys(self.cover_letter_dir)
                        elif 'required' in upload_type.text.lower():
                            upload_button.send_keys(self.resume_dir)
        except:
            print("Failed to upload resume or cover letter!")
            pass

    def enter_text(self, element, text):
        element.clear()
        element.send_keys(text)

    def select_dropdown(self, element, text):
        select = Select(element)
        select.select_by_visible_text(text)

    # Radio Select
    def radio_select(self, element, label_text, clickLast=False):
        label = element.find_element(By.TAG_NAME, 'label')
        if label_text in label.text.lower() or clickLast == True:
            label.click()
        else:
            pass

    def radio_select_simplified(self, element):
        label = element.find_element(By.TAG_NAME, 'label')
        label.click()

    # Contact info fill-up
    def contact_info(self):
        frm_el = self.browser.find_elements(By.CLASS_NAME, 'jobs-easy-apply-form-section__grouping')

        if len(frm_el) == 0:
            return

        for el in frm_el:
            text = el.text.lower()
            if 'email address' in text:
                continue
            elif 'phone number' in text:
                try:
                    country_code_picker = el.find_element(By.XPATH, '//select[contains(@id,"phoneNumber")][contains(@id,"country")]')
                    self.select_dropdown(country_code_picker, self.personal_info['Phone Country Code'])
                except Exception as e:
                    print("Country code " + self.personal_info['Phone Country Code'] + " not found! Make sure it is exact.")
                    print(e)
                try:
                    phone_number_field = el.find_element(By.XPATH, '//input[contains(@id,"phoneNumber")][contains(@id,"nationalNumber")]')
                    self.enter_text(phone_number_field, self.personal_info['Mobile Phone Number'])
                except Exception as e:
                    print("Could not input phone number:")
                    print(e)

    def fill_up(self):
        """
        Fills up the form with the resume information.
        """
        # TODO: Too many try/excepts. Refactor this.
        try:
            easy_apply_content = self.browser.find_element(By.CLASS_NAME, 'jobs-easy-apply-content')
            b4 = easy_apply_content.find_element(By.CLASS_NAME, 'pb4')
            pb4 = easy_apply_content.find_elements(By.CLASS_NAME, 'pb4')

            if len(pb4) == 0:
                raise Exception("No pb4 class elements found in element")

            for pb in pb4:
                try:
                    label = pb.find_element(By.TAG_NAME, 'h3').text.lower()

                    # 1. Fill up the form with the personal info if possible
                    # TODO: Change to GPT supported? This works really well
                    if 'home address' in label:
                        self.home_address(pb)
                        continue

                    if 'contact info' in label:
                        self.contact_info()
                        continue

                    # 2. Fill up the form with the other information
                    try:
                        self.additional_questions()
                    except Exception as e:
                        pass

                    # 3. Send the resume and cover letter
                    try:
                        self.send_resume()
                    except Exception as e:
                        pass

                except:
                    pass
        except:
            pass

    def write_to_file(self, company, job_title, link, location, search_location):
        to_write = [company, job_title, link, location]
        #file_path = self.output_file_directory + self.file_name + search_location + ".csv"
        file_path = self.file_name + search_location + ".csv"

        with open(file_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(to_write)

    def record_unprepared_question(self, answer_type, question_text):
        to_write = [answer_type, question_text]
        file_path = self.unprepared_questions_file_name + ".csv"

        try:
            with open(file_path, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(to_write)
        except:
            print("Could not write the unprepared question to the file! No special characters in the question is allowed: ")
            print(question_text)

    def record_gpt_answer(self, answer_type, question_text, gpt_response):
        to_write = [answer_type, question_text, gpt_response]
        file_path = self.unprepared_questions_gpt_file_name + ".csv"

        try:
            with open(file_path, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(to_write)
        except:
            print("Could not write the unprepared gpt question to the file! No special characters in the question is allowed: ")
            print(question_text)

    def scroll_slow(self, scrollable_element, start=0, end=3600, step=100, reverse=False):
        if reverse:
            start, end = end, start
            step = -step

        for i in range(start, end, step):
            self.browser.execute_script("arguments[0].scrollTo(0, {})".format(i), scrollable_element)
            time.sleep(random.uniform(1.0, 2.6))

    def avoid_lock(self):
        if self.disable_lock:
            return

        pyautogui.keyDown('ctrl')
        pyautogui.press('esc')
        pyautogui.keyUp('ctrl')
        time.sleep(1.0)
        pyautogui.press('esc')

    def get_base_search_url(self, parameters):
        remote_url = ""

        if parameters['remote']:
            remote_url = "f_CF=f_WRA"

        level = 1
        experience_level = parameters.get('experienceLevel', [])
        experience_url = "f_E="
        for key in experience_level.keys():
            if experience_level[key]:
                experience_url += "%2C" + str(level)
            level += 1

        distance_url = "?distance=" + str(parameters['distance'])

        job_types_url = "f_JT="
        job_types = parameters.get('experienceLevel', [])
        for key in job_types:
            if job_types[key]:
                job_types_url += "%2C" + key[0].upper()

        date_url = ""
        dates = {"all time": "", "month": "&f_TPR=r2592000", "week": "&f_TPR=r604800", "24 hours": "&f_TPR=r86400"}
        date_table = parameters.get('date', [])
        for key in date_table.keys():
            if date_table[key]:
                date_url = dates[key]
                break

        easy_apply_url = "&f_LF=f_AL"

        extra_search_terms = [distance_url, remote_url, job_types_url, experience_url]
        extra_search_terms_str = '&'.join(term for term in extra_search_terms if len(term) > 0) + easy_apply_url + date_url

        return extra_search_terms_str

    def next_job_page(self, position, location, job_page):
        self.browser.get("https://www.linkedin.com/jobs/search/" + self.base_search_url +
                         "&keywords=" + position + location + "&start=" + str(job_page*25))

        self.avoid_lock()

