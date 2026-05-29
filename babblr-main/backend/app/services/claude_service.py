import json
import logging
from typing import Dict, List, Tuple

import ollama  # SUBSTITUÍDO: Importamos a biblioteca do Ollama local no lugar da Anthropic

from app.config import settings
from app.services.prompt_builder import get_prompt_builder

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for AI conversation using LOCAL OLLAMA (Llama3) instead of Anthropic Claude."""

    def __init__(self):
        # REMOVIDO: A chave de API não é mais necessária!
        # Definimos o modelo local para o Ollama
        self.model = "llama3"
        self._prompt_builder = get_prompt_builder()

    async def correct_text(
        self, text: str, language: str, difficulty_level: str
    ) -> Tuple[str, List[Dict]]:
        """ Analyze user's text for errors and provide corrections. """
        
        # Get correction strategy for this level
        correction_strategy = self._prompt_builder.get_correction_strategy(difficulty_level)

        # Build correction guidance based on strategy
        ignore_list = []
        if correction_strategy.get("ignore_punctuation"):
            ignore_list.append("punctuation errors")
        if correction_strategy.get("ignore_capitalization"):
            ignore_list.append("capitalization mistakes")
        if correction_strategy.get("ignore_diacritics"):
            ignore_list.append("missing or incorrect diacritical marks (accents)")

        focus_list = correction_strategy.get("focus_on", [])

        guidance_parts = []
        if ignore_list:
            guidance_parts.append(f"IGNORE: {', '.join(ignore_list)}")
        if focus_list:
            focus_str = ", ".join(focus_list).replace("_", " ")
            guidance_parts.append(f"FOCUS ON: {focus_str}")

        correction_guidance = "\n".join(guidance_parts)

        # Normalize level for display
        normalized_level = self._prompt_builder.normalize_level(difficulty_level)

        prompt = f"""You are a language tutor teaching {language}. A {normalized_level} level student said:

"{text}"

Analyze this for errors based on the following correction strategy for {normalized_level} level:
{correction_guidance}

Respond with a JSON object containing:
1. "corrected_text": The corrected version (or original if perfect)
2. "corrections": Array of corrections, each with "original", "corrected", "explanation", and "type" (grammar/vocabulary/style)

Keep explanations brief and encouraging. If the text is perfect, return an empty corrections array.
IMPORTANT: Output ONLY valid JSON. Do not use markdown blocks like ```json.

Response format:
{{
  "corrected_text": "...",
  "corrections": [
    {{"original": "...", "corrected": "...", "explanation": "...", "type": "grammar"}}
  ]
}}"""

        try:
            # SUBSTITUÍDO: Chamada local para o Ollama
            response = ollama.chat(
                model=self.model, 
                messages=[{"role": "user", "content": prompt}]
            )

            text_content = response['message']['content']
            
            # Limpeza de segurança: Remove markdown se o Llama 3 for teimoso e enviar
            if "```json" in text_content:
                text_content = text_content.split("```json")[1].split("```")[0].strip()
            elif "```" in text_content:
                text_content = text_content.split("```")[1].split("```")[0].strip()

            result = json.loads(text_content)
            return result.get("corrected_text", text), result.get("corrections", [])
        
        except Exception as e:
            logger.error(f"Error in correct_text with Ollama: {e}")
            return text, []

    async def generate_response(
        self,
        user_message: str,
        language: str,
        difficulty_level: str,
        conversation_history: List[Dict[str, str]] | None = None,
    ) -> str:
        """ Generate a conversational response from the AI tutor. """
        
        if conversation_history is None:
            conversation_history = []

        # Build system prompt
        system_prompt = self._build_system_prompt(language, difficulty_level)

        # O Ollama usa a role "system", então injetamos o system_prompt na lista de mensagens
        messages = [{"role": "system", "content": system_prompt}]
        
        for msg in conversation_history[-10:]:  # Keep last 10 messages for context
            messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": user_message})

        try:
            # SUBSTITUÍDO: Chamada local para o Ollama
            response = ollama.chat(
                model=self.model, 
                messages=messages
            )

            assistant_message = response['message']['content']
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error in generate_response with Ollama: {e}")
            raise

    def _build_system_prompt(
        self,
        language: str,
        difficulty_level: str,
        topic: str = "general conversation",
        recent_vocab: list[str] | None = None,
        common_mistakes: list[str] | None = None,
    ) -> str:
        """Build system prompt using PromptBuilder."""
        return self._prompt_builder.build_prompt(
            language=language,
            level=difficulty_level,
            topic=topic,
            native_language=None,  # Will use settings.user_native_language by default
            recent_vocab=recent_vocab,
            common_mistakes=common_mistakes,
        )


# Create a singleton instance
claude_service = ClaudeService()