export HF_ENDPOINT=https://hf-mirror.com
MODEL_NAME="guillaumekln/faster-whisper-large-v2"
MODEL_NAME="guillaumekln/faster-whisper-medium"
MODEL_NAME="playgroundai/playground-v2-1024px-aesthetic"

MODEL_NAME="BAAI/bge-large-zh-v1.5"
huggingface-cli download --resume-download $MODEL_NAME --local-dir $MODEL_NAME --local-dir-use-symlinks False

#/Users/betterme/.cache/huggingface/hub/models--guillaumekIn--faster-whisper-medium
