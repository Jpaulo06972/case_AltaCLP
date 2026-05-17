# AltaCLP · Workspace

**URL:** https://fde-test.vercel.app/comunicacao

---

AltaCLP
VISÃO GERAL
Início
ORGANIZAÇÃO
Empresa
Pessoas
Governança
OPERAÇÕES
Visão Operacional
Incidentes
COMERCIAL
Clientes
ARQUIVO
Arquivos
Comunicação
/08 — ARQUIVO · COMUNICAÇÃO
Trilha de mensagens.

Dez threads de email entre sócios e equipe. Duas semanas de chat operacional (WhatsApp + Slack). Tudo extraído cru. Lê com calma.

/08.1 — EMAIL INTERNO

Threads ordenadas por relevância, não por data. Cada cabeçalho marca quem escreveu e quando.

THREAD 01
Números da preditiva (Marcos × Roberto, Cláudia em cc)
MENSAGEM INICIAL
Roberto Drummond
roberto.drummond@altaclp.com.br
22/04 · 08:14
PARA
Marcos Tedesco
CC
Cláudia Santarém
ASSUNTO
Visita falsa - Q1 fechado

Marcos,

Fechei o Q1 ontem com a Beatriz. Os números de visita técnica perdida deram R$ 94.200 no trimestre. Anualizado dá R$ 376.800. Isso é mais do que eu te falei na última reunião de conselho.

A Cláudia me mandou a planilha detalhada faz tempo, eu repassei pra você em fevereiro mas acho que você não abriu. Tá em anexo de novo.

Precisamos resolver isso antes do dia 18. Você sabe por quê.

Abs,
Roberto

RESPOSTA
Marcos Tedesco
marcos.tedesco@altaclp.com.br
22/04 · 11:47
PARA
Roberto Drummond
CC
Cláudia Santarém
ASSUNTO
Re: Visita falsa - Q1 fechado

Roberto,

Tô em cima. Contratei uma consultoria de SP, HomoDeus, pra atacar isso com IA. Manutenção preditiva, modelo treinado em cima do nosso histórico. Eles entregam em três meses. Vou levar o escopo na reunião do dia 18.

R$ 27k/mês é o número que eu tô passando pra eles. Cláudia, se o número certo é outro, me corrige.

Att,
Marcos

RESPOSTA
Cláudia Santarém
claudia.santarem@altaclp.com.br
22/04 · 14:02
PARA
Marcos Tedesco
CC
Roberto Drummond
ASSUNTO
Re: Re: Visita falsa - Q1 fechado

Marcos,

O número é R$ 31.4k/mês. Te mandei a planilha atualizada em 24/mar (anexo de novo, terceira vez). A diferença é o reajuste de combustível de fevereiro e o aumento dos técnicos.

Sobre IA pra preditiva, registro de novo o que já falei em ata: com nosso label de dado a 50%, expectativa realista é 20% de redução, não 70%. Existe um caminho mais rápido pra metade do problema (ajuste de threshold máquina-a-máquina, ~1 semana de trabalho dedicado), mas vc descartou na última conversa.

Att,
Cláudia

THREAD 02
Incidente Diadema (cosméticos)
MENSAGEM INICIAL
Cláudia Santarém
claudia.santarem@altaclp.com.br
23/01 · 22:48
PARA
Equipe Engenharia
CC
Marcos Tedesco
ASSUNTO
URGENTE - Belmare Cosméticos Diadema - linha parada

Time,

Linha 3 da Belmare parou às 19h40. Batelada transbordou no tanque T-204, derrubou misturador e linha de envase. Cliente estima 36h pra limpar e voltar.

Júnior tá no chão agora. Acabei de subir o supervisório aqui de casa, o timer do batch tá em 45min. Anderson, vc lembra de ter alterado isso pra 30min em janeiro do ano passado? O cliente jurou que tinha pedido a mudança.

Júnior fez deploy da v2.4.7 hoje cedo (off-hours, conforme combinado). Subiu o que tava no Git. Não passou pela validação porque a gente nunca padronizou isso, eu sei, e agora não é a hora de discutir isso.

Quem viu o changelog da v2.4.7? Tem algum delta de timer?

Cláudia

