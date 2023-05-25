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
    
    I am writing to apply for the [position] position at [company]. With a Bachelor of Science in Computer Science and 2 years of experience specializing in iOS app development, I am confident in my ability to contribute to innovative mobile solutions.
    
    I have a strong command of iOS frameworks such as UIKit, Core Data, and Core Animation, and I am proficient in Swift and Objective-C. I have a proven track record of delivering high-quality products, meeting deadlines, and collaborating effectively with cross-functional teams.
    
    I am excited to bring my expertise in developing key features and resolving bugs to your team. Projects like SocialConnect and eShop demonstrate my leadership in implementing user authentication, real-time messaging, and push notifications, as well as integrating RESTful APIs and optimizing app performance with Core Data.
    
    As an Apple Certified iOS Developer, I stay up-to-date with the latest trends and technologies. I possess excellent problem-solving and communication skills, and I am committed to driving the development of cutting-edge mobile solutions.
    
    I am confident that my technical skills and motivation make me an excellent fit for this position. Thank you for considering my application. I have attached my resume and look forward to the opportunity to discuss my qualifications further.
    
    Sincerely,
    John Doe
    """

    demo_job_description_text = """
    
    ## Job Description
    - **iOS Developer** 
    - Company: ZXY Incorporated 
    - Location: Sometown, USA
            
    ## Requirements
    - Proficient in iOS app development using Swift and Objective-C
    - Strong knowledge of iOS frameworks such as UIKit, Core Data, and Core Animation
    - Experience developing iOS apps and working with a team to create an app that was featured in the App Store
    - Word experience is a plus
    
    ## Soft Skills
    - Excellent communication skills
    - Ability to work in a team from home
    
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
