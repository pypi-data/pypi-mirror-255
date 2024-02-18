from openai import OpenAI
from response import Response

def OpenAI_generate_response(prompt, openai_key=""):
    
    try:
        # Executes the prompt and returns the response without parsing
        print ("Warming Up the Wisdom Workshop!")
        client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
            api_key=openai_key  # Replace with your actual API key
        )

        print ("Assembling Words of Wisdom!")
        details_response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,  # Your prompt goes here
                }
            ],
            model="gpt-3.5-turbo"
        )
        
        #return details_response
        return Response(data=details_response)
    except OpenAI.error.InvalidRequestError as e:
        print(f"OpenAI BadRequestError: {e}")
        return Response(error=str(e), status_code=400)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return Response(error=str(e), status_code=500)
          
def OpenAI_generate_image(image_prompt, number_images=1, quality="standard", size="1024x1024", openai_key=""):
    
    try:
        # Executes the prompt and returns the response without parsing
        
        print ("Sparking the Synapses of Silicon!")
        client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
            api_key=openai_key  # Replace with your actual API key
        )
        print("Summoning Pixels from the Digital Depths!")

        print(image_prompt)
        
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            n=number_images,
            quality=quality,
            size=size
        )
        
        #return image_response
        return Response(data=image_response)
    
    except OpenAI.error.InvalidRequestError as e:
        print(f"OpenAI BadRequestError: {e}")
        return Response(error=str(e), status_code=400)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return Response(error=str(e), status_code=500)