RESPOSTA
Anderson Vasconcellos
anderson.vasconcellos@altaclp.com.br
23/01 · 23:31
PARA
Cláudia Santarém
CC
Equipe Engenharia
ASSUNTO
Re: URGENTE - Belmare Cosméticos Diadema - linha parada

Cláudia,

Lembro sim, alterei o timer pra 30min em 14/jan/25, foi uma visita de emergência, o cliente reclamou que a mistura tava saindo grossa. Eu não fiz push pro Git porque não consegui conectar internet no chão (a Belmare só libera VLAN pra equipamento deles). Deixei nota no caderno de campo, achei que tinha avisado.

Não tinha changelog formal do hotfix. Mil desculpas. Eu sei como isso parece.

Att,
Anderson

RESPOSTA
Marcos Tedesco
marcos.tedesco@altaclp.com.br
24/01 · 06:12
PARA
Cláudia Santarém
CC
Anderson Vasconcellos
ASSUNTO
Re: URGENTE - Belmare Cosméticos Diadema - linha parada

Cláudia, Anderson,

Acabei de falar com o Eduardo da Belmare. Eles vão cobrar. Vou negociar. Anderson, da próxima vez que vc fizer alteração no campo, manda pelo menos um whatsapp pra Cláudia, beleza? Caderno não conta.

Não quero falar de processo agora. Quero a linha de volta. Júnior tá no chão sozinho?

M.

THREAD 03
Cotação técnica perdida (comercial × engenharia)
MENSAGEM INICIAL
João Bittencourt
joao.bittencourt@altaclp.com.br
11/03 · 17:22
PARA
Cláudia Santarém
CC
Marcos Tedesco
ASSUNTO
Perdemos a Termalt

Cláudia,

Acabei de ligar pra Vinícius da Termalt. Eles fecharam com a Mecasul ontem. Cotação técnica deles chegou na segunda passada (5 dias depois do meu primeiro contato), a Mecasul tinha entregado na terça da semana anterior.

Cláudia, eu sei que vc tá afogada, mas isso aqui é o sexto que escorrega esse ano. Ticket de uns R$ 110k. Eu tô tendo que inventar desculpa pra cliente.

Marcos, a gente precisa conversar sobre isso. Eu mando os áudios, descrevo as fábricas direitinho, faço meu papel. Tá demorando demais aqui dentro.

Abs,
João B.

RESPOSTA
Cláudia Santarém
claudia.santarem@altaclp.com.br
11/03 · 19:08
PARA
João Bittencourt
CC
Marcos Tedesco
ASSUNTO
Re: Perdemos a Termalt

João,

Áudio da Termalt teve 11 minutos. Você descreveu três áreas da fábrica mas misturou nome de equipamento (chamou "extrusora" mas pelo contexto era moldadora). Eu mandei email com 4 perguntas dia 28/fev. Você respondeu dia 04/mar. Eu mandei mais 2 perguntas dia 04/mar tarde. Você respondeu dia 06/mar. Eu fechei BOM dia 06/mar à noite. Demorou pra você 6 dias, demorou pra mim 4 horas.

Não tô brigando. Tô dizendo. Se a gente acelera essa ponte, a gente fecha mais.

Cláudia

RESPOSTA
Marcos Tedesco
marcos.tedesco@altaclp.com.br
12/03 · 08:45
PARA
João Bittencourt
ASSUNTO
Re: Re: Perdemos a Termalt

João,

Almoço quinta? Bira's, 12h30.

M.

THREAD 04
Anaclara Alimentos (Boituva)
MENSAGEM INICIAL
Henrique Quintela
hquintela@anaclara.com.br
18/04 · 09:33
PARA
Marcos Tedesco
CC
João Bittencourt
ASSUNTO
Antecipação das 4 máquinas - junho

Marcos,

Bom dia. Como conversamos por telefone, precisamos antecipar a entrega das 4 máquinas da linha 7 de outubro para junho. Já reorganizamos nosso planejamento de obra civil e elétrica em função disso, e o cronograma de start-up da fábrica nova depende dessa antecipação.

Conto com você. As 4 máquinas representam R$ 780k pra nós e fizemos um esforço enorme pra fechar a compra com a AltaCLP no ano passado.

Aguardo confirmação até sexta-feira.

Att,
Henrique Quintela
Diretor Industrial — Anaclara Alimentos

RESPOSTA
Marcos Tedesco
marcos.tedesco@altaclp.com.br
18/04 · 11:24
PARA
Henrique Quintela
CC
João Bittencourt
ASSUNTO
Re: Antecipação das 4 máquinas - junho

Henrique,

Bom dia. Confirmado, entregamos em junho. Já estou reorganizando a equipe de engenharia internamente pra absorver. Cláudia vai te ligar essa semana pra alinhar os FATs.

Pode contar comigo.

Att,
Marcos Tedesco
Sócio-Fundador — AltaCLP Indústria S.A.

RESPOSTA
Cláudia Santarém
claudia.santarem@altaclp.com.br
18/04 · 14:50
PARA
Marcos Tedesco
ASSUNTO
Boituva - antecipação

Marcos,

Vi sua resposta pro Henrique. Não consigo entregar 4 máquinas em junho com a equipe atual e o backlog que está. Já te falei isso 2 vezes essa semana.

Pra fazer isso, eu precisaria de:
- Anderson 100% nas 4 da Anaclara (hoje ele tá em 2 outras)
- pausar 2 comissionamentos de cliente menor (Termoflex e Vinhal)
- ou contratar 2 engs sêniors imediatamente (4-6 meses pra estar produtivo)

Nenhum desses é viável em 4 semanas.

Cláudia

RESPOSTA
Marcos Tedesco
marcos.tedesco@altaclp.com.br
18/04 · 15:11
PARA
Cláudia Santarém
ASSUNTO
Re: Boituva - antecipação

Cláudia,

A gente dá um jeito. Eu não posso perder esse cliente agora. Conversa comigo segunda.

M.

THREAD 05
Sérgio do TPM apoiando (fachada)
MENSAGEM INICIAL
Sérgio Mancuso
sergio.mancuso@altaclp.com.br
19/02 · 10:14
PARA
Marcos Tedesco
CC
Cláudia Santarém
ASSUNTO
Projeto preditiva IA - meu apoio

Marcos,

Conforme conversamos hoje cedo, registrando aqui que apoio 100% o projeto de manutenção preditiva com IA. Os números da Cláudia são gritantes e a abordagem com modelo treinado em cima do histórico parece o caminho certo.

Pode contar com o TPM pra disponibilizar os dados do PostgreSQL e o broker MQTT. Vou pedir pro time já ir mapeando os schemas pra acelerar o onboarding da consultoria.

Att,
Sérgio Mancuso
Coordenador TPM — AltaCLP

THREAD 06
Sérgio bloqueando (a verdade)
MENSAGEM INICIAL
Sérgio Mancuso
sergio.mancuso@altaclp.com.br
29/04 · 17:48
PARA
Tiago Borba
ASSUNTO
Dados de sensor - HomoDeus

Tiago,

Aquela consultoria de SP (HomoDeus) provavelmente vai pedir acesso ao banco de sensores em algumas semanas. Quando pedirem, manda pra mim antes de liberar qualquer coisa. Eu quero dar uma olhada nos schemas e ver o que faz sentido expor.

Te falo entre nós: esse projeto de IA tá indo rápido demais. O Marcos comprou o discurso sem olhar com cuidado. Se a gente expor o banco inteiro pra consultoria externa eles vão achar coisa que a gente não quer expor (dados sujos da Belmare, NaN do sensor 7 que ficou 2 meses fora, log de manutenção sem padrão).

Eu não sou contra a IA, mas a gente precisa primeiro arrumar a casa. E isso eu venho falando faz tempo. Não foi ouvido. Agora a gente vai expor isso pra um terceiro.

Se eu fosse você, atrasaria a entrega dos schemas em uma semana. Diz que tá com problema de permissão no PG. Eu cubro vc.

Sérgio

THREAD 07
Roberto e advogado (DD em curso)
MENSAGEM INICIAL
Roberto Drummond
roberto.drummond@altaclp.com.br
15/04 · 19:33
PARA
Felipe Tannure
ASSUNTO
Materiais para DD - estágio 2

Felipe,

