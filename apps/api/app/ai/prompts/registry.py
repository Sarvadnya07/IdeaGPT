import os
import json
from typing import Dict, List, Optional

class PromptRegistry:
    def __init__(self, prompts_dir: str = None):
        if prompts_dir is None:
            # Resolve default directory: app/ai/prompts/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.prompts_dir = current_dir
        else:
            self.prompts_dir = prompts_dir
            
        self.prompts: Dict[str, Dict[str, dict]] = {}  # {prompt_id: {version: prompt_dict}}
        self.load_prompts()

    def load_prompts(self):
        """
        Recursively scans the prompts directory for JSON files and loads them.
        """
        self.prompts.clear()
        if not os.path.exists(self.prompts_dir):
            return

        for root, _, files in os.walk(self.prompts_dir):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            prompt_id = data.get("id")
                            version = data.get("version")
                            if prompt_id and version:
                                if prompt_id not in self.prompts:
                                    self.prompts[prompt_id] = {}
                                self.prompts[prompt_id][version] = data
                    except Exception as e:
                        # Log error or ignore corrupted JSON templates
                        pass

    def get_prompt(self, prompt_id: str, version: Optional[str] = None) -> Optional[dict]:
        """
        Retrieves a specific prompt configuration. If no version is specified, returns the latest version.
        """
        versions = self.prompts.get(prompt_id)
        if not versions:
            return None
        
        if version:
            return versions.get(version)
        
        # Sort versions alphabetically to retrieve the latest version
        sorted_versions = sorted(versions.keys(), reverse=True)
        if sorted_versions:
            return versions[sorted_versions[0]]
        return None

    def list_prompts(self) -> List[dict]:
        """
        Lists summary of all unique prompts available in the registry.
        """
        summary_list = []
        for prompt_id, versions in self.prompts.items():
            # Get latest version for details
            latest_version = sorted(versions.keys(), reverse=True)[0]
            latest_prompt = versions[latest_version]
            summary_list.append({
                "id": prompt_id,
                "latest_version": latest_version,
                "description": latest_prompt.get("description", ""),
                "versions": list(versions.keys())
            })
        return summary_list

    def list_versions(self, prompt_id: str) -> List[str]:
        """
        Lists all available versions for a prompt ID.
        """
        versions = self.prompts.get(prompt_id)
        if not versions:
            return []
        return sorted(list(versions.keys()), reverse=True)

    def render_prompt(self, prompt_id: str, context: dict, version: Optional[str] = None) -> dict:
        """
        Retrieves prompt and renders user_prompt_template using the context variables.
        """
        prompt_config = self.get_prompt(prompt_id, version)
        if not prompt_config:
            raise ValueError(f"Prompt with ID {prompt_id} and version {version} not found.")

        user_template = prompt_config.get("user_prompt_template", "")
        # Render template safely, default to empty string if variable missing from context
        rendered_user_prompt = user_template.format(**{
            k: context.get(k, "") for k in context
        })
        
        return {
            "id": prompt_config["id"],
            "version": prompt_config["version"],
            "system_prompt": prompt_config.get("system_prompt", ""),
            "user_prompt": rendered_user_prompt,
            "temperature": prompt_config.get("temperature", 0.2),
            "max_tokens": prompt_config.get("max_tokens", 1000)
        }

# Global registry instance
prompt_registry = PromptRegistry()
