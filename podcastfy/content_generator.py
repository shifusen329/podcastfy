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


class LongFormContentGenerator:
    """
    Handles generation of long-form podcast conversations by breaking content into manageable chunks.
    
    Uses a "Content Chunking with Contextual Linking" strategy to maintain context between segments
    while generating longer conversations.
    """
    
    def __init__(self, chain, llm, config_conversation: Dict[str, Any], template):
        """Initialize LongFormContentGenerator."""
        self.llm_chain = chain
        self.llm = llm
        self.template = template
        self.max_num_chunks = config_conversation.get("max_num_chunks", 7)
        self.min_chunk_size = config_conversation.get("min_chunk_size", 600)

    def __calculate_chunk_size(self, input_content: str) -> int:
        """Calculate chunk size based on input content length."""
        input_length = len(input_content)
        if input_length <= self.min_chunk_size:
            return input_length
        
        maximum_chunk_size = input_length // self.max_num_chunks
        if maximum_chunk_size >= self.min_chunk_size:
            return maximum_chunk_size
        
        return input_length // (input_length // self.min_chunk_size)

    def chunk_content(self, input_content: str, chunk_size: int) -> List[str]:
        """Split input content into manageable chunks while preserving context."""
        sentences = input_content.split('. ')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            if current_length + sentence_length > chunk_size and current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
                current_chunk = []
                current_length = 0
            current_chunk.append(sentence)
            current_length += sentence_length
            
        if current_chunk:
            chunks.append('. '.join(current_chunk) + '.')
        return chunks

    def enhance_prompt_params(self, prompt_params: Dict, 
                            part_idx: int, 
                            total_parts: int,
                            chat_context: str,
                            chunk: str) -> Dict:
        """Enhance prompt parameters for content generation."""
        # Log input state
        print(f"\n=== Enhancing Prompt for Part {part_idx+1}/{total_parts} ===")
        print(f"Context length: {len(chat_context) if chat_context else 0}")
        if chat_context:
            print(f"Previous context ends with: {chat_context[-200:] if len(chat_context) > 200 else chat_context}")
        else:
            print("No previous context")

        enhanced_params = prompt_params.copy()
        enhanced_params["context"] = chat_context

        # Get format-specific longform instructions
        format_instructions = self.template.get_longform_instructions()
        print(f"\nFormat Instructions:\n{format_instructions}")

        # Add chunk position rules
        print(f"\n{'First' if part_idx == 0 else 'Last' if part_idx == total_parts - 1 else 'Middle'} Chunk Instructions:")
        
        # Determine chunk-specific instructions
        if part_idx == 0:
            chunk_rules = f"""
            1. Start with: Welcome to {enhanced_params["podcast_name"]} - {enhanced_params["podcast_tagline"]}.
            2. Begin discussing the content.
            3. End with an open-ended question or statement that leads into the next topic.
            4. DO NOT end with any farewells or thank yous.
            """
        elif part_idx == total_parts - 1:
            chunk_rules = """
            1. Continue the previous discussion naturally.
            2. End with a brief thank you to the listeners.
            """
        else:
            chunk_rules = """
            1. Continue the conversation exactly where it left off.
            2. Respond directly to the last speaker's points.
            3. End with an open-ended question or statement that leads into the next topic.
            4. DO NOT:
               - Introduce yourself or the podcast
               - End with any farewells or thank yous
               - Mention PODCASTIFY
               - Add any transitional phrases like "moving on" or "next"
            """

        enhanced_params["instruction"] = f"""
        {format_instructions}

        IMPORTANT: You are generating part {part_idx + 1} of {total_parts}. 
        
        Previous context: {chat_context if chat_context else "No previous context - this is the start"}
        
        Rules for this part:
        {chunk_rules}
        
        Additional Rules:
        1. Use the previous context to maintain conversation flow.
        2. Each speaker must respond to what was previously said.
        3. NO meta-commentary about parts or segments.
        4. ONLY discuss the content from this section: {chunk[:200]}...
        """
        
        print(f"\nFinal Instructions:\n{enhanced_params['instruction']}")
        return enhanced_params

    def generate_long_form(self, input_content: str, prompt_params: Dict) -> str:
        """Generate a complete long-form conversation using chunked content.
        
        This version maintains conversation flow by:
        1. Using minimal context (only previous response)
        2. Avoiding redundant introductions/farewells
        3. Ensuring proper speaker alternation
        
        Args:
            input_content (str): Input text to be chunked and processed
            prompt_params (Dict): Base parameters for prompt generation
            
        Returns:
            str: Complete generated conversation with proper flow
            
        Implementation Notes:
        - chat_context starts empty (not full input_content)
        - Each chunk only sees previous response as context
        - Chunks are processed sequentially with minimal context
        - First chunk handles introduction
        - Middle chunks continue naturally
        - Last chunk handles conclusion
        """
        # Log initial state
        print("\n=== Starting Long Form Generation ===")
        print(f"Input content length: {len(input_content)}")
        print(f"First 200 chars: {input_content[:200]}...")
        
        # Calculate appropriate chunk size
        chunk_size = self.__calculate_chunk_size(input_content)
        print(f"\nCalculated chunk size: {chunk_size}")
        
        chunks = self.chunk_content(input_content, chunk_size)
        num_parts = len(chunks)
        print(f"Split into {num_parts} chunks")
        
        # Track conversation pieces
        conversation_parts = []
        chat_context = ""  # Start with empty context
        
        for i, chunk in enumerate(chunks):
            print(f"\n=== Processing Chunk {i+1}/{num_parts} ===")
            print(f"Chunk size: {len(chunk)}")
            print(f"Chunk preview: {chunk[:200]}...")
            
            # For middle and end parts, use only previous response as context
            if i > 0:
                chat_context = conversation_parts[-1]
                print(f"\nUsing previous response as context:")
                print(f"Context preview: {chat_context[:200]}...")
                print(f"Context ends with: {chat_context[-200:] if len(chat_context) > 200 else chat_context}")
            
            # Prepare parameters for this chunk
            enhanced_params = self.enhance_prompt_params(
                prompt_params,
                part_idx=i,
                total_parts=num_parts,
                chat_context=chat_context,
                chunk=chunk
            )
            enhanced_params["input_text"] = chunk
            
            # Generate response for this chunk
            print("\nGenerating response...")
            # Create a new chain for each chunk to avoid parameter persistence
            chain = ChatPromptTemplate.from_messages([
                SystemMessage(content=enhanced_params["instruction"]),
                HumanMessage(content=f"Please analyze this input and generate a conversation. {chunk}")
            ]) | self.llm | StrOutputParser()
            # Remove instruction from params since it's now in the system message
            params_without_instruction = {k: v for k, v in enhanced_params.items() if k != "instruction"}
            response = chain.invoke(params_without_instruction)
            print(f"\nGenerated Response Preview:")
            print(f"First 200 chars: {response[:200]}...")
            print(f"Last 200 chars: {response[-200:]}...")
            
            conversation_parts.append(response)
        
        # Combine all parts into final conversation
        print("\n=== Combining Parts ===")
        final_conversation = "\n".join(conversation_parts)
        print(f"Final length: {len(final_conversation)}")
        return final_conversation


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
2. Create a podcast that discusses ONLY the topics and information present
3. Do not introduce unrelated topics or make up information
4. Stay focused on the main themes and key points
5. Use evidence and examples from the provided content

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
            if longform:
                generator = LongFormContentGenerator(self.chain, self.llm, self.config_conversation, self.template)
                self.response = generator.generate_long_form(cleaned_input, prompt_params)
            else:
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