Boa noite. Conforme alinhado na nossa reunião de 08/abr, segue checklist do que ainda precisamos preparar pra próxima fase:

1. Balanço auditado dos últimos 3 anos (Beatriz já tem, faltam ajustes do auditor)
2. Lista de contratos ativos com cláusula de cessão (~42 contratos, ~18 com cláusula crítica)
3. Indicadores operacionais consolidados (Q1 2026) — pedi pra Beatriz consolidar
4. Mapa de propriedade intelectual (códigos-fonte, supervisórios, marcas registradas)
5. Litígios e contingências (sem novidade, mas precisa atualizar)
6. Quadro societário consolidado e acordo de acionistas (você tem a versão atual)

Sobre o ponto 3, eu tô preocupado. Os indicadores brutos têm umas pedras que vão chamar atenção do comitê de investimento (backlog de comissionamento, número de incidentes em campo, perdas operacionais recorrentes). Se a gente apresenta cru, o preço cai. O Marcos não tá tratando isso com a urgência necessária. Ele acha que tem 6 meses, e a gente tem 6 semanas.

Você consegue ver com o pessoal do fundo se dá pra escalonar a apresentação desses indicadores? Tipo, apresentar com plano de ação anexo?

A reunião do dia 18 de maio vai definir. O Marcos disse que vai chegar com pelo menos o projeto de preditiva fechado.

Confidencial. Não copio o Marcos nessa thread.

Abs,
Roberto

RESPOSTA
Felipe Tannure
ftannure@tannureadvogados.com.br
16/04 · 09:47
PARA
Roberto Drummond
ASSUNTO
Re: Materiais para DD - estágio 2

Roberto,

Sobre o ponto 3, dá sim. O comitê do fundo aceita apresentação consolidada acompanhada de plano de ação aprovado pelo board. O importante é que o plano seja crível, com prazo, custo, e responsáveis claros. Eles vão querer ver execução já em andamento, não promessa.

Sobre confidencialidade: estamos cobertos pelo NDA. Mas considera trazer o Marcos pra dentro logo. Se ele descobrir o estágio da conversa por terceiros, vc pode ter problema societário sério (ele tem 70% das ações ordinárias, lembra disso).

Marcamos pra próxima quarta às 16h?

Att,
Felipe Tannure

THREAD 08
Belmare ameaçando rescisão
MENSAGEM INICIAL
Eduardo Casagrande
ecasagrande@belmare.com.br
04/02 · 11:18
PARA
Marcos Tedesco
CC
Cláudia Santarém
ASSUNTO
Linha 3 - posição contratual

Marcos,

Bom dia.

Após o incidente de 23/01 que paralisou a Linha 3 por 36 horas, conforme já comunicamos verbalmente, nossa diretoria solicitou parecer jurídico sobre as opções contratuais. O contrato vigente prevê multa de 2% do valor anual por incidente que cause parada superior a 24 horas, e rescisão imediata sem ônus caso ocorram dois incidentes graves em 12 meses.

Este é o primeiro incidente. Mas é o sétimo evento de "manutenção" ou "ajuste" não planejado registrado pela nossa equipe nos últimos 14 meses. Estamos perdendo confiança.

Pra continuarmos, precisamos:
1. Relatório de causa raiz formal até 14/fev
2. Plano de ação corretiva com prazo
3. Crédito de R$ 140.000 conforme já alinhado verbalmente
4. Garantia de que o código rodando nos nossos CLPs é o mesmo do seu repositório central, com auditoria mensal

O ponto 4 é não-negociável. Não quero ouvir "achamos que sim". Quero auditoria automática.

Att,
Eduardo Casagrande
Diretor de Operações — Belmare Cosméticos

RESPOSTA
Marcos Tedesco
marcos.tedesco@altaclp.com.br
04/02 · 14:02
PARA
Eduardo Casagrande
CC
Cláudia Santarém
ASSUNTO
Re: Linha 3 - posição contratual

Eduardo,

Recebido. Eu te ligo amanhã cedo. A Cláudia já tá produzindo o relatório de causa raiz. Sobre o ponto 4 (auditoria automática), aceito e a gente vai implementar. É a coisa certa.

Crédito de R$ 140k aprovado.

Marcos

