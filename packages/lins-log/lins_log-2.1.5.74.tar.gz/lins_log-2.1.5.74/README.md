# Pacote Logs #

Pacote para Utilizar o Graylog em serviços e apis.

## Variaveis de Ambiente Necessárias

> ### GRAYLOG_EXTRA_RECORDS
>> Parametro necessário para adicionar novos campos no log do graylog.
Exemplo:
    'settings=NODE:teste22,application=SERVICE:'
Definição:
    settings -> representa nome do campo
    NODE     -> representa variavel de ambiente que sera traduzida
    teste22  -> representa o valor padrão caso não haja a variavel de ambiente

> ### GLF_NODE
>> Parametro necessário para saber onde esta alocado o serviço exemplo: GLF_NODE={{.Node.Hostname}}

> ### GLF_SERVICE
>> Parametro necessário para saber qual servico exemplo: GLF_SERVICE={{.Service.Name}}

> ### GLF_COMPANY
>> Parametro necessário para saber qual empresa. As possíveis opções são: pompeia, gang ou glf

> ### GLF_APPLICATION
>> Parametro para ser preenchido sempre com o nome do repositório para facilitar a identificação e padronização. Ex: servico-atualizacao-graylog

> ### GLF_SETTINGS
>> Parametro para ser preenchido production, sandbox ou development.

> ### GLF_IMAGE
>> Parametro para ser preenchido a image {{.Service.Image}}

> ### GRAYLOG_HOST
>> Parametro necessário para conectar no GrayLog. Dar preferência ao domínio, não ao endereço de IP.

> ### GRAYLOG_PORT
>> Parametro necessário para conectar no GrayLog

## Como Utilizar Pacote em servico

> ### importa pacote from lins_log import lins_log
>> Nas chamadas utilizar logging do python pois pacote importa as configurações do logging

## Como Utilizar Pacote em Api

> ### importa pacote from lins_log import lins_log dentro dos settings
>> nos settings informar LOGGING = None e LOGGING_CONFIG = None