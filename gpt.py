import os
from langchain import PromptTemplate, OpenAI


class GPTAnswerer:
    def __int__(self, resume: str):
        self.resume = resume
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

    def answer_question(self, question: str):
        template = """The following is a resume and an answered question about the resume, being answered by the person who's resume it is (first person).
        
        ## Example
        Resume: I'm a software engineer with 10 years of experience on swift and python.
        Question: What is your experience on swift?
        Answer: I have 10 years of experience on swift.

        ## Resume:
        ```
        {resume}
        ```

        ## Question:
        {question}
        
        ## Answer:"""

        prompt = PromptTemplate(input_variables=["resume", "question"], template=template)          # Define the prompt (template)
        formatted_prompt = prompt.format_prompt(resume=self.resume, question=question)              # Format the prompt with the data
        output = self.llm(formatted_prompt.to_string())                                             # Send the prompt to the llm

        return output
