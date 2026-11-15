# Iteração 1 (repetição): mesmo prompt, nova execução

- Experimento: `evaluation-prompt-bug_to_user_story_v2-2822a003`
- Prompt: `evaluation-prompt/bug_to_user_story_v2`
- Provider / modelo / juiz: `google` / `gemini-3.5-flash-lite` / `gemini-3.5-flash`
- Data: 2026-11-15 14:45 UTC
- Exemplos: 15

| Métrica | Média | ≥ 0.8 |
|---|---|---|
| helpfulness | 0.9900 | ✓ |
| correctness | 0.9417 | ✓ |
| f1_score | 0.8960 | ✓ |
| clarity | 0.9927 | ✓ |
| precision | 0.9873 | ✓ |
| **média geral** | **0.9615** | ✓ |

**Status: ✅ APROVADO**

## Por exemplo

| # | Relato (início) | F1 | Clarity | Precision |
|---|---|---|---|---|
| 1 | App de produtividade offline-first com bugs críticos de sincronização. | 0.82 | 1.00 | 1.00 |
| 2 | Sistema de relatórios gerenciais com problemas severos de performance  | 0.90 | 0.99 | 1.00 |
| 3 | Sistema de checkout com múltiplas falhas críticas. | 0.90 | 0.99 | 1.00 |
| 4 | Modal de confirmação de exclusão aparece atrás do menu lateral em tela | 0.82 | 1.00 | 1.00 |
| 5 | Carrinho permite finalizar compra mesmo com produto fora de estoque. | 0.84 | 1.00 | 0.97 |
| 6 | App Android trava ao carregar lista de notificações com mais de 50 ite | 0.92 | 1.00 | 1.00 |
| 7 | Pipeline de vendas calcula valor total errado quando há desconto. | 0.90 | 1.00 | 1.00 |
| 8 | Endpoint /api/users/:id retorna dados de qualquer usuário sem validar  | 0.93 | 0.98 | 1.00 |
| 9 | Relatório de vendas demora mais de 2 minutos para gerar quando filtro  | 0.85 | 0.98 | 0.98 |
| 10 | Webhook de pagamento aprovado não está sendo chamado. | 0.84 | 1.00 | 0.98 |
| 11 | Imagens de produtos não aparecem no Safari. No Chrome funciona normal. | 0.97 | 1.00 | 0.98 |
| 12 | Dashboard mostra contagem errada de usuários ativos. Mostra 50 mas só  | 0.75 | 0.95 | 0.90 |
| 13 | No iOS, ao girar o celular para landscape, o layout da tela de perfil  | 1.00 | 1.00 | 1.00 |
| 14 | Campo de email aceita texto sem @, permitindo cadastros inválidos. | 1.00 | 1.00 | 1.00 |
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
Como um vendedor em campo utilizando o app offline-first, eu quero que minhas alterações e anexos sejam sincronizados corretamente e em ordem, sem perdas de dados ou falhas de memória, para que eu possa confiar no aplicativo mesmo trabalhando sem conexão à internet.

=== USER STORY PRINCIPAL ===

Título: Sincronização offline robusta com resolução de conflitos, retomada de upload, ordenação cronológica e paginação de lote

Descrição:
Como um vendedor em campo utilizando o app mobile, eu quero uma sincronização confiável que resolva conflitos de edição, retome uploads interrompidos, respeite a ordem cronológica das operações e processe grandes volumes de dados em lotes, para que eu não perca compromissos nem sofra com crashes no app.

=== CRITÉRIOS DE ACEITAÇÃO ===

A. Conflito de dados - Notificação e preservação de edições concorrentes:
- Dado que o usuário A (offline) edita a tarefa #123 para "Ligar para cliente X às 14h"
- E o usuário B (offline) edita a mesma tarefa #123 para "Ligar para cliente X às 15h (reagendado)"
- Quando ambos realizam a sincronização com o servidor
- Então o sistema não deve sobrescrever os dados silenciosamente via "last write wins"
- E o sistema deve detectar o conflito, preservar ambas as versões e notificar o usuário A sobre a alteração concorrente para escolha da versão final

B. Sincronização - Retomada de upload de anexos grandes com feedback:
- Dado que anexo um PDF de 50MB em uma tarefa e inicio o upload via conexão 4G
- Quando a conexão cai no meio do envio (ex: em 40%)
- Então o app deve retomar o upload do ponto onde parou (chunked/resumable upload) sem reiniciar do 0%
- E após o limite de tentativas, caso falhe definitivamente, o status da tarefa não deve ser marcado como sincronizado
- E o app deve exibir uma mensagem clara informando a falha no envio do anexo ao usuário

C. Ordenação - Respeito ao timestamp client-side na sincronização:
- Dado que realizo operações offline em sequência (10:00 - Cria tarefa "Tarefa A", 10:15 - Edita "Tarefa A" para "Urgente", 10:30 - Deleta "Tarefa A")
- Quando a sincronização é realizada ao recuperar a conexão
- Então o servidor deve aplicar as operações respeitando estritamente o timestamp client-side e a ordem cronológica
- E o servidor não deve receber o DELETE antes do CREATE nem retornar erro 404
- E o resultado final da sincronização deve ser a exclusão da "Tarefa A"

D. Memória - Processamento em lotes para grande volume de itens pendentes:
- Dado que acumulei 1.500 operações pendentes (create, update, delete) após 1 semana offline
- Quando retorno para uma área com WiFi e a sincronização é iniciada
- Então o app não deve carregar todos os 1.500 itens de uma vez na memória
- E o app deve processar a sincronização em lotes paginados (batch processing)
- E o consumo de memória deve permanecer abaixo de 700MB no iOS, evitando crashes do sistema operacional ou OutOfMemoryError no Android

=== CRITÉRIOS TÉCNICOS ===

Resolução de Conflitos:
- Implementar estratégia de detecção de conflitos e merge interativo ou versionamento por optimistic locking ao invés de "last write wins"

Upload Resumível:
- Utilizar protocolo de upload fragmentado/resumível e validar o status real de sincronização do anexo antes de atualizar o estado da tarefa

Ordenação de Fila:
- Ordenar a fila de sincronização client-side pelo timestamp de criação/modificação antes do envio ao servidor (garantindo CREATE -> UPDATE -> DELETE)

Paginação de Lotes:
- Implementar processamento em lotes (batching) na fila de sincronização offline para limitar o consumo de memória RAM abaixo do limite crítico de 700MB

=== CONTEXTO DO BUG ===

Severidade: CRÍTICA
Impacto: 250+ usuários afetados, NPS caiu de 8.5 para 4.2, 80% dos reviews negativos mencionam "perda de dados", churn rate aumentou 15%, R$ 200k em oportunidades perdidas

Problemas Identificados:
1. Merge incorreto por "last write wins" causa perda de dados na tarefa #123
2. Upload de anexo de 50MB reinicia do zero após queda de conexão e marca tarefa como sincronizada falsamente
3. Operações offline aplicadas fora de ordem no servidor geram erro 404 ao tentar deletar tarefa inexistente antes da criação
4. Sincronização de 1.500+ itens pendentes carrega tudo na memória, causando Memory Warning no iOS (850MB > 700MB) e OutOfMemoryError no Android

=== TASKS TÉCNICAS SUGERIDAS ===

1. [BACKEND/FRONTEND] Implementar detecção de conflitos de edição concorrente e fluxo de notificação ao usuário
2. [MOBILE/BACKEND] Desenvolver suporte a upload resumível (chunked upload) e correção do status de sincronização de anexos
3. [MOBILE] Ajustar ordenação da fila de sincronização offline baseada em timestamp client-side
4. [MOBILE] Implementar processamento em lotes (batching) para reduzir o consumo de memória durante a sincronização de grandes volumes de dados
5. [TESTES] Executar testes de estresse com 1500+ itens offline e testes de interrupção de rede durante uploads de arquivos grandes
```

- **f1_score = 0.82**: A resposta gerada possui precisão máxima (1.0), pois todas as informações apresentadas são corretas, bem estruturadas e diretamente relevantes ao problema. O recall foi avaliado em 0.70 porque a resposta omitiu alguns detalhes aprofundados presentes no Ground Truth, como a especificação detalhada de endpoints e esquemas JSON nos critérios técnicos, a subdivisão completa das tasks técnicas em 4 fases (16 itens), detalhes da arquitetura atual e a seção inteira de Métricas de Sucesso (Antes vs Depois).
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. A estrutura é altamente organizada e padronizada (usando o formato BDD - Dado/Quando/Então nos critérios de aceitação), o que elimina qualquer ambiguidade sobre o comportamento esperado da solução. A linguagem é direta, precisa e adequada ao contexto técnico de desenvolvimento de software. Além disso, o texto é conciso, cobrindo com exatidão todos os 4 problemas relatados no contexto sem incluir redundâncias.
- **precision = 1.00**: A resposta do modelo é extremamente precisa, sem alucinações e totalmente focada no contexto fornecido. Ela mapeia com exatidão os 4 problemas relatados (conflito de edição A/B, upload resumível de 50MB, ordenação por timestamp e limite de memória de 700MB para 1500 itens). Todos os dados numéricos e impactos de negócios foram fielmente preservados e estruturados em formato de User Story e Critérios de Aceitação perfeitamente corretos.

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
Como um gestor financeiro e executivo utilizando o sistema, eu quero relatórios de desempenho rápidos, consolidados com regras consistentes de MRR, dados em tempo real e exportações otimizadas, para que eu possa confiar nos números para o board e tomar decisões sem travar a plataforma.

=== USER STORY PRINCIPAL ===

Título: Correção de performance, consistência de MRR, cache e concorrência no sistema de relatórios

Descrição:
Como um usuário corporativo do sistema SaaS, eu quero relatórios gerenciais eficientes, cálculo unificado de MRR, dados atualizados via Redis e exportações estáveis, para que a tomada de decisão seja ágil e confiável.

=== CRITÉRIOS DE ACEITAÇÃO ===

A. Performance - Otimização de consultas no dashboard executivo:
- Dado que acesso o endpoint GET /api/reports/executive-dashboard
- Quando o sistema carrega as métricas da empresa
- Então o tempo de resposta deve ser inferior ao SLA de 3 segundos
- E o problema de query N+1 deve ser eliminado utilizando carregamento em lote ou JOINs consolidados

B. Lógica de Negócio - Consistência no cálculo de MRR:
- Dado que consulto o faturamento recorrente
- Quando visualizo o MRR no dashboard, no relatório financeiro ou na exportação
- Então o valor calculado deve seguir a regra única de negócio (considerando assinaturas ativas sem distorções de cancelamentos futuros e aplicando o pró-rata de upgrades/downgrades)
- E todas as telas e relatórios devem apresentar exatamente o mesmo valor consolidado

C. Cache - Invalidação correta no Redis:
- Dado que ocorre uma alteração nos dados do cliente (como upgrade de plano)
- Quando o evento de atualização é processado
- Então o cache do Redis correspondente deve ser invalidado imediatamente
- E a invalidação manual pelo painel deve refletir os dados atualizados sem aguardar o TTL de 24 horas

D. Concorrência - Exportação de CSV estável e sem OOM Kill:
- Dado que solicito a exportação de um relatório anual com 50k linhas
- Quando o processo de geração do arquivo for executado
- Então o processamento não deve exceder o limite de 2GB de memória RAM
- E a requisição deve ser processada sem afetar a performance geral ou causar travamento (OOM Kill) do servidor

=== CRITÉRIOS TÉCNICOS ===

Performance:
- Substituir o loop de queries no banco pelo uso de carregamento em lote (Batch Loading/JOINs) no endpoint GET /api/reports/executive-dashboard

Negócio:
- Padronizar o algoritmo de cálculo de MRR no backend para unificar as regras entre o dashboard, relatórios e planilhas

Cache:
- Implementar eventos de invalidação imediata no Redis para mutações de dados do cliente e corrigir a rotina de limpeza manual

Concorrência:
- Processar a exportação de CSV em chunks/streams para manter o consumo de memória abaixo do limite de 2GB e evitar picos de CPU em 100%

=== CONTEXTO DO BUG ===

Severidade: CRÍTICA
Impacto: 15 clientes enterprise ameaçando cancelar contrato, CEO sem confiança para apresentar ao board, 40h/semana gastas pelo CS com discrepâncias, forecasting inviável

Problemas Identificados:
1. Query N+1 no dashboard executivo (GET /api/reports/executive-dashboard) gerando 101+ queries e 45s de resposta
2. Cálculo de MRR inconsistente entre dashboard (R$ 150k), relatório (R$ 145k) e contábil (R$ 147,5k)
3. Cache Redis com TTL de 24h exibe dados antigos após upgrade, com falha na invalidação manual
4. Exportação de CSV anual (50k linhas) consome 4GB de memória, causando OOM Kill e lentidão geral

=== TASKS TÉCNICAS SUGERIDAS ===

1. [BACKEND] Refatorar query do GET /api/reports/executive-dashboard para eliminar N+1
2. [BACKEND] Unificar regra de cálculo de MRR em um serviço centralizado
3. [CACHE] Corrigir mecanismo de invalidação automática e manual no Redis
4. [BACKEND] Implementar processamento em stream/chunks para exportação de relatórios grandes (CSV)
5. [INFRA/QA] Realizar testes de carga e de consumo de memória para validar o limite de 2GB e o SLA de 3s
```

- **f1_score = 0.90**: A resposta gerada é extremamente precisa e relevante, abordando corretamente todos os problemas apresentados (N+1, MRR, Cache Redis, Exportação CSV) sem inventar dados. O Precision é alto (0.95). O Recall é 0.85 pois, embora cubra a User Story, Critérios de Aceitação, Contexto e Tarefas, omitiu detalhes específicos do Ground Truth como o exemplo de query SQL otimizada, a estratégia detalhada de cache em camadas (sem cache / 5min / 1h), background job queues específicas (Sidekiq/Bull) e a divisão das tasks por Sprints.
- **clarity = 0.99**: A resposta possui excelente clareza. A estrutura é altamente organizada em seções bem delimitadas, utilizando o formato BDD (Dado-Quando-Então) nos critérios de aceitação, o que elimina ambiguidades. A linguagem é direta, objetiva e adequada ao contexto de engenharia de software e gestão de produto. Há concisão e precisão na apresentação dos problemas e das soluções técnicas recomendadas, mantendo a leitura fluida e fácil de compreender por diferentes stakeholders.
- **precision = 1.00**: A resposta do modelo é altamente precisa, factual e sem alucinações. Ela aborda perfeitamente todos os 4 problemas relatados no contexto (Query N+1, inconsistência do MRR, cache do Redis e OOM na exportação CSV). As soluções técnicas propostas (processamento em streaming/chunks, JOINs/batch loading, invalidação por eventos e unificação do cálculo de MRR) são totalmente corretas e alinhadas às boas práticas e ao esperado na resposta de referência, mantendo foco absoluto no problema apresentado.

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
Como um cliente finalizando uma compra, eu quero que o checkout seja seguro, processe pagamentos sem falhas, aplique cupons corretamente e forneça feedback em caso de demora, para que eu possa concluir meu pedido com segurança e confiança.

=== USER STORY PRINCIPAL ===

Título: Correção de falhas críticas de segurança, pagamento, concorrência e UX no checkout

Descrição:
Como um cliente realizando um pagamento, eu quero que o sistema sanitiza entradas, evite timeouts e esgotamento de conexões, respeite o limite de cupons de forma atômica e informe o status correto após atrasos, para que minhas transações sejam seguras e confiáveis.

=== CRITÉRIOS DE ACEITAÇÃO ===

A. Segurança - Sanitização do campo de cupom:
- Dado que estou na tela de checkout
- Quando insiro scripts maliciosos como <script>alert('xss')</script> no campo de cupom
- Então o sistema deve sanitizar a entrada e não executar o código
- E deve exibir uma mensagem indicando que o cupom é inválido

B. Integração - Processamento de pagamento sem timeouts e cobranças órfãs:
- Dado que o POST /api/payment/process é acionado
- Quando o gateway de pagamento processa a transação
- Então a requisição deve ser concluída sem retornar 504 Gateway Timeout
- E o pedido deve ser criado com sucesso quando o pagamento for aprovado
- E o pool de conexões do Postgres não deve ser esgotado

C. Lógica de Negócio - Validação atômica de cupons de desconto:
- Dado que um cupom como "PROMO10" possui um limite de 100 usos
- Quando múltiplos clientes aplicam o cupom simultaneamente
- Entonces a verificação e o incremento do uso devem ser atômicos
- E o sistema deve bloquear o uso do cupom estritamente após atingir o limite de 100 usos

D. UX - Feedback em caso de timeout no pagamento:
- Dado que o processamento do pagamento demora mais de 30 segundos
- Quando ocorre um timeout na requisição
- Então a tela não deve exibir um spinner infinito
- E o usuário deve receber uma mensagem clara informando o status do pagamento

=== CRITÉRIOS TÉCNICOS ===

Segurança:
- Implementar sanitização e escape de dados no campo de cupom para mitigar XSS

Integração:
- Otimizar o gerenciamento do connection pool do Postgres e o tratamento de timeout no POST /api/payment/process para evitar cobranças sem pedidos criados

Lógica de Negócio:
- Utilizar transações com bloqueio adequado (ex.: SELECT ... FOR UPDATE ou locks atômicos) para garantir que o limite de cupons seja respeitado sob concorrência

UX:
- Implementar tratamento de timeout no front-end após 30 segundos, removendo o spinner e exibindo estado e mensagem claros ao usuário

=== CONTEXTO DO BUG ===

Severidade: CRÍTICA
Impacto: 150+ clientes afetados na última semana, perda estimada de R$ 15.000 em cupons indevidos, 45 tickets de suporte abertos, rating do app caiu de 4.5 para 3.2 estrelas

Problemas Identificados:
1. XSS não sanitizado no campo de cupom
2. POST /api/payment/process retorna 504 Gateway Timeout com "Connection pool exhausted" no Postgres, gerando cobranças sem pedidos
3. Race condition permitiu 147 usos em cupom com limite de 100 usos
4. Tela fica com loading infinito em pagamentos com mais de 30s de demora

=== TASKS TÉCNICAS SUGERIDAS ===

1. [SEGURANÇA] Sanitizar entrada do campo de cupom para prevenir XSS
2. [BACKEND] Ajustar configuração e gerenciamento do connection pool do Postgres no POST /api/payment/process
3. [BANCO DE DADOS] Implementar atomicidade na verificação e atualização de limite de cupons
4. [FRONTEND] Tratar timeout de 30s no pagamento para remover o spinner infinito e exibir feedback adequado
5. [TESTES] Executar testes de carga, concorrência de cupons e segurança em XSS
```

- **f1_score = 0.90**: A precisão é excelente (0.95), pois todas as informações geradas são corretas, relevantes e alinhadas ao contexto. O recall é alto (0.85), cobrindo todas as seções principais (User Story, Critérios A-D, Contexto e Tasks), mas omitindo detalhes técnicos específicos do Ground Truth, como padrões de retry com exponential backoff, circuit breaker, headers CSP, Redis INCR, idempotency key e alertas de monitoramento.
- **clarity = 0.99**: A resposta é extremamente bem organizada, com estrutura visual clara em tópicos e seções bem delimitadas. A linguagem é precisa, direta e apropriada ao contexto técnico, contendo apenas um pequeno erro de digitação ('Entonces' no critério C). Não há ambiguidades nos critérios de aceitação e tarefas descritas, e a informação é apresentada de forma altamente concisa, sem redundâncias desnecessárias.
- **precision = 1.00**: A resposta do modelo é altamente precisa, focada e totalmente isenta de alucinações. Todos os 4 problemas relatados (XSS no cupom, erro 504 por exaustão de pool no Postgres, race condition no cupom PROMO10 e spinner infinito no frontend) foram abordados com soluções técnicas válidas e estruturados em User Story, Critérios de Aceitação e Tasks, demonstrando total alinhamento com a pergunta e o Ground Truth.

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
Como um usuário navegando em telas pequenas (< 768px), eu quero visualizar o modal de confirmação de exclusão acima do menu lateral, para que eu possa interagir com os botões do modal sem precisar fechar o menu primeiro.

Critérios de Aceitação:
- Dado que estou em um dispositivo com tela menor que 768px e o menu lateral está aberto
- Quando aciono a exclusão de um item e o modal de confirmação é exibido
- Então o modal deve aparecer sobreposto ao menu lateral
- E o z-index do modal deve ser superior ao z-index do menu lateral
- E devo conseguir clicar nos botões do modal sem obstáculos

Critérios Técnicos:
- Ajustar o z-index do modal para um valor superior a 1050 (por exemplo, 1100 ou acima da camada do menu lateral)
- Garantir que o comportamento de empilhamento (stacking context) respeite os breakpoints mobile (< 768px)

Contexto Técnico:
- Problema atual: Modal com z-index 1000 fica oculto atrás do menu lateral com z-index 1050 em telas < 768px
- Sintoma: Usuários não conseguem clicar nos botões do modal e precisam fechar o menu lateral manualmente
- Valores atuais: z-index modal = 1000, z-index menu lateral = 1050
```

- **f1_score = 0.82**: A resposta gerada é 100% precisa e relevante, abordando corretamente a história de usuário, contexto técnico e a solução de z-index sem introduzir informações incorretas. O recall é 0,70 pois, embora cubra os critérios básicos de aceitação e aspectos técnicos, omitiu completamente a seção de Critérios de Acessibilidade (foco de teclado, tecla ESC, fechar ao clicar no backdrop) e a exigência de largura mínima de 90% para o modal.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está perfeitamente organizada no formato padrão de História de Usuário com critérios de aceitação em estilo BDD (Dado/Quando/Então). A linguagem é direta, precisa e sem ambiguidades, explicando de forma transparente o problema do z-index e a solução esperada. É concisa, bem estruturada e fácil de entender tanto por desenvolvedores quanto por profissionais de produto.
- **precision = 1.00**: A resposta gerada é altamente precisa, focada e completamente livre de alucinações. Ela traduz perfeitamente o problema relatado (z-index 1000 do modal vs 1050 do menu lateral em telas < 768px) em uma estória de usuário bem estruturada. Os critérios de aceitação e contexto técnico propostos alinham-se perfeitamente com os dados fornecidos e com a resposta esperada, apresentando solução técnica correta (z-index > 1050).

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
Como um cliente no e-commerce, eu quero ser impedido de finalizar a compra quando um produto esgotar, para que eu não compre itens indisponíveis e evite problemas de entrega.

Critérios de Aceitação:
- Dado que um produto possui estoque igual a zero
- Quando o Cliente B tenta adicionar esse produto ao carrinho
- Então o sistema deve exibir a mensagem "Produto esgotado"
- E não deve permitir a adição do item ao carrinho
- E se o carrinho já continha itens que esgotaram antes da finalização, o sistema deve bloquear o checkout e destacar o produto indisponível

Contexto Técnico:
- Bug atual: Sistema permite finalizar compra de produtos com estoque zerado devido a concorrência (Cliente B adiciona após o Cliente A esgotar o estoque)
- Validar o estoque em tempo real tanto na adição ao carrinho quanto na etapa de finalização de compra (checkout)
- Garantir lock ou validação atômica no banco de dados para evitar overselling (venda sem estoque)
```

- **f1_score = 0.84**: A resposta gerada é extremamente precisa e relevante, identificando a causa raiz (concorrência) e propondo validações em tempo real e locks no banco de dados. No entanto, o recall é parcial pois omitiu critérios de prevenção específicos presentes no gabarito, tais como a reserva temporária de estoque por 15 minutos no checkout, o aviso de 'estoque limitado' ao adicionar e a sugestão para o cliente aguardar reposição do item.
- **clarity = 1.00**: A resposta gerada possui excelente clareza. Está estruturada de forma altamente organizada em seções bem definidas (História de Usuário, Critérios de Aceitação em BDD e Contexto Técnico). A linguagem é direta, profissional e de fácil compreensão. Não há ambiguidades sobre as regras de negócio para solucionar o bug tanto no carrinho quanto no checkout. Além disso, a resposta é concisa e cobre perfeitamente o problema relatado sem informações desnecessárias.
- **precision = 0.97**: A resposta do modelo é precisa, focada e totalmente alinhada ao bug relatado. Não apresenta alucinações; as informações técnicas (como lock atômico e validação em tempo real no checkout) são corretas e tratam diretamente a causa raiz descrita na pergunta. Em comparação com o Ground Truth, a resposta adota a perspectiva do cliente ('Como um cliente...') em vez do sistema, mas cobre perfeitamente a resolução do problema e os critérios de aceitação necessários para a correção da falha.

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
Como um usuário do app Android, eu quero que a lista de notificações seja carregada de forma fluida e paginada, para que o aplicativo não trave ao exibir muitos itens.

Critérios de Aceitação:
- Dado que acesso a tela de notificações do app Android
- Quando a lista possui mais de 50 itens
- Então os dados devem ser carregados de forma paginada para evitar travamentos
- E a Thread principal não deve ser bloqueada durante o carregamento
- E o tempo de resposta da tela deve ser inferior a 2 segundos
- E o app nunca deve exibir a tela de Application Not Responding (ANR)

Critérios Técnicos:
- Implementar paginação no carregamento da lista de notificações (infinite scroll ou paginação por páginas)
- Executar as chamadas de rede e processamento de dados fora da Thread principal (Main Thread), utilizando corrotinas ou threads em segundo plano

Contexto Técnico:
- Bug atual: App Android trava por 5-10 segundos e gera ANR ao carregar mais de 50 itens de uma vez na Thread principal
- Causa identificada: Ausência de paginação e processamento síncrono na Main Thread
```

