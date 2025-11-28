🎨 Paleta e identidade visual Market Lace (seu padrão atual)

✔ Fundo: #1A1A1A (dark premium)
✔ Neon principal: #00FF80 (verde neon)
✔ Texto padrão: branco
✔ Bordas secundárias: #2A2A2A / #3A3A3A
✔ Fonte: Inter
✔ Mood: moderno, tech, premium, “cyber sneaker marketplace“

--------------------------------------------------------------- 

Fluxo do Usuário
1) Visitante

Home → Feed → Detalhes → Login

2) Cadastro

Cadastro → Login → Minha Conta

3) Área Logada

Minha Conta → Perfil / Carteira / Configurações

4) Interações

Feed → Detalhes → Revender / Alugar / Trocar
ou
Minha Conta → Meus Anúncios / Meus Pedidos

--------------------------------------------------------

Ajustes para depois do MVP:

Quando estiver logado, trocar o "Login/Cadastro" para o nome do usuário ou para Minha Conta, mesmo ao navegar nas outras paginas

--------------------------------------------------------

 - O que ainda falta fazer?

| Requisito              | Está pronto? | Falta fazer                  |
| ---------------------- | ------------ | ---------------------------- |
| 10 UI                  | ✔            | —                            |
| 3 tabelas              | ✔            | Criar produtos, usuarios e pedidos     |
| 3 operações por tabela | ✔            | Criar INSERT, UPDATE, DELETE |
| Tela Login             | ✔            | —                            |
| Tela Sobre             | ❌            | Criar                        |
| Tela Menu              | ⚠️           | Criar página central         |
| Exportar para JSON zip | ❌            | Implementar rota             |
| Importar dados da web  | ❌            | Implementar requests + UI    |
| Sistema requer login   | ❌            | Proteger rotas               |


| Rota             | Status      | Tipo previsto             |
| ---------------- | ----------- | ------------------------- |
| `/criar-anuncio` | ❌ Em branco | INSERT na tabela anúncios |
| `/seguranca`     | ❌ Em branco | Atualizar senha → UPDATE  |
| `/enderecos`     | ❌ Em branco | CRUD de endereços         |
| `/verificacao`   | ❌ Em branco | Upload documento          |
| `/notificacoes`  | ❌ Em branco | SELECT notificações       |
