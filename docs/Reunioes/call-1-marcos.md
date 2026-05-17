# AltaCLP Indústria S.A. — Transcrições de Call

---

## CALL 1 — Marcos Tedesco (CEO/Sócio-Fundador) × João Paulo Ferreira

*Data: terça-feira, 14h05. Marcos liga do escritório dele em Sorocaba. Ruído de impressora ao fundo nos primeiros minutos. João Paulo do escritório da HomoDeus.*

---

**Marcos Tedesco** *[00:00]*: Alô, alô, é o João Paulo? Tá me ouvindo? Espera um pouquinho que essa porcaria de impressora aqui... DANIELA! DANIELA, fecha a porta aí por favor. Pronto, desculpa, é que aqui é uma loucura, a gente tá no meio de um startup de máquina pra um cliente em Anápolis e o pessoal tá entrando e saindo da minha sala que nem barata tonta. Mas beleza, tô com você.

**João Paulo** *[00:32]*: Tô ouvindo sim, Marcos, boa tarde. Obrigado pelo tempo. Pode falar à vontade.

**Marcos Tedesco** *[00:38]*: Então cara, deixa eu te situar. AltaCLP, a gente tá há vinte e dois anos no mercado, eu fundei a empresa com mais dois sócios, o Roberto e o falecido Augusto, Deus o tenha. Hoje a gente é uma empresa de uns trezentos e vinte funcionários, atende uns quarenta e poucos clientes, tudo fábrica grande, fábrica de verdade. Alimento, química, papel e celulose, mineração no norte, a gente tem cliente até numa fábrica de sódio lá em Cubatão, coisa pesada. A gente projeta, monta e programa CLP, faz supervisório em Lua, código de máquina em Structured Text, instala em campo, dá manutenção. Pacote completo. O cliente compra a máquina e a gente entrega ela viva, respirando.

**João Paulo** *[01:28]*: Entendi. E o time de campo, hoje, quantos técnicos vocês têm rodando?

**Marcos Tedesco** *[01:33]*: Olha, técnico de campo a gente tem... tem vinte e dois técnicos. Vinte e dois técnicos espalhados pelo Brasil. Mais quatro engenheiros de aplicação aqui dentro, que é o pessoal da Cláudia, você vai falar com ela depois, a Cláudia é foda, ela toca a engenharia de aplicação faz uns doze anos, conhece cada parafuso. E tem o time comercial, três vendedores, e o pessoal de back office. Mas o problema, cara, o PROBLEMA mesmo, que é o que eu queria te falar...

**Marcos Tedesco** *[02:08]*: ...é a manutenção preditiva. A gente tá afogado. Afogado. Os CLPs em campo geram um volume absurdo de dados, eu acho que é... peraí... a Cláudia me falou outro dia que era doze mil e quinhentas leituras por dia, por máquina, sensor digital, sensor analógico, válvula, bomba, motor, tudo mandando telemetria. E a gente bolou um sistema lá faz três anos pra gerar alerta quando algum sensor sai do range esperado. E aí o que acontece. O sistema dispara alerta, o técnico pega o carro, dirige três horas até o cliente, chega lá, mede tudo, tá tudo certo. Tá tudo certo. Sessenta por cento das visitas, sessenta por cento, é falso alarme. Sessenta por cento. Eu tô torrando vinte e sete mil reais por mês em deslocamento de técnico pra não fazer nada. Vinte e sete mil. Quase trezentos e cinquenta mil por ano jogados fora.

**João Paulo** *[03:12]*: E esse sistema de alerta, ele foi feito internamente?

**Marcos Tedesco** *[03:15]*: Internamente, pelo Sérgio. Não, peraí, foi o Sérgio do TPM ou foi o Sérgio da Cláudia? Foi o Sérgio da Cláudia, que saiu, agora tá na Weg. O cara fez uns threshold fixo em cima do sinal Modbus, depois a gente colocou OPC UA em algumas máquinas mais novas, mas o threshold continua burro. Se o sensor de temperatura passa de oitenta e cinco graus, alerta. Mas oitenta e cinco graus numa máquina de chocolate é uma coisa, oitenta e cinco numa caldeira de papel é outra. O sistema não sabe.

