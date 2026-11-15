# Baseline: prompt original v1

- Experimento: `leonanluppi-bug_to_user_story_v1-7052b145`
- Prompt: `leonanluppi/bug_to_user_story_v1`
- Provider / modelo / juiz: `google` / `gemini-3.5-flash-lite` / `gemini-3.5-flash`
- Data: 2026-11-15 14:41 UTC
- Exemplos: 15

| Métrica | Média | ≥ 0.8 |
|---|---|---|
| helpfulness | 0.9943 | ✓ |
| correctness | 0.9342 | ✓ |
| f1_score | 0.8771 | ✓ |
| clarity | 0.9973 | ✓ |
| precision | 0.9913 | ✓ |
| **média geral** | **0.9589** | ✓ |

**Status: ✅ APROVADO**

## Por exemplo

| # | Relato (início) | F1 | Clarity | Precision |
|---|---|---|---|---|
| 1 | App de produtividade offline-first com bugs críticos de sincronização. | 0.67 | 1.00 | 1.00 |
| 2 | Sistema de relatórios gerenciais com problemas severos de performance  | 0.79 | 1.00 | 1.00 |
| 3 | Sistema de checkout com múltiplas falhas críticas. | 0.89 | 1.00 | 1.00 |
| 4 | Modal de confirmação de exclusão aparece atrás do menu lateral em tela | 0.71 | 1.00 | 1.00 |
| 5 | Carrinho permite finalizar compra mesmo com produto fora de estoque. | 0.86 | 1.00 | 1.00 |
| 6 | App Android trava ao carregar lista de notificações com mais de 50 ite | 0.87 | 0.98 | 0.98 |
| 7 | Pipeline de vendas calcula valor total errado quando há desconto. | 0.92 | 1.00 | 1.00 |
| 8 | Endpoint /api/users/:id retorna dados de qualquer usuário sem validar  | 0.89 | 0.98 | 0.98 |
| 9 | Relatório de vendas demora mais de 2 minutos para gerar quando filtro  | 0.82 | 1.00 | 0.98 |
| 10 | Webhook de pagamento aprovado não está sendo chamado. | 0.90 | 1.00 | 1.00 |
| 11 | Imagens de produtos não aparecem no Safari. No Chrome funciona normal. | 0.97 | 1.00 | 0.98 |
| 12 | Dashboard mostra contagem errada de usuários ativos. Mostra 50 mas só  | 1.00 | 1.00 | 1.00 |
| 13 | No iOS, ao girar o celular para landscape, o layout da tela de perfil  | 1.00 | 1.00 | 1.00 |
| 14 | Campo de email aceita texto sem @, permitindo cadastros inválidos. | 0.87 | 1.00 | 0.95 |
| 15 | Botão de adicionar ao carrinho não funciona no produto ID 1234. | 1.00 | 1.00 | 1.00 |

## Traces detalhados (entrada, saída e justificativa do juiz)

### 1. App de produtividade offline-first com bugs críticos de sincronização.

<details><summary>Relato completo</summary>

```text
App de produtividade offline-first com bugs críticos de sincronização.

CONTEXTO:
App mobile (iOS + Android) que funciona offline e sincroniza quando tem internet.
Usuários: vendedores em campo, muitas vezes sem conexão.

PROBLEMAS REPORTADOS:

1. CONFLITO DE DADOS - Merge incorreto causa perda de dados:

   Cenário:
   - Usuário A (offline) edita tarefa #123: "Ligar para cliente X às 14h"
   - Usuário B (offline) edita mesma tarefa: "Ligar para cliente X às 15h (reagendado)"
   - Ambos sincronizam
   - Sistema aplica "last write wins" → dados do usuário A perdidos
   - Usuário A não sabe que seu agendamento foi sobrescrito

   Impacto: 30+ casos de compromissos perdidos na última semana

2. SINCRONIZAÇÃO - Upload infinito de anexos grandes:

   Cenário:
   - Usuário anexa PDF de 50MB em uma tarefa
   - Inicia upload via 4G
   - Conexão cai no meio (sinal fraco)
   - App reinicia upload do zero (não retoma)
   - Após 5 tentativas, desiste mas não avisa o usuário
   - Tarefa fica "sincronizada" mas sem anexo

   Logs:
   ```
   [SYNC] Uploading attachment.pdf (50MB)... 40% complete
   [NETWORK] Connection lost
   [SYNC] Retry 1/5 - Restarting from 0%
   [SYNC] Uploading attachment.pdf (50MB)... 35% complete
   [NETWORK] Connection lost
   [SYNC] Retry 2/5 - Restarting from 0%
   ...
   [SYNC] Max retries exceeded. Giving up.
   [ERROR] Upload failed but status marked as synced
   ```

3. ORDENAÇÃO - Operações aplicadas fora de ordem no servidor:

   Cenário offline (usuário sem internet por 2 horas):
   - 10:00 - Cria tarefa "Tarefa A"
   - 10:15 - Edita "Tarefa A" → "Tarefa A - Urgente"
   - 10:30 - Deleta "Tarefa A"

   Ao sincronizar:
   - Servidor recebe DELETE antes do CREATE (ordem errada)
   - Tenta deletar tarefa que não existe → erro 404
   - CREATE e UPDATE são aplicados depois
   - Resultado: tarefa existe (deveria estar deletada)
   - Timestamp client-side não é respeitado

4. MEMÓRIA - App crasha ao sincronizar 1000+ itens pendentes:

   Cenário:
   - Usuário fica 1 semana offline
   - Acumula 1.500 operações pendentes (create, update, delete)
   - Volta para área com WiFi
   - App tenta sincronizar tudo de uma vez
   - Carrega todos os 1.500 itens na memória
   - iOS: Memory Warning → App crashado pelo OS
   - Android: OutOfMemoryError

   Memória medida: 850MB (limite iOS: 700MB)

IMPACTO:
- 250+ usuários afetados
- NPS caiu de 8.5 para 4.2
- 80% dos reviews negativos mencionam "perda de dados"
- Churn rate aumentou 15% no último mês
- Time de vendas perdeu R$ 200k em oportunidades por dados perdidos
```
</details>

**Saída do prompt:**

```text
Com base no relato de bug fornecido, dividi a demanda em user stories estruturadas para o time de desenvolvimento (uma história principal para o motor de sincronização, ou histórias separadas para cada problema crítico). Abaixo está o formato padrão de User Story para atender a essa demanda:

---

### **User Story Principal: Estabilização e Resiliência do Motor de Sincronização Offline-First**

**Como** vendedor em campo que utiliza o aplicativo sem conexão com a internet,
**Eu quero** que minhas edições, anexos e operações sejam sincronizados de forma segura, ordenada e eficiente quando eu recuperar o sinal,
**Para que** eu não perca dados importantes, compromissos ou sofra com falhas e travamentos (crashes) no aplicativo.

---

### **Critérios de Aceitação (Definition of Done):**

#### **1. Resolução de Conflitos (Merge de Dados)**
- [ ] O sistema não deve mais aplicar cegamente a regra de *Last Write Wins* (última escrita vence) para sobrescrever dados em conflito.
- [ ] Quando houver edição concorrente do mesmo registro por usuários diferentes offline, o sistema deve detectar o conflito e implementar uma estratégia de notificação ao usuário ou merge inteligente (ex: histórico de versões ou alerta visual de conflito para escolha manual).

#### **2. Resiliência no Upload de Anexos**
- [ ] O mecanismo de upload de arquivos grandes (ex: PDFs de até 50MB) deve suportar retomada de ponto de parada (*resumable uploads*), em vez de reiniciar do 0% após uma queda de conexão.
- [ ] Caso o upload falhe após esgotar o limite de tentativas, a tarefa **não** deve ser marcada como "sincronizada".
- [ ] O usuário deve receber uma notificação/alerta clara informando que o anexo falhou ao enviar e tendo a opção de tentar novamente.

#### **3. Ordenação Cronológica de Operações**
- [ ] As operações realizadas offline (Criação, Edição, Deleção) devem ser enviadas e processadas pelo servidor estritamente respeitando os timestamps (ordem cronológica) gerados no cliente.
- [ ] O servidor deve processar a fila de eventos na ordem correta (ex: Garantir que um DELETE não seja processado antes de um CREATE), evitando erros 404 e estados inconsistências de dados fantasmas.

#### **4. Otimização de Memória e Sincronização em Lotes (Batching)**
- [ ] O app deve implementar sincronização baseada em paginação ou lotes (*batch processing*) quando houver um grande volume de itens pendentes (ex: 1.000+ operações acumuladas).
- [ ] O consumo de memória durante a sincronização em massa deve ser estritamente controlado para ficar abaixo do limite crítico do iOS (700MB) e Android, evitando estouros de memória (`OutOfMemoryError` / `Memory Warning`) e *crashes* do aplicativo.

---

### **Prioridade:** 
🚨 **Crítica (Blocker)** — Impacto financeiro direto, queda severa de NPS e risco de churn.
```

- **f1_score = 0.67**: A resposta gerada é 100% precisa e relevante, estruturando corretamente a User Story Principal e os Critérios de Aceitação funcionais para os 4 problemas relatados. No entanto, o Recall é moderado (0.50) pois a resposta omitiu detalhes técnicos específicos presentes no Ground Truth (como uso de CRDTs, chunks de 5MB, tamanho de lote de 50 itens, limites exatos de memória), além de não incluir as Tasks Técnicas divididas em fases e as Métricas de Sucesso.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está perfeitamente organizada na estrutura padrão de User Story e Critérios de Aceitação. A linguagem é direta, profissional e fácil de entender, utilizando terminologia técnica adequada ao contexto de desenvolvimento sem rodeios. Não há ambiguidades nos critérios apresentados, cobrindo com precisão os 4 problemas do contexto. Além disso, é extremamente concisa e objetiva, evitando redundâncias.
- **precision = 1.00**: A resposta gerada é extremamente precisa, sem alucinações e totalmente alinhada ao contexto fornecido. Ela atende diretamente à solicitação de criar user stories estruturadas com critérios de aceitação para os 4 problemas críticos relados (conflitos, upload resumável de 50MB, ordenação por timestamp e batching para controle de memória de 700MB). Todas as afirmações técnicas e de negócio são corretas e fiéis ao enunciado.

### 2. Sistema de relatórios gerenciais com problemas severos de performance e dados incorretos.

<details><summary>Relato completo</summary>

```text
Sistema de relatórios gerenciais com problemas severos de performance e dados incorretos.

CONTEXTO:
Aplicação SaaS B2B com 500+ empresas clientes, cada uma com 50-5000 usuários.

PROBLEMAS:

1. PERFORMANCE - Query N+1 no dashboard executivo:
   - Endpoint: GET /api/reports/executive-dashboard
   - Para cada empresa, faz query separada para buscar métricas
   - 1 cliente com 100 departamentos = 101 queries
   - Tempo de resposta: 45 segundos (SLA: 3s)
   - Database CPU: 95% em horário de pico

   Stack trace:
   ```
   SELECT * FROM metrics WHERE company_id = ?  (executado 100x)
   SELECT * FROM users WHERE company_id = ?     (executado 100x)
   SELECT * FROM licenses WHERE company_id = ?  (executado 100x)
   ```

2. LÓGICA DE NEGÓCIO - Cálculo de MRR (Monthly Recurring Revenue) inconsistente:
   - Dashboard mostra: R$ 150.000 MRR
   - Relatório financeiro: R$ 145.000 MRR
   - Planilha contábil: R$ 147.500 MRR

   Causas identificadas:
   - Dashboard: considera cancelamentos do mês anterior
   - Relatório: só considera assinaturas ativas
   - Contábil: considera pró-rata de upgrades/downgrades
   - Nenhuma fonte está 100% correta

3. CACHE - Cache Redis desatualizado causa dados old:
   - TTL do cache: 24 horas
   - Cliente faz upgrade de plano
   - Dashboard ainda mostra plano antigo por até 24h
   - Invalidação manual não funciona corretamente

4. CONCORRÊNCIA - Exportação de CSV trava servidor:
   - Exportar relatório anual (365 dias, 50k linhas)
   - Process fica em 100% CPU por 5 minutos
   - Outras requisições ficam lentas
   - Memória cresce até 4GB (limite: 2GB) → OOM Kill

IMPACTO BUSINESS:
- 15 clientes enterprise ameaçando cancelar contrato
- CEO não confia nos números para apresentar ao board
- Time de CS gastando 40h/semana explicando discrepâncias
- Impossível fazer forecasting confiável
```
</details>

**Saída do prompt:**