THREAD 09
RH: pedido de demissão Júnior
MENSAGEM INICIAL
Beatriz Ourique
beatriz.ourique@altaclp.com.br
06/05 · 16:42
PARA
Marcos Tedesco
CC
Cláudia Santarém
ASSUNTO
Pedido de demissão - João Roberto Salenave (Júnior)

Marcos, Cláudia,

O Júnior entregou o pedido de demissão hoje cedo. Ele aceitou proposta da Atos pra ir como engenheiro de aplicação sênior, salário 38% acima do que ele recebe aqui. Aviso prévio até 05/jun.

Cláudia, ele me falou que tinha conversado com você na semana passada sobre as entrevistas. Marcos, ela não tinha te contado ainda porque queria primeiro tentar a contraproposta. A diferença salarial é grande demais pra cobrirmos.

Posso já abrir a vaga? Ou vocês querem conversar primeiro?

Att,
Beatriz Ourique
RH — AltaCLP

RESPOSTA
Cláudia Santarém
claudia.santarem@altaclp.com.br
06/05 · 17:08
PARA
Beatriz Ourique
CC
Marcos Tedesco
ASSUNTO
Re: Pedido de demissão - João Roberto Salenave (Júnior)

Beatriz,

Pode abrir. Marcos, com Júnior saindo eu fico com 3 engs pra 26 máquinas no backlog (e Boituva no meio). Antes de você responder, lê isso: NÃO É HORA de adiar comissionamento. Vamos conversar amanhã 8h.

Cláudia

RESPOSTA
Marcos Tedesco
marcos.tedesco@altaclp.com.br
06/05 · 19:33
PARA
Cláudia Santarém
CC
Beatriz Ourique
ASSUNTO
Re: Re: Pedido de demissão - João Roberto Salenave (Júnior)

Cláudia,

Amanhã 8h. Beatriz, abre a vaga. Considera publicar no LinkedIn e na lista da Aciesp também.

Cláudia, sobre adiar comissionamento, ninguém falou em adiar. Só não posso aumentar headcount essa semana com a DD acontecend... com o trimestre como tá.

M.

THREAD 10
Anderson reclamando da carga
MENSAGEM INICIAL
Anderson Vasconcellos
anderson.vasconcellos@altaclp.com.br
09/05 · 22:14
PARA
Cláudia Santarém
ASSUNTO
Off

Cláudia,

To em casa, acabei de chegar de Anápolis. Foram 11 dias no chão lá. O Henrique da Anaclara me ligou três vezes nos últimos dois dias perguntando da antecipação. Eu não tenho resposta pra dar.

Eu queria te falar uma coisa direta. Eu tô cansado. Nas últimas 8 semanas eu trabalhei 7 fins de semana. Eu tenho dois filhos pequenos. Eu não tô pedindo aumento, eu tô pedindo planejamento. A gente tá tampando buraco há tanto tempo que eu não lembro mais qual era o plano original.

A Daniela me falou que vc deu uma trabalhada nos templates de comissionamento na semana passada. Manda pra mim antes do fim de semana? Eu posso testar segunda no comissionamento da Vinhal.

Sobre o Júnior, fica entre nós, ele já tinha me falado faz um mês. Eu tava esperando ele te contar.

Anderson

RESPOSTA
Cláudia Santarém
claudia.santarem@altaclp.com.br
09/05 · 23:02
PARA
Anderson Vasconcellos
ASSUNTO
Re: Off

Anderson,

Vou te mandar amanhã o template. Tá em rascunho, falta a parte de validação farma e calibração de pressão. Versão suja, vc vai ter que adaptar pra Vinhal.

Sobre o resto. Eu tô vendo. Eu tô falando com gente externa pra ajudar (consultoria de SP, HomoDeus, talvez você já tenha ouvido). Não é solução de mês que vem, é solução de daqui 6-8 semanas. Eu preciso que vc segure até lá. Eu sei que é injusto pedir.

Se ficar insustentável, me fala antes de mandar email pro Marcos.

Cláudia

