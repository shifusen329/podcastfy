"""Content Generator Module

This module is responsible for generating podcast content based on input texts using
LangChain and various LLM backends. It handles the interaction with the AI model and
provides methods to generate and save the generated content.
"""

import os
from typing import Optional, Dict, Any, List
import re

from langchain_community.chat_models import ChatLiteLLM
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms.llamafile import Llamafile
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain import hub

from podcastfy.utils.config_conversation import load_conversation_config
from podcastfy.utils.config import load_config
from podcastfy.templates import ConversationTemplate, MonologueTemplate
from podcastfy.templates.formats import get_template

import logging

logger = logging.getLogger(__name__)

class LLMBackend:
    def __init__(
        self,
        is_local: bool,
        temperature: float,
        max_output_tokens: int,
        model_name: str,
        api_key_label: str = "GEMINI_API_KEY",
    ):
        """Initialize the LLMBackend."""
        self.is_local = is_local
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.model_name = model_name
        self.is_multimodal = not is_local

        common_params = {
            "temperature": temperature,
            "presence_penalty": 0.75,
            "frequency_penalty": 0.75,
        }

        if is_local:
            self.llm = Llamafile()
        elif "gemini" in self.model_name.lower():
            self.llm = ChatGoogleGenerativeAI(
                api_key=os.environ["GEMINI_API_KEY"],
                model=model_name,
                max_output_tokens=max_output_tokens,
                **common_params,
            )
        else:
            self.llm = ChatLiteLLM(
                model=self.model_name,
                temperature=temperature,
                api_key=os.environ[api_key_label],
            )

class ContentGenerator:
    def __init__(
        self, 
        is_local: bool=False, 
        model_name: str="gemini-1.5-pro-latest", 
        api_key_label: str="GEMINI_API_KEY",
        conversation_config: Optional[Dict[str, Any]] = None,
        format_type: str = None
    ):
        """Initialize the ContentGenerator."""
        self.is_local = is_local
        self.config = load_config()
        self.content_generator_config = self.config.get("content_generator", {})
        self.config_conversation = load_conversation_config(conversation_config).to_dict()
        
        # Get output directories
        self.output_directories = self.config_conversation.get("text_to_speech", {}).get("output_directories", {})
        transcripts_dir = self.output_directories.get("transcripts")
        if transcripts_dir and not os.path.exists(transcripts_dir):
            os.makedirs(transcripts_dir)
        
        # Initialize LLM backend
        if not model_name:
            model_name = self.content_generator_config.get("llm_model")
        if is_local:
            model_name = "User provided local model"

        llm_backend = LLMBackend(
            is_local=is_local,
            temperature=self.config_conversation.get("creativity", 1),
            max_output_tokens=self.content_generator_config.get("max_output_tokens", 8192),
            model_name=model_name,
            api_key_label=api_key_label,
        )
        self.llm = llm_backend.llm
        
        # Set format type
        if not format_type:
            format_type = self.content_generator_config.get("default_format", "conversation")
        self.format_type = format_type
        
        # Initialize template
        self.template = get_template(format_type)()

    def __compose_prompt(self, num_images: int) -> ChatPromptTemplate:
        """Compose the prompt for the LLM."""
        image_path_keys = []
        messages = []

        # Get format-specific template
        template_str = self.template.get_template()
        
        # Create system message with format requirements
        system_content = template_str
        
        # Add style parameters as system instructions
        style_instructions = """
Style Guidelines:
- Use a {conversation_style} style
- Follow this structure: {dialogue_structure}
- Use these engagement techniques: {engagement_techniques}

Content Instructions:
1. Read and understand the provided content carefully
2. Create a podcast that discusses ONLY the topics and information present in this content
3. Do not introduce unrelated topics or make up information
4. For conversation format:
   - Each speaker's line must be properly tagged with <Person1> or <Person2>
   - Tags must be adjacent with no spaces between them (e.g., </Person1><Person2>)
   - Each line should be a complete thought
   - Maintain natural turn-taking between speakers

The podcast should be titled "{podcast_name}" with the tagline "{podcast_tagline}"."""
        system_content = f"{system_content}\n\n{style_instructions}"

        # Add any user instructions
        user_instructions = self.config_conversation.get("user_instructions", "")
        if user_instructions:
            system_content = f"{system_content}\n\nAdditional Instructions:\n{user_instructions}"
        
        # Create list of message dicts
        messages = [
            # System message as dict
            {
                "type": "system",
                "text": system_content
            },
            # Text content as dict with format-specific prompt
            {
                "type": "text",
                "text": ("Please analyze this input and generate a monologue using <Speaker> tags for all speech. " if self.format_type == "monologue" else "Please analyze this input and generate a conversation. ") + "{input_text}",
            }
        ]

        # Add image content if any
        for i in range(num_images):
            key = f"image_path_{i}"
            image_content = {
                "type": "image_url",
                "image_url": {"url": "{" + key + "}", "detail": "high"}
            }
            image_path_keys.append(key)
            messages.append(image_content)

        # Create template from message dicts
        user_prompt_template = ChatPromptTemplate.from_messages(
            messages=[HumanMessagePromptTemplate.from_template(messages)]
        )

        return user_prompt_template, image_path_keys

    def generate_qa_content(
        self,
        input_texts: str = "",
        image_file_paths: List[str] = [],
        output_filepath: Optional[str] = None,
        longform: bool = False
    ) -> str:
        """Generate podcast content based on input texts."""
        try:
            # Validate parameters
            self.template.validate_params(self.config_conversation)

            # Setup chain
            num_images = 0 if self.is_local else len(image_file_paths)
            self.prompt_template, image_path_keys = self.__compose_prompt(num_images)
            self.parser = StrOutputParser()
            self.chain = self.prompt_template | self.llm | self.parser

            # Clean input text
            cleaned_input = input_texts.replace("{input_text}", "").strip()
            
            # Prepare parameters
            prompt_params = {
                "input_text": cleaned_input,
                "conversation_style": ", ".join(
                    self.config_conversation.get("conversation_style", [])
                ),
                "dialogue_structure": ", ".join(
                    self.config_conversation.get("dialogue_structure", [])
                ),
                "podcast_name": self.config_conversation.get("podcast_name"),
                "podcast_tagline": self.config_conversation.get("podcast_tagline"),
                "output_language": self.config_conversation.get("output_language"),
                "engagement_techniques": ", ".join(
                    self.config_conversation.get("engagement_techniques", [])
                ),
                "user_instructions": self.config_conversation.get("user_instructions", "")
            }

            # Add image paths if any
            for key, path in zip(image_path_keys, image_file_paths):
                prompt_params[key] = path

            # Log prompt parameters
            logger.info(f"Generating content with format: {self.format_type}")
            logger.info(f"Input text (first 500 chars): {input_texts[:500]}...")
            logger.info(f"Parameters: {prompt_params}")

            # Generate content
            self.response = self.chain.invoke(prompt_params)
            logger.info(f"Raw LLM response (first 500 chars): {self.response[:500]}...")

            # Clean response
            self.response = self.template.clean_markup(self.response)
            logger.info(f"Cleaned response (first 500 chars): {self.response[:500]}...")
                
            logger.info("Content generated successfully")

            # Save output if requested
            if output_filepath:
                with open(output_filepath, "w") as file:
                    file.write(self.response)
                logger.info(f"Response content saved to {output_filepath}")
                print(f"Transcript saved to {output_filepath}")

            return self.response
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise
