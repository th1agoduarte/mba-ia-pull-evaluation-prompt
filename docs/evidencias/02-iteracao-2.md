# Iteração 2: regras de completude, regra dinâmica e anti-redundância

- Experimento: `evaluation-prompt-bug_to_user_story_v2-dc46ad83`
- Prompt: `evaluation-prompt/bug_to_user_story_v2`
- Provider / modelo / juiz: `google` / `gemini-3.5-flash-lite` / `gemini-3.5-flash`
- Data: 2026-11-15 14:49 UTC
- Exemplos: 15

| Métrica | Média | ≥ 0.8 |
|---|---|---|
| helpfulness | 0.9907 | ✓ |
| correctness | 0.9574 | ✓ |
| f1_score | 0.9240 | ✓ |
| clarity | 0.9907 | ✓ |
| precision | 0.9907 | ✓ |
| **média geral** | **0.9707** | ✓ |

**Status: ✅ APROVADO**

## Por exemplo

| # | Relato (início) | F1 | Clarity | Precision |
|---|---|---|---|---|
| 1 | App de produtividade offline-first com bugs críticos de sincronização. | 0.86 | 1.00 | 1.00 |
| 2 | Sistema de relatórios gerenciais com problemas severos de performance  | 0.89 | 1.00 | 1.00 |
| 3 | Sistema de checkout com múltiplas falhas críticas. | 0.96 | 1.00 | 1.00 |
| 4 | Modal de confirmação de exclusão aparece atrás do menu lateral em tela | 0.75 | 0.98 | 1.00 |
| 5 | Carrinho permite finalizar compra mesmo com produto fora de estoque. | 0.92 | 1.00 | 0.98 |
| 6 | App Android trava ao carregar lista de notificações com mais de 50 ite | 0.92 | 0.98 | 1.00 |
| 7 | Pipeline de vendas calcula valor total errado quando há desconto. | 0.92 | 0.90 | 0.97 |
| 8 | Endpoint /api/users/:id retorna dados de qualquer usuário sem validar  | 0.90 | 1.00 | 0.98 |
| 9 | Relatório de vendas demora mais de 2 minutos para gerar quando filtro  | 1.00 | 1.00 | 0.97 |
| 10 | Webhook de pagamento aprovado não está sendo chamado. | 0.92 | 1.00 | 0.98 |
| 11 | Imagens de produtos não aparecem no Safari. No Chrome funciona normal. | 0.97 | 1.00 | 1.00 |
| 12 | Dashboard mostra contagem errada de usuários ativos. Mostra 50 mas só  | 0.87 | 1.00 | 0.98 |
| 13 | No iOS, ao girar o celular para landscape, o layout da tela de perfil  | 0.97 | 1.00 | 1.00 |
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
Como um vendedor em campo utilizando o app offline-first, eu quero que minhas alterações e anexos sejam sincronizados de forma íntegra, ordenada e resiliente, para que eu não perca dados importantes, compromissos ou oportunidades de vendas.

=== USER STORY PRINCIPAL ===

Título: Sincronização offline robusta com resolução de conflitos, retentativa de anexos, ordenação cronológica e paginação de lote

Descrição:
Como um vendedor em campo, eu quero que a sincronização do app gerencie conflitos de edição, retome uploads interrompidos, respeite a ordem cronológica das ações e processe grandes volumes de dados em lotes, para que meus dados fiquem seguros e acessíveis independentemente da qualidade da minha conexão.

=== CRITÉRIOS DE ACEITAÇÃO ===

A. Conflito de dados - Resolução interativa:
- Dado que o Usuário A e o Usuário B editaram offline a mesma tarefa #123
- Quando ambos realizam a sincronização com o servidor
- Então o sistema deve detectar o conflito de edição em vez de aplicar "last write wins"
- E deve apresentar uma tela de resolução de conflito para que o usuário escolha a versão correta ou mescle os dados
- E o Usuário A deve ser notificado sobre a sobreposição de dados

B. Sincronização - Retomada de upload de anexos:
- Dado que estou anexando um PDF de 50MB em uma tarefa via 4G
- Quando a conexão cai e é restabelecida durante o envio
- Então o app deve retomar o upload a partir do último byte enviado (chunked upload / resumable upload)
- E após o limite de 5 tentativas sem sucesso, o upload deve falhar explicitamente
- E o app deve exibir uma mensagem clara de erro informando a falha, sem marcar incorretamente a tarefa como sincronizada

C. Ordenação - Respeito ao timestamp client-side:
- Dado que realizei operações offline em sequência (Criação às 10:00, Edição às 10:15 e Deleção às 10:30 da Tarefa A)
- Quando o dispositivo recupera a conexão e envia a fila de sincronização
- Então o servidor deve processar as operações respeitando estritamente o timestamp client-side
- E a Tarefa A deve ser definitivamente deletada, evitando o erro 404 e o reaparecimento incorreto do registro

D. Memória - Sincronização em lotes paginados:
- Dado que acumulei 1.500 operações pendentes após 1 semana offline
- Quando retorno para uma área com WiFi e a sincronização é iniciada
- Então o app deve processar as operações em lotes paginados para evitar o estouro de memória
- E o consumo de memória do app deve permanecer abaixo do limite de 700MB no iOS e evitar OutOfMemoryError no Android
- E todas as 1.500 operações pendentes devem ser sincronizadas com sucesso

=== CRITÉRIOS TÉCNICOS ===

Resolução de Conflitos:
- Implementar algoritmo de detecção de conflitos baseado em vetor de versões (version vectors) ou carimbo de data/hora por campo, acionando interface de merge ou notificação quando houver colisão.

Upload Resiliente:
- Substituir o envio em requisição única por protocolo de upload particionado (resumable upload), permitindo persistir o ponteiro de bytes enviados localmente na base SQLite/Room do dispositivo.

Ordenação de Fila:
- Ordenar a fila de sincronização no cliente e forçar o motor de ingestão do backend a processar o payload estritamente baseado no vetor de tempo (`client_timestamp`), independentemente da ordem de chegada dos pacotes HTTP.

Paginação de Lote:
- Implementar processamento em lotes (batching) com limite de itens por transação (ex.: lotes de 100 itens) na rotina de sync, liberando referências da memória RAM após a confirmação (ACK) de cada lote pelo servidor.

=== CONTEXTO DO BUG ===

Severidade: CRÍTICA
Impacto: 250+ usuários afetados, NPS caiu de 8.5 para 4.2, 80% dos reviews negativos citam "perda de dados", churn rate aumentou 15%, R$ 200k perdidos em oportunidades

Problemas Identificados:
1. Merge incorreto com "last write wins" causa perda de dados de edição
2. Upload de anexo grande reinicia do zero ao cair a conexão e marca tarefa como sincronizada em caso de falha definitiva
3. Servidor recebe operações fora de ordem gerando erro 404 e ressurreição de itens deletados
4. Sincronização de 1.500 itens de uma só vez estoura a memória e causa crash no iOS e Android

=== TASKS TÉCNICAS SUGERIDAS ===

1. [BACKEND] Ajustar motor de ingestão de sync para ordenar operações por client_timestamp
2. [MOBILE] Implementar lógica de chunked/resumable upload para arquivos grandes
3. [MOBILE] Adicionar paginação na rotina de sincronização de filas longas para proteger o uso de memória (iOS/Android)
4. [FULLSTACK] Desenvolver mecanismo de detecção de conflitos de edição concorrente e interface de resolução para o usuário
5. [TESTES] Criar cenários de testes automatizados simulando perda intermitente de conexão e concorrência offline
```

- **f1_score = 0.86**: A resposta gerada é altamente precisa e alinhada ao contexto, sem dados incorretos ou alucinações. Cobriu com clareza os Critérios de Aceitação (A a D), contexto do bug e tarefas principais. No entanto, o recall foi reduzido pois omitiu a seção de Métricas de Sucesso, os detalhamentos técnicos específicos do Ground Truth (como snippets de JSON, especificação do protocolo HTTP e algoritmo detalhado de batch) e o plano de tarefas dividido em 4 fases, simplificando-o em apenas 5 tarefas gerais.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está perfeitamente organizada em seções lógicas (User Story, Critérios de Aceitação em formato BDD, Critérios Técnicos e Tasks). A linguagem é direta, utilizando termos técnicos precisos sem obscuridade. Não há ambiguidades nos critérios estabelecidos, facilitando o entendimento por equipes de produto e desenvolvimento. Além disso, é extremamente concisa e objetiva, cobrindo todos os pontos críticos reportados sem redundâncias.
- **precision = 1.00**: A resposta gerada é extremamente precisa, alinhada ao contexto e livre de alucinações. Aborda corretamente todos os 4 problemas relatados (conflitos de dados, retomada de uploads de 50MB, ordenação por timestamp e paginação para conter o uso de memória em 700MB/iOS). As especificações e tarefas técnicas sugeridas são totalmente pertinentes para resolver as falhas descritas, mantendo fidelidade absoluta às métricas de impacto e severidade do problema.

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
Como um gestor de empresas no SaaS, eu quero acessar relatórios gerenciais rápidos, com dados financeiros precisos, cache atualizado e exportações seguras, para que eu possa acompanhar métricas confiáveis e tomar decisões estratégicas sem lentidão ou falhas no sistema.

=== USER STORY PRINCIPAL ===

Título: Desempenho, consistência de dados e estabilidade nos relatórios gerenciais

Descrição:
Como um usuário do sistema de relatórios gerenciais, eu quero um dashboard rápido, cálculo unificado de MRR, cache atualizado em tempo real e exportações que não derrubem o servidor, para que eu tenha confiança nos dados e uma experiência estável.

=== CRITÉRIOS DE ACEITAÇÃO ===

A. Performance - Carregamento otimizado do dashboard executivo:
- Dado que estou acessando o dashboard executivo via GET /api/reports/executive-dashboard
- Quando o sistema busca métricas, departamentos e usuários
- Então o tempo de resposta deve ser inferior ao SLA de 3 segundos
- E a consulta não deve gerar queries N+1 para buscar dados por departamento ou empresa

B. Lógica de Negócio - Cálculo padronizado de MRR (Monthly Recurring Revenue):
- Dado que o sistema consolida as receitas recorrentes
- Quando consulto o MRR no dashboard, no relatório financeiro ou em exportações
- Então o valor calculado deve seguir a regra oficial de considerar apenas assinaturas ativas e pró-rata de upgrades/downgrades
- E todas as telas e relatórios devem apresentar exatamente o mesmo valor consolidado, sem divergências

C. Cache - Invalidação automática e dados atualizados no Redis:
- Dado que o cache Redis possui TTL configurado
- Quando um cliente realiza um upgrade de plano
- Então o cache correspondente deve ser invalidado imediatamente
- E o dashboard deve refletir o plano atualizado sem esperar o período de 24 horas

D. Concorrência - Exportação estável de relatórios em massa:
- Dado que solicito a exportação de um relatório anual com 365 dias e 50k linhas
- Quando o processo de geração do CSV é executado
- Então o consumo de memória não deve ultrapassar o limite de 2GB
- E o servidor não deve sofrer OOM Kill nem impactar a performance de outras requisições

=== CRITÉRIOS TÉCNICOS ===

Performance:
- Substituir as queries N+1 por consultas agregadas utilizando `JOIN` ou `IN` clauses no banco de dados

Negócio:
- Consolidar a regra de cálculo de MRR em um único serviço centralizado de domínio financeiro

Cache:
- Implementar mecanismo de invalidação de cache acoplado ao evento de alteração de plano do cliente

Concorrência:
- Processar a exportação de CSV em background utilizando streams e paginação para controlar o consumo de CPU e memória

=== CONTEXTO DO BUG ===

Severidade: CRÍTICA
Impacto: 15 clientes enterprise ameaçando cancelar contrato, CEO sem confiança para apresentar ao board, time de CS gastando 40h/semana explicando discrepâncias, impossibilidade de fazer forecasting confiável

Problemas Identificados:
1. Query N+1 no dashboard executivo gera 101 queries e estoura SLA de 3s
2. Cálculo de MRR inconsistente entre dashboard, relatório financeiro e planilha contábil
3. Cache Redis desatualizado por até 24 horas após upgrade de plano
4. Exportação de CSV causa 100% de CPU e estoura memória (OOM Kill a 4GB)

=== TASKS TÉCNICAS SUGERIDAS ===

1. [BACKEND] Refatorar query do GET /api/reports/executive-dashboard para eliminar N+1
2. [BACKEND] Unificar regra de cálculo de MRR em serviço compartilhado
3. [CACHE] Ajustar invalidate do Redis em eventos de alteração de plano
4. [BACKEND] Implementar processamento em background via stream para exportação de CSV
5. [INFRA] Configurar limites de memória e monitoramento para processos pesados
```

- **f1_score = 0.89**: A resposta gerada possui precisão máxima (1.0), sem alucinações ou erros técnicos, mantendo perfeita coerência com o contexto. O recall é 0.80 pois, embora tenha coberto com sucesso a User Story, os 4 Critérios de Aceitação e o Contexto do Bug, omitiu detalhes presentes no Ground Truth como a query SQL de exemplo, a estratificação de cache (tempo real/5min/1h) e a divisão detalhada das tarefas técnicas em 3 Sprints (gerou apenas 5 tarefas genéricas).
- **clarity = 1.00**: A resposta possui clareza exemplar. É organizada em seções lógicas e bem delimitadas (User Story, Critérios de Aceitação BDD, Critérios Técnicos e Tasks). Utiliza linguagem técnica precisa e direta, sem redundâncias ou jargões desnecessários. O formato Given-When-Then (Dado/Quando/Então) nos critérios de aceitação garante total ausência de ambiguidade quanto aos comportamentos esperados do sistema.
- **precision = 1.00**: A resposta gerada é extremamente precisa, sem alucinações e totalmente baseada nos dados fornecidos no contexto. Ela traduz perfeitamente os 4 problemas relatados (N+1 no dashboard, cálculo de MRR, cache Redis desatualizado e exportação em CSV com OOM) em uma User Story bem estruturada, Critérios de Aceitação rigorosos, Soluções Técnicas adequadas e Tarefas acionáveis. O foco foi mantido 100% no problema, mantendo total correção factual.

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
Como um cliente finalizando uma compra, eu quero que o checkout seja seguro, processe pagamentos e cupons de forma confiável e me informe claramente caso ocorra uma lentidão, para que eu possa concluir minha transação com segurança e sem cobranças incorretas.

=== USER STORY PRINCIPAL ===

Título: Correção de falhas críticas de segurança, integração e concorrência no checkout

Descrição:
Como um cliente do e-commerce, eu quero um fluxo de checkout protegido contra vulnerabilidades, estável nas transações de pagamento, preciso no controle de cupons de desconto e transparente em casos de timeout, para que minha experiência de compra seja segura e confiável.

=== CRITÉRIOS DE ACEITAÇÃO ===

A. Segurança - Sanitização do campo de cupom:
- Dado que estou na tela de checkout no campo de cupom
- Quando insiro caracteres maliciosos como `<script>alert('xss')</script>` e tento aplicar
- Então o sistema deve sanitizar a entrada e recusar a execução de scripts
- E o campo deve exibir apenas caracteres válidos ou mensagem de erro de formato

B. Integração - Resiliência e consistência no processamento de pagamento:
- Dado que submeto o pagamento via POST /api/payment/process
- Quando ocorre lentidão ou timeout no gateway de pagamento
- Então o sistema deve tratar a falha sem esgotar o pool de conexões do Postgres
- E se o pagamento for confirmado, o pedido deve ser criado com sucesso, evitando cobranças sem registro do pedido

C. Lógica de Negócio - Controle atômico de limite de cupons:
- Dado que um cupom possui limite máximo de usos, como o "PROMO10" limitado a 100 usos
- Quando múltiplos clientes aplicam o cupom simultaneamente
- Então a contagem e a verificação de uso devem ocorrer de forma atômica
- E o sistema deve bloquear o uso do cupom exatamente ao atingir o limite de 100 utilizações

D. UX - Tratamento de timeout no pagamento:
- Dado que a requisição de pagamento excede 30 segundos
- Quando o timeout é atingido
- Então a tela de loading com o spinner deve ser encerrada
- E devo visualizar uma mensagem clara informando o status do processamento e orientando sobre os próximos passos

=== CRITÉRIOS TÉCNICOS ===

Segurança:
- Implementar sanitização e escape estrito de inputs no campo de cupom para prevenir XSS

Integração:
- Otimizar o gerenciamento do connection pool do Postgres e implementar tratamento de retry/circuit breaker para chamadas ao POST /api/payment/process

Concorrência:
- Utilizar transações com bloqueio adequado (SELECT ... FOR UPDATE) ou operações atômicas para validar e decrementar/incrementar o limite de uso de cupons

UX e Resiliência:
- Configurar timeout de requisição no front-end com tempo limite de 30s para exibir feedback visual e estado de erro descritivo ao usuário

=== CONTEXTO DO BUG ===

Severidade: CRÍTICA
Impacto: 150+ clientes afetados na última semana, perda estimada de R$ 15.000 em cupons indevidos, 45 tickets de suporte abertos, rating do app caiu de 4.5 para 3.2 estrelas

Problemas Identificados:
1. XSS não sanitizado no campo de cupom
2. POST /api/payment/process retorna 504 Gateway Timeout por esgotamento do connection pool no Postgres
3. Race condition permite uso excessivo do cupom "PROMO10" além do limite de 100 usos
4. Loading infinito (spinner eterno) após timeout de pagamento superior a 30s

=== TASKS TÉCNICAS SUGERIDAS ===

1. [SEGURANÇA] Sanitizar entrada de dados no campo de cupom no front-end e back-end
2. [BACKEND] Ajustar o gerenciamento do connection pool do Postgres e o tratamento de timeout do gateway
3. [BANCO DE DADOS] Implementar atomicidade no controle de limite de cupons para evitar race conditions
4. [FRONTEND] Tratar o timeout de 30s removendo o spinner e exibindo mensagem amigável ao usuário
5. [TESTES] Executar testes de carga, concorrência em cupons e varredura de segurança contra XSS
```

- **f1_score = 0.96**: A resposta gerada é extremamente precisa e alinhada ao Ground Truth, sem alucinações ou informações incorretas (Precision = 1.0). Todos os pontos principais (Segurança, Integração, Concorrência e UX) foram bem contemplados nos critérios de aceitação, técnicos e tarefas. O Recall é alto (0.92), com pequenas omissões de detalhes específicos presentes no GT, como o uso explícito de CSP headers, Redis INCR, métricas de monitoramento (>5% timeout rate) e detalhamento de infraestrutura como task separada.
- **clarity = 1.00**: A resposta gerada apresenta excelente organização, estruturando a informação no formato de User Story, critérios de aceitação BDD (Dado-Quando-Então), requisitos técnicos e tasks. A linguagem é precisa, direta e profissional, eliminando qualquer ambiguidade. O texto é extremamente conciso e vai direto ao ponto, cobrindo todos os 4 problemas relatados sem redundâncias.
- **precision = 1.00**: A resposta gerada é extremamente precisa, sem alucinações e totalmente alinhada ao contexto fornecido e à resposta esperada. Ela cobriu exatamente os quatro problemas relatados (XSS, esgotamento do pool de conexões/timeout no gateway, race condition no cupom PROMO10 e spinner infinito na UX). Os critérios de aceitação, especificações técnicas e tarefas propostas abordam diretamente as causas raízes e impactos sem inventar dados não verificáveis.

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
Como um usuário em uma tela pequena (< 768px), eu quero que o modal de confirmação de exclusão seja exibido acima do menu lateral, para que eu possa interagir com os botões do modal sem precisar fechar o menu lateral primeiro.

Critérios de Aceitação:
- Dado que estou acessando o sistema em uma tela com largura menor que 768px
- Quando abro o menu lateral e aciono a exclusão de um item
- Então o modal de confirmação de exclusão deve ser exibido sobreposto ao menu lateral
- E devo conseguir clicar nos botões de confirmação e cancelamento do modal sem impedimentos
- E o z-index do modal de confirmação deve ser superior ao z-index do menu lateral (maior que 1050)

Critérios Técnicos:
- Ajustar o z-index do modal de confirmação para um valor superior a 1050 (por exemplo, 1100 ou superior, garantindo prioridade sobre o menu lateral que possui z-index 1050)

Contexto Técnico:
- Problema atual: Modal com z-index 1000 fica oculto atrás do menu lateral com z-index 1050 em viewports < 768px
- Valores atuais: z-index do modal = 1000, z-index do menu lateral = 1050
- Impacto: Bloqueio da experiência do usuário, impedindo cliques diretos nos botões do modal de exclusão
```

- **f1_score = 0.75**: A resposta gerada obteve precisão perfeita (1.0), pois todas as informações apresentadas são corretas, coerentes e diretamente relevantes ao problema. O recall foi de 0.60 devido à omissão de pontos importantes presentes no Ground Truth, principalmente a seção inteira de Critérios de Acessibilidade (foco do teclado, fechar com ESC, clique no backdrop) e alguns Critérios de Aceitação específicos (desfocar o menu/backdrop e largura do modal de pelo menos 90%).
- **clarity = 0.98**: A resposta gerada possui excelente clareza, estando impecavelmente organizada no formato padrão de História de Usuário (User Story). A linguagem é precisa, direta e extremamente fácil de compreender. Não há ambiguidades quanto ao problema relatado (z-index) ou à solução proposta. O texto é conciso e focado, apresentando apenas uma leve repetição dos valores de z-index entre os critérios de aceitação e técnicos, o que é comum e aceitável nesse tipo de documentação.
- **precision = 1.00**: A resposta do modelo é precisa, factual e totalmente alinhada ao contexto fornecido. Ela identifica corretamente o problema de z-index (modal 1000 vs menu 1050 em telas < 768px) e propõe a solução técnica adequada (ajustar z-index do modal para > 1050). Não foram encontradas alucinações ou informações incorretas em relação ao Ground Truth e à pergunta.

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
Como um cliente comprando na loja, eu quero que o sistema impeça a adição e a finalização de compra de produtos sem estoque, para que eu não compre itens indisponíveis e evite frustrações com entregas não realizadas.

Critérios de Aceitação:
- Dado que um produto possui estoque limitado a 2 unidades
- Quando as 2 unidades são adicionadas ao carrinho pelo Cliente A
- Então o estoque disponível deve ser atualizado para zero
- E o sistema deve impedir que o Cliente B adicione unidades adicionais desse produto ao carrinho
- E o sistema deve bloquear a finalização da compra se houver itens esgotados no carrinho, exibindo mensagem clara
- E o sistema não deve gerar pedidos para produtos sem estoque

Contexto Técnico:
- Bug atual: Concorrência de estoque permite que clientes adicionem e finalize a compra de produtos com estoque zerado
- Implementar validação de estoque atômica no momento da adição ao carrinho e no fechamento do pedido (checkout)
- Reservar o estoque temporariamente ao adicionar o produto ou validar no momento da transação para evitar overselling
```

- **f1_score = 0.92**: A resposta gerada é altamente precisa e relevante. A Precision (0.95) é alta pois todas as informações e critérios propostos são corretos e aplicáveis ao bug. O Recall (0.90) é elevado por cobrir a validação no checkout, bloqueio de pedidos sem estoque, exibição de mensagem clara e reserva temporária. Omitiu apenas a instrução específica de sugerir ao usuário remover o item ou aguardar reposição.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Estrutura-se de forma muito bem organizada em seções distintas (História de Usuário, Critérios de Aceitação e Contexto Técnico). A linguagem é direta, acessível e usa o formato BDD (Dado/Quando/Então), o que elimina ambiguidades sobre os cenários e comportamentos esperados do sistema. É concisa, objetiva e aborda exatamente a solução do bug relatado sem redundâncias.
- **precision = 0.98**: A resposta gerada é altamente precisa e não apresenta alucinações. Ela traduz o bug relatado em uma história de usuário estruturada com critérios de aceitação e contexto técnico alinhados à resposta esperada. Foca exatamente no problema de concorrência de estoque e overselling. A única pequena variação é a perspectiva da História de Usuário ('Como um cliente' vs 'Como o sistema'), mas a solução técnica proposta (validação atômica e reserva de estoque) é factualmente correta e equivalente.

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
Como um usuário do app Android, eu quero que a lista de notificações carregue de forma fluida mesmo com muitos registros, para que o aplicativo não trave ao exibir o histórico de mensagens.

Critérios de Aceitação:
- Dado que abro a tela de notificações e tenho mais de 50 itens
- Quando a lista é carregada
- Então a interface não deve congelar e o carregamento deve ocorrer em menos de 2 segundos
- E não deve ocorrer nenhum erro de ANR (Application Not Responding)
- E a listagem deve implementar paginação para exibir os itens em blocos (infinite scroll ou carregamento sob demanda)
- E o processamento de dados e requisições de rede devem ser executados em uma Thread secundária (background), mantendo a Thread principal livre

Critérios Técnicos:
- Implementar paginação no carregamento da lista de notificações (carregando lotes de itens por vez)
- Deslocar a lógica de busca de dados e mapeamento para uma Thread em segundo plano, utilizando corrotinas ou threads dedicadas para evitar bloqueio da UI Thread

Contexto Técnico:
- Problema atual: App Android trava por 5-10 segundos e gera ANR ao carregar mais de 50 notificações
- Causa raiz: Ausência de paginação e processamento síncrono de grande volume de dados diretamente na Thread principal
```

- **f1_score = 0.92**: A resposta gerada possui precisão máxima (1.0), pois todas as informações são corretas, coerentes e relevantes para o problema. O recall é 0.85 porque abrangeu quase todos os pontos essenciais do Ground Truth (história do usuário, ausência de ANR, tempo <2s, paginação e background thread), mas omitiu detalhes técnicos específicos contidos na resposta esperada, como a quantidade exata de itens por lote (20 itens) e o uso explícito de RecyclerView com ViewHolder pattern.
- **clarity = 0.98**: A resposta gerada apresenta excelente clareza e estrutura bem definida (História de Usuário, Critérios de Aceitação e Contexto Técnico). A linguagem é direta, técnica na medida certa e sem ambiguidades, transmitindo os requisitos de forma acionável. A organização lógica é impecável. O único detalhe em concisão é a leve repetição sobre paginação e processamento em background entre os Critérios de Aceitação e Técnicos, mas sem comprometer a excelente qualidade.
- **precision = 1.00**: A resposta do modelo é altamente precisa, factual e totalmente alinhada com o problema relatado e a resposta esperada. Não contém alucinações, aborda diretamente o problema de ANR e concorrência na Main Thread, e propõe a solução correta (paginação e background thread com corrotinas) mantendo o formato de História de Usuário exigido.

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
Como um gerente de vendas, eu quero que o pipeline de vendas aplique o desconto corretamente sobre o valor total dos produtos, para que o valor exibido nas negociações esteja correto e evite divergências comerciais.

Critérios de Aceitação:
- Dado que uma negociação contém o Produto A no valor de R$ 1.000 e o Produto B no valor de R$ 500
- Quando um desconto de 10% é aplicado à negociação
- Então o valor total calculado deve ser de R$ 1.350
- E o sistema não deve aplicar o desconto apenas sobre o primeiro produto
- E o valor mostrado na interface deve refletir o total com o desconto global corretamente aplicado

Exemplo de Cálculo:
- Subtotal dos produtos: R$ 1.000,00 + R$ 500,00 = R$ 1.500,00
- Aplicação do desconto de 10%: R$ 1.500,00 - (15% 10% de R$ 1.500,00) = R$ 1.500,00 - R$ 150,00
- Valor total esperado: R$ 1.350,00

Critérios Técnicos:
- Ajustar a lógica de cálculo do pipeline para que o percentual de desconto seja aplicado sobre a soma de todos os itens da negociação e não de forma isolada no primeiro item da lista.

Contexto Técnico:
- Problema atual: O sistema aplica o desconto de 10% apenas no primeiro produto (R$ 1.000 com 10% = R$ 900 + R$ 500 = R$ 1.400)
- Valor atual mostrado: R$ 1.400 | Valor esperado: R$ 1.350
```

- **f1_score = 0.92**: A resposta gerada é extremamente precisa e relevante, contendo a história de usuário, contexto técnico detalhado e exemplo correto, com apenas um pequeno erro de digitação ('15% 10%'). Quanto ao recall, a resposta cobriu quase tudo, mas tornou os critérios de aceitação específicos ao exemplo em vez de manter a regra genérica, omitindo a fórmula matemática explícita e o requisito de exibir o detalhamento (subtotal, desconto e total).
- **clarity = 0.90**: A resposta está muito bem organizada em seções lógicas (História de Usuário, Critérios de Aceitação e Contexto Técnico). A linguagem é simples e transmite a solução sem ambiguidades. Contudo, há um pequeno erro de digitação no exemplo de cálculo ('(15% 10% de R$ 1.500,00)'), o que prejudica ligeiramente a fluidez da leitura, embora não comprometa o entendimento final. A concisão é adequada ao padrão de documentação.
- **precision = 0.97**: A resposta gerada é altamente precisa, responde exatamente ao problema reportado e segue a estrutura esperada. Não foram detectadas alucinações de dados. O único pequeno deslize ocorre no Exemplo de Cálculo, onde há um erro de digitação no trecho '(15% 10% de R$ 1.500,00)', embora o valor final calculado (R$ 150,00 e total de R$ 1.350,00) esteja factual e matematicamente correto.

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
Como um administrador do sistema, eu quero que o endpoint /api/users/:id valide as permissões de acesso, para que usuários comuns não possam visualizar dados pessoais de outros usuários.

Critérios de Aceitação:
- Dado que estou autenticado como um usuário comum
- Quando faço uma requisição GET para o endpoint /api/users/:id de outro usuário
- Então o sistema deve retornar o código de status HTTP 403 (Forbidden)
- E os dados pessoais como email, telefone e endereço não devem ser expostos na resposta
- E o acesso deve ser permitido apenas quando o usuário autenticado possuir o perfil de administrador ou for o próprio usuário consultado

Critérios Técnicos:
- Implementar middleware de autorização baseado em papéis (RBAC) no endpoint /api/users/:id para verificar se o usuário autenticado é admin ou é o dono do recurso

Contexto de Segurança:
- Severidade: ALTA - vazamento de dados pessoais (LGPD/GDPR)
- Problema atual: GET /api/users/:id permite que usuários comuns acessem dados sensíveis de administradores (como o usuário ID 100 acessando ID 1) sem validação de permissões
```

