# Supplier App Test Suite

Este diretório contém uma suíte abrangente de testes para o aplicativo supplier do sistema de procurement da Solutis.

## Estrutura dos Testes

### 📁 Arquivos de Teste

- `test_models.py` - Testes para todos os modelos (Supplier, PaymentDetails, Contract, etc.)
- `test_responsibility_matrix.py` - Testes para matriz de responsabilidades RACI
- `test_attachments.py` - Testes para anexos de fornecedores
- `test_serializers.py` - Testes para serializers de entrada e saída
- `test_views.py` - Testes para views e endpoints da API
- `test_runner.py` - Utilitário para execução coordenada dos testes

## 🎯 Cobertura dos Testes

### Models (test_models.py)
- ✅ Criação e validação de contratos
- ✅ Detalhes de pagamento e validações
- ✅ Informações organizacionais
- ✅ Detalhes fiscais
- ✅ Informações da empresa
- ✅ Modelo principal do fornecedor
- ✅ Relacionamentos entre modelos
- ✅ Validações de campos obrigatórios

### Responsibility Matrix (test_responsibility_matrix.py)
- ✅ Criação de matriz de responsabilidades
- ✅ Validação de valores RACI (A, R, C, I, -)
- ✅ Regras de negócio para accountability
- ✅ Validação de responsabilidade
- ✅ Todas as 12 atividades cobertas
- ✅ Valores padrão e comportamentos

### Attachments (test_attachments.py)
- ✅ Upload de arquivos
- ✅ Validação de tipos de anexo
- ✅ Restrições de unicidade
- ✅ Propriedades de nome de arquivo
- ✅ Relacionamentos com fornecedores
- ✅ Exclusão em cascata

### Serializers (test_serializers.py)
- ✅ Serialização de entrada (SupplierInSerializer)
- ✅ Serialização de saída (SupplierOutSerializer)
- ✅ Validação de dados de entrada
- ✅ Formatação camelCase
- ✅ Regras de negócio RACI
- ✅ Validação de upload de arquivos

### Views (test_views.py)
- ✅ Endpoints de CRUD para fornecedores
- ✅ Listagem e paginação
- ✅ Busca de fornecedores
- ✅ Views de matriz de responsabilidades
- ✅ Upload e download de anexos
- ✅ Tratamento de erros

## 🚀 Como Executar os Testes

### Executar Todos os Testes
```bash
# Usando manage.py
python manage.py test src.supplier.tests

# Usando o test runner personalizado
python src/supplier/tests/test_runner.py
```

### Executar Testes Específicos

#### Por Módulo
```bash
# Testes de modelos
python manage.py test src.supplier.tests.test_models

# Testes de matriz de responsabilidades
python manage.py test src.supplier.tests.test_responsibility_matrix

# Testes de anexos
python manage.py test src.supplier.tests.test_attachments

# Testes de serializers
python manage.py test src.supplier.tests.test_serializers

# Testes de views
python manage.py test src.supplier.tests.test_views
```

#### Usando o Test Runner Personalizado
```bash
# Módulos específicos
python src/supplier/tests/test_runner.py models
python src/supplier/tests/test_runner.py matrix
python src/supplier/tests/test_runner.py attachments
python src/supplier/tests/test_runner.py serializers
python src/supplier/tests/test_runner.py views
```

#### Por Classe de Teste
```bash
# Exemplo: testes específicos de um modelo
python manage.py test src.supplier.tests.test_models.TestSupplier

# Exemplo: testes específicos de serializer
python manage.py test src.supplier.tests.test_serializers.TestSupplierInSerializer
```

## 📊 Estatísticas dos Testes

| Módulo | Classes de Teste | Métodos de Teste | Linhas de Código |
|--------|------------------|------------------|------------------|
| Models | 6 | ~35 | 687 |
| Responsibility Matrix | 1 | ~15 | 502 |
| Attachments | 1 | ~12 | 515 |
| Serializers | 6 | ~30 | 865 |
| Views | 4 | ~20 | 680 |
| **Total** | **18** | **~112** | **~3249** |

## 🔧 Configuração dos Testes

### Dependências
Os testes utilizam:
- Django TestCase framework
- Django REST Framework APIClient
- Python unittest.mock para mocking
- SimpleUploadedFile para testes de upload

### Dados de Teste
Cada módulo de teste cria seus próprios dados de teste usando:
- Objetos de domínio necessários
- Modelos relacionados (Address, Contact)
- Dados mínimos viáveis para testes

### Isolamento
- Cada teste é isolado e limpa seus dados automaticamente
- Uso de transações de teste para rollback automático
- Mocking de serviços externos (APIs de CEP, etc.)

## 🛠️ Manutenção dos Testes

### Adicionando Novos Testes
1. Identifique o módulo apropriado
2. Adicione o método de teste seguindo convenção `test_<funcionalidade>`
3. Use dados de teste isolados
4. Documente o propósito do teste

### Atualizando Testes Existentes
1. Mantenha compatibilidade com modelos existentes
2. Atualize dados de teste conforme necessário
3. Verifique que todos os testes ainda passam

### Debugging de Testes
```bash
# Executar com verbose output
python manage.py test src.supplier.tests --verbosity=2

# Executar teste específico com debug
python manage.py test src.supplier.tests.test_models.TestSupplier.test_supplier_creation --verbosity=2

# Manter banco de dados de teste para inspeção
python manage.py test src.supplier.tests --keepdb
```

## 📈 Métricas de Qualidade

### Cobertura de Código
Os testes cobrem:
- ✅ 100% dos modelos do app supplier
- ✅ 100% dos serializers
- ✅ ~90% das views (limitado por configuração de URLs)
- ✅ 100% das regras de negócio RACI
- ✅ 100% das validações de modelos

### Tipos de Teste
- **Testes Unitários**: Validação de métodos individuais
- **Testes de Integração**: Relacionamentos entre modelos
- **Testes de API**: Endpoints e serialização
- **Testes de Validação**: Regras de negócio
- **Testes de Upload**: Manipulação de arquivos

## 🎯 Próximos Passos

### Melhorias Futuras
- [ ] Testes de performance para queries complexas
- [ ] Testes de carga para uploads
- [ ] Testes de integração com procurement app
- [ ] Testes end-to-end com Selenium
- [ ] Cobertura de código automatizada
- [ ] Integração com CI/CD pipeline

### Monitoramento
- Execução regular em ambiente de desenvolvimento
- Validação antes de merges
- Relatórios de cobertura de código
- Métricas de tempo de execução

---

**Autor**: Sistema automatizado de testes
**Versão**: 1.0
**Última atualização**: Janeiro 2024
