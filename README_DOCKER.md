# Docker Setup - GenAIFinOps

## Estrutura de Arquivos Docker

```
gen_ai_finops/
├── Dockerfile.backend      # Backend Python/FastAPI
├── docker-compose.yml      # Orquestração completa
├── frontend/
│   ├── Dockerfile          # Frontend React (Multi-stage)
│   └── nginx.conf          # Configuração Nginx para SPA
└── .dockerignore           # Arquivos ignorados no build
```

## Como Usar

### 1. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production-min-32-chars

# LLM API Keys (opcional)
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here

# CORS
CORS_ORIGINS=http://localhost:3000
```

### 2. Build e Execução

```bash
# Build e start todos os serviços
docker-compose up --build

# Ou em background
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Parar e remover volumes (limpa banco de dados)
docker-compose down -v
```

### 3. Acessar os Serviços

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

### 4. Primeira Execução

Na primeira execução, o backend automaticamente:
1. Aguarda o PostgreSQL ficar pronto
2. Executa as migrations do Alembic
3. Inicia o servidor FastAPI

### 5. Criar Usuário Admin

Após o primeiro start, crie um usuário admin:

```bash
# Entrar no container do backend
docker-compose exec backend bash

# Criar usuário admin
python scripts/create_admin_user.py

# Ou com parâmetros customizados
python scripts/create_admin_user.py --username admin --password sua_senha --email admin@example.com
```

## Estrutura dos Containers

### Backend (`gen_ai_finops_backend`)
- **Imagem**: Python 3.11-slim
- **Porta**: 8000
- **Volumes**: 
  - `./gen_ai_finops/data` → `/app/gen_ai_finops/data` (ChromaDB)
- **Dependências**: PostgreSQL

### Frontend (`gen_ai_finops_frontend`)
- **Build**: Multi-stage (Node.js → Nginx)
- **Porta**: 3000 (mapeada para 80 no container)
- **Servidor**: Nginx Alpine (leve e rápido)
- **Dependências**: Backend

### PostgreSQL (`gen_ai_finops_db`)
- **Imagem**: postgres:15-alpine
- **Porta**: 5432
- **Volume**: `postgres_data` (persistente)
- **Database**: `gen_ai_finops`

## Troubleshooting

### Backend não conecta ao banco
```bash
# Verificar se PostgreSQL está rodando
docker-compose ps

# Ver logs do PostgreSQL
docker-compose logs postgres

# Verificar conexão
docker-compose exec backend python -c "from db.database import engine; print(engine.connect())"
```

### Frontend não carrega
```bash
# Verificar build do frontend
docker-compose logs frontend

# Rebuild apenas o frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Migrations não rodam
```bash
# Rodar migrations manualmente
docker-compose exec backend alembic upgrade head

# Ver status das migrations
docker-compose exec backend alembic current
```

### Limpar tudo e começar do zero
```bash
# Para e remove tudo (incluindo volumes)
docker-compose down -v

# Remove imagens também
docker-compose down -v --rmi all

# Build e start novamente
docker-compose up --build
```

## Desenvolvimento

### Modo Desenvolvimento (Hot Reload)

Para desenvolvimento com hot reload, use os comandos locais:

**Backend:**
```bash
cd gen_ai_finops
python main.py server
```

**Frontend:**
```bash
npm run dev
```

### Apenas Banco de Dados no Docker

Se quiser rodar apenas o PostgreSQL no Docker:

```bash
# Start apenas o PostgreSQL
docker-compose up -d postgres

# Backend e Frontend rodam localmente
# Configure DATABASE_URL no .env
```

## Produção

### Variáveis de Ambiente de Produção

No `.env` de produção, configure:

```bash
# Segurança
JWT_SECRET_KEY=<strong-random-key-min-32-chars>
CORS_ORIGINS=https://yourdomain.com

# Database (use SSL em produção)
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Build Otimizado

```bash
# Build sem cache (força rebuild completo)
docker-compose build --no-cache

# Build apenas serviços específicos
docker-compose build backend
docker-compose build frontend
```

## Comandos Úteis

```bash
# Ver status dos containers
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f backend
docker-compose logs -f frontend

# Executar comando no container
docker-compose exec backend python main.py scrape
docker-compose exec backend alembic upgrade head

# Restart um serviço
docker-compose restart backend

# Ver uso de recursos
docker stats
```