- **f1_score = 0.92**: A precisão é 1.0 pois todas as informações geradas são corretas, altamente relevantes e sem alucinações. O recall é 0.85 pois a resposta cobriu quase a totalidade da resposta esperada (User Story, tempo limite <2s, ausência de ANR, background thread e paginação), omitindo apenas detalhes técnicos específicos como o uso de RecyclerView com ViewHolder pattern e a quantidade exata de itens por página (20 itens).
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. É extremamente bem organizada em seções lógicas (História de Usuário, Critérios de Aceitação BDD, Critérios Técnicos e Contexto). A linguagem é simples, precisa e acessível. O formato Given-When-Then (Dado/Quando/Então) elimina qualquer ambiguidade sobre o comportamento esperado. Além disso, o texto é muito conciso e direto ao ponto, cobrindo com precisão todas as observações do problema sem incluir informações redundantes.
- **precision = 1.00**: A resposta do modelo é extremamente precisa e totalmente alinhada com a referência e as observações da pergunta. Não há alucinações; todas as informações e sugestões técnicas (como uso de corrotinas/threads em segundo plano e paginação) são factualmente corretas para o problema de ANR no Android. O foco é mantido 100% no problema relatado, apresentando critérios de aceitação e contexto técnico claros e corretos.

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
Como um gerente de vendas, eu quero que o pipeline de vendas calcule o valor total aplicando o desconto corretamente sobre o valor total dos produtos, para que os valores dos negócios exibidos estejam corretos.

Critérios de Aceitação:
- Dado que crio um negócio com o Produto A no valor de R$ 1.000 e o Produto B no valor de R$ 500
- Quando aplico um desconto de 10%
- Então o valor total calculado deve ser de R$ 1.350
- E o sistema não deve aplicar o desconto apenas no primeiro produto
- E o valor mostrado na tela deve ser exatamente R$ 1.350

Exemplo de Cálculo:
- Subtotal dos produtos: R$ 1.000 (Produto A) + R$ 500 (Produto B) = R$ 1.500
- Cálculo do desconto de 10%: R$ 1.500 * 0,10 = R$ 150 de desconto
- Valor total final: R$ 1.500 - R$ 150 = R$ 1.350

Contexto Técnico:
- Problema atual: O sistema aplica o desconto de 10% apenas no Produto A (R$ 1.000 - 10% = R$ 900 + R$ 500 = R$ 1.400)
- Valor atual incorreto: R$ 1.400 | Valor esperado: R$ 1.350
- Ajustar a lógica de aplicação de desconto no backend para que incida sobre a soma total dos itens do pipeline e não de forma isolada no primeiro item.
```

- **f1_score = 0.90**: A resposta gerada é altamente precisa, com informações corretas, relevantes e incluindo um ajuste útil no contexto técnico. A precisão só não é perfeita pela troca secundária do papel da persona (gerente de vendas em vez de vendedor). O recall é 0.85 pois os critérios de aceitação foram descritos com valores específicos em vez de estabelecer regras e fórmulas genéricas, omitindo o critério explícito de exibição do detalhamento (subtotal, desconto e total).
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. É extremamente organizada no padrão BDD (História de Usuário, Critérios de Aceitação, Exemplo e Contexto Técnico), facilitando a leitura imediata. Utiliza linguagem simples, direta e precisa, eliminando qualquer ambiguidade ao demonstrar numericamente o problema e a solução esperada. Além disso, é concisa e objetiva, cobrindo todos os pontos necessários sem prolixidade.
- **precision = 1.00**: A resposta gerada é extremamente precisa, sem alucinações e completamente alinhada ao Ground Truth. Ela descreve perfeitamente a História de Usuário, os Critérios de Aceitação e o Contexto Técnico baseando-se estritamente nos dados do cenário fornecido (Produto A: R$ 1.000, Produto B: R$ 500, Desconto: 10%, Total: R$ 1.350). Os cálculos matemáticos estão corretos, inclusive a explicação de como o valor incorreto de R$ 1.400 é gerado pelo bug atual. O foco na solução do problema é total.

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
Como um administrador do sistema, eu quero que o acesso ao endpoint `/api/users/:id` seja restrito apenas a usuários com permissão de administrador, para que dados sensíveis como email, telefone e endereço fiquem protegidos contra vazamentos.

=== USER STORY PRINCIPAL ===

Título: Proteção de dados de usuários por validação de permissões no endpoint GET /api/users/:id

Descrição:
Como um administrador do sistema, eu quero que o endpoint `/api/users/:id` valide as permissões do usuário solicitante, para que usuários comuns não tenham acesso a informações pessoais de outros usuários.

=== CRITÉRIOS DE ACEITAÇÃO ===

A. Segurança - Restrição de acesso para administradores:
- Dado que estou autenticado como um usuário comum (ex.: ID 100)
- Quando faço uma requisição GET para `/api/users/1` (perfil de outro usuário ou administrador)
- Então a API deve retornar o código HTTP 403 (Forbidden)
- E nenhum dado pessoal (email, telefone, endereço) deve ser retornado

B. Segurança - Acesso autorizado para administradores:
- Dado que estou autenticado como um usuário administrador
- Quando faço uma requisição GET para `/api/users/1`
- Então a API deve retornar o código HTTP 200 (OK)
- E os dados do usuário solicitado devem ser exibidos corretamente

C. Segurança - Registro em log de auditoria:
- Dado que um usuário comum tenta acessar dados protegidos de outro usuário
- Quando a tentativa é bloqueada pela API
- Então um evento de segurança deve ser registrado no log de auditoria com o ID do usuário e o timestamp da tentativa

=== CRITÉRIOS TÉCNICOS ===

Controle de Acesso:
- Implementar middleware de autorização baseado em papéis (RBAC) no endpoint GET `/api/users/:id` para verificar se o token JWT contém a role de administrador ou se o ID do token corresponde ao recurso solicitado (se aplicável), bloqueando acessos não autorizados com HTTP 403.

=== CONTEXTO DE SEGURANÇA ===

Severidade: ALTA
Impacto: Vazamento de dados pessoais (email, telefone, endereço)

Problemas Identificados:
1. Endpoint /api/users/:id retorna dados de qualquer usuário sem validar permissões
2. Usuário comum consegue acessar perfis de administradores ou de outros usuários

=== TASKS TÉCNICAS SUGERIDAS ===

1. [BACKEND] Implementar validação de permissões/roles no endpoint GET /api/users/:id
2. [SEGURANÇA] Garantir o retorno do código HTTP 403 para tentativas de acesso não autorizadas
3. [BACKEND] Adicionar registro em log de auditoria para tentativas de acesso negadas
4. [TESTES] Criar testes unitários e de integração para validar o controle de acesso por perfil (usuário comum vs. admin)
```

