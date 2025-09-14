build:
	docker compose up --build

# Sobe e fica ligado ao backend (como se fosse logs em tempo real)
up:
	docker compose up --attach backend

# Roda as migrações do Django
migrate:
	docker compose run --rm backend python manage.py migrate

# Abre um shell interativo no container backend
bash:
	docker compose exec backend bash

# Cria um superusuário Django interativo
superuser:
	docker compose run --rm backend python manage.py createsuperuser

# Atalho para git add/commit/push
git:
	git add .
	git commit -m "update"
	git push origin main