**Marcos Tedesco** *[03:51]*: E aí o que eu quero, cara, é uma IA. Uma IA que olha o histórico e decide se é alerta de verdade ou não. Eu quero te contratar pra construir isso. Manutenção preditiva com IA. Eu já vi várias empresas vendendo isso, GE, Siemens, mas é caríssimo, e eu acho que com vocês da HomoDeus a gente faz mais rápido, mais barato, mais sob medida. Esse é o problema número um. Esse é o que tá me tirando o sono.

**João Paulo** *[04:22]*: Anotado. E o número dois?

**Marcos Tedesco** *[04:25]*: O número dois é... espera, deixa eu pensar... ah, é o comissionamento. Cara, comissionamento. Toda vez que a gente vende uma máquina nova, ou monta uma máquina nova pra um cliente, tem que comissionar. Comissionar é o seguinte, é configurar o CLP pro cenário específico do cliente, pôr os limites, calibrar sensor, fazer o FAT, fazer o SAT, treinar o operador do cliente. Cada máquina nova come três, quatro dias de engenheiro de aplicação. Engenheiro de aplicação, não técnico de campo, engenheiro. Que aqui ganha bem, e que eu só tenho quatro. A Cláudia mais três meninos. E hoje eu tenho um backlog de vinte e duas máquinas esperando comissionamento. Vinte e duas. Algumas dessas máquinas tão paradas no galpão do cliente há sessenta dias, o cliente já pagou, e a gente não consegue ligar.

**João Paulo** *[05:18]*: Vocês têm um runbook ou um template padrão pra comissionamento?

**Marcos Tedesco** *[05:22]*: Tem... tem uma coisa, mas é cada engenheiro com o jeito dele. O Anderson tem o caderninho dele, a Cláudia tem uma planilha, o Júnior eu acho que só tem na cabeça. Claro, funciona super bem o nosso sistema atual de notas no caderno. A gente tentou padronizar duas vezes, não rolou. E aí toda vez que entra alguém novo, leva seis meses pra produtir igual a um cara antigo. Seis meses. E o pior, cada cliente tem seu jeito, cliente alimento exige um nível de validação, cliente farmacêutico exige outro, cliente químico é outra história ainda, então não dá pra fazer um template único.

**João Paulo** *[06:04]*: Eu queria voltar nos vinte e dois técnicos. Eles tão divididos por região?

**Marcos Tedesco** *[06:09]*: Tão, tão sim. Sudeste tem dez, sul tem quatro, nordeste tem três, e o resto rodando. Mas isso é menos importante agora. Continuando, o problema três. Problema três é o seguinte, e isso aqui é, cara, isso aqui me dá vontade de chorar. A gente tem um repositório Git central. Tudo bonito. Toda a base de código dos supervisórios, toda a base de Structured Text, tudo versionado, tudo certinho. Aí o técnico vai pra campo, tá lá no cliente, máquina parou. Cliente gritando. O técnico abre o notebook, conecta no CLP, descobre que tem um bug. Faz um hotfix ali na hora, no Structured Text, na Lua do supervisório, salva, máquina volta a rodar, cliente para de gritar, todo mundo feliz. Aí o técnico vai embora.

**Marcos Tedesco** *[06:58]*: E o fix nunca volta pro repositório central. Nunca. O cara não dá push. Não tem como dar push do campo às vezes, o cliente não deixa conectar internet, ou o cara esquece, ou tá morto de cansado, ou simplesmente não pensa nisso porque ele é técnico de chão, não é desenvolvedor. Então o que acontece. Seis meses depois, outro técnico vai pro mesmo cliente, baixa a versão "oficial" do código, sobe na máquina, e quebra tudo. Porque o que tá rodando lá não é o que tá no Git. Esse ano deu três incidentes graves. TRÊS. Um deles foi numa fábrica de cosméticos em Diadema, parou a linha por quase trinta e seis horas. O cliente quase rescindiu contrato.

**João Paulo** *[07:42]*: Vocês têm algum mecanismo de pull do código que tá rodando na máquina pra comparar com o Git?

**Marcos Tedesco** *[07:48]*: Não. Não temos. A gente confiava na disciplina do técnico. Spoiler, não funciona.

**Marcos Tedesco** *[07:56]*: Problema quatro, comercial. Cara, comercial é matador. O ciclo de cotação técnica. Cliente liga pro vendedor, ou manda WhatsApp, fala "preciso de um sistema pra automatizar a linha tal, isso, isso e isso." Vendedor manda pra engenharia, engenharia dimensiona, escolhe os CLPs, calcula quantos pontos de IO, quantos sensores, quantos atuadores, monta a BOM, manda pra precificação, volta pro vendedor, vendedor manda pro cliente. Esse ciclo todo, hoje, tá levando cinco a sete dias. Cinco a sete. E olha, o nosso concorrente principal, a Mecasul, devolve cotação técnica em vinte e quatro horas. Vinte e quatro. A gente tá perdendo... a gente tá perdendo seis negócios por mês por causa disso. Seis. Em fechamento isso é uns... uns oitenta mil reais por mês de ticket médio que escorrega pela mão.

**João Paulo** *[08:51]*: Por que demora cinco a sete dias?

**Marcos Tedesco** *[08:54]*: Por quê? Porque a engenharia tá afogada, porque cada cotação é manual, porque o vendedor manda um WhatsApp de áudio de oito minutos descrevendo a fábrica do cliente, porque a engenharia tem que ouvir, transcrever, entender, e aí ir lá montar a BOM no Excel, e o Excel mata um pouco do Roberto toda vez. E enquanto isso o cliente tá esperando. Cinco dias depois ele já comprou da Mecasul. Acabou.

**Marcos Tedesco** *[09:21]*: E aí tem o quinto, que é... peraí, deixa eu te falar uma coisa primeiro, fora do roteiro. O meu filho, o Bruno, ele tá entrando agora na faculdade de engenharia em Campinas, na Unicamp, passou no vestibular, eu tô explodindo de orgulho. O cara é... ele é mais inteligente do que eu já fui na vida, e ele tem dezessete anos. Eu tô falando isso porque, sei lá, eu olho pra ele e penso, esse cara vai entrar num mercado onde a IA já tá fazendo metade do trabalho. E o que eu posso ensinar pra ele? Ah, e isso me lembrou, o cliente de Boituva, Anaclara Alimentos, pediu pra antecipar quatro máquinas pra junho. Quatro máquinas que tavam previstas pra outubro. Eu não tenho como entregar. Eu não tenho engenheiro de aplicação pra comissionar isso. E é cliente grande, quatro máquinas é cliente grande, é meio milhão de faturamento.

**João Paulo** *[10:18]*: Junho desse ano?

**Marcos Tedesco** *[10:20]*: Junho desse ano. Daqui quatro semanas.

**João Paulo** *[10:24]*: Beleza. E o quinto problema?

**Marcos Tedesco** *[10:27]*: O quinto. O quinto é o suporte de campo. O técnico vai pro cliente, chega lá, e não tem contexto nenhum sobre o que aconteceu antes. Não sabe se outro técnico já foi no mês passado. Não sabe que peça foi trocada. Não sabe o histórico de alarme da máquina. Chega lá e começa a investigar do zero. O cliente fica puto porque tem que explicar tudo de novo. O NPS da gente caiu de oitenta e dois pra sessenta e oito em dezoito meses. Caiu catorze pontos. E a gente sabe que metade disso é por causa de suporte de campo sem contexto. Metade. A outra metade é... ah, isso é mais complicado, depois eu explico.

**Marcos Tedesco** *[11:08]*: Então cara, esses são os cinco. Manutenção preditiva, comissionamento, drift de código, cotação lenta, suporte sem contexto. Mas o que eu quero atacar primeiro, e isso eu já decidi, é a preditiva. Manutenção preditiva com IA. Esse é o que tá me sangrando dinheiro todo mês. Vinte e sete mil reais por mês. É isso que eu quero pagar a HomoDeus pra resolver.

