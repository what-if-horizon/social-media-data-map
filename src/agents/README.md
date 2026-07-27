When running got-oss-20b install tiktoken_encodings to fix this bug

https://docs.vllm.ai/projects/recipes/en/latest/OpenAI/GPT-OSS.html#troubleshooting

mkdir -p tiktoken_encodings
wget -O tiktoken_encodings/o200k_base.tiktoken "https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken"
wget -O tiktoken_encodings/cl100k_base.tiktoken "https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken"