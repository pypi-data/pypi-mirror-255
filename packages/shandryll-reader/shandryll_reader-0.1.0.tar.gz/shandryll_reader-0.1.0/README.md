# TWBlog Reader

Esse é uma simples CLI (Command Line Interface) para ler os artigos do blog da [TreinaWeb](https://treinaweb.com.br/blog). Esse projeto foi desenvolvido para o artigo [Empacotando e publicando pacotes Python](https://treinaweb.com.br/blog/empacotando-e-publicando-pacotes-python/).

## Instalação

Para instalar o pacote, basta executar o comando abaixo:

```bash
pip install twblog-reader
```

## Uso

Após a instalação do pacote será disponibilizado o comando `twblog` na linha de comando. Para ver a lista do dezesseis últimos artigos, basta executar o comando abaixo:

```bash
twblog
```

A saída será parecida com a abaixo:

```txt
Últimos artigos do blog da TreinaWeb:

0 - Desenvolvedor mobile: por que investir nessa carreira?
1 - ASP.NET - Conhecendo a Minimal API
2 - Como se preparar para entrevistas técnicas
3 - Seletores avançados do CSS
4 - Criando o primeiro CRUD com NestJS
5 - Seletores Básicos do CSS
6 - Orientação a objetos em Dart
7 - 5 dicas para entrevistas na área de TI
8 - Novos recursos do ECMAScript 2022
9 - O que preciso conhecer antes de iniciar estudos em uma linguagem de programação?
10 - Criando o primeiro CRUD com FastAPI
11 - Unidades de medidas no CSS
12 - Orientação a objetos no C#
13 - Guia da linguagem C#
14 - Estruturas condicionais e de repetição no C#
15 - Conhecendo variáveis e constantes no C#
```

Para ver o conteúdo de um artigo específico, basta executar o comando abaixo:

```bash
twblog [id]
```

Onde `[id]` é o identificador do artigo que você deseja ver. Por exemplo, para ver o artigo de identificador 5, basta executar o comando abaixo:

```bash
twblog 5
```

## Licença

Esse projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