**João Paulo** *[11:32]*: Marcos, posso te fazer uma pergunta meio ortogonal? Quem decide nessas reuniões internas o que vocês vão atacar primeiro? É você sozinho, é o Roberto também?

**Marcos Tedesco** *[11:43]*: É... é compartilhado. O Roberto é meu sócio, ele toca a parte financeira e o conselho. A gente queria... bom, na verdade, é mais que o conselho... aliás, é o sócio Roberto que tá pedindo... então... é, o Roberto tá pedindo pra cortar custo. Ele olhou os números do trimestre passado e viu os vinte e sete mil de visita perdida, e disse, Marcos, isso aqui é absurdo, resolve. E aí eu falei beleza, vou contratar consultoria. E aí eu tô aqui falando com você.

**Marcos Tedesco** *[12:18]*: Mas a Cláudia, ela acha que o problema maior não é a preditiva. Ela acha que é o comissionamento. Ela vive me enchendo o saco com isso. Mas ela é eng de aplicação, ela vê o problema dela. Eu vejo o problema da empresa toda. E o problema da empresa toda é os vinte e sete mil por mês que tão saindo pelo ralo. Tá ligado?

**João Paulo** *[12:38]*: Tô. Quanto tempo o engenheiro de aplicação gasta hoje, em média, por máquina comissionada? E quanto fica parado por máquina no backlog?

**Marcos Tedesco** *[12:48]*: Três a quatro dias por máquina, eu já falei. E parado... olha, cada dia que a máquina fica parada no cliente, sem comissionar, é cliente bravo. Tem cliente que cobra multa contratual de uns oitocentos reais por dia. Mas o pior não é a multa. O pior é a reputação. Se a gente combina entregar a máquina dia primeiro do mês e só consegue ligar dia quinze, o cliente nunca mais te chama. E hoje, com vinte e duas máquinas esperando, mais ou menos a metade tá com atraso. Metade.

**João Paulo** *[13:21]*: Onze máquinas atrasadas?

**Marcos Tedesco** *[13:24]*: Onze, doze, por aí. Mas isso é o problema da Cláudia. Foco. Preditiva. Preditiva é o que eu quero. Manutenção preditiva com IA, em cima dos doze mil e quinhentas leituras por dia, parando os falsos alarmes, reduzindo o vinte e sete mil de visita perdida. Esse é o projeto.

**João Paulo** *[13:44]*: Entendido. E o time, esses vinte e dois técnicos, eles têm autonomia pra decidir se vão ou não pro cliente quando o alerta sobe?

**Marcos Tedesco** *[13:52]*: Não. O alerta sobe, vai pro Carlos, que é o coordenador de campo, e o Carlos despacha. O Carlos olha o alerta, olha quem tá perto, manda alguém. Mas o Carlos confia no alerta. Se o sistema disse que é grave, ele despacha. E aí às vezes não é nada.

**João Paulo** *[14:11]*: O Carlos tem alguma ferramenta pra ver o histórico do sensor antes de despachar?

**Marcos Tedesco** *[14:15]*: Tem o supervisório, mas o supervisório só mostra o instantâneo. Pra ver histórico ele tem que pedir pro time de TI puxar do banco, e isso demora horas. Então ele não pede. Despacha e pronto.

**Marcos Tedesco** *[14:30]*: Ah, e o vendedor, fala dele um pouquinho. O João, vendedor sênior, o cara é uma máquina, fecha contrato dormindo. Mas ele odeia tecnologia. Ele anota tudo no caderno, manda áudio de WhatsApp, não usa CRM. Eu já tentei colocar Salesforce, ele boicotou. Aí o que acontece, quando o áudio do João chega na Cláudia, a Cláudia tem que decifrar. Áudio de oito minutos, dez minutos, o cara descrevendo a fábrica do cliente, e ela tem que tirar dali o que precisa. É um inferno.

**João Paulo** *[15:08]*: Vocês têm transcrição automática desses áudios? Whisper, alguma coisa?