```text
Com base no relato de problema fornecido, dividi a demanda em subtarefas estruturadas como User Stories para facilitar o planejamento do time de desenvolvimento, priorizando a estabilidade do sistema e a precisão dos dados.

---

### **User Story Principal (Epic): Otimização, Correção e Estabilização do Sistema de Relatórios Gerenciais**

**Como** usuário executivo/gestor de uma empresa cliente,
**Eu quero** acessar o dashboard executivo e os relatórios financeiros de forma rápida, com dados unificados e precisos,
**Para que** eu possa tomar decisões estratégicas confiáveis sem enfrentar lentidão ou quedas no sistema.

---

### **Sub-tarefas (User Stories Técnicas):**

#### **US 01: Otimização de Performance do Dashboard Executivo (Resolver N+1)**
* **Como** usuário da aplicação,
* **Eu quero** que o endpoint `GET /api/reports/executive-dashboard` carregue em menos de 3 segundos,
* **Para que** eu possa visualizar os dados da minha empresa sem timeout ou lentidão.
* **Critérios de Aceite:**
  * [ ] Eliminar o problema de Query N+1 no endpoint `GET /api/reports/executive-dashboard`.
  * [ ] Utilizar *joins*, *eager loading* ou consultas agregadas para buscar métricas, usuários e licenças em lote.
  * [ ] O tempo de resposta da API deve atender ao SLA de **até 3 segundos** (atualmente em 45s).
  * [ ] O uso de CPU do banco de dados deve cair significativamente abaixo dos 95% atuais em horário de pico.

#### **US 02: Padronização e Correção do Cálculo de MRR**
* **Como** CEO / Gestor Financeiro,
* **Eu quero** que o cálculo de MRR (Monthly Recurring Revenue) seja consistente em todas as telas (Dashboard, Relatório Financeiro e Exportações),
* **Para que** eu possa confiar nos números para análises e apresentações ao board.
* **Critérios de Aceite:**
  * [ ] Definir e documentar a regra de negócio oficial para o cálculo de MRR (ex: consideração correta de assinaturas ativas, cancelamentos do mês vigente e pró-rata de upgrades/downgrades).
  * [ ] Atualizar o código do Dashboard, Relatórios e rotinas contábeis para utilizarem a mesma fonte de verdade (mesmo método/serviço de cálculo).
  * [ ] Garantir que não haja divergências de valores entre as diferentes visões do sistema.

#### **US 03: Estratégia de Cache e Invalidação Eficiente no Redis**
* **Como** usuário que realizou um upgrade/mudança de plano,
* **Eu quero** ver os dados atualizados imediatamente no dashboard,
* **Para que** eu não fique preso a informações desatualizadas devido ao cache.
* **Critérios de Aceite:**
  * [ ] Reduzir ou ajustar o TTL (Time-To-Live) do cache Redis para dados sensíveis.
  * [ ] Implementar um mecanismo robusto de invalidação automática de cache disparado sempre que ocorrer um evento de alteração de plano ou dados críticos (ex: upgrades).
  * [ ] Garantir que a invalidação manual via painel/sistema funcione corretamente.

#### **US 04: Processamento Assíncrono para Exportação de Relatórios CSV**
* **Como** usuário que precisa exportar grandes volumes de dados (ex: relatório anual com 50k linhas),
* **Eu quero** que a exportação ocorra em segundo plano (background job),
* **Para que** o servidor não sofra com picos de CPU, consumo excessivo de memória (OOM Kill) e travamentos para outros usuários.
* **Critérios de Aceite:**
  * [ ] Migrar a geração de relatórios grandes em CSV para uma fila de processamento assíncrono (ex: Background Jobs / Workers).
  * [ ] O usuário deve receber uma notificação ou link para download assim que o arquivo estiver pronto, evitando prender a conexão HTTP.
  * [ ] O consumo de memória do servidor não deve ultrapassar o limite de 2GB, eliminando os erros de *OOM Kill*.
```

- **f1_score = 0.79**: A resposta gerada possui precisão máxima (1.0), pois todas as User Stories e critérios estruturados são extremamente corretos, relevantes e sem alucinações. O recall ficou em 0.65 porque, embora cubra muito bem os quatro problemas principais (Performance N+1, Cálculo MRR, Cache Redis e Exportação Assíncrona), a resposta omitiu elementos detalhados presentes no Ground Truth, como o exemplo de query SQL otimizada, o detalhamento das regras técnicas de cache por camada, o resumo de contexto/SLA e o plano de tasks dividido por Sprints.
- **clarity = 1.00**: A resposta é extremamente clara, bem organizada e utiliza a estrutura padronizada de User Stories com critérios de aceite bem definidos. A linguagem é direta, objetiva e adequada para times de tecnologia e produto, eliminando ambiguidades sobre os requisitos necessários. Além disso, o texto é conciso e aborda todos os quatro problemas apresentados de forma eficiente e sem redundâncias.
- **precision = 1.00**: A resposta do modelo é altamente precisa, factual e totalmente alinhada ao contexto fornecido. Não há alucinações; todas as informações e métricas citadas (SLA de 3s, endpoint, OOM Kill com limite de 2GB, MRR) são fiéis ao problema descrito. As soluções propostas nas User Stories (eager loading para N+1, centralização de regra para MRR, invalidação por eventos no Redis e background jobs para CSV) correspondem com exatidão às boas práticas e à resposta de referência.

### 3. Sistema de checkout com múltiplas falhas críticas.

<details><summary>Relato completo</summary>

```text
Sistema de checkout com múltiplas falhas críticas.

PROBLEMAS IDENTIFICADOS:

1. SEGURANÇA - XSS no campo de cupom:
   - Input: <script>alert('xss')</script>
   - Sistema executa o script
   - Não há sanitização de entrada

2. INTEGRAÇÃO - Gateway de pagamento retorna erro intermitente:
   - POST /api/payment/process retorna 504 Gateway Timeout em 30% dos casos
   - Clientes são cobrados mas pedido não é criado
   - Logs: "Connection pool exhausted" no Postgres

3. LÓGICA DE NEGÓCIO - Race condition em cupons de desconto:
   - Cupom "PROMO10" (limite: 100 usos)
   - Sistema permitiu 147 usos
   - Verificação de limite não é atômica

4. UX - Loading infinito após timeout:
   - Se pagamento demora > 30s
   - Tela fica com spinner eternamente
   - Usuário não sabe se pagamento foi processado

IMPACTO:
- 150+ clientes afetados na última semana
- Perda estimada: R$ 15.000 em cupons indevidos
- 45 tickets de suporte abertos
- Rating do app caiu de 4.5 para 3.2 estrelas
```
</details>

**Saída do prompt:**

```text
Com base no relato de bug fornecido, dividi as correções em User Stories específicas para garantir que cada problema crítico seja tratado adequadamente pelos desenvolvedores. 

Aqui estão as User Stories estruturadas:

---

### User Story 1: Sanitização de entrada no campo de cupom (Segurança)

**Título:** Prevenir vulnerabilidade XSS no campo de inserção de cupom de desconto.

**História do Usuário:**
* **Como** sistema de e-commerce,
* **Quero** sanitizar e escapar todas as entradas de dados no campo de cupom de desconto,
* **Para que** scripts maliciosos (XSS) não sejam executados, garantindo a segurança dos usuários.

**Critérios de Aceitação:**
* [ ] O campo de cupom deve rejeitar ou sanitizar caracteres especiais HTML/JS (ex: `<script>`).
* [ ] Inserir um payload XSS (ex: `<script>alert('xss')</script>`) deve resultar apenas em texto plano ou mensagem de "Cupom inválido", sem executar nenhum script no navegador.

---

### User Story 2: Tratamento de timeout e falhas no Gateway de Pagamento (Integração & Resiliência)

**Título:** Corrigir erros de timeout (504) e esgotamento de conexões no processamento de pagamentos.

**História do Usuário:**
* **Como** cliente realizando uma compra,
* **Quero** que o sistema trate corretamente os timeouts da API de pagamento e gerencie as conexões com o banco de dados,
* **Para que** eu não seja cobrado indevidamente sem que o meu pedido seja criado.

**Critérios de Aceitação:**
* [ ] Otimizar o gerenciamento de conexões (`Connection pool`) com o PostgreSQL para evitar o erro "Connection pool exhausted".
* [ ] Implementar transações atômicas ou mecanismos de compensação/idempotência para garantir que cobranças no gateway só ocorram se o pedido for criado com sucesso (ou estorno automático em caso de falha na criação do pedido).
* [ ] Reduzir a taxa de erros 504 no endpoint `POST /api/payment/process`.

---

### User Story 3: Correção de Race Condition no uso de cupons (Lógica de Negócio)

**Título:** Garantir controle atômico do limite de uso de cupons de desconto.

**História do Usuário:**
* **Como** administrador da plataforma,
* **Quero** que a contagem de uso de cupons seja feita de forma atômica,
* **Para que** o limite máximo de utilizações (ex: 100 usos) não seja ultrapassado mesmo em compras simultâneas.

**Critérios de Aceitação:**
* [ ] A validação e o incremento do contador de uso do cupom devem utilizar transações de banco de dados isoladas (ex: `SELECT ... FOR UPDATE` ou operações atômicas equivalentes).
* [ ] O sistema deve impedir estritamente que o cupom seja aplicado após atingir o limite estipulado, eliminando a *race condition*.

---

### User Story 4: Tratamento de UX para timeouts de pagamento (Experiência do Usuário)

**Título:** Remover loading infinito e informar o usuário em caso de timeout no pagamento.

**História do Usuário:**
* **Como** cliente final,
* **Quero** receber um feedback claro caso o processamento do pagamento demore mais de 30 segundos,
* **Para que** eu não fique preso em uma tela de carregamento infinito e saiba o status real da minha compra.

**Critérios de Aceitação:**
* [ ] Se a requisição de pagamento ultrapassar 30 segundos, o *spinner* de loading deve parar.
* [ ] O sistema deve exibir uma mensagem amigável informando sobre a lentidão/timeout e orientando o usuário a verificar o status do pedido (ou consultar o histórico) antes de tentar novamente, evitando dupla cobrança.
```

