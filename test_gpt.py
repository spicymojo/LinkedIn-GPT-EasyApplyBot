import unittest
from gpt import GPTAnswerer

class TestGPT(unittest.TestCase):

    personal_data_text = """
    John Doe
    123 Main Street
    Anytown, USA 12345
    555-555-5555
    
    ## Skills:
    - Swift and Objective-C
    - iOS frameworks: UIKit, Core Data, and Core Animation
    - Git
    - Microsoft Office
    
    - Willing to relocate
    - Willing to travel
    """

    demo_resume_text = """
    John Doe
    123 Main Street
    Anytown, USA 12345
    555-555-5555
    
    ## Education
    - **Bachelor of Science in Computer Science**  
          Ohio State University, Columbus, Ohio  
          Year of Graduation: 2020

    ## Skills:
    - Proficient in iOS app development using Swift and Objective-C
    - Strong knowledge of iOS frameworks such as UIKit, Core Data, and Core Animation
    
    ## Experience:
    - **iOS Developer**
            ABC Company, Anytown, USA
            January 2019 - Present
            - Developed and maintained 4 iOS apps that are used by thousands of users
            - Worked with the design team to create an app that was featured in the App Store
    
    ## Projects:
    - **Pooping selfie app**
            - Created an app that allows users to take a selfie only while pooping
            - Image recognition algorithm detects if the user is pooping, sees the bathroom, and is wearing pants.
    """

    demo_cover_letter_text = """
    Dear Hiring Manager,
    
    I am writing to express my interest in the iOS Developer position at [Company]. I have experience developing iOS apps and working with a team to create an app that was featured in the App Store.
    
    I am proficient in iOS app development using Swift and Objective-C. I have strong knowledge of iOS frameworks such as UIKit, Core Data, and Core Animation. I have developed and maintained 4 iOS apps that are used by thousands of users.
    
    I am excited to learn more about the iOS Developer position at [Company]. I have attached my resume for your review. Please feel free to contact me at 555-555-5555 or via email at john-doe@gmail.com.
    
    Sincerely,
    John Doe
    """

    demo_job_description_text = """
    
    ## Job Description
    - **iOS Developer** 
    - Company: ZXY Company ltd. 
    - Location: Anytown, USA
            
    ## Requirements
    - Proficient in iOS app development using Swift and Objective-C
    - Strong knowledge of iOS frameworks such as UIKit, Core Data, and Core Animation
    - Experience developing iOS apps and working with a team to create an app that was featured in the App Store
    - Word experience is a plus
    
    Travel up to 25% of the time.
    """

    answerer = GPTAnswerer(demo_resume_text, personal_data_text, demo_cover_letter_text, demo_job_description_text)

    def test_answer_question_textual_wide_range_name(self):
        question = "What is your name?"
        answer = self.answerer.answer_question_textual_wide_range(question)
        print(f"Name: {answer}")
        self.assertIn("John Doe", answer)

    def test_answer_question_textual_wide_range_phone_number(self):
        question = "What is your phone number?"
        answer = self.answerer.answer_question_textual_wide_range(question)
        print(f"Phone number: {answer}")
        self.assertIn("555-555-5555", answer)

    def test_answer_question_textual_wide_range_experience(self):
        question = "What is the name of the last company you worked at?"
        answer = self.answerer.answer_question_textual_wide_range(question)
        print(f"Experience: {answer}")
        self.assertIn("ABC Company", answer)

    def test_answer_question_textual_wide_range_cover_letter(self):
        question = "Cover Letter"
        answer = self.answerer.answer_question_textual_wide_range(question)
        print(f"Cover letter: {answer}")


if __name__ == '__main__':
    unittest.main()
