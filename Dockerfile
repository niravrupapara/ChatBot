FROM python:3.11-slim

WORKDIR /app

# Set PYTHONPATH so Python resolves top-level package imports (ui.*, src.*)
ENV PYTHONPATH=/app

# 1. Pre-install CPU-only PyTorch and torchvision
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 2. Copy dependency manifests first for 100% layer caching
COPY requirements.txt pyproject.toml ./

RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy remaining application files
COPY . .

CMD ["streamlit", "run", "ui/app.py", "--server.address=0.0.0.0", "--server.fileWatcherType=none"]