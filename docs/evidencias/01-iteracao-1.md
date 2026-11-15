# Iteração 1: v2 inicial

- Experimento: `evaluation-prompt-bug_to_user_story_v2-56bea99b`
- Prompt: `evaluation-prompt/bug_to_user_story_v2`
- Provider / modelo / juiz: `google` / `gemini-3.5-flash-lite` / `gemini-3.5-flash`
- Data: 2026-11-15 14:35 UTC
- Exemplos: 15

| Métrica | Média | ≥ 0.8 |
|---|---|---|
| helpfulness | 0.9873 | ✓ |
| correctness | 0.9501 | ✓ |
| f1_score | 0.9088 | ✓ |
| clarity | 0.9833 | ✓ |
| precision | 0.9913 | ✓ |
| **média geral** | **0.9642** | ✓ |

**Status: ✅ APROVADO**

## Por exemplo

| # | Relato (início) | F1 | Clarity | Precision |
|---|---|---|---|---|
| 1 | App de produtividade offline-first com bugs críticos de sincronização. | 0.85 | 1.00 | 1.00 |
| 2 | Sistema de relatórios gerenciais com problemas severos de performance  | 0.89 | 0.98 | 1.00 |
| 3 | Sistema de checkout com múltiplas falhas críticas. | 0.94 | 0.95 | 0.98 |
| 4 | Modal de confirmação de exclusão aparece atrás do menu lateral em tela | 0.80 | 0.98 | 1.00 |
| 5 | Carrinho permite finalizar compra mesmo com produto fora de estoque. | 0.88 | 1.00 | 1.00 |
| 6 | App Android trava ao carregar lista de notificações com mais de 50 ite | 0.92 | 1.00 | 1.00 |
| 7 | Pipeline de vendas calcula valor total errado quando há desconto. | 0.92 | 1.00 | 1.00 |
| 8 | Endpoint /api/users/:id retorna dados de qualquer usuário sem validar  | 0.97 | 0.98 | 1.00 |
| 9 | Relatório de vendas demora mais de 2 minutos para gerar quando filtro  | 1.00 | 1.00 | 0.98 |
| 10 | Webhook de pagamento aprovado não está sendo chamado. | 0.79 | 1.00 | 0.98 |
| 11 | Imagens de produtos não aparecem no Safari. No Chrome funciona normal. | 0.95 | 0.98 | 1.00 |
| 12 | Dashboard mostra contagem errada de usuários ativos. Mostra 50 mas só  | 0.72 | 0.88 | 0.93 |
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
Como um vendedor em campo utilizando o app offline-first, eu quero que minhas alterações, uploads de anexos, ordenações de operações e grandes volumes de dados sejam sincronizados de forma segura, com resolução de conflitos, retomada de arquivos e paginação de memória, para que nenhum dado seja perdido e eu possa confiar na ferramenta de trabalho.

=== USER STORY PRINCIPAL ===

Título: Sincronização offline-first robusta e segura para dispositivos móveis

Descrição:
Como um usuário em campo, eu quero um mecanismo de sincronização confiável que trate conflitos de edição, retome uploads interrompidos, respeite a ordem cronológica das ações e processe lotes grandes sem travamentos, para que minhas informações fiquem íntegras independentemente da conexão.

=== CRITÉRIOS DE ACEITAÇÃO ===

A. Conflito de dados - Resolução interativa:
- Dado que o Usuário A e o Usuário B editaram a tarefa #123 offline simultaneamente
- Quando ambos realizam a sincronização com o servidor
- Então o sistema não deve aplicar "last write wins" silenciosamente
- E o usuário deve ser notificado sobre o conflito de dados
- E uma interface de resolução de conflitos deve permitir escolher qual versão manter ou mesclar

B. Sincronização - Retomada de upload de anexos:
- Dado que estou anexando um arquivo PDF de 50MB em uma tarefa via 4G
- Quando a conexão cai durante o envio do arquivo
- Então o app deve pausar o upload e retomar a partir do último byte enviado (chunked upload / resumable upload)
- E após atingir o limite de tentativas sem sucesso, o usuário deve ser notificado explicitamente da falha
- E a tarefa nunca deve ser marcada incorretamente como "sincronizada" sem o anexo

C. Ordenação - Respeito à cronologia do cliente:
- Dado que realizei operações offline sequenciais na mesma tarefa (Criar às 10:00, Editar às 10:15 e Deletar às 10:30)
- Quando o dispositivo recupera a conexão e envia a fila de operações
- Então o servidor deve processar os eventos estritamente baseados no timestamp client-side e na ordem de execução
- E o evento de DELETE deve ser aplicado por último, garantindo que a tarefa não reapareça indevidamente

D. Memória - Sincronização em lotes paginados:
- Dado que acumulei 1.500 operações pendentes após uma semana offline
- Quando o app se conecta a uma rede WiFi e inicia a sincronização
- Então o app deve processar os itens em lotes paginados (chunking/streaming) em vez de carregar todos de uma vez
- E o consumo de memória não deve exceder o limite seguro do sistema operacional (abaixo de 700MB)
- E a sincronização deve ser concluída sem crashes (Memory Warning ou OutOfMemoryError)

=== CRITÉRIOS TÉCNICOS ===

Conflitos:
- Implementar algoritmo de detecção de concorrência com versionamento de registros e tela de merge no cliente

Uploads:
- Implementar protocolo de upload resumível (ex.: Tus protocol ou equivalente) mantendo o estado correto da tarefa

Ordenação:
- Utilizar vetor de relógio / timestamps client-side ordenados no payload de sincronização do servidor

Memória:
- Processar a fila de sincronização em lotes (batch size configurável, ex.: 100 itens por lote) com liberação de ponteiros de memória (garbage collection explícito se necessário)

=== CONTEXTO DO BUG ===

Severidade: CRÍTICA
Impacto: 250+ usuários afetados, NPS caiu de 8.5 para 4.2, 80% reviews negativos sobre perda de dados, churn aumentou 15%, R$ 200k em oportunidades perdidas

Problemas Identificados:
1. "Last write wins" causa perda silenciosa de dados em edições concorrentes
2. Upload de anexos grandes reinicia do zero e marca tarefa como sincronizada em caso de falha
3. Servidor recebe operações fora de ordem (DELETE antes de CREATE) quebrando a consistência
4. Carregamento de 1.500+ itens pendentes de uma vez estoura o limite de memória e crasha o app (iOS e Android)

