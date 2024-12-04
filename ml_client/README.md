# LLM Client for Web App

### Once dependencies from the Pipfile are loaded, you may use the below code prompts to install any model of your choosing, so long as it is on huggingface and uses the .gguf file extension for quantized models
#### NOTE: The "SmolLM-135M.Q2_K.gguf" model is given by default because it is so small, but it is not truly functional as an LLM

```python
!pip install -U "huggingface_hub[cli]"

# actual usable model for product
!huggingface-cli download bartowski/Ministral-8B-Instruct-2410-GGUF --include "Ministral-8B-Instruct-2410-Q4_K_M.gguf" --local-dir ./


# much smaller useless model for testing
!huggingface-cli download QuantFactory/SmolLM-135M-GGUF --include "SmolLM-135M.Q2_K.gguf" --local-dir ./ml_client/models
```
