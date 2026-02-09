import logging
from typing import List, Optional

# Configure logging
logger = logging.getLogger(__name__)

class Planner:
    def __init__(self, llm_client, model: str = "gpt-4-turbo"):
        """
        Initializes the Planner.

        Args:
            llm_client: A client with a `chat.completions.create` interface (like OpenAI).
            model: The model identifier to use.
        """
        self.llm = llm_client
        self.model = model

    def plan(self, user_task: str) -> List[str]:
        """
        Decomposes the user task into a list of subtasks.

        Args:
            user_task: The high-level task description.

        Returns:
            A list of strings, where each string is a subtask.
        """
        logger.info(f"Planning task: {user_task}")
        
        system_prompt = (
            "You are a research planner. Your goal is to decompose a complex "
            "research task into sequential, actionable subtasks.\n"
            "Return the subtasks as a newline-separated list.\n"
            "Do not include numbering or bullet points in the content of the lines, just the text.\n"
            "Example:\n"
            "Search for X\n"
            "Analyze Y\n"
            "Summarize Z"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Task: {user_task}"}
        ]

        try:
            logger.debug(f"Sending prompt to LLM: {messages}")
            response = self.llm.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2
            )
            content = response.choices[0].message.content.strip()
            logger.debug(f"LLM Response: {content}")
            
            # Parse the content into a list
            subtasks = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Filter out numbering if the model halluncinated it despite instructions
            cleaned_subtasks = []
            for task in subtasks:
                # specific check for '1. ', '2. ', etc.
                if task[0].isdigit() and task[1] in ['.', ')']:
                     cleaned_subtasks.append(task.split(' ', 1)[1])
                elif task.startswith('- '):
                    cleaned_subtasks.append(task[2:])
                else:
                    cleaned_subtasks.append(task)
            
            logger.info(f"Generated {len(cleaned_subtasks)} subtasks")
            for i, task in enumerate(cleaned_subtasks):
                logger.info(f"Subtask {i+1}: {task}")
                
            return cleaned_subtasks

        except Exception as e:
            logger.error(f"Error during planning: {e}")
            raise