=== TASKS TÉCNICAS SUGERIDAS ===

1. [BACKEND/MOBILE] Implementar sistema de detecção e notificação de conflitos de dados (Three-way merge ou notificação ao usuário)
2. [MOBILE/BACKEND] Substituir upload simples por protocolo de upload resumível (resumable chunks)
3. [BACKEND] Ajustar motor de sincronização para ordenar fila de requisições por timestamp client-side
4. [MOBILE] Refatorar fila de sync para processar operações em lotes (batching), prevenindo estouro de memória
5. [TESTES] Criar testes de estresse para cenários offline prolongados com mais de 1.000 itens pendentes
```

- **f1_score = 0.85**: A resposta gerada é altamente precisa e relevante, sem inventar informações incorretas. Ela abordou corretamente a User Story, os 4 Critérios de Aceitação (A, B, C, D), o Contexto do Bug e tarefas técnicas. No entanto, o Recall é menor pois omitiu detalhes técnicos específicos presentes no Ground Truth, como os snippets de código/protocolos (JSON da operação, algoritmo de batch), a divisão estruturada em 4 fases com 16 tasks detalhadas, a arquitetura do app e a seção de Métricas de Sucesso.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está estruturada de forma lógica com seções bem definidas (User Story, Critérios de Aceitação em formato BDD, Critérios Técnicos, Contexto e Tasks). A linguagem é direta, precisa e adequada ao contexto técnico. Não há ambiguidades nas especificações dos comportamentos esperados e a concisão é mantida sem sacrificar detalhes essenciais de cada um dos quatro problemas reportados.
- **precision = 1.00**: A resposta gerada está perfeitamente alinhada com o contexto fornecido e a resposta esperada. Ela cobriu com precisão todos os 4 problemas críticos (conflito de dados, upload de 50MB sem resumo, ordenação via timestamp e estouro de memória com 1.500 itens acima de 700MB), mantendo a fidelidade aos fatos, sem alucinações, com foco total na solicitação e com absoluta correção técnica.

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
Como um gerente executivo consultando o dashboard e os relatórios gerenciais, eu quero visualizar dados financeiros consistentes, relatórios de alta performance, informações atualizadas em tempo real e exportações seguras, para que eu possa confiar nos números para o board, tomar decisões estratégicas e evitar cancelamentos de contratos.

=== USER STORY PRINCIPAL ===

Título: Correção de performance, consistência de MRR, cache e exportação de relatórios gerenciais

Descrição:
Como um usuário corporativo acessando o sistema de relatórios, eu quero uma experiência rápida, cálculos de MRR unificados e corretos, dados atualizados sem delay de cache e exportações estáveis, para que eu possa operar o sistema com confiança e sem quedas de performance.

=== CRITÉRIOS DE ACEITAÇÃO ===

A. Performance - Otimização de query no dashboard executivo:
- Dado que estou acessando o endpoint GET /api/reports/executive-dashboard
- Quando o sistema carrega as métricas, departamentos, usuários e licenças
- Então o carregamento deve ser feito em lote utilizando joins ou eager loading em vez de queries N+1
- E o tempo de resposta da API deve ser inferior a 3 segundos (SLA)
- E o uso de CPU do banco de dados não deve atingir 95% em horários de pico

B. Lógica de Negócio - Consistência do cálculo de MRR:
- Dado que o sistema calcula o Monthly Recurring Revenue (MRR)
- Quando o cálculo é executado no dashboard, relatório financeiro e exportações
- Então o valor do MRR deve seguir a regra de negócio oficial baseada exclusivamente em assinaturas ativas e pró-rata de upgrades/downgrades
- E o dashboard, o relatório financeiro e os dados contábeis devem exibir exatamente o mesmo valor de MRR, eliminando discrepâncias

C. Cache - Invalidação de cache Redis em alterações de plano:
- Dado que um cliente realiza um upgrade de plano
- Quando a alteração é persistida no banco de dados
- E o cache Redis é acionado
- Então o cache do dashboard da empresa deve ser invalidado imediatamente
- E a alteração de plano deve ser refletida na interface em tempo real, sem aguardar o TTL de 24 horas

D. Concorrência - Exportação assíncrona de CSV sem esgotar recursos:
- Dado que solicito a exportação de um relatório anual (365 dias, 50k linhas)
- Quando o processo de exportação é iniciado
- Então a geração do arquivo deve ser processada em background (assíncrona)
- E não deve causar picos de 100% de CPU nas requisições síncronas nem exceder o limite de 2GB de memória (evitando OOM Kill)

=== CRITÉRIOS TÉCNICOS ===

Performance:
- Refatorar o endpoint GET /api/reports/executive-dashboard para eliminar o padrão N+1, utilizando consultas agregadas no banco de dados relacional.

Lógica de Negócio (MRR):
- Padronizar a regra de cálculo do MRR em uma única função/serviço compartilhado por todas as views e relatórios, contemplando tratamento correto de pró-rata para upgrades/downgrades e exclusão de cancelamentos fora do período vigente.

Cache:
- Implementar a estratégia de cache-aside com invalidação explícita da chave correspondente no Redis no momento exato em que o evento de upgrade de plano for confirmado.

Concorrência:
- Migrar a exportação de relatórios pesados (CSV) para uma fila de processamento em background (ex.: workers assíncronos) utilizando paginação/streaming de dados para manter o consumo de memória abaixo do limite de 2GB.

=== CONTEXTO DO BUG ===

Severidade: CRÍTICA
Impacto: 15 clientes enterprise ameaçando cancelar contrato, CEO sem confiança para apresentar ao board, time de CS gastando 40h/semana explicando discrepâncias, impossibilidade de forecasting confiável, 500+ empresas clientes afetadas (50-5000 usuários cada).

Problemas Identificados:
1. Query N+1 no dashboard executivo (GET /api/reports/executive-dashboard) gera 101 queries por cliente com 100 departamentos, com tempo de resposta de 45 segundos e CPU a 95%.
2. Cálculo de MRR inconsistente entre dashboard (R$ 150.000), relatório financeiro (R$ 145.000) e planilha contábil (R$ 147.500) devido a regras divergentes de cancelamentos e pró-rata.
3. Cache Redis com TTL de 24 horas exibe dados desatualizados de planos após upgrade, com falha na invalidação manual.
4. Exportação de CSV de relatório anual (50k linhas) causa 100% de CPU por 5 minutos e estouro de memória (>4GB vs limite de 2GB), resultando em OOM Kill e lentidão geral.

=== TASKS TÉCNICAS SUGERIDAS ===

1. [BACKEND] Refatorar query do executive-dashboard para remover N+1 e atender ao SLA de 3s
2. [BACKEND] Unificar a regra de cálculo de MRR em serviço centralizado
3. [BACKEND/CACHE] Implementar invalidação automática de cache Redis em eventos de upgrade
4. [BACKEND] Migrar exportação de CSV para processamento em background/streaming para evitar OOM Kill
5. [TESTES] Criar testes de carga e concorrência para exportação de grandes volumes e validação de consistência de MRR
```

- **f1_score = 0.89**: A resposta gerada possui precisão perfeita (1.0), sem alucinações ou informações incorretas. O Recall (0.80) é alto por cobrir a estrutura completa do Ground Truth (User Story, Critérios de Aceitação, Contexto do Bug e Soluções Técnicas), porém omitiu detalhes técnicos específicos presentes no gabarito, tais como: o exemplo de query SQL otimizada, a divisão detalhada em 3 Sprints (11 tarefas), a estratégia de cache em 3 níveis (tempo real, 5min e 1h) e a meta de CPU < 70%.
- **clarity = 0.98**: A resposta gerada é extremamente clara e bem estruturada. A organização em seções bem delimitadas (User Story, Critérios em formato BDD, Especificações Técnicas e Tasks) facilita a leitura e compreensão. A linguagem é direta, técnica na medida certa e fluida. O uso do padrão BDD (Dado/Quando/Então) nos critérios de aceitação elimina ambiguidades sobre o comportamento esperado. O texto é conciso e focado nos problemas descritos, sem redundâncias ou prolixidade.
- **precision = 1.00**: A resposta gerada é extremamente precisa, sem nenhuma alucinação, totalmente focada no problema apresentado e factualmente correta. Ela abordou com precisão técnica exata os 4 problemas do contexto (N+1 no dashboard, cálculo inconsistente de MRR, invalidação de cache Redis e exportação CSV com OOM Kill), definindo critérios de aceitação e tasks técnicas perfeitamente alinhadas com as soluções de engenharia esperadas.

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
Como um cliente finalizando uma compra, eu quero que o checkout seja seguro, processe pagamentos e cupons corretamente e me informe em caso de lentidão, para que eu possa concluir minha transação com segurança e confiança.

=== USER STORY PRINCIPAL ===

Título: Correção de falhas críticas no checkout (Segurança, Integração, Concorrência e UX)

Descrição:
Como um cliente no sistema de checkout, eu quero a sanitização do campo de cupons, processamento estável de pagamentos, controle atômico do limite de uso de cupons e feedback visual em caso de timeout, para que meus dados fiquem seguros, meus pedidos sejam criados corretamente e eu não fique preso em uma tela de carregamento.

=== CRITÉRIOS DE ACEITAÇÃO ===

A. Segurança - Sanitização do campo de cupom:
- Dado que estou na tela de checkout no campo de cupom de desconto
- Quando informo `<script>alert('xss')</script>` e tento aplicar
- Então o sistema deve sanitizar a entrada e recusar o código inválido
- E nenhum script malicioso deve ser executado no navegador

B. Integração - Estabilidade e resiliência no processamento de pagamentos:
- Dado que submeto o pagamento via POST /api/payment/process
- Quando o gateway demora para responder ou ocorre instabilidade
- Entonces o sistema não deve esgotar o connection pool do Postgres
- E transações confirmadas devem criar o pedido correspondente sem falhas
- E erros de timeout devem ser tratados adequadamente sem deixar o cliente cobrado sem pedido

C. Lógica de Negócio - Controle atômico de limite de cupons:
- Dado que um cupom possui limite máximo de uso (ex.: "PROMO10" com limite de 100 usos)
- Quando múltiplos clientes tentam aplicar o mesmo cupom simultaneamente
- Entonces a verificação e o incremento do contador de uso devem ser executados de forma atômica
- E o sistema deve bloquear estritamente o uso do cupom após atingir o limite de 100 usos

D. UX - Feedback claro após timeout no pagamento:
- Dado que o processamento do pagamento demora mais de 30 segundos
- Cuando ocorre um timeout na requisição
- Entonces o spinner de loading infinito deve ser interrompido
- E devo visualizar uma mensagem clara informando o status do pagamento e orientando sobre os próximos passos

=== CRITÉRIOS TÉCNICOS ===

Segurança:
- Implementar sanitização e validação estrita no input do campo de cupom para prevenir ataques XSS

Integração:
- Otimizar o gerenciamento do connection pool do Postgres e implementar circuit breaker e retry para o POST /api/payment/process

Lógica de Negócio:
- Utilizar transações atômicas com locks apropriados (ou operações atômicas no banco) na validação e contagem de cupons

UX:
- Adicionar tratamento de timeout (ex.: limite de 30s) no front-end com remoção do spinner e exibição de tela/mensagem de erro ou verificação de status

=== CONTEXTO DO BUG ===

Severidade: CRÍTICA
Impacto: 150+ clientes afetados na última semana, perda estimada de R$ 15.000 em cupons indevidos, 45 tickets de suporte abertos, rating do app caiu de 4.5 para 3.2 estrelas

Problemas Identificados:
1. XSS não sanitizado no campo de cupom
2. POST /api/payment/process retorna 504 Gateway Timeout com falha de criação de pedido e esgotamento do connection pool do Postgres
3. Race condition em cupons de desconto permitindo uso acima do limite
4. Loading infinito após timeout superior a 30 segundos no pagamento

=== TASKS TÉCNICAS SUGERIDAS ===