**Marcos Tedesco** *[15:13]*: Não. Não temos. A Cláudia ouve. Cláudia coitada, ouve oito áudios de dez minutos por semana. Oitenta minutos só de ouvir áudio. E ela ainda tem que comissionar máquina.

**Marcos Tedesco** *[15:28]*: Mas voltando. Preditiva. Olha, deixa eu te falar mais sobre os dados. A gente tem um banco PostgreSQL onde a gente armazena todas as leituras de sensor. É um banco grande. A gente tem... peraí, eu tenho que olhar a planilha que a Cláudia mandou pro Sérgio, ela tá aqui... ela falou que a gente tem uns duzentos e oitenta gigas de dados históricos. Dois anos e meio de leitura. Sensor digital, sensor analógico, válvula, bomba, motor, contador de OEE, alarme antigo, tudo lá. Isso aí é mina de ouro pra IA, né? Dois anos e meio de histórico.

**João Paulo** *[16:09]*: E os alertas que dispararam, ficam rotulados? Tipo, esse alerta foi falso, esse foi verdadeiro?

**Marcos Tedesco** *[16:15]*: Ficam... ah, ficam mais ou menos. Quando o técnico volta da visita, ele preenche um relatório no sistema interno da gente, e tem um checkbox de "falso alarme sim ou não." Mas o técnico nem sempre preenche. Eu diria que metade preenche. Talvez menos.

**João Paulo** *[16:34]*: Então pra treinar um modelo a gente tem uns dois anos e meio de leitura, com cinquenta por cento de label nos alertas históricos.

**Marcos Tedesco** *[16:42]*: Mais ou menos isso. Mas dá pra trabalhar, né? Dá pra trabalhar. A IA não precisa de rótulo perfeito, ela aprende sozinha, ouvi dizer.

**Marcos Tedesco** *[17:00]*: E aí, falando de time, a gente queria fechar o ano que vem com vinte e cinco técnicos em campo. Vinte e cinco. Crescer um pouquinho. Mas hoje tá meio mais magro do que eu gostaria, uns dezoito, eu acho, faltam quatro que pediram demissão nos últimos seis meses, demanda fora foi pra Weg, foi pra Atos, demanda dentro, salário tá apertado. Eu tô tentando recompor, mas tá difícil. Técnico de CLP bom é raro. Cara que sabe Lua, Structured Text, sabe ler diagrama elétrico, sabe sujar a mão no chão de fábrica, é raro. E cobram bem.

**João Paulo** *[17:42]*: Marcos, no início você falou em vinte e dois técnicos. Agora você falou em dezoito. Qual é o número que eu posso usar?

**Marcos Tedesco** *[17:50]*: Ah, é... olha... é dezoito hoje, dezoito ativos. Os vinte e dois é com os que tão saindo no aviso prévio ou os que eu queria ter. Foi mal, eu misturo isso na cabeça. Dezoito. Coloca dezoito.

**João Paulo** *[18:06]*: Beleza. E o ROI estimado da preditiva, vocês já fizeram conta?

**Marcos Tedesco** *[18:12]*: Conta a gente fez. Se a gente cortar setenta por cento dos falsos alarmes, a gente economiza uns... vinte mil por mês, vinte e dois mil por mês. Cem por cento, vinte e sete mil por mês. Em doze meses isso é trezentos mil. Então qualquer coisa que custe menos que trezentos mil pra construir já se paga em um ano. E a HomoDeus, eu imagino, vai cobrar quanto pra construir isso? Cem? Cento e cinquenta?

**João Paulo** *[18:42]*: A gente discute valor depois de entender escopo. Posso te perguntar uma coisa? Vocês já tentaram simplesmente ajustar os thresholds dos alertas atuais? Antes de partir pra IA?

**Marcos Tedesco** *[18:54]*: Ah, isso a Cláudia fica em cima. Ela já mexeu nuns. Mas é trabalho braçal, máquina a máquina, e ela não tem tempo. Tempo da Cláudia tá sendo gasto em comissionamento. Tá vendo? Tudo conecta. Por isso que eu quero IA, pra resolver o problema sem ter que botar humano pra mexer em threshold.