- **f1_score = 0.89**: A resposta gerada é extremamente precisa, relevante e sem alucinações, abordando corretamente os 4 problemas críticos identificados. A precisão é 1.0. O recall é 0.8 pois, embora o modelo tenha coberto perfeitamente os critérios de aceitação e soluções técnicas principais (como SELECT FOR UPDATE e pool do Postgres) dividindo em 4 User Stories, omitiu seções explícitas do gabarito como a lista dedicada de Tasks Técnicas, o resumo do Contexto/Impacto (métricas de perdas/tickets) e alguns detalhes de infraestrutura/monitoramento (Circuit Breaker, Redis, alertas).
- **clarity = 1.00**: A resposta gerada possui excelente clareza. Está perfeitamente organizada em 4 User Stories bem delimitadas, utilizando o padrão ágil (Como/Quero/Para) e critérios de aceitação objetivos em Markdown. A linguagem é direta, profissional e livre de ambiguidades, permitindo a compreensão imediata das ações necessárias para cada bug. Além disso, a resposta é concisa, focando no que é essencial sem inclusão de informações redundantes.
- **precision = 1.00**: A resposta gerada tratou com extrema precisão todos os 4 problemas relatados (XSS, Connection Pool/504, Race Condition e UX Timeout). As soluções técnicas propostas nos critérios de aceitação (sanitização de HTML/JS, ajuste de pool de conexões, transações atômicas com `SELECT ... FOR UPDATE` e encerramento do spinner em 30s) estão factualmente corretas e totalmente baseadas no contexto fornecido, sem qualquer alucinação ou fuga do tema. Embora a formatação seja em 4 User Stories separadas, o conteúdo é completo e preciso.

### 4. Modal de confirmação de exclusão aparece atrás do menu lateral em telas pequenas (< 768px)

<details><summary>Relato completo</summary>

```text
Modal de confirmação de exclusão aparece atrás do menu lateral em telas pequenas (< 768px).

Detalhes:
- z-index do modal: 1000
- z-index do menu lateral: 1050
- Usuários não conseguem clicar nos botões do modal
- Precisam fechar o menu lateral antes
```
</details>

**Saída do prompt:**

```text
**Título:** Ajustar o z-index do modal de confirmação de exclusão em telas pequenas para evitar sobreposição do menu lateral

**User Story:**

**Como** usuário acessando o sistema em dispositivos móveis ou telas pequenas (< 768px),  
**Quero** que o modal de confirmação de exclusão seja exibido na camada superior ao menu lateral,  
**Para que** eu possa interagir com os botões do modal sem precisar fechar o menu lateral manualmente.

---

**Critérios de Aceitação:**
1. Em telas com largura menor que 768px, quando o menu lateral e o modal de confirmação de exclusão estiverem abertos simultaneamente, o modal deve aparecer visível e acessível acima do menu lateral.
2. O valor do `z-index` do modal de confirmação deve ser atualizado para ser superior ao do menu lateral (que atualmente é 1050), garantindo que os botões de ação do modal fiquem clicáveis.
3. O comportamento deve ser testado e validado em diferentes resoluções menores que 768px (ex: smartphones e tablets em modo retrato).
```

- **f1_score = 0.71**: A resposta gerada possui precisão máxima (1.0), pois todas as informações apresentadas são corretas, bem estruturadas e diretamente alinhadas ao problema. Contudo, o recall é moderado (0.55) devido à omissão completa da seção de 'Critérios de Acessibilidade' (foco de teclado, tecla ESC, fechar no backdrop) e de alguns critérios de aceitação específicos da resposta esperada (como a largura mínima de 90% do modal e o desfoque do backdrop).
- **clarity = 1.00**: A resposta gerada possui excelente clareza. Está perfeitamente organizada na estrutura padrão de User Story e Critérios de Aceitação. A linguagem é direta, objetiva e fácil de compreender por qualquer membro da equipe. Não há ambiguidades nas instruções de correção do z-index e os critérios cobrem com precisão o problema relatado. Além disso, a resposta é concisa, sem redundâncias ou prolixidade.
- **precision = 1.00**: A resposta gerada é extremamente precisa e bem estruturada. Não contém alucinações, pois todas as informações apresentadas derivam diretamente do problema relatado (z-index 1000 vs 1050 e telas < 768px). Mantém foco total no problema de sobreposição do modal e apresenta soluções e critérios factualmente corretos e alinhados à boa prática de desenvolvimento de software.

### 5. Carrinho permite finalizar compra mesmo com produto fora de estoque.

<details><summary>Relato completo</summary>

```text
Carrinho permite finalizar compra mesmo com produto fora de estoque.

Fluxo do bug:
1. Produto tem 2 unidades em estoque
2. Cliente A adiciona 2 unidades ao carrinho
3. Estoque fica zerado
4. Cliente B ainda consegue adicionar ao carrinho
5. Cliente B finaliza compra
6. Sistema gera pedido mas não tem estoque para enviar
```
</details>

**Saída do prompt:**

```text
**Título:** Validação de estoque no carrinho e no checkout para evitar vendas sem estoque

**User Story:**

**Como** gerente de e-commerce / cliente do sistema,
**Quero** que o sistema valide a disponibilidade de estoque em tempo real (ao adicionar um item ao carrinho e, principalmente, no momento de finalizar a compra),
**Para que** não sejam gerados pedidos de produtos esgotados, evitando frustração do cliente e problemas logísticos.

---

**Critérios de Aceitação:**

1. **Validação ao Adicionar ao Carrinho:** O sistema não deve permitir que um usuário adicione uma quantidade de itens ao carrinho superior à quantidade disponível em estoque naquele momento.
2. **Validação no Checkout (Finalização):** No momento em que o usuário clica em "Finalizar Compra", o sistema deve fazer uma verificação final do estoque de cada item no carrinho.
3. **Tratamento de Concorrência (Estoque Esgotado):** Se o estoque de um item esgotar durante o processo de compra de outro usuário (ex: Cliente A comprou as últimas unidades enquanto o Cliente B estava no checkout), o sistema deve:
   * Bloquear a finalização do pedido.
   * Exibir uma mensagem clara informando qual produto ficou sem estoque.
   * Atualizar o carrinho do usuário para refletir a indisponibilidade, permitindo que ele remova ou ajuste a quantidade antes de tentar novamente.
```

