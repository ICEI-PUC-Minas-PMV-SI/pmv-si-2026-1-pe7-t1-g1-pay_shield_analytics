# Implantação da solução

A solução desenvolvida foi implantada em ambiente de computação em nuvem, permitindo a realização de inferências em tempo real a partir de dados fornecidos pelo usuário. O sistema foi disponibilizado por meio da aplicação web PayShield, acessível via navegador, eliminando a necessidade de instalação local.

A arquitetura da solução é composta por uma interface web responsável pela coleta dos dados da transação e por um backend que realiza o carregamento do modelo previamente treinado. Durante a execução, os dados informados pelo usuário são submetidos ao mesmo fluxo de pré-processamento utilizado na etapa de treinamento e, em seguida, enviados ao modelo de Machine Learning para geração da predição.

## Infraestrutura em nuvem

O deploy da aplicação foi realizado em um servidor virtual localizado na Hetzner, provedor de infraestrutura em nuvem escolhido para hospedar a solução. No servidor, a aplicação executa de forma conteinerizada por meio do Docker, garantindo isolamento, reprodutibilidade e facilidade de manutenção.

Para tornar o acesso ao sistema mais amigável, foi configurado um registro DNS na Cloudflare. O subdomínio **payshield.pnuneslabs.com.br** foi apontado para o endereço IP público do servidor Hetzner, permitindo que os usuários acessem a aplicação diretamente pelo navegador, sem a necessidade de informar o endereço IP do servidor.

## Pipeline de build e deployment

Todo o processo de build e deploy é executado de forma automatizada por meio de uma pipeline de integração e entrega contínua (CI/CD), localizada no diretório `.github/workflows/` do repositório. A pipeline é composta pelos seguintes arquivos:

- `ci.yml`: orquestra o fluxo completo, permitindo executar o build, o deploy ou ambos de forma combinada, com base em uma versão de release informada manualmente.
- `build.yml`: responsável pelo build da imagem Docker e pela publicação no Docker Hub. Ao final do processo, também cria uma release no GitHub com as notas geradas automaticamente.
- `deploy.yml`: executa o deployment no servidor Hetzner por meio de conexão SSH. O workflow atualiza a versão da aplicação no arquivo de ambiente, realiza o pull da nova imagem publicada no Docker Hub e reinicia os containers com o Docker Compose.

Dessa forma, a publicação de uma nova versão da aplicação segue um fluxo padronizado: build da imagem, publicação no registro de containers, criação de release no GitHub e deploy automatizado no servidor de produção.

## Inferência em tempo real

A aplicação em produção está preparada para realizar inferência dinâmica, utilizando os modelos previamente treinados, com interface para entrada de novos dados fornecidos pelo usuário, de modo que as **predições sejam realizadas em tempo de execução**, sem reprocessamento ou atualização do treinamento.


# Apresentação da solução

Nesta seção, deve ser produzido um vídeo de até 15 minutos apresentando o escopo geral do projeto, um resumo das etapas desenvolvidas, a demonstração da solução publicada e as conclusões finais, destacando aprendizados, impacto e possibilidades de melhorias.

# É IMPRESCINDÍVEL: 
* Atualizar o arquivo **CITATION.cff** disponível no diretório raiz do repositório
* Atualizar as **Instruções de utilização** no arquivo read.me



