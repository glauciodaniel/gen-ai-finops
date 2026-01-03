# Testes - GenAIFinOps

## Instalação de Dependências

Para executar os testes, primeiro instale as dependências:

```bash
cd gen_ai_finops
pip install -r requirements.txt
pip install pytest pytest-cov
```

## Executar Testes

```bash
# Todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/test_auth.py -v
pytest tests/test_api.py -v
pytest tests/test_logger.py -v
pytest tests/test_rate_limit.py -v

# Com cobertura
pytest tests/ --cov=. --cov-report=html
```

## Estrutura de Testes

- `test_auth.py` - Testes de autenticação JWT
- `test_api.py` - Testes de integração da API
- `test_logger.py` - Testes de logging estruturado
- `test_rate_limit.py` - Testes de rate limiting
- `conftest.py` - Configuração e fixtures do pytest

## Notas

- Os testes requerem que as dependências estejam instaladas
- Alguns testes podem falhar se o ChromaDB não tiver dados
- Os testes de API usam TestClient do FastAPI (não requer servidor rodando)