- **f1_score = 0.93**: A resposta gerada é altamente precisa e cobre quase todos os pontos do Ground Truth. Incluiu a User Story, critérios de aceitação para usuário comum e admin (retorno 403 e 200), severidade alta, dados expostos e a necessidade de middleware de autorização. O recall só não foi 1.0 porque omitiu a referência explícita à OWASP A01:2021 e associou o log de auditoria primariamente às tentativas bloqueadas em vez do acesso do admin. A precisão é altíssima, com adições técnicas relevantes e sem alucinações.
- **clarity = 0.98**: A resposta apresenta excelente clareza. A organização visual é exemplar, dividida em seções lógicas (User Story, Critérios BDD, Critérios Técnicos, Contexto e Tasks). A linguagem é direta, profissional e fácil de compreender. Os critérios de aceitação no formato Dado/Quando/Então eliminam ambiguidades ao especificar comportamentos e códigos de status HTTP exatos. Há uma leve redundância no resumo de contexto de segurança, mas sem comprometer a excelente concisão e legibilidade do texto.
- **precision = 1.00**: A resposta do modelo é altamente precisa, factual e sem alucinações. Ela converte corretamente o relatório de vulnerabilidade em uma User Story completa com Critérios de Aceitação no formato BDD, alinhando-se perfeitamente à resposta esperada. Trata com exatidão o controle de acesso (HTTP 403 para acesso não autorizado de usuários comuns, 200 para admins), logs de auditoria, severidade ALTA e implementação de middleware RBAC/JWT, sem inventar fatos ou divagar.

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
Como um gerente de vendas, eu quero gerar o relatório de vendas com filtros acima de 1.000 registros em menos de 2 minutos, para que eu possa analisar os dados de vendas no horário comercial sem sofrer com timeouts no navegador.

Critérios de Aceitação:
- Dado que acesso a tela de relatórios e aplico um filtro que excede 1.000 registros
- Quando clico em "Gerar Relatório"
- Então o relatório deve ser processado e exibido com sucesso antes de atingir o timeout de 120 segundos
- E não deve ocorrer timeout no navegador durante a geração
- E a consulta aos dados de vendas deve ser otimizada para o horário comercial

Critérios Técnicos:
- Criar um índice na coluna `data_venda` da tabela de vendas para otimizar a performance da query SQL
- Otimizar a execução da query para suportar volumes superiores a 1.000 registros dentro do limite de tempo aceitável

Contexto Técnico:
- Problema atual: Relatório demora mais de 2 minutos para gerar com filtros acima de 1.000 registros, causando timeout no navegador após 120 segundos
- Causa técnica: Query SQL sem índice na coluna `data_venda`
- Impacto: Lentidão relatada pelos usuários durante o horário comercial
```

- **f1_score = 0.85**: A resposta do modelo é estruturada e cobre quase todos os pontos relevantes do contexto técnico e de negócio. No entanto, houve uma imprecisão importante nos Critérios de Aceitação e na User Story: o modelo definiu como meta apenas gerar em 'menos de 2 minutos' (antes do timeout de 120s), enquanto o esperado exigia uma meta de desempenho inferior a 30 segundos. Isso afetou a precisão da solução proposta e o recall da meta de tempo esperada.
- **clarity = 0.98**: A resposta do modelo possui excelente clareza. Está perfeitamente organizada na estrutura de História de Usuário, Critérios de Aceitação (BDD) e Contexto Técnico. A linguagem é simples, direta e sem ambiguidades, explicitando exatamente o problema, as causas e as soluções. Apresenta concisão ideal, contendo apenas uma leve redundância ao mencionar a ausência de timeout duas vezes nos critérios de aceitação, mas sem comprometer a excelente qualidade da comunicação.
- **precision = 0.98**: A resposta gerada é altamente precisa e totalmente baseada nos dados fornecidos na pergunta (sem alucinações). Ela capturou corretamente o problema do índice na coluna 'data_venda', o timeout de 120s e o impacto no horário comercial. O foco foi perfeito, transformando o problema em uma História de Usuário estruturada. A única divergência sutil em relação ao Ground Truth é que o modelo definiu o critério de sucesso como 'abaixo de 2 minutos' (evitando o timeout), enquanto o Ground Truth estipulou '<30s', mas ambos mantêm a exatidão dos fatos apresentados.

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
Como um sistema de pagamentos, eu quero processar com sucesso o webhook de pagamento aprovado enviado pelo gateway, para que o status do pedido seja atualizado automaticamente para "aprovado".

Critérios de Aceitação:
- Dado que um pedido de R$ 100 foi pago e aprovado no gateway
- Quando o gateway envia a notificação via POST /api/webhooks/payment
- Então o endpoint deve processar a requisição com sucesso (HTTP 200)
- E o status do pedido correspondente deve ser atualizado de "pendente" para "aprovado"
- E os logs não devem registrar erro HTTP 500 no endpoint de webhook

Critérios Técnicos:
- Investigar e corrigir a causa raiz do erro HTTP 500 no endpoint POST /api/webhooks/payment
- Garantir tratamento adequado de exceções e persistência correta dos dados recebidos no payload do webhook

Contexto Técnico:
- Problema atual: POST /api/webhooks/payment retorna HTTP 500
- Sintoma: Sistema não recebe a notificação do gateway e o status do pedido permanece como "pendente" após o pagamento de R$ 100 com cartão de crédito
```

