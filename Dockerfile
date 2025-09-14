# Backend Dockerfile
FROM python:3.12-slim

# Diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar código do backend
COPY . .

# Expõe porta do Django
EXPOSE 8000

# Comando default
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