- **f1_score = 0.86**: A resposta gerada é totalmente correta e relevante (Precision 1.0), cobrindo muito bem a User Story e os Critérios de Aceitação principais, como validação em tempo real no checkout, bloqueio de pedido sem estoque, mensagem clara e atualização do carrinho. Contudo, o Recall foi 0.75 pois omitiu os 'Critérios de Prevenção' específicos previstos no Ground Truth (aviso de 'estoque limitado' e reserva temporária de 15 minutos no checkout).
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. A estrutura é impecável, organizada em formato padrão de User Story e Critérios de Aceitação numerados. A linguagem é simples, direta e profissional, tornando a leitura fluida. Não há ambiguidades: as ações do sistema (validação no carrinho, checkout e tratamento de concorrência) estão explicitadas com total precisão. Além disso, o texto é conciso e focado exatamente no problema relatado, sem informações redundantes.
- **precision = 1.00**: A resposta do modelo é altamente precisa, focada e totalmente isenta de alucinações. Aborda diretamente o problema de venda sem estoque relatado no bug. A User Story e os Critérios de Aceitação propostos cobrem com exatidão as soluções necessárias presentes no gabarito, como validação em tempo real no checkout, bloqueio de compra, exibição de mensagem clara e tratamento do cenário de concorrência entre múltiplos usuários.

### 6. App Android trava ao carregar lista de notificações com mais de 50 itens.

<details><summary>Relato completo</summary>

```text
App Android trava ao carregar lista de notificações com mais de 50 itens.

Observações:
- Tela fica congelada por 5-10 segundos
- ANR (Application Not Responding) em alguns casos
- Lista não está usando paginação
- Carrega tudo de uma vez na Thread principal
```
</details>

**Saída do prompt:**

```text
**Título:** Implementar paginação e carregamento assíncrono na lista de notificações do Android

**User Story:**
Como usuário do aplicativo Android,
Eu quero que a lista de notificações seja carregada de forma fluida e paginada,
Para que o aplicativo não trabue (ANR) ou congele ao acessar o histórico com mais de 50 itens.

**Critérios de Aceite:**
1. A lista de notificações não deve mais carregar todos os itens de uma só vez na Thread principal (Main Thread).
2. O carregamento dos dados deve ser movido para uma Thread em segundo plano (Background Thread / Coroutines).
3. Deve ser implementada a paginação (ex: carregamento infinito ou paginação por páginas/lotes) na listagem de notificações.
4. A interface (UI) não deve apresentar congelamentos (trava de 5 a 10 segundos) ou erros de ANR (Application Not Responding) ao abrir a tela com um grande volume de notificações.
```

- **f1_score = 0.87**: Precisão alta (0.95): O modelo gerou informações corretas e altamente relevantes para a solução do bug, sem dados inventados (apenas um pequeno erro de digitação 'trabue'). Recall (0.80): O modelo cobriu bem os conceitos principais (User Story, paginação, thread em segundo plano e eliminação de ANR), mas omitiu detalhes técnicos específicos da resposta esperada, como o limite de tempo (< 2s), a meta exata de 20 itens por página e o uso explícito do padrão RecyclerView com ViewHolder.
- **clarity = 0.98**: A resposta gerada é extremamente clara e bem estruturada no formato padrão de User Story e Critérios de Aceite. A organização é perfeita e facilita a leitura. A linguagem é direta e fácil de entender, apresentando apenas um pequeno erro de digitação na palavra 'trabue'. Não há ambiguidades nas instruções de correção e o texto é conciso, indo direto ao ponto sem informações desnecessárias.
- **precision = 0.98**: A resposta gerada é altamente precisa, sem alucinações e focada no problema relatado. Ela identifica corretamente as causas do ANR (carregamento na Main Thread e ausência de paginação) e propõe as soluções adequadas (background thread/coroutines e paginação), perfeitamente alinhada com o Ground Truth. Houve apenas um pequeno erro de digitação na User Story ('trabue' em vez de 'trave'), mas isso não compromete a exatidão técnica do conteúdo.

### 7. Pipeline de vendas calcula valor total errado quando há desconto.

<details><summary>Relato completo</summary>

```text
Pipeline de vendas calcula valor total errado quando há desconto.

Cenário:
- Produto A: R$ 1.000
- Produto B: R$ 500
- Desconto: 10%
- Valor esperado: R$ 1.350
- Valor mostrado: R$ 1.400

O sistema aplica desconto só no primeiro produto.
```
</details>

**Saída do prompt:**

```text
**Título:** Corrigir cálculo do valor total no Pipeline de Vendas ao aplicar desconto

**User Story:**
**Como** usuário do sistema de vendas,
**Quero** que o desconto seja aplicado sobre o valor total da pipeline (ou proporcionalmente a todos os produtos),
**Para que** o valor final calculado reflita corretamente a regra de negócio e não haja cobrança indevida.

---

**Critérios de Aceitação:**
1. **Dado** que tenho uma pipeline de vendas com múltiplos produtos (ex: Produto A por R$ 1.000 e Produto B por R$ 500),
   **Quando** eu aplicar um desconto percentual (ex: 10%),
   **Então** o sistema deve calcular o valor total considerando o desconto aplicado a todos os itens.
2. **Dado** o cenário de teste com Produto A (R$ 1.000) e Produto B (R$ 500) e 10% de desconto,
   **Quando** o valor total for exibido na tela,
   **Então** o valor mostrado deve ser exatamente **R$ 1.350** (e não R$ 1.400).
3. O sistema não deve restringir a aplicação do desconto apenas ao primeiro produto da lista.
```

- **f1_score = 0.92**: A precisão é 1.0 pois todo o conteúdo gerado é correto, altamente relevante e bem formatado no padrão de User Story/BDD. O recall é 0.85 porque a resposta cobriu a história do usuário, o contexto do bug e o exemplo numérico (R$ 1.350), mas omitiu a fórmula matemática genérica e o critério de aceitação específico exigindo a exibição detalhada (subtotal, desconto e total).
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está perfeitamente organizada na estrutura padrão de User Story e BDD (Dado/Quando/Então). A linguagem é simples, direta e acessível. Não há ambiguidades, pois inclui dados concretos do cenário de teste para ilustrar o resultado esperado (R$ 1.350). Além disso, é extremamente concisa e objetiva, focando na correção do bug sem nenhuma informação desnecessária.
- **precision = 1.00**: A resposta gerada é extremamente precisa e bem estruturada em formato de User Story e Critérios de Aceitação. Não apresenta alucinações, mantém o foco total no problema relatado e reflete com exatidão os fatos e cálculos descritos no cenário de entrada e no gabarito (Produto A R$ 1.000 + Produto B R$ 500 com 10% de desconto resultando em R$ 1.350).

### 8. Endpoint /api/users/:id retorna dados de qualquer usuário sem validar permissões.

<details><summary>Relato completo</summary>