**João Paulo** *[19:14]*: E se a IA reduzir os falsos alarmes mas a Cláudia continuar com vinte e duas máquinas no backlog, a empresa muda?

**Marcos Tedesco** *[19:21]*: A empresa... cara, a empresa muda no caixa, com certeza. Vinte e sete mil por mês a mais no caixa é... peraí... vinte e sete vezes doze é trezentos e vinte e quatro, mas com encargo, manutenção do carro, hora extra, é fácil quase trezentos e cinquenta. Mas você tá certo, o backlog continua. O backlog é outro projeto, eu sei. Mas eu quero começar pela preditiva.

**Marcos Tedesco** *[19:48]*: E olha, eu sei que a IA tá na moda, eu sei. Todo mundo tá vendendo IA. Mas eu acho que faz sentido aqui. A gente tem dado, tem volume, tem caso de uso claro. Eu não tô comprando ChatGPT pra fazer marketing, eu tô comprando inteligência artificial pra ler vinte e oito mil sensores e me dizer quais alarmes são reais.

**João Paulo** *[20:09]*: Vinte e oito mil sensores no total?

**Marcos Tedesco** *[20:12]*: Mais ou menos. Quarenta clientes, cada um com sete, oito máquinas em média, cada máquina com cem sensores. Faz a conta. Trinta mil sensores. Talvez vinte e oito. Não sei exato, a Cláudia sabe.

**João Paulo** *[20:30]*: E vocês têm OPC UA em quantas máquinas?

**Marcos Tedesco** *[20:33]*: OPC UA tá nas máquinas novas, dos últimos quatro anos. O resto é Modbus TCP, e umas máquinas mais antigas é Modbus RTU, serial. A gente tem um broker que normaliza tudo pra um formato interno. Eu acho que é MQTT na ponta. O Sérgio sabe. O Sérgio do TPM, não o Sérgio que saiu.

**João Paulo** *[20:55]*: Beleza. E a planilha de prejuízo dos vinte e sete mil mensais, vocês têm ela? Posso pedir pra Cláudia?

**Marcos Tedesco** *[21:02]*: Pode pedir. Ela tem. Ela mandou pro Sérgio mês passado. Tem lá quebrado por cliente, por mês, por técnico. Ela é organizada nisso, a Cláudia.

**Marcos Tedesco** *[21:14]*: Ah, deixa eu te falar mais uma coisa. A gente tem uma reunião de conselho daqui três semanas. O Roberto, meu sócio, vai querer ouvir como a gente vai resolver os vinte e sete mil. Se eu chegar lá com um projeto fechado, escopo, prazo, preço, eu compro paz por seis meses. Se eu chegar lá sem nada, ele vai me pressionar a demitir técnico, e eu não quero demitir. Eu já tô com a equipe magra. Demitir técnico bom agora é tiro no pé.

**João Paulo** *[21:48]*: Entendi. Marcos, eu vou falar com a Cláudia depois pra cruzar números. Mas só pra eu ter clareza, do seu lado, o que tem que estar no escopo do primeiro projeto?

**Marcos Tedesco** *[22:00]*: Manutenção preditiva. Pega o histórico de dois anos e meio, treina uma IA, plugga ela no fluxo de alerta, faz com que os alertas que sobem pro Carlos sejam alertas reais. Setenta por cento de redução dos falsos. Esse é o sucesso. Em três meses. Tá bom pra você?

**João Paulo** *[22:20]*: Em três meses, com qualidade de dado de cinquenta por cento de label, é ambicioso. Mas a gente avalia. E os outros quatro problemas, fica pra fase dois?

**Marcos Tedesco** *[22:30]*: Fica. Fase dois, fase três. Mas antes me prova que vocês resolvem o primeiro. Eu já fui mordido por consultoria duas vezes, cara. Em dois mil e vinte um eu contratei uma galera de São Paulo pra fazer dashboard de OEE pra mim, gastei oitenta mil, o cara entregou um Power BI que ninguém usa até hoje. Em dois mil e vinte três eu contratei outro, indiano, fazer chatbot pra atendimento de campo, gastei sessenta mil, nunca funcionou. Eu não tô a fim de pagar adiantado pra ninguém. Pague conforme entrega.

