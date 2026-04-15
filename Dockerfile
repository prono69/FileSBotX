# ---------- Builder Stage ----------
FROM python:3.11-slim AS builder

WORKDIR /install

# Install build deps (only here, not in final image)
RUN apt-get update && apt-get install -y \
gcc \
build-essential \
&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies into a custom directory
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- Final Stage ----------
FROM python:3.11-slim

WORKDIR /app

# Copy only installed packages from builder
COPY --from=builder /install /usr/local

# Copy app source
COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["python", "-m", "FileStream"]