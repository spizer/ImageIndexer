"""
LLM API interaction logic
"""
import requests


class LLMProcessor:
    """Handles communication with LLM API for image analysis"""
    
    def __init__(self, config):
        self.api_url = config.api_url
        self.config = config
        self.instruction = getattr(config, 'general_instruction', getattr(config, 'instruction', ''))
        self.system_instruction = config.system_instruction
        self.description_instruction = getattr(config, 'description_instruction', getattr(config, 'caption_instruction', ''))
        self.keyword_instruction = getattr(config, 'keyword_instruction', self.instruction)
        self.requests = requests
        self.api_password = config.api_password
        self.max_tokens = config.gen_count
        self.temperature = config.temperature
        self.top_p = config.top_p
        self.rep_pen = config.rep_pen
        self.top_k = config.top_k
        self.min_p = config.min_p

    def describe_content(self, task="", processed_image=None):
        """
        Send image to LLM API for analysis.
        
        Args:
            task: Task type - "caption", "keywords_only", "caption_and_keywords", or "keywords"
            processed_image: Base64-encoded image string
            
        Returns:
            API response content string, or None on error
        """
        if not processed_image:
            print("No image to describe.")
            return None
        
        # Select instruction based on task
        if task == "caption":
            instruction = self.description_instruction
        elif task == "keywords":
            instruction = self.instruction
        elif task == "caption_and_keywords":
            instruction = self.instruction
        elif task == "keywords_only":
            instruction = self.keyword_instruction
        else:
            print(f"invalid task: {task}")
            return None
            
        try:
            messages = [
                {"role": "system", "content": self.system_instruction},
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": instruction},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{processed_image}"
                            }
                        }
                    ]
                }
            ]
            
            payload = {
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "min_p": self.min_p,
                "rep_pen": self.rep_pen
            }
            
            endpoint = f"{self.api_url}/v1/chat/completions"
            headers = {
                "Content-Type": "application/json"
            }
            if self.api_password:
                headers["Authorization"] = f"Bearer {self.api_password}"
            
            # Add timeout to prevent hanging (120 seconds should be enough for most LLM responses)
            response = self.requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=120
            )
            
            response.raise_for_status()
            response_json = response.json()
            
            if "choices" in response_json and len(response_json["choices"]) > 0:
                if "message" in response_json["choices"][0]:
                    return response_json["choices"][0]["message"]["content"]
                else:
                    return response_json["choices"][0].get("text", "")
            return None
            
        except Exception as e:
            print(f"Error in API call: {str(e)}")
            return None