**João Paulo** *[23:09]*: Justo. A gente discute modelo comercial depois. Marcos, quanto tempo o Carlos, o coordenador de campo, leva pra triar um alerta hoje? Tipo, do alerta subir até ele despachar.

**Marcos Tedesco** *[23:21]*: Ah, isso é rápido. Cinco minutos, dez minutos. Ele olha, despacha. Não tem ciência aí. Por isso que sai tanto falso. Ele confia no sistema.

**João Paulo** *[23:33]*: E se o Carlos tivesse uma ferramenta que mostrasse, junto com o alerta, o histórico do mesmo sensor nas últimas trinta e seis horas, e uma probabilidade de falso alarme? Ele usaria?

**Marcos Tedesco** *[23:45]*: Usaria. Usaria. O Carlos é um cara aberto. Ele só não tem ferramenta. Se você der ferramenta boa, ele usa. Foi até ideia dele uma vez, sabe? Ele falou comigo faz uns oito meses, "Marcos, dá pra colocar um gráfico do histórico aqui no alerta?" Eu falei dá, e nunca fiz. Foi vergonhoso.

**João Paulo** *[24:08]*: Marcos, e o problema do drift de código, dos hotfix que não voltam pro Git. Quão crítico isso é em relação ao prejuízo dos vinte e sete mil?

**Marcos Tedesco** *[24:18]*: Cara, o drift é... o drift é caro pontualmente, quando dá merda. A fábrica de cosméticos de Diadema, foi uns oitenta mil de prejuízo direto, mais o desconto comercial que eu tive que dar pra segurar o contrato, foi uns cento e quarenta mil total. Mas não é mensal. É evento. Acontece duas, três vezes por ano. Os vinte e sete mil é todo mês, todo mês, todo mês. Sangra mais.

**João Paulo** *[24:48]*: Faz sentido.

**Marcos Tedesco** *[24:51]*: Mas o drift assusta porque um dia vai acontecer numa máquina crítica e a gente vai perder um cliente grande. Tô pensando em colocar uma regra obrigando o técnico a fazer git push antes de fechar o chamado. Mas o técnico não vai fazer. Ele vai esquecer. E aí?

**João Paulo** *[25:08]*: Dá pra fazer automaticamente. O CLP pode mandar o diff do código rodando pra um endpoint, sempre que houver alteração local. Sem depender do técnico.

**Marcos Tedesco** *[25:18]*: Pode? Você consegue fazer isso?

**João Paulo** *[25:20]*: Consigo, é coisa relativamente simples se o CLP tem rede. Mas não é o que você quer atacar primeiro, é?

**Marcos Tedesco** *[25:27]*: Não. Preditiva primeiro. Mas anota isso aí. Anota tudo. Eu quero que vocês me façam um mapa dos cinco problemas, com proposta pra cada um, e a gente discute. Mas o primeiro fica preditiva. Tô fixo nisso.

**João Paulo** *[25:43]*: Beleza. Eu vou falar com a Cláudia, vou olhar a planilha dela, e te volto com um plano em uma semana.

**Marcos Tedesco** *[25:50]*: Perfeito. Cláudia eu já avisei que você liga. Ela é direta, viu. Cuidado. Ela tem o jeito dela. Mas ela é a melhor que eu tenho. Se ela falar que algo não dá pra fazer, ouve. Se ela falar que algo é fácil, desconfia, porque ela acha tudo fácil.

**João Paulo** *[26:10]*: Anotado. Marcos, mais uma. Os clientes, eles aceitariam que vocês instalassem um modelo de IA rodando em cima dos dados deles?

**Marcos Tedesco** *[26:20]*: Aceitam. A maioria. Tem cliente, tipo o pessoal de farma e o pessoal de sódio, que é rígido com dado saindo. Esses a gente teria que rodar on-premise, no servidor deles. Mas os outros aceitam exportar pro nosso banco. A gente tem cláusula de uso de dado nos contratos. Não no contrato antigo, no contrato dos últimos três anos. Tem uns quinze clientes que tem cláusula. O resto a gente teria que renegociar.