/08.2 — CHAT OPERACIONAL · 28/04 → 16/05
O que vaza no WhatsApp.
28 ABR
08:14
Daniela P.
gente alguém viu o relatório da visita da Vinhal? Carlos tá pedindo
08:16
Carlos M.
deixa quieto, achei
08:17
Carlos M.
visita de ontem do Tarcísio. Alerta sensor pressão M-VH-118. Tarcísio anotou aqui "tudo normal, sensor calibrando, sem evento"
08:18
Carlos M.
terceira visita "sem evento" no mesmo sensor em 6 semanas
08:19
Cláudia S.
terceira???
08:21
Carlos M.
19/mar, 03/abr, 27/abr
08:22
Cláudia S.
Carlos isso é gritante. Põe na próxima reunião comigo
08:23
Carlos M.
tá. mas quando
29 ABR
11:48
Daniela P.
ALÔ pessoal, Belmare ligando, é a Cláudia ou o Anderson?
11:49
Daniela P.
pessoal????
11:51
Anderson V.
eu pego, manda pra mim
11:53
Daniela P.
já passei. Eduardo deles, quer falar do plano de auditoria. avisado.
30 ABR
14:02
Marcos T.
Anderson liga aqui qd puder
14:04
Anderson V.
30min
14:33
Marcos T.
ok
02 MAI
09:11
Júnior
galera, tô em Ponta Grossa, o CLP da máquina 4 não tá conectando. firmware certo, IP certo. alguém pode dar uma luz
09:14
Anderson V.
tá usando o cabo novo ou o velho?
09:15
Júnior
novo
09:15
Anderson V.
troca pelo velho
09:21
Júnior
kkkkk conectou. velho engatou de primeira
09:22
Anderson V.
o cabo novo é Made in China, não confia
09:24
Cláudia S.
anota isso em algum lugar antes que outra pessoa caia na mesma
04 MAI
16:34
Daniela P.
Henrique Anaclara ligou de novo, quer falar com Marcos
16:35
Daniela P.
Marcos tá em call
16:37
Daniela P.
ok ele pediu pra retornar amanhã. terceira vez essa semana
16:38
Cláudia S.
não tenho como responder o Henrique sem o Marcos
16:42
Marcos T.
eu falo com o Henrique amanhã cedo. Cláudia me liga 7h30
05 MAI
07:14
Marcos T.
Cláudia, no whats agora?
07:16
Cláudia S.
tô
07:16
Marcos T.
ligo
10:48
Daniela P.
pessoal sistema do supervisório da Termoplast caiu, eles tão ligando
10:49
Júnior
não é com a gente, Termoplast é Mecasul
10:50
Daniela P.
ahhh é mesmo. eles confundem todo mês
10:51
Anderson V.
porque o operador deles é nosso ex
10:52
Daniela P.
kkkkk
07 MAI
13:22
Beatriz A.
galera, lembrando, na sexta dia 18/maio tem reunião de conselho, escritório fica fechado de 14h às 18h. Daniela, segura tudo
13:23
Daniela P.
anotado
13:25
Cláudia S.
Bea o material da reunião você já fechou? Quero ver os números antes
13:26
Beatriz A.
Marcos pediu pra fechar só com ele primeiro
13:27
Cláudia S.
tá
13:27
Cláudia S.
👀
08 MAI
17:48
Júnior
cláudia, tá vendo o pull request da v2.5.2? aprovei o do Anderson, mas tem um conflito no timer da Belmare. ele tá tentando subir 30min, no Git tá 45min
17:50
Cláudia S.
30min. Não MEXE no 45 pelo amor de deus. Anderson, tá vendo isso?
17:51
Anderson V.
tô. Júnior, deixa o 30min. eu mando uma issue depois explicando
17:52
Júnior
ok mergeado
09 MAI
09:11
Daniela P.
João vendedor mandou áudio de 14 min pro Whats do comercial pedindo cotação Termalt 2
09:12
Daniela P.
14 minutos cláudia
09:14
Cláudia S.
⛓️‍💥
09:14
Cláudia S.
manda pra mim depois eu ouço enquanto janto
10 MAI
22:08
Anderson V.
Cláudia tô voltando agora de Anápolis. cliente fechou o site. 11 dias.
22:10
Cláudia S.
boa Anderson. obrigada. te ligo amanhã
11 MAI
08:33
Carlos M.
alerta da Belmare máquina 3 de novo. sensor temp tanque T-204. já dispararam 3x essa semana
08:34
Carlos M.
o Joelson tá em Sorocaba, posso mandar ele agora
08:35
Cláudia S.
ESPERA. é a mesma máquina do incidente. tô vendo o histórico aqui. último alerta dia 8, dia 9, hoje. Não despacha ainda
08:36
Carlos M.
tá. mas o cliente vai cobrar
08:37
Cláudia S.
cobra. eu prefiro 1 hora de cliente bravo do que 1 dia de carro à toa
08:40
Cláudia S.
Joelson, NÃO sai. me liga
08:41
Joelson
ok
12 MAI
11:14
Marcos T.
gente quem viu o Sérgio?
11:15
Daniela P.
tá em reunião com o pessoal do PG
11:16
Marcos T.
ok
14:32
Daniela P.
gente alguém viu o Júnior? cliente Termalt no telefone bravo
14:34
Cláudia S.
deve ter saído pro almoço, eu pego
14:35
Daniela P.
Termalt 2, não Termalt 1, só pra confirmar
14:36
Cláudia S.
ok
13 MAI
16:08
Júnior
galera, último dia hoje é dia 05/06. tô passando coisa pra Daniela L. e pro Anderson essa semana. qualquer coisa me chama
16:09
Anderson V.
👍
16:09
Cláudia S.
❤️
16:14
Beatriz A.
Júnior, vc tem que assinar a rescisão na sexta às 10h, manda confirmação
16:15
Júnior
confirmado
14 MAI
08:48
Marcos T.
Cláudia, a consultoria de SP confirma sexta às 15h. João Paulo Ferreira da HomoDeus, lembra
08:49
Cláudia S.
lembro. falei com ele quarta
08:50
Marcos T.
ele te pediu o que?
08:52
Cláudia S.
número, contexto, planilhas
08:53
Marcos T.
ok. me passa o que você passou pra ele
09:01
Cláudia S.
já tá no email que mandei dia 22/abr pra vc e pro Roberto
09:02
Marcos T.
👍
15 MAI
10:22
Daniela P.
pessoal, "executivos externos" chegando hj 14h, visita confidencial conforme Roberto. servir café. Sérgio reservou sala 3.
10:23
Cláudia S.
quem
10:24
Daniela P.
Roberto não passou nome
10:25
Cláudia S.
hmm
10:27
Anderson V.
👀
10:30
Daniela P.
Marcos, ele falou que ficaria a tarde na fábrica acompanhando
10:31
Anderson V.
estranho ninguém ter pautado essa visita antes
10:33
Cláudia S.
Anderson volta pro template
17:42
Carlos M.
alerta válvula M-SR-409 Sorocaba Industrial. critico. mandar alguém?
17:44
Carlos M.
alô???
17:48
Anderson V.
opa desculpa estava no shutdown. é a quinta vez essa válvula esse mês. cancela. provavelmente sujeira no sensor
17:49
Carlos M.
cliente vai cobrar
17:50
Anderson V.
cobra. eu falo com eles
17:52
Cláudia S.
anota válvula M-SR-409 pra revisar threshold semana que vem
16 MAI
09:14
Marcos T.
Cláudia, Beatriz, Roberto. Reunião dia 18 às 14h. material final tem que estar pronto até quarta 17h. Beatriz fecha o financeiro, Cláudia fecha o operacional. Tudo num pdf único.
09:15
Beatriz A.
ok
09:18
Cláudia S.
o operacional vai mostrar o backlog real (26 máquinas, 13 atrasadas) ou os números arredondados que vc tem usado?
09:21
Marcos T.
número real. sem maquiar. te confio.
09:22
Cláudia S.
ok
09:23
Cláudia S.
🙏
13:48
Daniela P.
pessoal, Henrique Anaclara mandou email pedindo confirmação final das datas das 4 máquinas. Quem responde?
13:50
Cláudia S.
eu peguei. respondo até segunda.
13:51
Anderson V.
o que vai falar?
13:53
Cláudia S.
verdade. 2 das 4 a gente entrega em junho. as outras 2 só em julho. melhor escutar agora do que depois.
13:54
Anderson V.
e o Marcos?
13:55
Cláudia S.
eu aviso ele antes de mandar