1. [SEGURANÇA] Sanitizar o campo de entrada de cupons no front-end e back-end
2. [BACKEND] Ajustar o gerenciamento do connection pool do Postgres e otimizar POST /api/payment/process
3. [BANCO DE DADOS] Implementar atomicidade na validação e decremento/incremento de limite de cupons
4. [FRONTEND] Implementar tratamento de timeout na requisição de pagamento removendo o spinner e exibindo mensagem de erro amigável
5. [TESTES] Executar testes de carga, concorrência e segurança (XSS) no checkout
```

- **f1_score = 0.94**: A resposta gerada é altamente precisa, relevante e sem alucinações. Cobriu perfeitamente a estrutura (User Story, Critérios de Aceitação A-D, Contexto do Bug e Tasks). O Recall é 0.88 pois omitiu alguns detalhes técnicos específicos presentes no Ground Truth, como tecnologias/padrões concretos (DOMPurify, CSP headers, Redis INCR / SELECT FOR UPDATE, Polling/Webhooks) e a task de monitoramento (alertas para timeout rate > 5%), embora tenha generalizado esses pontos adequadamente.
- **clarity = 0.95**: A resposta apresenta excelente organização estrutural e formato visual limpo (utilizando BDD nos critérios de aceitação), o que garante alta clareza e ausência de ambiguidades. É extremamente objetiva e concisa. A única ressalva na linguagem foi a inserção pontual de palavras em espanhol ('Entonces' e 'Cuando') nos critérios B, C e D, que prejudica levemente o alinhamento linguístico, mas sem afetar a compreensão técnica do conteúdo.
- **precision = 0.98**: A resposta gerada é extremamente precisa, sem alucinações e totalmente alinhada ao contexto fornecido. Ela mapeou corretamente os 4 problemas críticos (XSS, timeout/connection pool, race condition e UX) transformando-os em User Stories, Critérios de Aceitação e Tasks Técnicas coerentes com o Ground Truth. A única ressalva mínima foi o uso acidental da palavra em espanhol 'Entonces' em alguns tópicos dos critérios de aceitação, mas a precisão técnica e factual manteve-se perfeita.

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
Como um usuário navegando em telas pequenas (< 768px), eu quero visualizar o modal de confirmação de exclusão na camada superior ao menu lateral, para que eu possa interagir com os botões de confirmação sem precisar fechar o menu lateral manualmente.

Critérios de Aceitação:
- Dado que estou acessando a aplicação em uma tela menor que 768px
- Quando abro o modal de confirmação de exclusão com o menu lateral aberto
- Então o modal deve ser exibido em primeiro plano, sobrepondo o menu lateral
- E devo conseguir clicar nos botões do modal sem impedimentos visuais ou de clique
- E o menu lateral não deve bloquear a interação com o modal

Critérios Técnicos:
- Ajustar o z-index do modal para um valor superior ao z-index do menu lateral (que atualmente é 1050), garantindo que o modal utilize z-index 1051 ou superior.

Contexto Técnico:
- Problema atual: O modal de confirmação possui z-index 1000, enquanto o menu lateral possui z-index 1050, fazendo com que o menu fique sobreposto em resoluções menores que 768px.
- Valores atuais: Modal (z-index 1000), Menu lateral (z-index 1050).
- Valores esperados: Modal com z-index superior ao menu lateral (ex: z-index 1051 ou superior).
```

- **f1_score = 0.80**: A precisão foi 1.0 pois todas as informações geradas são corretas, altamente relevantes e diretamente alinhadas ao problema. O recall foi 0.67 porque o modelo omitiu completamente a seção de Critérios de Acessibilidade (foco de teclado, tecla ESC, fechar no backdrop) e alguns detalhes dos Critérios de Aceitação (largura de 90% da tela e efeito de backdrop desensocado).
- **clarity = 0.98**: A resposta possui excelente clareza, estrutura altamente organizada e sem ambiguidade. A história de usuário e os critérios de aceitação no formato BDD (Dado-Quando-Então) tornam a comunicação precisa e fácil de entender. A linguagem é direta e apropriada ao contexto técnico. Há uma leve redundância entre a seção de 'Critérios Técnicos' e 'Contexto Técnico' ao repetir os valores exatos de z-index (1000 vs 1050), o que reduz minimamente a concisão, mas não impacta negativamente a compreensão.
- **precision = 1.00**: A resposta gerada é altamente precisa, factual e totalmente focada no problema relatado. Todas as informações (z-index 1000 do modal vs 1050 do menu, comportamento em telas < 768px e a necessidade de sobreposição) baseiam-se estritamente nos fatos fornecidos na pergunta e alinham-se com a resposta esperada. Não foram identificadas alucinações nem desvios do tópico.

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
Como um cliente finalizando uma compra, eu quero que o sistema valide a disponibilidade do estoque antes de permitir a conclusão do pedido, para que eu não consiga comprar produtos esgotados e evite transtornos com entregas impossíveis.

Critérios de Aceitação:
- Dado que um produto possui 2 unidades em estoque
- Quando o Cliente A adiciona essas 2 unidades ao carrinho e o estoque fica zerado
- Então o Cliente B não deve conseguir adicionar o produto esgotado ao carrinho
- E se o Cliente B tentar finalizar uma compra com itens indisponíveis
- Então o sistema deve bloquear a finalização e exibir uma mensagem informando que o produto está esgotado
- E nenhum pedido inválido sem estoque correspondente deve ser gerado

Critérios Técnicos:
- Implementar verificação atômica de estoque no momento da adição ao carrinho e no fechamento do pedido (checkout)
- Atualizar a reserva de estoque de forma síncrona para evitar condições de corrida (race condition) entre múltiplos usuários