- **f1_score = 0.90**: A resposta gerada é altamente precisa e relevante, identificando corretamente o erro HTTP 403, a restrição de acesso a dados próprios/admin e o uso de middleware RBAC. Contudo, o recall foi impactado pela ausência da exigência do log de auditoria para acessos administrativos e pela falta da referência à OWASP A01:2021 presentes no Ground Truth.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está perfeitamente organizada em seções lógicas (História de Usuário, Critérios de Aceitação, Critérios Técnicos e Contexto de Segurança). A linguagem é direta e objetiva, utilizando o formato padrão BDD (Dado/Quando/Então) de maneira impecável. Não há ambiguidades quanto às regras de acesso ou códigos HTTP esperados, e o conteúdo é extremamente conciso, transmitindo todas as informações necessárias sem redundâncias.
- **precision = 0.98**: A resposta é excelente e altamente precisa. Não há alucinações (1.0), estando 100% alinhada ao problema relatado. O foco é total (1.0) na estruturação dos critérios de aceitação e contexto de segurança. A correção factual (0.95) é quase perfeita, cobrindo retorno HTTP 403, proteção de dados (email, telefone, endereço) e validação RBAC, divergindo do Ground Truth apenas pontualmente na persona da história de usuário ('administrador' em vez de 'sistema') e na menção explícita a logs de auditoria.

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
Como um gerente de vendas, eu quero gerar o relatório de vendas em poucos segundos mesmo para filtros com mais de 1000 registros, para que eu possa analisar os dados rapidamente durante o horário comercial sem enfrentar erros de timeout.

Critérios de Aceitação:
- Dado que acesso a tela de relatórios de vendas
- Quando seleciono um filtro que abrange mais de 1000 registros e clico em "Gerar Relatório"
- Então o relatório deve ser gerado e exibido na tela em menos de 10 segundos
- E não deve ocorrer timeout após 120 segundos
- E o sistema deve lidar eficientemente com o volume de dados sem lentidão no horário comercial

Critérios Técnicos:
- Criar um índice (index) na coluna `data_venda` na tabela de vendas para otimizar a performance da query SQL
- Otimizar a consulta de banco de dados para evitar varreduras completas na tabela (full table scan)

Contexto Técnico:
- Problema atual: Query SQL sem index na coluna `data_venda`
- Impacto: Relatório demora mais de 2 minutos para gerar para filtros acima de 1000 registros
- Sintoma: Timeout do navegador após 120 segundos e reclamações de lentidão no horário comercial
```

- **f1_score = 1.00**: A resposta gerada atendeu perfeitamente à resposta esperada. A História de Usuário e os Critérios de Aceitação foram cobertos integralmente, incluindo o tempo de resposta (10s atende a <30s), ausência de timeout e performance em horário comercial. O Contexto e Critérios Técnicos abordaram com precisão a ausência do índice na coluna `data_venda` e a otimização da query SQL. Nenhuma informação incorreta ou irrelevante foi inserida.
- **clarity = 1.00**: A resposta gerada apresenta clareza exemplar. É extremamente bem organizada, estruturada nos formatos padrão de User Story e BDD (Dado/Quando/Então), o que facilita a compreensão rápida. A linguagem é simples, direta e precisa, utilizando jargões técnicos apenas quando necessário e adequado ao contexto. A mensagem é completamente livre de ambiguidades, definindo critérios mensuráveis (como limite de 10 segundos) e ações técnicas bem delimitadas. Além disso, é concisa, focando estritamente na resolução do problema informado sem incluir redundâncias.
- **precision = 0.97**: A resposta gerada é precisa, focada e estruturada corretamente em formato de História de Usuário. Não apresenta alucinações e utiliza todos os dados fornecidos no contexto (falta de índice em data_venda, timeout de 120s, lentidão no horário comercial e filtro de 1000+ registros). A única pequena variação factual em relação à resposta esperada foi estipular o tempo limite de execução em 'menos de 10 segundos' (em vez de 'menos de 30 segundos'), o que permanece factível e adequado à solicitação.

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
Como o sistema de processamento de pagamentos, eu quero processar com sucesso as notificações de webhook enviadas pelo gateway, para que o status do pedido seja atualizado automaticamente para "aprovado" após a confirmação do pagamento.

Critérios de Aceitação:
- Dado que um pagamento de R$ 100 foi aprovado no gateway de pagamento
- Quando o gateway envia a notificação via POST /api/webhooks/payment
- Então o endpoint deve processar a requisição com sucesso e retornar HTTP 200
- E o status do pedido correspondente deve ser atualizado de "pendente" para "aprovado"
- E um log de auditoria deve registrar o recebimento bem-sucedido do webhook

Critérios Técnicos:
- Corrigir o erro HTTP 500 no endpoint POST /api/webhooks/payment
- Tratar exceções não tratadas e garantir a resiliência no mapeamento dos dados enviados pelo gateway

Contexto Técnico:
- Bug atual: O endpoint POST /api/webhooks/payment retorna HTTP 500 ao receber a notificação do gateway
- Sintoma: Pedidos permanecem com status "pendente" mesmo após a aprovação do pagamento no gateway
```

- **f1_score = 0.92**: A resposta gerada obteve precisão perfeita (1.0), pois todas as informações apresentadas são corretas, bem estruturadas e diretamente relevantes ao problema. Quanto ao recall (0.85), o modelo cobriu com sucesso quase todos os elementos da resposta esperada: história de usuário, retorno HTTP 200, transição de status ('pendente' para 'aprovado'), registro em log de auditoria e contexto técnico. A única omissão foi o critério de envio do e-mail de confirmação ao cliente.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está perfeitamente organizada no formato de História de Usuário e critérios BDD (Dado/Quando/Então), o que torna a leitura fluida e estruturada. A linguagem é direta, profissional e precisa, utilizando termos adequados sem rebuscamento excessivo. Não apresenta ambiguidades, definindo exatamente o comportamento esperado, a rota e a solução da falha (HTTP 500). Por fim, é concisa e objetiva, cobrindo todos os pontos necessários sem qualquer redundância.
- **precision = 0.98**: A resposta do modelo é altamente precisa, focada e livre de alucinações. Ela transforma o relato do bug em uma história de usuário bem estruturada com critérios de aceitação e contexto técnico coerentes com o problema relatado (erro HTTP 500 no endpoint POST /api/webhooks/payment). Todas as informações derivam diretamente do prompt. Em comparação com a resposta esperada (Ground Truth), a única omissão foi a menção ao envio de e-mail de confirmação ao cliente, mas todos os demais pontos chave foram contemplados com exatidão factual.

### 11. Imagens de produtos não aparecem no Safari. No Chrome funciona normal.

<details><summary>Relato completo</summary>

```text
Imagens de produtos não aparecem no Safari. No Chrome funciona normal.
```
</details>

**Saída do prompt:**

```text
Como um usuário acessando a loja pelo navegador Safari, eu quero visualizar as imagens dos produtos corretamente, para que eu possa avaliar os itens antes de comprá-los.

Critérios de Aceitação:
- Dado que acesso a página de produtos utilizando o navegador Safari
- Quando a página é carregada
- Então todas as imagens dos produtos devem ser exibidas corretamente
- E a renderização deve ser consistente com o comportamento observado no Chrome
- E nenhuma imagem deve apresentar falha de carregamento ou espaço em branco
```

- **f1_score = 0.97**: A precisão é 1.0 pois toda a resposta é correta, relevante e sem alucinações. O recall é 0.95 pois a resposta gerada cobriu a User Story e quase todos os critérios de aceitação da resposta esperada com excelente equivalência semântica. A resposta gerada inclusive melhorou a especificação ao citar o Chrome (mencionado no problema original), omitindo apenas o detalhe explícito sobre o 'tempo de carregamento'.
- **clarity = 1.00**: A resposta apresenta excelente clareza. Está perfeitamente organizada no formato de História de Usuário e Critérios de Aceitação (BDD). A linguagem é simples, direta e acessível. Não há ambiguidades, definindo claramente o comportamento esperado no Safari em relação ao Chrome. A mensagem é concisa e foca estritamente na solução do problema sem redundâncias.
- **precision = 1.00**: A resposta gerada é extremamente precisa, sem alucinações e totalmente focada na resolução do problema relatado. O modelo transformou a reclamação sobre o Safari/Chrome em uma User Story impecável com Critérios de Aceitação no formato BDD, perfeitamente alinhada com a resposta esperada. Inclusive, a menção direta ao Chrome nos critérios reflete com fidelidade o contexto original do usuário.

### 12. Dashboard mostra contagem errada de usuários ativos. Mostra 50 mas só há 42 na lista.

<details><summary>Relato completo</summary>

```text
Dashboard mostra contagem errada de usuários ativos. Mostra 50 mas só há 42 na lista.
```
</details>

**Saída do prompt:**

```text
Como um gerente de produto, eu quero que o dashboard exiba a contagem exata de usuários ativos, para que eu possa acompanhar métricas confiáveis de engajamento da base.

Critérios de Aceitação:
- Dado que acesso o dashboard do sistema
- Quando o sistema calcula a quantidade de usuários ativos
- Então o número exibido no contador deve corresponder exatamente ao total real de registros presentes na lista de usuários ativos
- E o valor não deve apresentar divergências em relação aos dados tabulares
- E o contador deve ser atualizado automaticamente sempre que novos usuários se tornarem ativos ou inativos
```

- **f1_score = 0.87**: A resposta do modelo é precisa e altamente relevante para o problema relatado, detalhando bem a correção da divergência entre o contador e a lista. O recall é elevado, pois cobre quase todos os pontos da resposta esperada (acesso ao dashboard, correspondência com total real e atualização automática). Houve pequenas omissões/alterações: alterou a persona de 'admin' para 'gerente de produto' e não explicitou a condição do filtro de status 'ativo'.
- **clarity = 1.00**: A resposta gerada possui excelente clareza. A organização é impecável, estruturada no formato padrão de História de Usuário e BDD (Dado/Quando/Então). A linguagem é simples, direta e profissional. Não há ambiguidades, especificando claramente a necessidade de alinhamento entre o contador e a lista tabular. É concisa, cobrindo o problema com precisão e sem informações redundantes.
- **precision = 0.98**: A resposta é precisa, focada e livre de alucinações. Ela traduz o problema relatado pelo usuário em uma história de usuário estruturada com critérios de aceitação claros (Gherkin). Comparada à referência, atende perfeitamente ao objetivo do teste, apresentando apenas uma divergência irrelevante na persona ('gerente de produto' em vez de 'administrador'), mas mantendo a mesma lógica factual e funcional de resolução da contagem incorreta.

### 13. No iOS, ao girar o celular para landscape, o layout da tela de perfil fica quebrado.

<details><summary>Relato completo</summary>

