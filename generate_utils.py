import os
import random
import requests
from together import Together
from concurrent.futures import ThreadPoolExecutor

def generate_image_from_prompt(prompt: str, seed: int = None):
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        raise Exception("TOGETHER_API_KEY not set in environment.")
    
    client = Together(api_key=api_key)
    # print(f"Using Together API client: {client}")
    if seed is None:
        seed = random.randint(0, 1_000_000)
    try:
        response = client.images.generate(
            prompt=prompt,
            negative_prompt="",
            model="black-forest-labs/FLUX.1-schnell",
            steps=12,
            seed=seed,
            width=512,
            height=512,
        )

        if not response or not hasattr(response, "data") or not response.data:
            raise Exception("Image generation failed: response has no data.")
        return response.data[0].url

    except Exception as e:
        # print(f" Error in generate_image_from_prompt: {e}")
        raise Exception(f"Image generation failed: {e}")

def generate_multiple_images(prompts, image_paths,number):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(generate_image_from_prompt, prompt)
            for prompt in [prompts]*number
        ]
        for future in futures:
            try:
                future.result()  # Raises exception if any
                # Print the URL of the generated image
            except Exception as e:
                print(f" Error generating image: {e}")
                return e
        image_paths=[future.result() for future in futures if future.result() is not None]
        
        return image_paths