Contexto Técnico:
- Problema atual: O carrinho e o checkout permitem a adição e compra de produtos com estoque zerado
- Valores observados: 2 unidades em estoque inicial, mas o sistema permite overbooking para o Cliente B após esgotamento
- Ajustar a lógica de concorrência e validação de estoque nos endpoints de carrinho e checkout
```

- **f1_score = 0.88**: A resposta do modelo é altamente precisa, trazendo informações corretas e adicionando valor com critérios técnicos pertinentes ao bug (como tratamento de race conditions). O recall é bom: cobriu a história de usuário, a validação no checkout, a exibição de mensagem e o bloqueio de pedidos sem estoque. Contudo, omitiu pontos específicos da resposta esperada, como a sugestão de remover o item/aguardar reposição e a reserva temporária por 15 minutos.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está perfeitamente organizada em seções lógicas (História de Usuário, Critérios de Aceitação no formato BDD e Contexto Técnico). A linguagem é direta, precisa e adequada ao contexto de desenvolvimento de software. Não há ambiguidades, pois especifica com exatidão as regras de negócio e os cenários testáveis com base no bug informado. Além disso, é concisa, fornecendo todas as informações necessárias de forma direta e sem redundâncias.
- **precision = 1.00**: A resposta gerada é extremamente precisa, focada e livre de alucinações. O modelo estruturou com maestria o bug informado em formato de História de Usuário, Critérios de Aceitação e Contexto Técnico. As informações estão corretas e abordam diretamente a solução do problema de condição de corrida (race condition) e validação de estoque citados na pergunta, mantendo alinhamento total com a resposta esperada.

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
Como um usuário do app Android, eu quero que a lista de notificações carregue de forma fluida e paginada, para que o aplicativo não trave ao exibir muitos itens.

Critérios de Aceitação:
- Dado que abro a tela de notificações do app Android
- Quando a lista possui mais de 50 itens
- Então os itens devem ser carregados de forma paginada sem congelar a tela
- E a Thread principal não deve ser bloqueada durante o carregamento
- E o app nunca deve apresentar erro de ANR (Application Not Responding)
- E a navegação deve permanecer responsiva com tempo de resposta inferior a 2 segundos

Critérios Técnicos:
- Implementar paginação na API ou no carregamento da lista de notificações
- Mover o processamento e a carga de dados para uma Background Thread (usando Coroutines, RxJava ou similar)
- Otimizar a renderização da lista para evitar gargalos na Thread principal

Contexto Técnico:
- Problema atual: App trava por 5-10 segundos e gera ANR ao carregar mais de 50 notificações
- Causa identificada: Lista sem paginação carregando todos os itens de uma vez na Thread principal
```

- **f1_score = 0.92**: A precisão é máxima (1.0), pois todas as informações geradas são corretas, coerentes com o desenvolvimento Android e diretamente relevantes para a resolução do bug. O recall é 0.85 porque, embora a resposta cubra perfeitamente o contexto e os critérios de aceitação, omitiu alguns detalhes técnicos específicos do gabarito, tais como: o limite explícito de 20 itens por página, o uso de RecyclerView com ViewHolder pattern e a implementação de scroll infinito.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está perfeitamente organizada no padrão de História de Usuário e BDD, utilizando uma estrutura lógica e fácil de acompanhar. A linguagem é direta, técnica na medida certa e sem jargões desnecessários. Não há ambiguidades nos critérios de aceitação e técnicos estabelecidos, e a resposta é concisa, focando exatamente na resolução dos problemas apontados (ANR, Thread principal e falta de paginação) sem redundâncias.
- **precision = 1.00**: A resposta gerada é extremamente precisa, factual e focada na solução do problema relatado. Não contém nenhuma alucinação, capturando corretamente todas as observações do usuário (travamento da Thread principal, ANR e ausência de paginação). As soluções técnicas propostas (uso de background thread com Coroutines/RxJava e paginação) e os critérios de aceitação estão perfeitamente alinhados com a resposta de referência e as melhores práticas do desenvolvimento Android.

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
Como um gerente de vendas, eu quero que o pipeline de vendas calcule o valor total aplicando o desconto sobre o montante correto de todos os produtos, para que os valores dos negócios exibidos estejam corretos.

Critérios de Aceitação:
- Dado que crio um negócio com o Produto A no valor de R$ 1.000 e o Produto B no valor de R$ 500
- Quando aplico um desconto global de 10% no pedido
- Então o valor total calculado deve ser de R$ 1.350
- E o sistema não deve aplicar o desconto apenas no primeiro produto
- E o valor mostrado na interface do pipeline deve refletir exatamente R$ 1.350

Exemplo de Cálculo:
- Subtotal dos produtos: R$ 1.000 (Produto A) + R$ 500 (Produto B) = R$ 1.500
- Desconto de 10%: 10% de R$ 1.500 = R$ 150
- Valor total correto: R$ 1.500 - R$ 150 = R$ 1.350

Contexto Técnico:
- Bug atual: O sistema calcula o desconto considerando apenas o primeiro item da lista (R$ 1.000 com 10% de desconto = R$ 900 + R$ 500 = R$ 1400)
- Valor atual incorreto: R$ 1.400 | Valor esperado: R$ 1.350
- Ajustar a lógica de cálculo no motor de preços para aplicar a porcentagem de desconto sobre a soma total dos itens e não de forma isolada no primeiro produto
```

- **f1_score = 0.92**: A resposta gerada é precisa e altamente relevante, detalhando o cálculo e trazendo sugestões técnicas corretas. A precisão é alta, com apenas uma leve variação na persona (gerente de vendas em vez de vendedor). O recall é ótimo, cobrindo a história do usuário, contexto técnico e o exemplo de cálculo completo, embora os critérios de aceitação tenham focado no exemplo específico em vez de definir regras e fórmulas genéricas como na resposta esperada.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está perfeitamente organizada no formato de história de usuário, critérios de aceitação (BDD), exemplo prático e contexto técnico. A linguagem é direta, acessível e isenta de ambiguidades, explicando claramente a causa do erro e como o sistema deve se comportar. Além disso, é concisa e estruturada de maneira altamente eficiente.
- **precision = 1.00**: A resposta gerada é extremamente precisa, sem alucinações e totalmente alinhada com o prompt e a resposta esperada. Ela estruturou adequadamente o cenário de bug em uma User Story clara, com critérios de aceitação BDD e explicação técnica correta. Os cálculos apresentados (subtotal de R$ 1.500, desconto de R$ 150, total esperado de R$ 1.350 e valor incorreto de R$ 1.400) estão matematicamente perfeitos e explicam exatamente a causa raiz do problema.

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
Como o sistema, eu quero bloquear o acesso de usuários comuns a dados sensíveis de outros perfis na API, para que informações pessoais e administrativas fiquem protegidas contra vazamentos.

=== USER STORY PRINCIPAL ===

Título: Validação de permissão no endpoint de usuários

Descrição:
Como um usuário administrador, eu quero que o endpoint /api/users/:id valide as permissões de acesso, para que usuários comuns não consigam visualizar dados confidenciais de outros usuários.

=== CRITÉRIOS DE ACEITAÇÃO ===

A. Segurança - Bloqueio de usuário comum:
- Dado que estou autenticado como um usuário comum com ID 100
- Quando faço uma requisição GET para /api/users/1 de um usuário administrador
- Então a API deve retornar o código HTTP 403 (Forbidden)
- E a resposta não deve conter dados como email, telefone ou endereço

B. Autorização - Acesso permitido para administradores:
- Dado que estou autenticado como um usuário administrador
- Quando faço uma requisição GET para /api/users/:id de qualquer usuário
- Então a API deve retornar o código HTTP 200 (OK)
- E os dados do usuário solicitado devem ser retornados corretamente

=== CRITÉRIOS TÉCNICOS ===

Controle de Acesso:
- Implementar middleware de validação de papéis (roles) no endpoint GET /api/users/:id para permitir apenas o perfil "admin" ou o próprio usuário proprietário da conta.

=== CONTEXTO DE SEGURANÇA ===

Severidade: ALTA - vazamento de dados pessoais
Categoria OWASP: Broken Object Level Authorization (BOLA)

Problemas Identificados:
1. Endpoint /api/users/:id retorna dados de qualquer usuário sem validar permissões
2. Usuário comum (ID 100) consegue acessar GET /api/users/1 e visualizar email, telefone e endereço do admin

=== TASKS TÉCNICAS SUGERIDAS ===

1. [BACKEND] Implementar validação de autorização no endpoint /api/users/:id
2. [SEGURANÇA] Adicionar testes unitários e de integração para validar o bloqueio HTTP 403 em tentativas de acesso não autorizadas
3. [AUDITORIA] Registrar tentativas de acesso negado em log de segurança
```

