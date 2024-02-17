# Validações para os parâmetros utilizados no graylog

def valida_envs(envs):

    envs_de_para = {
        'glf_node': 'GRAYLOG_NODE',
        'glf_service': 'GRAYLOG_SERVICE',
        'glf_company': 'GRAYLOG_COMPANY',
        'glf_application': 'GRAYLOG_APPLICATION',
        'glf_settings': 'GRAYLOG_SETTINGS',
        'glf_image': 'GRAYLOG_IMAGE',
        'graylog_host': 'GRAYLOG_HOST',
        'graylog_port': 'GRAYLOG_PORT',
    }

    for chave, env_var_name in envs_de_para.items():
        valor = envs.get(env_var_name, '')
        if valor == '':
            raise ValueError(f'A env {env_var_name} não pode estar vazia! Consulte o Readme do projeto pypck-logs para orientações de preenchimento!')

        if chave == 'glf_company':
            if valor.lower() not in ('pompeia', 'gang', 'glf'):
                raise ValueError(f'A env {env_var_name} deve ser pompeia, gang ou glf. Valor atual: {valor}')

        elif chave == 'glf_settings':
            if valor.lower() not in ('production', 'development', 'sandbox'):
                raise ValueError(f'A env {env_var_name} deve ser production, sandbox ou development. Valor atual: {valor}')
