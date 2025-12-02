"""
FairLLM-Inspired Agent Framework with Phi-3-mini
Implements Agent and Flow patterns with actual LLM reasoning
"""
from typing import Dict, Any, List, Optional
import json
from abc import ABC, abstractmethod


class Agent(ABC):
    """
    Base Agent class inspired by FairLLM framework.
    Each agent uses LLM reasoning for their specialized task.
    """
    
    def __init__(self, name: str, model_name: str = "microsoft/Phi-3-mini-4k-instruct"):
        """
        Initialize agent with LLM backend
        
        Args:
            name: Agent name
            model_name: HuggingFace model to use (default: Phi-3-mini)
        """
        self.name = name
        self.model_name = model_name
        self.expertise = ""
        self.system_prompt = ""
        self._model = None
        self._tokenizer = None
    
    def _load_model(self):
        """Lazy load the LLM model"""
        if self._model is None:
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                import torch
                
                print(f"[{self.name}] Loading {self.model_name}...")
                
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None,
                    trust_remote_code=True
                )
                
                print(f"[{self.name}] Model loaded successfully!")
            except Exception as e:
                print(f"[{self.name}] Warning: Could not load LLM model: {e}")
                print(f"[{self.name}] Falling back to rule-based processing")
                self._model = None
    
    def invoke_llm(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Invoke the LLM with a prompt
        
        Args:
            prompt: Input prompt for the LLM
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLM response text
        """
        self._load_model()
        
        if self._model is None:
            # Fallback: return a structured response without LLM
            return self._fallback_response(prompt)
        
        try:
            # Format prompt with system message
            full_prompt = f"{self.system_prompt}\n\n{prompt}"
            
            inputs = self._tokenizer(full_prompt, return_tensors="pt")
            if self._model.device.type == "cuda":
                inputs = {k: v.to(self._model.device) for k, v in inputs.items()}
            
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self._tokenizer.eos_token_id
            )
            
            response = self._tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
            return response.strip()
            
        except Exception as e:
            print(f"[{self.name}] LLM invocation error: {e}")
            return self._fallback_response(prompt)
    
    @abstractmethod
    def _fallback_response(self, prompt: str) -> str:
        """Fallback response when LLM is unavailable"""
        pass
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Main execution method for the agent.
        Each agent implements their specialized task here.
        """
        pass


class Flow:
    """
    Flow coordinator that manages agent execution pipeline.
    Inspired by FairLLM's Flow pattern.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.agents: List[Agent] = []
    
    def add_agent(self, agent: Agent):
        """Add an agent to the flow"""
        self.agents.append(agent)
    
    def run(self, initial_input: Any) -> Any:
        """
        Execute the flow by running agents sequentially.
        Each agent's output becomes input to the next agent.
        
        Args:
            initial_input: Input to first agent
            
        Returns:
            Output from final agent
        """
        current_data = initial_input
        
        for agent in self.agents:
            print(f"\n[{self.name}] Executing agent: {agent.name}")
            current_data = agent.run(current_data)
        
        return current_data


class LLMConfig:
    """Configuration for LLM-based agents"""
    
    # Available models
    PHI3_MINI = "microsoft/Phi-3-mini-4k-instruct"
    PHI3_SMALL = "microsoft/Phi-3-small-8k-instruct"
    PHI3_MEDIUM = "microsoft/Phi-3-medium-4k-instruct"
    
    # Default settings
    DEFAULT_MODEL = PHI3_MINI
    DEFAULT_MAX_TOKENS = 500
    DEFAULT_TEMPERATURE = 0.7


# Export classes
__all__ = ['Agent', 'Flow', 'LLMConfig']