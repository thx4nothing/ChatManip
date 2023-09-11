FROM python:3.11-slim
LABEL authors="Marlon Beck"
WORKDIR /ChatManip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api_server/ /ChatManip/api_server
COPY static/ /ChatManip/static
COPY templates/ /ChatManip/templates
EXPOSE 8000
CMD ["uvicorn", "api_server.main:app", "--host", "0.0.0.0", "--port", "8000"]