- **f1_score = 0.97**: A resposta gerada abrange com alta precisão e completude todos os elementos da resposta esperada. Contém os critérios de aceitação para usuário comum (HTTP 403) e admin (HTTP 200), a autorização do próprio usuário, o contexto de segurança (Severidade Alta, OWASP BOLA), o uso de middleware e o registro em log de auditoria. Não foram identificadas informações incorretas ou irrelevantes.
- **clarity = 0.98**: A resposta gerada possui excelente clareza. Está muito bem organizada em seções bem delimitadas e utiliza o padrão BDD nos critérios de aceitação. A linguagem é direta e profissional. Não há ambiguidades, pois especifica claramente os status HTTP, permissões e cenários. Apresenta apenas uma leve redundância ao recontextualizar o problema na seção de segurança, mas mantém-se concisa e altamente compreensível.
- **precision = 1.00**: A resposta é totalmente precisa, sem alucinações e com foco correto. Ela estruturou a solução da vulnerabilidade de forma excelente em formato de User Story, definindo os critérios de aceitação com códigos HTTP adequados (403 para acesso negado e 200 para admins) e identificando corretamente a categoria OWASP (BOLA / Broken Access Control). Todas as informações estão factualmente corretas e perfeitamente alinhadas com a resposta esperada.

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
Como um gerente comercial gerando relatórios de vendas, eu quero exportar relatórios com mais de 1000 registros em poucos segundos, para que eu possa analisar os dados rapidamente durante o horário comercial sem sofrer com lentidão ou timeout.

Critérios de Aceitação:
- Dado que acesso a tela de relatórios de vendas e aplico um filtro que ultrapassa 1000 registros
- Quando clico para gerar o relatório
- Então os dados devem ser exibidos ou exportados em menos de 10 segundos
- E o navegador nunca deve sofrer timeout após 120 segundos
- E o sistema deve lidar eficientemente com o volume de dados durante o horário comercial

Critérios Técnicos:
- Criar um índice na coluna data_venda da tabela de vendas para otimizar a query SQL
- Otimizar a execução da consulta e garantir que o tempo de resposta fique abaixo do limite de timeout do navegador

Contexto Técnico:
- Problema atual: Relatório demora mais de 2 minutos para gerar com filtros acima de 1000 registros e o navegador sofre timeout após 120 segundos
- Causa técnica: Query SQL sem index na coluna data_venda
- Impacto: Lentidão relatada pelos usuários no horário comercial
```

- **f1_score = 1.00**: A resposta gerada foi excelente, cobrindo com precisão e completude todos os elementos do Ground Truth (User Story, Critérios de Aceitação e Contexto Técnico). Todas as informações fornecidas são corretas, relevantes e diretamente aplicáveis ao problema relatado (como a criação do índice na coluna data_venda e mitigação do timeout).
- **clarity = 1.00**: A resposta gerada possui clareza exemplar. É perfeitamente organizada na estrutura padronizada de Histórias de Usuário (Como/Quero/Para), Critérios de Aceitação em formato BDD (Dado/Quando/Então) e Contexto Técnico bem delimitado. A linguagem é direta, precisa e sem jargões desnecessários. Não apresenta ambiguidades em relação aos objetivos ou à solução técnica necessária, e mantém-se concisa, sem redundâncias, facilitando a leitura e o entendimento imediato da demanda.
- **precision = 0.98**: A resposta gerada é extremamente precisa, focada e livre de alucinações. Todas as informações técnicas fornecidas (falta de índice na coluna data_venda, timeout de 120s e impacto no horário comercial) foram corretamente incorporadas na estrutura de História de Usuário. A resposta atendeu perfeitamente ao pedido. Houve apenas uma pequena divergência estimativa em relação ao Ground Truth no critério de tempo esperado (<10s na resposta gerada vs <30s no Ground Truth), o que não compromete a qualidade geral.

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
Como um cliente efetuando um pagamento, eu quero que o sistema receba a confirmação do pagamento aprovado pelo gateway, para que o status do meu pedido seja atualizado automaticamente para "pago" após a transação.

Critérios de Aceitação:
- Dado que faço um pedido de R$ 100 e o pagamento com cartão de crédito é aprovado no gateway
- Quando o gateway envia a notificação de pagamento aprovado
- Então o webhook POST /api/webhooks/payment deve ser processado com sucesso (HTTP 200)
- E o status do pedido deve mudar de "pendente" para "pago"
- E não deve ocorrer erro HTTP 500 no endpoint do webhook

Critérios Técnicos:
- Investigar e corrigir a causa do erro HTTP 500 no endpoint POST /api/webhooks/payment
- Garantir o tratamento correto do payload enviado pelo gateway de pagamento

Contexto Técnico:
- Problema atual: O endpoint POST /api/webhooks/payment retorna HTTP 500 ao receber a notificação do gateway
- Comportamento atual: Status do pedido permanece como "pendente" mesmo após a aprovação
- Comportamento esperado: Processamento bem-sucedido (HTTP 200) e atualização do status do pedido
```

