from openai import APIConnectionError, AuthenticationError, BadRequestError, NotFoundError, OpenAI, RateLimitError
from config import Config
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
import json
import logging

logger = logging.getLogger(__name__)


class AIService:
    PROMPTS = {
        "explain": "You are an expert academic tutor. Provide a clear, structured, detailed explanation using headings, bullets, and examples.",
        "summary": "You are a concise academic summarizer. Give a short summary with key bullet points.",
        "stepbystep": "You are a step-by-step problem solver. Break the solution into numbered steps with reasoning.",
        "flashcards": "Create 5 Q&A flashcards in JSON format: [{\"q\":\"...\",\"a\":\"...\"}]. Return ONLY valid JSON, no prose."
    }

    def __init__(self):
        if not Config.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set!")
        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_BASE_URL,
        )
        self.model = Config.OPENAI_MODEL

    def _create_completion(self, messages, temperature):
        if not Config.OPENAI_API_KEY:
            raise RuntimeError("No AI API key is configured.")

        try:
            return self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
        except AuthenticationError as exc:
            raise RuntimeError(
                "AI provider authentication failed. Check your API key and provider base URL."
            ) from exc
        except NotFoundError as exc:
            raise RuntimeError(
                f"The configured model '{self.model}' is not available for the current AI provider."
            ) from exc
        except RateLimitError as exc:
            raise RuntimeError(
                "The AI provider rate limit was reached. Please wait a moment and try again."
            ) from exc
        except APIConnectionError as exc:
            raise RuntimeError(
                "Could not reach the AI provider. Check your internet connection and provider base URL."
            ) from exc
        except BadRequestError as exc:
            raise RuntimeError(
                "The AI provider rejected the request. Check the configured model and request settings."
            ) from exc

    def ask(self, question, mode="explain"):
        system_prompt = self.PROMPTS.get(mode, self.PROMPTS["explain"])
        response = self._create_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.5,
        )
        return response.choices[0].message.content

    def visualize(self, topic):
        response = self._create_completion(
            messages=[
                {"role": "system", "content":
                    "You are a concept-map generator. Return ONLY valid JSON with keys: "
                    "'title', 'nodes' (list of {id, label}), 'edges' (list of {from, to, label}). "
                    "Keep 6-10 nodes. No prose."},
                {"role": "user", "content": f"Topic: {topic}"}
            ],
            temperature=0.4,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:]
        graph = json.loads(raw)

        # bar chart
        fig, ax = plt.subplots(figsize=(8, 4.5))
        labels = [n["label"] for n in graph["nodes"]]
        values = [len(n["label"]) for n in graph["nodes"]]
        ax.barh(labels, values, color="#6366f1")
        ax.set_title(f"Key Concepts: {graph.get('title', topic)}")
        ax.set_xlabel("Relative Emphasis")
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=110)
        plt.close(fig)
        buf.seek(0)
        chart_b64 = base64.b64encode(buf.read()).decode("utf-8")
        return graph, chart_b64