```text
No iOS, ao girar o celular para landscape, o layout da tela de perfil fica quebrado.
```
</details>

**Saída do prompt:**

```text
Como um usuário de iOS, eu quero que o layout da tela de perfil se ajuste corretamente ao girar o celular para o modo landscape, para que eu possa visualizar e interagir com minhas informações sem que elementos fiquem quebrados ou sobrepostos.

Critérios de Aceitação:
- Dado que estou na tela de perfil no aplicativo para iOS
- Quando giro o celular para o modo landscape
- Então o layout da tela de perfil deve se adaptar à nova orientação sem quebras visuais
- E todos os campos e botões devem permanecer visíveis e acessíveis
- E o conteúdo deve rolar adequadamente caso exceda a altura da tela
```

- **f1_score = 0.97**: A resposta gerada cobre todos os pontos da resposta esperada (Recall 1.0), mantendo a estrutura da História de Usuário e dos Critérios de Aceitação (contexto iOS, rotação para landscape, adaptação sem quebras e visibilidade dos elementos). A precisão é alta (0.95), pois todas as informações são corretas e relevantes, adicionando apenas um critério extra totalmente pertinente sobre a rolagem do conteúdo.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está perfeitamente organizada no formato padrão de História de Usuário com Critérios de Aceitação em BDD. A linguagem é direta, objetiva e acessível. Não há ambiguidades, pois define claramente as condições de teste e o comportamento esperado do aplicativo ao mudar a orientação da tela. É concisa e completa, sem redundâncias.
- **precision = 1.00**: A resposta gerada é altamente precisa, factual e sem alucinações. O modelo transformou corretamente o relato do bug em uma User Story com critérios de aceitação no formato BDD (Dado/Quando/Então), perfeitamente alinhada à resposta esperada. As informações adicionadas no critério de aceitação (ex: rolagem de conteúdo) complementam a usabilidade da funcionalidade descrita de maneira totalmente pertinente e focada na pergunta.

### 14. Campo de email aceita texto sem @, permitindo cadastros inválidos.

<details><summary>Relato completo</summary>

```text
Campo de email aceita texto sem @, permitindo cadastros inválidos.
```
</details>

**Saída do prompt:**

```text
Como um usuário criando uma conta, eu quero que o campo de email valide o formato do texto inserido, para que eu não consiga concluir o cadastro com um endereço de email inválido.

Critérios de Aceitação:
- Dado que estou na tela de cadastro
- Quando digito um texto sem o caractere "@" no campo de email
- Então o campo deve exibir um erro indicando formato de email inválido
- E o botão de envio deve permanecer desabilitado ou o cadastro deve ser bloqueado
- E quando insiro um email no formato correto (ex: usuario@dominio.com), o erro deve desaparecer e o cadastro deve ser permitido
```

- **f1_score = 1.00**: A resposta gerada cobriu perfeitamente todos os elementos da resposta esperada (Ground Truth). A história de usuário é equivalente e todos os critérios de aceitação foram contemplados: contexto do formulário, digitação sem '@', exibição de mensagem de erro explicativa e bloqueio do cadastro. Além disso, a adição do cenário positivo (inserção do e-mail correto para limpar o erro) é altamente relevante e precisa no contexto da história.
- **clarity = 1.00**: A resposta gerada apresenta clareza exemplar. Está perfeitamente organizada no formato padrão de User Story e Critérios de Aceitação (BDD). A linguagem é simples, direta e acessível. Não há ambiguidades, pois especifica detalhadamente as ações, os estados esperados e inclusive dá um exemplo prático de formato correto. Além disso, é extremamente concisa, cobrindo todos os pontos necessários sem qualquer redundância.
- **precision = 1.00**: A resposta gerada é totalmente precisa, sem alucinações e extremamente focada no problema relatado. O Modelo estruturou uma História de Usuário e Critérios de Aceitação em formato BDD idênticos em intenção e fatos ao Ground Truth, cobrindo o bloqueio do cadastro, a validação do caractere '@' e a exibição de mensagem de erro adequada.

### 15. Botão de adicionar ao carrinho não funciona no produto ID 1234.

<details><summary>Relato completo</summary>

```text
Botão de adicionar ao carrinho não funciona no produto ID 1234.
```
</details>

**Saída do prompt:**

```text
Como um usuário navegando na loja virtual, eu quero adicionar o produto ID 1234 ao meu carrinho ao clicar no botão correspondente, para que eu possa prosseguir com a compra do item desejado.

Critérios de Aceitação:
- Dado que estou na página do produto ID 1234
- Quando clico no botão "Adicionar ao carrinho"
- Então o produto ID 1234 deve ser incluído com sucesso no meu carrinho de compras
- E devo ver uma confirmação visual ou notificação de que o item foi adicionado
- E o contador de itens no ícone do carrinho deve ser atualizado corretamente
```

- **f1_score = 1.00**: A resposta gerada cobriu perfeitamente todos os elementos da resposta esperada. A estrutura da História de Usuário e os 5 critérios de aceite (Dado, Quando, Então, confirmação visual e atualização do contador) foram totalmente contemplados. O modelo incorporou especificamente o ID 1234 citado na pergunta do usuário sem adicionar informações incorretas ou irrelevantes, mantendo a precisão e a cobertura completas.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está organizada de forma exemplar no padrão clássico de História de Usuário e Critérios de Aceitação (BDD). A linguagem é direta, simples e fácil de compreender. Por especificar o produto ID 1234 mencionado na pergunta, elimina ambiguidades e contextualiza com precisão a resolução do problema. Além disso, é concisa, focada e sem informações redundantes.
- **precision = 1.00**: A resposta gerada é extremamente precisa e alinhada à referência (Ground Truth). Ela estrutura corretamente a História de Usuário e os Critérios de Aceitação para a funcionalidade do botão de adicionar ao carrinho, cobrindo todos os passos essenciais (inclusão do item, confirmação visual e atualização do contador). A inclusão do ID 1234 contextualizou perfeitamente a solicitação sem gerar alucinações ou imprecisões.