```text
Endpoint /api/users/:id retorna dados de qualquer usuário sem validar permissões.

Exemplo:
- Usuário comum (ID 100) consegue acessar GET /api/users/1 (admin)
- Recebe email, telefone, endereço do admin
- Apenas admins deveriam ver dados de outros usuários

Severidade: ALTA - vazamento de dados pessoais
```
</details>

**Saída do prompt:**

```text
**Título:** Correção de falha de autorização no endpoint de consulta de usuários (`GET /api/users/:id`)

**User Story:**

**Como** administrador do sistema,  
**Quero** que o endpoint `GET /api/users/:id` valide se o usuário autenticado possui permissões de administrador,  
**Para que** usuários comuns não tenham acesso a dados pessoais e confidenciais (como email, telefone e endereço) de outros usuários.

---

**Critérios de Aceitação:**

1. **Validação de Papel (Role):** 
   - O endpoint `GET /api/users/:id` deve verificar se o usuário que está fazendo a requisição possui a role de `admin`.
   - *Exceção:* Um usuário comum deve ter permissão apenas para acessar os seus próprios dados (caso aplicável pela regra de negócio, ou seja, se ID do token for igual ao ID da rota).

2. **Tratamento de Acesso Negado:**
   - Se um usuário comum tentar acessar os dados de outro usuário, o sistema deve retornar o status HTTP `403 Forbidden`.

3. **Proteção de Dados Sensíveis:**
   - Garantir que dados sensíveis (email, telefone, endereço) não sejam expostos indevidamente em nenhuma circunstância para usuários não autorizados.

4. **Testes Automatizados:**
   - Adicionar testes unitários/integração validando que um usuário com perfil `USER` receba `403` ao tentar consultar o perfil de outro usuário.
   - Validar que um usuário com perfil `ADMIN` consiga acessar o endpoint com sucesso.
```

- **f1_score = 0.89**: A precisão é 1.0 pois todas as informações geradas são corretas, coerentes e relevantes para a solução da falha. O recall é 0.8 porque a resposta cobriu com precisão a User Story e os principais critérios de aceitação (status 403, acesso a dados próprios e permissões de admin), mas omitiu o registro em log de auditoria para ações de administradores e menções explícitas ao contexto OWASP A01:2021 e middleware.
- **clarity = 0.98**: A resposta apresenta excelente clareza. Está muito bem organizada com estrutura lógica clara (Título, User Story e Critérios de Aceitação), utiliza linguagem simples, precisa e acessível, e é livre de ambiguidades ao definir comportamentos esperados (como retornos HTTP e regras de papel). É altamente concisa, cobrindo todos os pontos necessários sem rodeios.
- **precision = 0.98**: A resposta é altamente precisa, sem alucinações e totalmente focada na resolução da falha reportada. Estrutura corretamente a User Story e os critérios de aceitação em perfeita consonância com a referência, cobrindo validação de perfil (roles), retorno do status HTTP 403 e controle de acesso aos próprios dados. Há apenas pequenas divergências de formato (a referência utiliza o padrão Dado/Quando/Então) e a omissão de detalhes secundários como log de auditoria e classificação OWASP, sem comprometer a exatidão técnica.

### 9. Relatório de vendas demora mais de 2 minutos para gerar quando filtro ultrapassa 1000 regi

<details><summary>Relato completo</summary>

```text
Relatório de vendas demora mais de 2 minutos para gerar quando filtro ultrapassa 1000 registros.

Detalhes:
- Query SQL está sem index na coluna data_venda
- Timeout do navegador após 120 segundos
- Usuários reclamando de lentidão no horário comercial
```
</details>

**Saída do prompt:**

```text
**Título:** Otimização da geração do relatório de vendas para grandes volumes de dados

**User Story:**
Como **usuário do sistema**,
Quero **que o relatório de vendas seja gerado rapidamente (em menos de 2 minutos), mesmo ao filtrar mais de 1000 registros**,
Para que **eu possa analisar os dados no horário comercial sem sofrer com lentidão ou timeout no navegador.**

---

**Critérios de Aceite:**
1. O tempo de resposta para a geração do relatório com mais de 1000 registros deve ser significativamente reduzido (idealmente abaixo de 5 segundos).
2. O erro de timeout do navegador (após 120 segundos) não deve mais ocorrer para este relatório.

**Notas Técnicas para o Desenvolvedor:**
- Criar um índice (Index) na coluna `data_venda` na tabela correspondente do banco de dados para otimizar a query SQL utilizada na geração do relatório.
```

- **f1_score = 0.82**: Precisão (0.85): A resposta é relevante e acertou ao sugerir o índice na coluna `data_venda` e resolver o timeout. Porém, apresenta uma pequena inconsistência interna ao mencionar '< 2 minutos' na história e '< 5 segundos' nos critérios. Recall (0.80): Cobriu os pontos principais da solicitação, mas omitiu a persona específica ('gerente de vendas'), o formato BDD (Dado/Quando/Então) nos Critérios de Aceite e o teste de desempenho explícito para horários de pico.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está perfeitamente organizada em seções lógicas (Título, User Story, Critérios de Aceite e Notas Técnicas). Utiliza linguagem direta e precisa, eliminando ambiguidades ao definir metas de desempenho e a ação técnica necessária (criação do índice na coluna data_venda). É concisa, focada e responde exatamente ao problema relatado sem redundâncias.
- **precision = 0.98**: A resposta gerada é precisa, focada e livre de alucinações. Traduz o problema informado em uma User Story bem estruturada com critérios de aceite e notas técnicas. Todos os fatos apontados estão corretos em relação ao contexto (falta de índice na coluna data_venda, timeout de 120s e lentidão com 1000+ registros). A única pequena divergência em relação ao Ground Truth é a especificação da meta de tempo no critério de aceite (idealmente <5s contra <30s na resposta esperada), o que não compromete a correção factual.

### 10. Webhook de pagamento aprovado não está sendo chamado.

<details><summary>Relato completo</summary>

```text
Webhook de pagamento aprovado não está sendo chamado.

Steps to reproduce:
1. Fazer pedido de R$ 100
2. Pagar com cartão de crédito
3. Pagamento é aprovado no gateway
4. Sistema não recebe notificação
5. Status do pedido fica como "pendente"

Logs do gateway mostram: HTTP 500 ao tentar POST /api/webhooks/payment
```
</details>

**Saída do prompt:**

```text
**Título:** Corrigir erro 500 no endpoint de webhook de pagamento para atualizar status do pedido automaticamente

**User Story:**
Como **sistema de e-commerce**, 
Eu quero **processar corretamente as notificações de pagamento aprovado enviadas pelo gateway via webhook**, 
Para que **o status do pedido seja atualizado de "pendente" para "pago" automaticamente após a aprovação da compra.**

---

**Critérios de Aceitação:**
1. O endpoint `POST /api/webhooks/payment` deve processar com sucesso as requisições enviadas pelo gateway de pagamento, retornando status HTTP 2xx (ex: 200 OK ou 204 No Content).
2. O erro interno (HTTP 500) que ocorre atualmente ao receber a requisição deve ser investigado e corrigido.
3. Ao receber um webhook de pagamento aprovado, o sistema deve atualizar o status do pedido correspondente de "pendente" para "pago" (ou o status equivalente de sucesso).
4. **Dado** que um pagamento foi aprovado no gateway, **Quando** o gateway enviar a notificação para o webhook, **Então** o sistema deve registrar a transação e atualizar o pedido sem falhas.

---

**Notas Técnicas / Contexto:**
* **Endpoint afetado:** `POST /api/webhooks/payment`
* **Sintoma:** O gateway recebe um erro `HTTP 500` ao tentar entregar a notificação, impedindo a mudança de status do pedido. Verificar os logs da aplicação para identificar a exceção exata no momento do POST.
```

