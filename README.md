# Auxiliar

Script para automatizar os testes da Ju.

Instalar dependências:
```shell
    pip install -r requirements.txt
```

Create your ENV file with the following structure:
```
    REGION = us-west-2
    AGENT_ID = 
    AGENT_ALIAS_ID = 
```

**AGENT ID :** CAN BE OBTAINED IN THE AWS CONSOLE
**AGENT_ALIAS_ID :** RUN THE BEDROCK.PY AND ADD THE RESULT INTO YOUR .ENV

- ADD YOUR QUESTIONS TO THE QUESTION VAR 
- THEN RUN THE MAIN.PY