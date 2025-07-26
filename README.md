# Solutis Procurement

Sistema de gerenciamento de fornecedores desenvolvido em Django com suporte assíncrono usando ASGI e Uvicorn.

## 📋 Sobre o Projeto

O Solutis Procurement é um sistema completo para gestão de fornecedores, desenvolvido com Django 5.2.4 e configurado para execução assíncrona usando Uvicorn. O sistema oferece funcionalidades para cadastro, validação e gerenciamento de fornecedores com validações específicas para documentos brasileiros.

### Principais Funcionalidades

- ✅ Gestão completa de fornecedores
- ✅ Validação de documentos brasileiros (CPF/CNPJ)
- ✅ Integração com API de CEP
- ✅ Suporte assíncrono com ASGI
- ✅ Interface administrativa Django
- ✅ Containerização com Docker
- ✅ Health checks integrados

## 🚀 Tecnologias Utilizadas

- **Python**: 3.11+
- **Framework**: Django 5.2.4
- **Servidor**: Uvicorn com suporte ASGI
- **Validação**: Pydantic 2.11.7+
- **Documentos BR**: validate-docbr 1.11.1+
- **CEP**: brazilcep 7.0.0+
- **Testes**: pytest 8.4.1+
- **Container**: Docker + Docker Compose
- **Gerenciador de Dependências**: Poetry

## 📁 Estrutura do Projeto

```
solutis_procurement/
├── config/                 # Configurações Django
│   ├── __init__.py
│   ├── asgi.py            # Configuração ASGI
│   ├── settings.py        # Configurações principais
│   ├── urls.py            # URLs principais
│   └── wsgi.py            # Configuração WSGI
├── src/                   # Código fonte
│   ├── procurement/       # App procurement
│   ├── supplier/          # App fornecedores
│   └── shared/           # Modelos compartilhados
├── db.sqlite3            # Banco de dados (dev)
├── manage.py             # Script de gerenciamento Django
├── pyproject.toml        # Configuração Poetry
├── Dockerfile            # Configuração Docker
├── docker-compose.yaml   # Orquestração Docker
└── README.md            # Este arquivo
```

## 🛠 Instalação e Configuração

### Pré-requisitos

- Python 3.11+
- Poetry
- Docker (opcional)
- Docker Compose (opcional)

### Instalação Local

1. **Clone o repositório**
```bash
git clone <repository-url>
cd solutis_procurement
```

2. **Instale as dependências**
```bash
poetry install
```

3. **Ative o ambiente virtual**
```bash
poetry shell
```

4. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. **Execute as migrations**
```bash
python manage.py migrate
```

6. **Crie um superusuário**
```bash
python manage.py createsuperuser
```

7. **Colete arquivos estáticos**
```bash
python manage.py collectstatic
```

8. **Execute o servidor**
```bash
# Desenvolvimento
python manage.py runserver

# Produção com Uvicorn
uvicorn config.asgi:application --host 0.0.0.0 --port 8000
```

## 🐳 Execução com Docker

### Docker Compose (Recomendado)

1. **Suba o serviço**
```bash
docker-compose up -d
```

2. **Visualize os logs**
```bash
docker-compose logs -f solutis-procurement
```

3. **Pare o serviço**
```bash
docker-compose down
```

### Docker Manual

1. **Build da imagem**
```bash
docker build -t solutis-procurement .
```

2. **Execute o container**
```bash
docker run -p 8081:8081 solutis-procurement
```

## 🔧 Configurações

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Locale
LANG=pt_BR.UTF-8
LC_ALL=pt_BR.UTF-8
```

### Docker Compose

O arquivo `docker-compose.yaml` já está configurado com:

- **Porta**: 8081
- **Volumes**: Código fonte, logs, storage e .env
- **Network**: agile-network
- **Health Check**: Verificação automática de saúde
- **Auto Migrations**: Execução automática das migrations
- **Static Files**: Coleta automática de arquivos estáticos

## 📊 Apps do Django

### Supplier (Fornecedores)
- Gestão completa de fornecedores
- Validação de documentos brasileiros
- Integração com APIs de CEP

### Procurement (Compras)
- Funcionalidades de compras (em desenvolvimento)

### Shared (Compartilhado)
- Modelos base compartilhados
- Utilities comuns

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar testes com coverage
pytest --cov=src

# Executar testes de um app específico
pytest src/supplier/tests.py
```

## 📝 Scripts de Desenvolvimento

### Poetry Scripts

```bash
# Formatação de código
poetry run black .

# Linting
poetry run flake8

# Testes
poetry run pytest
```

### Django Management Commands

```bash
# Criar migrations
python manage.py makemigrations

# Aplicar migrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Shell Django
python manage.py shell

# Servidor de desenvolvimento
python manage.py runserver
```

## 🚀 Deploy

### Produção

1. **Configure as variáveis de ambiente para produção**
```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com
SECRET_KEY=production-secret-key
```

2. **Use o Docker Compose**
```bash
docker-compose -f docker-compose.prod.yaml up -d
```

### Health Check

O serviço inclui health check automático:
- **Endpoint**: `http://localhost:8081/`
- **Intervalo**: 30s
- **Timeout**: 10s
- **Retries**: 3

## 📚 API Documentation

A documentação da API estará disponível em:
- **Admin**: `http://localhost:8081/admin/`
- **API**: `http://localhost:8081/api/` (quando implementada)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).

## 👥 Autor

**Pedro Gustavo Santana**
- Email: pedro.parametrize@gmail.com
- GitHub: [@pedro-parametrize](https://github.com/pedro-parametrize)

## 🆘 Suporte

Se você encontrar algum problema ou tiver dúvidas:

1. Verifique a [documentação](README.md)
2. Consulte os [logs do container](#-execução-com-docker)
3. Abra uma [issue](issues) no repositório

---

## 📋 Troubleshooting

### Problemas Comuns

**Container não inicia**
```bash
# Verifique os logs
docker-compose logs solutis-procurement

# Reconstrua a imagem
docker-compose build --no-cache
```

**Erro de migrations**
```bash
# Execute migrations manualmente
docker-compose exec solutis-procurement python manage.py migrate
```

**Problemas de permissão**
```bash
# Ajuste permissões dos volumes
sudo chown -R $USER:$USER ./logs
sudo chown -R $USER:$USER /mnt/storage
```

**Porta já em uso**
```bash
# Altere a porta no docker-compose.yaml
ports:
  - "8081:8081"  # Mude 8081 para 8081
```