- **f1_score = 0.84**: A resposta gerada é extremamente precisa e relevante, adicionando critérios técnicos coerentes com o problema sem inventar informações incorretas. Quanto ao Recall, cobriu os pontos principais (endpoint, HTTP 200, mudança de status), mas omitiu dois critérios de aceitação presentes no Ground Truth: o envio do e-mail de confirmação ao cliente e o log de auditoria.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está perfeitamente organizada no formato padrão de História de Usuário com critérios em BDD (Dado/Quando/Então), o que elimina qualquer ambiguidade sobre os cenários de teste e solução. A linguagem é direta, precisa e adequada ao contexto técnico. O conteúdo é conciso, sem informações redundantes, permitindo que a equipe de desenvolvimento compreenda imediatamente a causa do problema e o resultado esperado.
- **precision = 0.98**: A resposta gerada é extremamente precisa e baseada estritamente nos fatos fornecidos no prompt (erro HTTP 500 no endpoint, valor de R$ 100, status pendente). Não apresentou alucinações, mantendo-se fiel aos dados passados sem inventar funcionalidades extras. O foco foi perfeito ao transformar o bug report em uma história de usuário estruturada com critérios de aceitação coerentes. Houve apenas uma leve imprecisão conceitual na persona ('sistema de pagamentos' em vez de 'sistema de e-commerce').

### 11. Imagens de produtos não aparecem no Safari. No Chrome funciona normal.

<details><summary>Relato completo</summary>

```text
Imagens de produtos não aparecem no Safari. No Chrome funciona normal.
```
</details>

**Saída do prompt:**

```text
Como um cliente usando o navegador Safari, eu quero visualizar as imagens dos produtos corretamente, para que eu possa avaliar os itens antes de decidir a compra.

Critérios de Aceitação:
- Dado que acesso a página de um produto no navegador Safari
- Quando a página é carregada
- Então as imagens do produto devem ser exibidas corretamente
- E o comportamento visual deve ser idêntico ao apresentado no Google Chrome
- E nenhum erro de carregamento de mídia deve ocorrer no console do navegador
```

- **f1_score = 0.97**: A resposta gerada é extremamente precisa e relevante. A História de Usuário foi reproduzida com perfeição. Nos critérios de aceitação, a precisão é 1.0, pois todas as adições (como a comparação específica com o Chrome e checagem no console) são corretas e úteis. O recall é 0.95, cobrindo praticamente todos os pontos da resposta esperada (navegador, acesso à página, exibição e paridade entre navegadores), apenas trocando a menção explícita ao tempo de carregamento por erros de mídia no console.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está perfeitamente organizada no formato padrão de História de Usuário e Critérios de Aceitação (BDD). A linguagem é simples, objetiva e adequada ao contexto. Não há ambiguidades, pois estabelece claramente o contexto, as ações e os resultados esperados. A resposta é concisa, contendo todas as informações necessárias de forma direta e sem redundâncias.
- **precision = 0.98**: A resposta gerada é altamente precisa e totalmente alinhada à resposta esperada. Não apresentou alucinações, mantendo 100% de foco no problema relatado (imagens no Safari vs. Chrome) ao estruturá-lo no formato de História de Usuário e BDD (Dado/Quando/Então). As pequenas divergências nos critérios de aceitação (como mencionar 'console do navegador' em vez de 'tempo de carregamento') são variações técnicas válidas e pertinentes que preservam a correção factual e a intenção da referência.

### 12. Dashboard mostra contagem errada de usuários ativos. Mostra 50 mas só há 42 na lista.

<details><summary>Relato completo</summary>

```text
Dashboard mostra contagem errada de usuários ativos. Mostra 50 mas só há 42 na lista.
```
</details>

**Saída do prompt:**

```text
Como um administrador visualizando o dashboard, eu quero que a contagem de usuários ativos exiba o número correto correspondente à listagem, para que eu tenha dados confiáveis sobre a base de usuários.

Critérios de Aceitação:
- Dado que estou acessando o dashboard
- Quando visualizo o card de contagem de usuários ativos
- Então o número exibido deve ser exatamente 42
- E deve corresponder ao total de registros presentes na lista de usuários ativos
- E a contagem nunca deve divergir do número real de itens listados
```

- **f1_score = 0.75**: A História de Usuário foi capturada com precisão. A Precisão é 0.8 porque a resposta gerada é relevante, mas cometeu o erro de fixar o número '42' (má prática para ACs) e gerou redundância entre critérios. O Recall é 0.7 pois omitiu pontos essenciais da resposta esperada, como a atualização em tempo real e a regra explícita de filtrar apenas usuários com status 'ativo'.
- **clarity = 0.95**: A resposta gerada apresenta excelente clareza, estruturada no formato padrão de História de Usuário com Critérios de Aceitação (BDD). A organização é impecável e a linguagem é simples, direta e fácil de entender. A mensagem é totalmente sem ambiguidade. Há apenas uma leve redundância entre os dois últimos critérios de aceitação, além de ter fixado o valor dinâmico '42' no texto, mas nada que comprometa a compreensão ou a concisão geral.
- **precision = 0.90**: A resposta gerada reflete com precisão o problema relatado e foca na criação da História de Usuário. Contudo, comete uma pequena imprecisão factual/lógica nos critérios de aceitação ao 'chumbar' o valor 'exatamente 42' como regra fixa, em vez de tratá-lo como um valor dinâmico correspondente ao total real (como na resposta esperada). Não há alucinações graves, pois todos os elementos foram extraídos diretamente do prompt do usuário.

