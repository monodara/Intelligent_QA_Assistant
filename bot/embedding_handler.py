import os
# 设置环境变量以避免meta tensor问题
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

import numpy as np
import torch
from PIL import Image
from paddleocr import PaddleOCR
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer
from .config import CLIP_MODEL_NAME


class EmbeddingHandler:
    def __init__(self):
        # Auto detect device
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Delay model loading - only load when needed
        self._text_model = None
        self._clip_model = None
        self._clip_processor = None
        self.TEXT_EMBEDDING_DIM = None
        
        # OCR
        self.ocr_model = PaddleOCR(use_textline_orientation=True, lang='ch')

    @property
    def text_model(self):
        if self._text_model is None:
            import os
            os.environ['TOKENIZERS_PARALLELISM'] = 'false'
            print("Loading text Embedding model...")
            # Try to specify device during initialization
            self._text_model = SentenceTransformer(
                'all-MiniLM-L6-v2',
                device=self.device
            )
            self.TEXT_EMBEDDING_DIM = self._text_model.get_sentence_embedding_dimension()
            print("Text Embedding model loaded successfully.")
        return self._text_model

    @property
    def clip_model(self):
        if self._clip_model is None:
            print("Loading CLIP model...")
            # Use auto to let framework choose appropriate precision
            try:
                import transformers
                from transformers import CLIPModel
                self._clip_model = CLIPModel.from_pretrained(
                    CLIP_MODEL_NAME,
                    torch_dtype=torch.float32 if self.device == "cpu" else torch.float16,
                    low_cpu_mem_usage=True,
                    use_safetensors=True
                )
                self._clip_model = self._clip_model.to(self.device)
            except RuntimeError:
                # If there are issues, fall back to CPU
                print("Using CPU to process CLIP model...")
                self._clip_model = CLIPModel.from_pretrained(
                    CLIP_MODEL_NAME,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True,
                    use_safetensors=True
                )
                self._clip_model = self._clip_model.to('cpu')
            print("CLIP model loaded successfully.")
        return self._clip_model

    @property
    def clip_processor(self):
        if self._clip_processor is None:
            print("Loading CLIP processor...")
            self._clip_processor = CLIPProcessor.from_pretrained(CLIP_MODEL_NAME)
            print("CLIP processor loaded successfully.")
        return self._clip_processor

    def get_text_embedding_offline(self, text):
        """Get text embedding"""
        try:
            vector = self.text_model.encode(text)
            return (vector / np.linalg.norm(vector)).astype("float32")
        except RuntimeError as e:
            if "meta tensor" in str(e):
                # If meta tensor error occurs, reinitialize model
                self._text_model = None  # Clear cache
                vector = self.text_model.encode(text)  # Reload and use
                return (vector / np.linalg.norm(vector)).astype("float32")
            else:
                raise e

    def get_clip_text_embedding_cpu(self, text):
        """CLIP text vectorization"""
        print(f"CLIP text vectorization: {text}")
        try:
            inputs = self.clip_processor(text=[text], return_tensors="pt", padding=True)
            # Ensure input tensors are moved to correct device
            for key, value in inputs.items():
                inputs[key] = value.to(self.device)
            with torch.no_grad():
                vector = self.clip_model.get_text_features(**inputs)
            vec = vector[0].detach().cpu().numpy()  # Must be CPU before storing to FAISS
            vec /= np.linalg.norm(vec)
            return vec.astype("float32")
        except RuntimeError as e:
            if "meta tensor" in str(e):
                # If meta tensor error occurs, reinitialize model
                self._clip_model = None  # Clear cache
                inputs = self.clip_processor(text=[text], return_tensors="pt", padding=True)
                # Ensure input tensors are moved to correct device
                for key, value in inputs.items():
                    inputs[key] = value.to(self.device)
                with torch.no_grad():
                    vector = self.clip_model.get_text_features(**inputs)
                vec = vector[0].detach().cpu().numpy()  # Must be CPU before storing to FAISS
                vec /= np.linalg.norm(vec)
                return vec.astype("float32")
            else:
                raise e

    def get_image_embedding_mps(self, image_path):
        """Get image embedding"""
        try:
            image = Image.open(image_path).convert("RGB").resize((224, 224))
            inputs = self.clip_processor(images=image, return_tensors="pt", padding=True)
            # Ensure input tensors are moved to correct device
            for key, value in inputs.items():
                inputs[key] = value.to(self.device)
            with torch.no_grad():
                vector = self.clip_model.get_image_features(**inputs)
            vec = vector[0].detach().cpu().numpy()
            vec /= np.linalg.norm(vec)
            return vec.astype("float32")
        except RuntimeError as e:
            if "meta tensor" in str(e):
                # If meta tensor error occurs, reinitialize model
                self._clip_model = None  # Clear cache
                image = Image.open(image_path).convert("RGB").resize((224, 224))
                inputs = self.clip_processor(images=image, return_tensors="pt", padding=True)
                # Ensure input tensors are moved to correct device
                for key, value in inputs.items():
                    inputs[key] = value.to(self.device)
                with torch.no_grad():
                    vector = self.clip_model.get_image_features(**inputs)
                vec = vector[0].detach().cpu().numpy()
                vec /= np.linalg.norm(vec)
                return vec.astype("float32")
            else:
                raise e

    def image_to_text(self, image_path):
        """Extract text from image using OCR"""
        try:
            result = self.ocr_model.predict(image_path)
            text = ""
            for line in result:
                if line:
                    for word_info in line:
                        if word_info:
                            text += word_info[1][0] + " "
            return text.strip()
        except Exception as e:
            print(f"OCR failed {image_path}: {e}")
            return ""