- **f1_score = 0.90**: A resposta gerada é extremamente precisa, relevante e bem estruturada segundo boas práticas de engenharia de software, sem conter informações incorretas. O Recall foi de 0.85 pois o modelo abordou quase todos os pontos da resposta esperada (User Story, retorno HTTP 200, atualização de status e logs), mas omitiu um critério de aceitação importante: o envio do e-mail de confirmação para o cliente.
- **clarity = 1.00**: A resposta apresenta excelente clareza. Está estruturada de forma altamente organizada no padrão formal de User Story (Organização: 1.0), utiliza linguagem técnica direta e compreensível (Linguagem: 1.0), descreve o problema e os critérios de aceite sem margem para dúvidas (Ausência de Ambiguidade: 1.0) e é objetiva, contendo apenas as informações necessárias para a resolução do problema (Concisão: 1.0).
- **precision = 1.00**: A resposta gerada é extremamente precisa, sem alucinações e perfeitamente focada no problema relatado. Ela estrutura a tarefa no formato de User Story, Critérios de Aceitação e Contexto Técnico utilizando exatamente os dados fornecidos no bug report (como o endpoint `POST /api/webhooks/payment`, o erro HTTP 500 e a falha na transição de status do pedido). As adições técnicas são coerentes com boas práticas e com a resposta de referência, mantendo total correção factual.

### 11. Imagens de produtos não aparecem no Safari. No Chrome funciona normal.

<details><summary>Relato completo</summary>

```text
Imagens de produtos não aparecem no Safari. No Chrome funciona normal.
```
</details>

**Saída do prompt:**

```text
**Título:** Corrigir exibição de imagens de produtos no navegador Safari

**User Story:**
* **Como** usuário do navegador Safari,
* **Quero** conseguir visualizar as imagens dos produtos corretamente na página de detalhes/listagem,
* **Para que** eu possa avaliar o produto visualmente antes de tomar uma decisão de compra, tendo a mesma experiência que os usuários do Google Chrome.

**Critérios de Aceitação:**
1. O sistema deve carregar e exibir todas as imagens de produtos corretamente quando acessado através do navegador Safari (versões recentes para macOS e iOS).
2. Não deve haver erros no console do desenvolvedor relacionados ao carregamento ou formato das imagens especificamente no Safari.
3. O comportamento de exibição das imagens no Safari deve ser idêntico ao verificado atualmente no Google Chrome.
```

- **f1_score = 0.97**: A resposta gerada é excelente e segue com precisão a estrutura de User Story e Critérios de Aceitação. A precisão é 1.0, pois todo o conteúdo é correto, relevante e agrega valor técnico à solução. O recall é 0.95, cobrindo praticamente todos os pontos da resposta esperada (persona, visualização de imagens, objetivo de compra e paridade com o Chrome), omitindo apenas a menção explícita ao tempo de carregamento.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Possui estrutura lógica impecável (Título, User Story e Critérios de Aceitação), tornando a leitura fluida. A linguagem é simples, direta e acessível, evitando jargões desnecessários. É totalmente isenta de ambiguidades, especificando com precisão o comportamento esperado no Safari em relação ao Chrome (incluindo versões macOS e iOS e verificação no console). Além disso, é concisa e objetiva, cobrindo todas as informações necessárias sem redundâncias.
- **precision = 0.98**: A resposta gerada é extremamente precisa e bem estruturada. Ausência de alucinações (1.0): Nenhuma informação falsa ou inventada foi adicionada, mantendo-se fiel ao problema do Safari vs Chrome. Foco na pergunta (1.0): Respondeu exatamente criando uma User Story e Critérios de Aceitação para o problema relatado. Correção Factual (0.95): Alinha-se perfeitamente com a resposta esperada em significado e objetivo, agregando detalhes técnicos pertinentes (como erros no console), embora não use o formato estrito 'Dado-Quando-Então' nos critérios.

### 12. Dashboard mostra contagem errada de usuários ativos. Mostra 50 mas só há 42 na lista.

<details><summary>Relato completo</summary>

```text
Dashboard mostra contagem errada de usuários ativos. Mostra 50 mas só há 42 na lista.
```
</details>

**Saída do prompt:**

```text
**Título:** Corrigir divergência na contagem de usuários ativos no Dashboard

**User Story:**

**Como** administrador do sistema,  
**Quero** que a contagem de usuários ativos exibida no Dashboard corresponda exatamente ao número real de usuários listados,  
**Para que** eu possa ter métricas confiáveis e evitar confusão ao analisar os dados da plataforma.

---

**Critérios de Aceitação:**

1. **Dado** que estou na página do Dashboard,  
   **Quando** visualizo o card de "Usuários ativos",  
   **Então** o número exibido deve ser idêntico ao total de registros presentes na listagem de usuários ativos (ex: se há 42 usuários na lista, o contador deve mostrar 42).

2. **Dado** que novos usuários são ativados ou desativados,  
   **Quando** a listagem é atualizada,  
   **Então** a contagem no Dashboard deve refletir essa alteração em tempo real (ou após o refresh).

3. **Dado** que a consulta (query) ao banco de dados é realizada para o contador e para a lista,  
   **Quando** o sistema for refatorado,  
   **Então** ambas as visualizações devem utilizar a mesma regra de negócio/filtros (ex: considerar os mesmos status de atividade, exclusão lógica, etc.).
```

- **f1_score = 1.00**: A resposta gerada cobre com precisão e totalidade todos os elementos da resposta esperada: a User Story bem formatada, a persona do administrador, a correspondência dos valores, a atualização em tempo real e o alinhamento de filtros de status. Não há informações incorretas ou irrelevantes; as adições feitas (como exemplos e regras de negócio de backend) agregam valor técnico ao contexto da correção do bug.
- **clarity = 1.00**: A resposta é extremamente clara e bem estruturada, utilizando o padrão consagrado de User Story e critérios de aceitação em formato BDD (Dado/Quando/Então). A organização visual com formatação em markdown facilita a leitura. A linguagem é direta, objetiva e sem ambiguidades, usando inclusive o exemplo numérico citado pelo usuário para ilustrar a regra. A resposta é concisa e cobre todos os aspectos do problema sem redundâncias.
- **precision = 1.00**: A resposta do modelo é extremamente precisa, livre de alucinações e totalmente focada no problema relatado. Ela transforma a reclamação sobre a contagem incorreta em uma User Story completa e bem estruturada, utilizando critérios de aceitação no formato BDD (Dado/Quando/Então). O modelo aborda com precisão a necessidade de alinhamento da contagem com a lista (incluindo o exemplo de 42 usuários citado na pergunta), sincronização dos dados e consistência nas regras de negócio.

### 13. No iOS, ao girar o celular para landscape, o layout da tela de perfil fica quebrado.

<details><summary>Relato completo</summary>

