from openai_python_api import ChatGPT, DALLE
import asyncio

oai_token = "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"
oai_organization = "org-e5YmDzgD1qWRBsIHPg8sD2dt"

gpt = ChatGPT(auth_token=oai_token, organization=oai_organization, stream=False, model="gpt-3.5-turbo", max_tokens=50, choices=2)
dalle = DALLE(auth_token=oai_token, organization=oai_organization, model="dall-e-3")


async def main():
    #response = await gpt.str_chat(prompt="Hello, could you please tell me about ChatGPT-4-turbo?").__anext__()
    response = await dalle.create_image("A beautiful necromancer girl riding white unicorn in the forest.")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
