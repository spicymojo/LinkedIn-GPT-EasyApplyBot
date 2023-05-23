import os
from langchain import PromptTemplate, OpenAI
from Levenshtein import distance


# TODO: Add the personal data to the context.
# TODO: Add a preprocessor to select better the context: resume, personal data, or cover letter.
class GPTAnswerer:
    def __init__(self, resume: str, personal_data: str, cover_letter: str = ""):
        self.resume = resume
        self.personal_data = personal_data
        self.cover_letter = cover_letter
        self.llm = OpenAI(model_name="text-davinci-003", openai_api_key=GPTAnswerer.openai_api_key(), temperature=0.5, max_tokens=-1)

    @staticmethod
    def openai_api_key():
        """
        Returns the OpenAI API key.
        environment variable used: OPEN_AI_API_KEY
        Returns: The OpenAI API key.
        """
        key = os.getenv('OPEN_AI_API_KEY')

        if key is None:
            raise Exception("OpenAI API key not found. Please set the OPEN_AOI_API_KEY environment variable.")

        return key

    def answer_question_textual(self, question: str) -> str:
        template = """The following is a resume and an answered question about the resume, being answered by the person who's resume it is (first person).
        ## Rules
        - Answer the question directly, if possible.
        - If seems likely that you have the experience based on the resume, even if is not explicit on the resume, answer as if you have the experience.
        - If you cannot answer the question, answer things like "I have no experience with that, but I learn fast, very fast".
        - The answer must not be larger than a tweet (140 characters).

        ## Example
        Resume: I'm a software engineer with 10 years of experience on both swift and python.
        Question: What is your experience with swift?
        Answer: I have 10 years of experience with swift.
        
        -----
        
        ## Extended personal data:
        ```
        {personal_data}
        ```
        
        ## Resume:
        ```
        {resume}
        ```

        ## Question:
        {question}
        
        ## Answer:"""

        prompt = PromptTemplate(input_variables=["personal_data", "resume", "question"], template=template)                 # Define the prompt (template)
        formatted_prompt = prompt.format_prompt(personal_data=self.personal_data, resume=self.resume, question=question)    # Format the prompt with the data
        output = self.llm(formatted_prompt.to_string())                                                                     # Send the prompt to the llm

        return output

    def answer_question_numeric(self, question: str, default_experience: int = 0) -> int:
        template = """The following is a resume and an answered question about the resume, the answer is an integer number.
        
        ## Rules
        - The answer must be an integer number.
        - The answer must only contain digits.
        - If you cannot answer the question, answer {default_experience}.
        
        ## Example
        Resume: I'm a software engineer with 10 years of experience on swift and python.
        Question: How many years of experience do you have on swift?
        Answer: 10
        
        -----
        
        ## Extended personal data:
        ```
        {personal_data}
        ```
        
        ## Resume:
        ```
        {resume}
        ```

        ## Question:
        {question}
        
        ## Answer:"""

        prompt = PromptTemplate(input_variables=["default_experience", "personal_data", "resume", "question"], template=template)                # Define the prompt (template)
        formatted_prompt = prompt.format_prompt(personal_data=self.personal_data, resume=self.resume, question=question, default_experience=default_experience)   # Format the prompt with the data
        output_str = self.llm(formatted_prompt.to_string())                 # Send the prompt to the llm
        # Convert to int with error handling
        try:
            output = int(output_str)                                            # Convert the output to an integer
        except ValueError:
            output = default_experience                                         # If the output is not an integer, return the default experience
            # Print error message
            print(f"Error: The output of the LLM is not an integer number. The default experience ({default_experience}) will be returned instead. The output was: {output_str}")

        return output

    def answer_question_from_options(self, question: str, options: list[str]) -> str:
        template = """The following is a resume and an answered question about the resume, the answer is one of the options.
        
        ## Rules
        - The answer must be one of the options.
        - The answer must exclusively contain one of the options.
        - Answer the option that seems most likely based on the resume.
        
        ## Example
        Resume: I'm a software engineer with 10 years of experience on swift, python, C, C++.
        Question: How many years of experience do you have on python?
        Options: [1-2, 3-5, 6-10, 10+]
        Answer: 10+
        
        -----
        
        ## Extended personal data:
        ```
        {personal_data}
        ```

        ## Resume:
        ```
        {resume}
        ```

        ## Question:
        {question}
        
        ## Options:
        {options}
        
        ## Answer:"""

        prompt = PromptTemplate(input_variables=["personal_data" "resume", "question", "options"], template=template)                # Define the prompt (template)
        formatted_prompt = prompt.format_prompt(personal_data=self.personal_data, resume=self.resume, question=question, options=options)   # Format the prompt with the data

        output = self.llm(formatted_prompt.to_string())                 # Send the prompt to the llm

        # Guard the output is one of the options
        if output not in options:
            # Choose the closest option to the output, using a levenshtein distance
            closest_option = min(options, key=lambda option: distance(output, option))
            output = closest_option
            print(f"Error: The output of the LLM is not one of the options. The closest option ({closest_option}) will be returned instead. The output was: {output}, options were: {options}")

        return output
