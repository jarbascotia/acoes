API para gestão de investimentos em ações e fundos imobiliários, integrada com cotações em tempo real.

## 🛠 Rotas Disponíveis
| Método | Rota                   | Descrição                       |
|--------|------------------------|---------------------------------|
| GET    | `/api/carteira`        | Listar todos os ativos          |
| POST   | `/api/carteira`        | Adicionar novo ativo            |
| PUT    | `/api/carteira/{id}`   | Editar ativo existente          |
| DELETE | `/api/carteira/{id}`   | Excluir ativo                   |
| GET    | `/api/quote/{ticker}`  | Buscar cotação (ex: PETR4)      |

## 🐳 Execução com Docker
```bash
docker build -t acoes .
docker run -p 3003:3003 acoes

API Externa
Brapi: Consulta cotações de ações em tempo real.
(token: 7ENBXpDBTfhsgwDBW5Dzhq)