- **f1_score = 0.79**: A resposta gerada é altamente precisa e relevante sobre o problema técnico e o fluxo principal (HTTP 200, erro 500 e atualização de status). O recall foi reduzido pois foram omitidos dois critérios de aceitação importantes presentes no Ground Truth: o envio de e-mail de confirmação ao cliente e o registro do evento em log para auditoria.
- **clarity = 1.00**: A resposta possui clareza excelente. Está muito bem organizada na estrutura padrão de História de Usuário e BDD (Dado/Quando/Então). A linguagem é direta, técnica e de fácil compreensão. Não há ambiguidades: o problema (HTTP 500 no endpoint) e o comportamento esperado (HTTP 200 e alteração do status do pedido) estão definidos expressamente. A concisão é ideal, sem dados redundantes ou enrolação.
- **precision = 0.98**: A resposta gerada é extremamente precisa e fiel às informações do problema. Ela estruturou a solução do bug em uma User Story clara, abordando diretamente a falha HTTP 500 no endpoint `/api/webhooks/payment` e a transição do status do pedido. Não há alucinações ou informações inventadas. A única divergência em relação ao Ground Truth é o ponto de vista da persona ('cliente' vs 'sistema') e pequenas variações na nomenclatura de status ('pago' em vez de 'aprovado'), mantendo total relevância e foco factual.

### 11. Imagens de produtos não aparecem no Safari. No Chrome funciona normal.

<details><summary>Relato completo</summary>

```text
Imagens de produtos não aparecem no Safari. No Chrome funciona normal.
```
</details>

**Saída do prompt:**

```text
Como um usuário navegando pelo Safari, eu quero visualizar as imagens dos produtos corretamente, para que eu possa avaliar os itens antes de adicioná-los ao carrinho.

Critérios de Aceitação:
- Dado que estou acessando a página de produtos utilizando o navegador Safari
- Quando a página é carregada
- Então todas as imagens dos produtos devem ser exibidas corretamente
- E não devem ocorrer falhas de renderização em comparação ao navegador Chrome
- E o formato e a codificação das imagens devem ser compatíveis com o motor do Safari
```

- **f1_score = 0.95**: A resposta gerada é totalmente correta e relevante. Ela seguiu perfeitamente a estrutura de História de Usuário e Critérios de Aceite (Dado/Quando/Então). Cobriu quase todos os pontos da resposta esperada (persona, visualização de imagens, comparação com Chrome e funcionamento correto no Safari). Apenas o detalhe do 'tempo de carregamento similar' foi omitido/substituído por compatibilidade de formato e codificação de imagem, o que ainda é muito relevante para o contexto.
- **clarity = 0.98**: A resposta gerada possui excelente clareza. Está perfeitamente organizada no formato padrão de User Story e BDD (Dado/Quando/Então), o que garante uma estrutura lógica impecável e elimina ambiguidades. A linguagem é direta, precisa e adequada ao contexto de desenvolvimento, apresentando apenas um leve detalhamento técnico ao mencionar a compatibilidade com o motor do navegador, sem comprometer a compreensão. É concisa, objetiva e vai direto ao ponto.
- **precision = 1.00**: A resposta gerada é altamente precisa, focada e alinhada com a resposta esperada. Ela converte o problema relatado (imagens que não carregam no Safari) em uma História de Usuário com Critérios de Aceitação bem estruturados no padrão BDD (Dado/Quando/Então). Não há alucinações nem informações inventadas; a menção à compatibilidade de formato e codificação de imagem é tecnicamente correta para resolver problemas específicos do Safari. Todos os critérios foram atendidos perfeitamente.

### 12. Dashboard mostra contagem errada de usuários ativos. Mostra 50 mas só há 42 na lista.

<details><summary>Relato completo</summary>

```text
Dashboard mostra contagem errada de usuários ativos. Mostra 50 mas só há 42 na lista.
```
</details>

**Saída do prompt:**

```text
Como um administrador acessando o dashboard, eu quero visualizar a contagem correta de usuários ativos, para que eu possa acompanhar o número real de usuários na plataforma.

Critérios de Aceitação:
- Dado que estou no dashboard do sistema
- Quando visualizo o indicador de usuários ativos
- Então o número exibido deve corresponder exatamente a 42
- E deve ser igual à quantidade total de registros listados na tabela de usuários ativos
- E a contagem não deve exibir divergências em relação aos dados reais listados
```

- **f1_score = 0.72**: Precisão (0.75): A resposta é relevante, mas peca ao chumbado o valor '42' nos critérios de aceitação (tornando a regra rígida em vez de dinâmica) e por apresentar redundância nos critérios 4 e 5. Recall (0.70): A história de usuário e o contexto geral foram cobertos, mas a resposta omitiu pontos importantes do gabarito, como a atualização em tempo real e o filtro explícito para incluir apenas usuários com status 'ativo'.
- **clarity = 0.88**: A resposta é bem organizada no formato padrão de User Story (BDD) e utiliza linguagem simples e direta. No entanto, perde pontos em concisão devido à redundância nos critérios de aceitação, que repetem a mesma regra de validação de três formas diferentes. Além disso, especificar o número estático '42' em vez de uma regra dinâmica afeta levemente a precisão conceitual, embora o texto seja perfeitamente compreensível.
- **precision = 0.93**: A resposta gerada é altamente focada e não apresenta alucinações (nota 1.0 em foco e ausência de alucinações). Ela transforma corretamente o problema relatado em uma User Story com critérios de aceite. O único ponto de imprecisão factual/conceitual está no terceiro critério de aceite, onde o modelo fixou o número '42' como valor estático ('deve corresponder exatamente a 42'), em vez de usar um valor dinâmico baseado no total real da lista (como na resposta esperada). Isso reduz ligeiramente a correção factual (0.8). Média: 0.93.

