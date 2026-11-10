FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HOME=/home/appuser \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_MAX_UPLOAD_SIZE=10

WORKDIR /workspace

RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup --home /home/appuser appuser \
    && mkdir -p /home/appuser/.streamlit \
    && chown -R appuser:appgroup /home/appuser

COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt

COPY --chown=appuser:appgroup . .
WORKDIR /workspace/app/intermedio/cv_analyzer
USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health', timeout=3)"

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]