**João Paulo** *[26:48]*: Vinte e cinco clientes precisariam de renegociação?

**Marcos Tedesco** *[26:51]*: Mais ou menos. Mas é coisa que o comercial faz em paralelo. Não trava o projeto.

**João Paulo** *[27:00]*: Pode travar. Se a gente precisar de dado de cliente X pra treinar o modelo e não tem cláusula contratual, dá problema jurídico.

**Marcos Tedesco** *[27:08]*: Hmm. É verdade. Anota isso aí. Vou pedir pro Daniela do jurídico mapear quem tem cláusula e quem não tem. Eu não tinha pensado nisso.

**Marcos Tedesco** *[27:21]*: Cara, é por isso que eu tô contratando vocês. Pra eu não esquecer essas coisas. Eu sou tocador de empresa, eu não sou tecnólogo. Eu fundei isso aqui há vinte e dois anos com um osciloscópio e uma vontade de fazer dar certo. Hoje eu tenho trezentos e vinte funcionários e um problema diferente a cada quinze minutos.

**João Paulo** *[27:42]*: Eu entendo. Marcos, posso te fazer uma pergunta um pouco fora?

**Marcos Tedesco** *[27:47]*: Pode.

**João Paulo** *[27:49]*: Se você pudesse acordar amanhã e ter UM dos cinco problemas resolvido, mas só um, qual seria?

**Marcos Tedesco** *[27:57]*: Preditiva. Já falei.

**João Paulo** *[27:59]*: E se eu te falar que a Cláudia, na sua frente, falar pra você que o problema é o comissionamento, você muda?

**Marcos Tedesco** *[28:08]*: Cláudia... ela já me falou. Várias vezes. Não, eu não mudo. Porque o vinte e sete mil é o que o Roberto vai me cobrar no conselho. Roberto não tá nem aí pro backlog de máquina, ele tá olhando o caixa. Eu tô tocando uma empresa, não tô tocando uma engenharia. Você vai entender quando você for sócio.

**João Paulo** *[28:32]*: Entendi. Marcos, uma última. O comissionamento, hoje, custa quanto pra empresa, em folha de eng de aplicação parada nisso?

**Marcos Tedesco** *[28:42]*: Eng de aplicação custa uns... oito, nove mil reais com encargo, por mês. Tenho quatro. São trinta e seis mil de folha por mês com eles. Se eles tão cem por cento alocados em comissionamento, então o custo de comissionamento é trinta e seis mil por mês. Mas é folha que já tá lá, eu já pago. Não é custo marginal.

**João Paulo** *[29:05]*: Trinta e seis mil por mês de custo opportunity, mais o cliente bravo pelo atraso, mais a multa contratual, mais as quatro máquinas do Boituva que talvez gerem cancelamento. Comissionamento parece maior que preditiva.

**Marcos Tedesco** *[29:20]*: Hmm. Eu sei o que você tá fazendo. Você tá tentando me empurrar pro outro lado. Olha, tá registrado. Manda a proposta cobrindo os dois. Mas o um primeiro tem que ser preditiva, por compromisso meu com o conselho. Mais alguma coisa?

**João Paulo** *[29:38]*: Não, foi bom. Vou falar com a Cláudia amanhã, ela já tá agendada. Marcos, obrigado.

**Marcos Tedesco** *[29:45]*: Imagina. E olha, qualquer coisa, me liga direto. Não passa por secretária, não passa por ninguém, liga direto no meu celular. E não confia em tudo que a Cláudia falar. Ela é jaded. Doze anos de chão de fábrica deixa qualquer um jaded.

**João Paulo** *[30:02]*: Tá bom, Marcos.

**Marcos Tedesco** *[30:04]*: E manda a proposta até quarta que vem, pra eu ter tempo de massagear antes do conselho.

**João Paulo** *[30:10]*: Quarta que vem. Anotado.

**Marcos Tedesco** *[30:13]*: Tchau, valeu, beijo no coração.

**João Paulo** *[30:16]*: Valeu, Marcos, até.

---
