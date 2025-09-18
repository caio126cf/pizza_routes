Este projeto tem como objetivo otimizar entregas múltiplas, resolvendo o problema enfrentado por entregadores que saem com mais de três entregas por rota, e gastam tempo calculando qual seria a melhor rota/ ordem. Ele incluí recursos para facilitar a adição das rotas via imagem das comandas e também tem diversas formas de adicionar os endereços, afim de otimizar ao máximo o tempo de saída para as entregas.

A aplicação é composta por um backend em Django com DRF (Django Rest Framework) e Django Allauth configurado em modo headless para autenticação, integrado a uma SPA (Single Page Application) em React. O sistema utiliza PostgreSQL como banco de dados e é totalmente conteinerizado com Docker, garantindo portabilidade e consistência no ambiente de execução.

Diferente do modelo Django MVC tradicional, aqui o Django funciona exclusivamente como backend/API com DRF, enquanto toda a experiência do usuário é entregue pelo React no frontend.
