<h1>🤖 Rossmann Telegram Bot</h1>

<p>
Bot do Telegram que atua como <b>interface de consumo</b> de um modelo de
<b>Machine Learning em produção</b>, entregando previsões de vendas das lojas
Rossmann de forma simples e acessível ao usuário final.
</p>

<hr/>

<h2>📌 Visão Geral</h2>

<p>
Este projeto implementa um bot que permite ao usuário solicitar previsões
de vendas enviando o número de uma ou mais lojas diretamente pelo Telegram.
</p>

<p>
O bot consome uma <b>API Flask em produção</b> e traduz previsões técnicas
em uma experiência conversacional clara, simulando o uso real de um
produto de dados.
</p>

<p>
O projeto demonstra:
</p>

<ul>
  <li>Consumo de APIs de Machine Learning</li>
  <li>Entrega de valor orientada ao usuário final</li>
  <li>Produto de dados com foco em UX</li>
  <li>Arquitetura baseada em Webhook</li>
</ul>

<hr/>

<h2>💬 Funcionamento</h2>

<ol>
  <li>Usuário envia o número de uma ou mais lojas</li>
  <li>Bot valida e limpa a entrada</li>
  <li>Requisição HTTP é enviada para a API de previsão</li>
  <li>Resultados são tratados, agregados e formatados</li>
  <li>Resposta é enviada ao usuário via Telegram</li>
</ol>

<hr/>

<h2>🧾 Exemplos de Uso</h2>

<b>Loja única</b>
<pre>
25
</pre>

<b>Múltiplas lojas</b>
<pre>
25,3,6,8
</pre>

<hr/>

<h2>📊 Exemplo de Resposta</h2>

<pre>
🏪 Store 25: 💰 R$ 523.412,90
🏪 Store 6: 🚫 closed
🏪 Store 99: ❓ not found

📊 Summary
• Valid predictions: 2
• Closed stores: 1
• Not found: 1

🏆 Top store: 25 (R$ 523.412,90)
🥈 Second: 3 (R$ 487.110,30)
📉 Difference: R$ 36.302,60
</pre>

<hr/>

<h2>⚙️ Funcionalidades</h2>

<ul>
  <li>Consulta de uma ou múltiplas lojas</li>
  <li>Validação de entrada do usuário</li>
  <li>Detecção de lojas fechadas</li>
  <li>Identificação de lojas inexistentes</li>
  <li>Resumo agregado das previsões</li>
  <li>Comparação entre maiores faturamentos</li>
  <li>Rate limit básico por usuário</li>
</ul>

<hr/>

<h2>🏗️ Stack Tecnológica</h2>

<ul>
  <li>Python</li>
  <li>Requests</li>
  <li>Pandas</li>
  <li>Telegram Bot API</li>
  <li>Flask (Webhook)</li>
  <li>Gunicorn</li>
  <li>Render</li>
</ul>

<hr/>

<h2>🌐 Deploy</h2>

<ul>
  <li>Bot publicado em ambiente de produção</li>
  <li>Comunicação via Webhook</li>
  <li>Serviço stateless</li>
  <li>Dependência direta de API externa de ML</li>
  <li>Endpoint de health check</li>
</ul>

<hr/>

<h2>🔗 Projeto Relacionado</h2>

<p>
📡 API de Previsão de Vendas<br/>
<a href="https://github.com/polloncarlos/rossmann_api">
rossmann_api
</a>
</p>

<hr/>

<h2>📈 Próximas Evoluções</h2>

<ul>
  <li>Botões interativos</li>
  <li>Requisições assíncronas</li>
  <li>Histórico de consultas por usuário</li>
  <li>Cache de lojas mais consultadas</li>
</ul>

<hr/>