### 13. No iOS, ao girar o celular para landscape, o layout da tela de perfil fica quebrado.

<details><summary>Relato completo</summary>

```text
No iOS, ao girar o celular para landscape, o layout da tela de perfil fica quebrado.
```
</details>

**Saída do prompt:**

```text
Como um usuário de iOS, eu quero que o layout da tela de perfil se ajuste corretamente ao girar o celular para o modo paisagem (landscape), para que eu possa visualizar e editar meus dados sem que elementos fiquem quebrados ou cortados.

Critérios de Aceitação:
- Dado que estou na tela de perfil no aplicativo para iOS
- Quando giro o celular para o modo landscape (paisagem)
- Então o layout da tela de perfil deve se adaptar adequadamente à orientação horizontal
- E todos os campos e botões devem permanecer visíveis e acessíveis
- E nenhum elemento visual deve sobrepor ou cortar informações importantes
```

- **f1_score = 1.00**: A resposta gerada é extremamente precisa e completa. A História de Usuário segue a estrutura correta (Persona, Desejo, Benefício) mantendo o contexto de iOS e orientação em paisagem. Os Critérios de Aceitação em sintaxe BDD cobrem 100% das informações do Ground Truth: contexto da tela de perfil no iOS (Dado), ação de girar para paisagem (Quando) e os resultados esperados de adaptação, visibilidade e ausência de sobreposição (Então/E). Nenhuma informação incorreta ou irrelevante foi inserida.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está perfeitamente organizada no formato padrão de História de Usuário e Critérios de Aceitação (BDD). A linguagem é direta, acessível e precisa. Não há ambiguidades na especificação do comportamento esperado nem redundâncias desnecessárias, cobrindo o problema relatado pelo usuário de forma concisa, legível e estruturada.
- **precision = 1.00**: A resposta gerada é extremamente precisa e alinhada com a resposta esperada. Ela transforma o problema informado em uma história de usuário estruturada com critérios de aceitação no formato BDD (Dado/Quando/Então) equivalentes em significado e escopo aos da referência. Não há presença de alucinações, erros factuais ou desvios do foco.

### 14. Campo de email aceita texto sem @, permitindo cadastros inválidos.

<details><summary>Relato completo</summary>

```text
Campo de email aceita texto sem @, permitindo cadastros inválidos.
```
</details>

**Saída do prompt:**

```text
Como um usuário preenchendo o cadastro, eu quero que o campo de email valide o formato do texto inserido, para que eu não consiga concluir o cadastro com um endereço de email inválido (sem o caractere "@").

Critérios de Aceitação:
- Dado que estou na tela de cadastro
- Quando digito um texto sem o caractere "@" no campo de email
- Então o campo deve exibir um erro indicando que o formato do email é inválido
- E o botão de envio ou avanço do cadastro deve permanecer desabilitado ou barrar a submissão
- E quando preencho um email válido contendo "@", o erro deve desaparecer e o cadastro deve prosseguir normalmente
```

- **f1_score = 1.00**: A resposta gerada cobriu perfeitamente a História de Usuário e todos os Critérios de Aceitação do Ground Truth (validação, exibição de erro explicativo e bloqueio de cadastro). Além disso, adicionou um critério complementar sobre o comportamento ao inserir um email válido, o que é altamente relevante no contexto de BDD/QA, sem introduzir nenhuma informação incorreta.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza, estando perfeitamente organizada no formato padrão de História de Usuário e BDD. A linguagem é simples, direta e profissional. Não há ambiguidades, cobrindo com precisão a regra de validação do e-mail e as consequências na interface. O texto é conciso, sem redundâncias, fornecendo todas as informações necessárias de forma fluida e fácil de entender.
- **precision = 1.00**: A resposta gerada está perfeitamente alinhada com a resposta esperada. Ela transforma a falha relatada em uma User Story bem estruturada com Critérios de Aceitação claros e precisos. Não há alucinações nem erros factuais; os detalhes adicionados (como o comportamento do botão de envio e a validação do fluxo positivo ao inserir um e-mail válido) são desdobramentos lógicos do problema apresentado e enriquecem os critérios sem fugir do foco.

### 15. Botão de adicionar ao carrinho não funciona no produto ID 1234.

<details><summary>Relato completo</summary>

```text
Botão de adicionar ao carrinho não funciona no produto ID 1234.
```
</details>

**Saída do prompt:**

```text
Como um cliente tentando comprar um produto, eu quero que o botão de adicionar ao carrinho funcione no produto ID 1234, para que eu possa concluir a minha compra.

Critérios de Aceitação:
- Dado que estou na página do produto ID 1234
- Quando clico no botão de adicionar ao carrinho
- Então o produto ID 1234 deve ser adicionado ao meu carrinho de compras
- E devo ver uma mensagem de confirmação de que o produto foi adicionado
- E o ícone do carrinho deve atualizar a contagem de itens corretamente
```

- **f1_score = 1.00**: A resposta gerada atendeu perfeitamente a todos os elementos da resposta esperada. A estrutura da história de usuário e os cinco critérios de aceitação (visualização, clique, adição ao carrinho, confirmação visual e atualização do contador) foram completamente cobertos. O modelo adaptou o conteúdo de forma relevante para incluir o ID 1234 citado na pergunta do usuário, mantendo a precisão técnica e sem omitir informações.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está perfeitamente organizada no formato padrão de História de Usuário e Critérios de Aceitação (BDD). A linguagem é simples, direta e fácil de entender. A mensagem é totalmente isenta de ambiguidades, especificando com precisão o produto (ID 1234), as ações do usuário e os comportamentos esperados do sistema. Além disso, é extremamente concisa e objetiva, sem qualquer conteúdo desnecessário.
- **precision = 1.00**: A resposta gerada é extremamente precisa, focada e livre de alucinações. Ela traduz o problema relatado no produto ID 1234 em uma História de Usuário perfeita, com Critérios de Aceitação claros e equivalentes ao Ground Truth. Ao incluir o ID 1234 fornecido pelo usuário, o modelo manteve total fidelidade factual ao contexto da pergunta, mantendo a estrutura padrão de teste BDD/Cucumber.