### 13. No iOS, ao girar o celular para landscape, o layout da tela de perfil fica quebrado.

<details><summary>Relato completo</summary>

```text
No iOS, ao girar o celular para landscape, o layout da tela de perfil fica quebrado.
```
</details>

**Saída do prompt:**

```text
Como um usuário usando iOS, eu quero visualizar corretamente o layout da tela de perfil ao girar o celular para o modo paisagem (landscape), para que eu possa navegar e interagir com minhas informações sem problemas visuais.

Critérios de Aceitação:
- Dado que estou na tela de perfil no aplicativo para iOS
- Quando giro o celular para o modo paisagem (landscape)
- Então o layout da tela de perfil deve se adaptar adequadamente à orientação horizontal
- E todos os elementos visuais, campos e botões devem permanecer visíveis e acessíveis
- E não deve ocorrer nenhuma quebra de layout ou sobreposição de componentes
```

- **f1_score = 1.00**: A resposta gerada cobre perfeitamente todas as informações da resposta esperada (Ground Truth), incluindo a estrutura da história de usuário (persona, objetivo e benefício) e todos os critérios de aceitação (Dado, Quando e Entãos). As pequenas adições do modelo, como detalhar 'campos e botões' ou especificar 'orientação horizontal', são inteiramente relevantes e agregam clareza sem introduzir informações incorretas. Portanto, tanto a Precision quanto o Recall são máximos.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está organizada de forma exemplar no padrão de História de Usuário e Critérios de Aceitação (BDD). A linguagem é direta, simples e precisa, sem qualquer ambiguidade sobre os comportamentos esperados do sistema. Além disso, é extremamente concisa e vai direto ao ponto, mantendo total alinhamento com a resposta de referência.
- **precision = 1.00**: A resposta gerada é altamente precisa, sem nenhuma alucinação e perfeitamente alinhada com a resposta esperada. O modelo transformou a queixa do usuário em uma História de Usuário com Critérios de Aceitação BDD completos e corretos. Todos os elementos (adaptação ao modo paisagem, visibilidade e ausência de sobreposição de componentes) mantêm foco absoluto na pergunta e precisão factual exemplar.

### 14. Campo de email aceita texto sem @, permitindo cadastros inválidos.

<details><summary>Relato completo</summary>

```text
Campo de email aceita texto sem @, permitindo cadastros inválidos.
```
</details>

**Saída do prompt:**

```text
Como um usuário realizando cadastro, eu quero que o campo de email valide o formato correto com "@", para que eu não consiga concluir um cadastro com dados inválidos.

Critérios de Aceitação:
- Dado que estou na tela de cadastro
- Quando informo um texto sem o caractere "@" no campo de email
- Então devo ver uma mensagem de erro indicando que o formato do email é inválido
- E o botão de envio ou cadastro deve permanecer desabilitado ou impedir a submissão
- E o sistema só deve aceitar o cadastro quando um email válido contendo "@" for fornecido
```

- **f1_score = 1.00**: A resposta gerada é excelente, capturando com precisão e completude todos os elementos da resposta esperada. A História de Usuário mantém o mesmo objetivo e valor de negócio. Os Critérios de Aceitação em formato BDD/Gherkin cobrem a tela de cadastro, a ação de inserir e-mail sem '@', a exibição da mensagem de erro explicativa e a impossibilidade de prosseguir com o cadastro. Não há informações incorretas ou irrelevantes.
- **clarity = 1.00**: A resposta gerada apresenta excelente clareza. Está perfeitamente organizada no formato clássico de História de Usuário e Critérios de Aceitação (BDD). A linguagem é simples, direta e acessível. Não há ambiguidade na especificação das regras de validação do formulário, e a resposta é concisa, contendo apenas as informações necessárias para resolver o problema relatado.
- **precision = 1.00**: A resposta gerada é altamente precisa, perfeita no foco e livre de alucinações. O modelo interpretou o problema relatado ('campo de email aceita texto sem @') e estruturou corretamente uma História de Usuário com Critérios de Aceitação em formato BDD (Dado/Quando/Então). O conteúdo reflete perfeitamente a Resposta Esperada (Ground Truth), mantendo a mesma intenção, regras de validação e bloqueio de cadastro para emails inválidos, sem inventar fatos ou adicionar divagações.

### 15. Botão de adicionar ao carrinho não funciona no produto ID 1234.

<details><summary>Relato completo</summary>

```text
Botão de adicionar ao carrinho não funciona no produto ID 1234.
```
</details>

**Saída do prompt:**

```text
Como um cliente navegando na loja, eu quero conseguir adicionar o produto ID 1234 ao carrinho ao clicar no botão correspondente, para que eu possa prosseguir com a minha compra.

Critérios de Aceitação:
- Dado que estou na página do produto ID 1234
- Quando clico no botão de adicionar ao carrinho
- Então o produto deve ser adicionado com sucesso ao meu carrinho de compras
- E devo ver uma confirmação visual de que o item foi adicionado
- E o contador do carrinho deve ser atualizado com a quantidade correta
```

- **f1_score = 1.00**: A resposta gerada manteve perfeitamente a estrutura de História de Usuário e BDD da resposta esperada, cobrindo todos os critérios de aceitação exigidos (Recall = 1.0). Além disso, todas as informações são altamente relevantes e precisas, incorporando corretamente o contexto do produto ID 1234 citado no prompt sem adicionar alucinações (Precision = 1.0).
- **clarity = 1.00**: A resposta possui excelente clareza. Está perfeitamente organizada no formato padrão de História de Usuário com Critérios de Aceitação (Dado-Quando-Então). A linguagem é simples, direta e acessível. Não apresenta ambiguidades, pois especifica claramente o contexto (produto ID 1234), a ação do usuário e os comportamentos esperados do sistema (confirmação visual e atualização do contador). Além disso, é extremamente concisa e objetiva, sem informações redundantes.
- **precision = 1.00**: A resposta gerada é altamente precisa e sem alucinações. Ela traduz o problema do usuário (produto ID 1234) em uma história de usuário e critérios de aceitação praticamente idênticos à resposta esperada (Ground Truth). A única diferença é a especificação do ID 1234 (presente na pergunta), o que torna a resposta até mais contextualizada e totalmente correta factual e funcionalmente.
