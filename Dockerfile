
FROM python:3.9-slim

WORKDIR /app

RUN pip install pipenv

COPY ["Pipfile", "Pipfile.lock", "risk_analysis_app.py", "./"]

RUN pipenv install --system --deploy

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "risk_analysis_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
