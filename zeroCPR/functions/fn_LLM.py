# integrations of different LLMs
class fn_LLM():

    def query_llm(self, prompt):

        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-70b-8192",
            # model="mixtral-8x7b-32768",
        )

        output = chat_completion.choices[0].message.content
        return output