```text
No iOS, ao girar o celular para landscape, o layout da tela de perfil fica quebrado.
```
</details>

**Saída do prompt:**

```text
**Título:** Corrigir quebra de layout na tela de perfil ao rotacionar para o modo paisagem (Landscape) no iOS

**User Story:**

**Como** usuário do aplicativo no iOS,  
**Quero** que a tela de perfil se ajuste corretamente quando eu girar o celular para o modo paisagem (landscape),  
**Para que** eu possa visualizar todas as informações e interagir com a tela sem que o layout fique quebrado ou ilegível.

---

**Critérios de Aceitação:**
1. **Dado** que o usuário está na tela de perfil em um dispositivo iOS no modo retrato (portrait),  
   **Quando** ele rotaciona o dispositivo para o modo paisagem (landscape),  
   **Então** o layout deve se adaptar fluidamente, sem sobreposição de elementos, cortes de texto ou botões inacessíveis.
2. **Dado** que o usuário está no modo paisagem na tela de perfil,  
   **Quando** ele retorna o dispositivo para o modo retrato,  
   **Então** o layout deve retornar ao estado original corretamente.
3. A correção deve ser validada nos principais tamanhos de tela de dispositivos iOS (iPhone e iPad).
```

- **f1_score = 1.00**: A resposta gerada cobre perfeitamente todos os pontos do Ground Truth. A User Story preserva o mesmo papel, intenção e benefício. Os Critérios de Aceitação contemplam a transição para o modo paisagem, adaptação do layout e ausência de sobreposição de elementos. As adições feitas pelo modelo (retorno ao modo retrato e abrangência de dispositivos) são extremamente pertinentes e enriquecem a especificação sem gerar redundâncias ou erros técnicos.
- **clarity = 1.00**: A resposta gerada possui excelente clareza. Está perfeitamente organizada no formato padrão de User Story e Critérios de Aceitação (BDD), com uma estrutura lógica impecável. A linguagem é direta, profissional e simples de compreender. Não apresenta ambiguidades em relação ao comportamento esperado do sistema e é concisa, fornecendo todas as informações necessárias sem redundâncias.
- **precision = 1.00**: A resposta gerada é altamente precisa, focada e totalmente livre de alucinações. O modelo interpretou o relato do problema e construiu uma User Story completa com critérios de aceitação no formato BDD (Dado/Quando/Então). O conteúdo atende perfeitamente à intenção da resposta esperada, adicionando estrutura clara e relevante para resolução do bug em iOS sem inventar informações incorretas.

### 14. Campo de email aceita texto sem @, permitindo cadastros inválidos.

<details><summary>Relato completo</summary>

```text
Campo de email aceita texto sem @, permitindo cadastros inválidos.
```
</details>

**Saída do prompt:**

```text
**Título da Tarefa:** Validação de formato de e-mail no formulário de cadastro

**User Story:**
* **Como** um administrador do sistema,
* **Quero** que o campo de e-mail valide a presença do caractere "@" (e outras regras básicas de formato) antes de permitir a conclusão do cadastro,
* **Para que** sejam evitados registros com endereços de e-mail inválidos ou incorretos na base de dados.

**Critérios de Aceite:**
1. O sistema deve validar se o texto inserido no campo de e-mail contém o caractere "@".
2. O sistema deve validar a presença de um domínio válido após o "@" (ex: `.com`, `.br`).
3. Se o usuário tentar enviar o formulário com um e-mail inválido (sem "@"), o cadastro não deve ser realizado.
4. Uma mensagem de erro clara deve ser exibida ao usuário (Ex: "Por favor, insira um endereço de e-mail válido").
```

- **f1_score = 0.87**: A resposta gerada cobre com precisão a regra de negócio e os critérios essenciais (impedir cadastro sem '@' e exibir mensagem de erro). O recall é alto pois atende aos requisitos principais da resposta esperada. No entanto, a precisão sofreu uma leve redução por alterar a persona da User Story de 'usuário criando conta' para 'administrador do sistema' e por não utilizar a estrutura BDD (Dado/Quando/Então) solicitada implicitamente no Ground Truth.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza e estrutura. Está perfeitamente organizada com títulos, tópicos e listas numeradas. A linguagem é direta, acessível e profissional, evitando termos desnecessariamente complexos. Não há ambiguidades, pois as regras de validação e o comportamento esperado da tela estão descritos com precisão. Por fim, a resposta é concisa, contendo apenas as informações essenciais para a especificação do requisito sem gerar redundâncias.
- **precision = 0.95**: A resposta não apresenta alucinações e responde com precisão à questão apresentada. O modelo estruturou corretamente a solução para o problema de validação de e-mail. Houve apenas uma leve divergência na escolha da persona da User Story ('administrador do sistema' em vez de 'usuário') e no formato dos critérios de aceite (lista numerada em vez do padrão Dado/Quando/Então), mas o conteúdo técnico e funcional está correto e alinhado ao objetivo.

### 15. Botão de adicionar ao carrinho não funciona no produto ID 1234.

<details><summary>Relato completo</summary>

```text
Botão de adicionar ao carrinho não funciona no produto ID 1234.
```
</details>

**Saída do prompt:**

```text
**Título:** Corrigir falha no botão "Adicionar ao Carrinho" do produto ID 1234

**User Story:**
* **Como** usuário da loja virtual,
* **Quero** conseguir clicar no botão "Adicionar ao Carrinho" na página do produto ID 1234 e ter o item adicionado com sucesso ao meu carrinho de compras,
* **Para que** eu possa finalizar a compra deste produto específico sem encontrar bloqueios.

---

**Critérios de Aceitação:**
1. Dado que o usuário está na página do produto ID 1234, quando ele clica no botão "Adicionar ao Carrinho", então o produto deve ser adicionado ao carrinho de compras.
2. Dado que o produto foi adicionado, quando a ação for concluída, então o contador do carrinho deve ser atualizado e uma mensagem de confirmação (ou feedback visual) deve ser exibida ao usuário.
3. O botão não deve apresentar erros de console (JavaScript) ao ser clicado.
```

- **f1_score = 1.00**: A resposta gerada abrange com precisão e totalidade todos os elementos da resposta esperada. O papel, ação e benefício da User Story foram mantidos. Todos os Critérios de Aceitação exigidos (estar no produto, clicar no botão, adicionar ao carrinho, confirmação visual e atualização do contador) foram contemplados de forma clara. As adições feitas (como checar erros no console) são perfeitamente corretas e relevantes para o contexto.
- **clarity = 1.00**: A resposta gerada possui excelente clareza. Está impecavelmente organizada no formato padrão de User Story e critérios de aceite (BDD). A linguagem é simples, direta e acessível. Não há qualquer ambiguidade, especificando com precisão o comportamento esperado para o produto ID 1234, incluindo feedback visual e ausência de erros de console. Além disso, é perfeitamente concisa, entregando exatamente o que é necessário sem redundâncias.
- **precision = 1.00**: A resposta gerada é altamente precisa, factual e livre de alucinações. Ela adapta corretamente o relato do problema com o produto ID 1234 para o formato de User Story e Critérios de Aceitação, cobrindo com exatidão todos os pontos da resposta de referência (adição ao carrinho, confirmação visual e atualização do contador) e mantendo foco total no pedido do usuário.
