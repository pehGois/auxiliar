# Auxiliar

Script para automatizar os testes da Ju.

Create your virtual enviroment
```shell
    python -m venv venv
    venv/Scripts/activate
```

Install dependances:
```shell
    pip install -r requirements.txt
```

Create your ENV file with the following structure:
```
    REGION = us-west-2
    AGENT_ID = 
    AGENT_ALIAS_ID = 
    AWS_SECRET_ACCESS_KEY = 
    AWS_ACCES_KEY_ID = 
```

**AGENT ID :** Can be obtained in the AWS console

**AGENT ALIAS ID :** Run the Bedrock.py and add the result to your .env

If you'll not use the interative mode, **don't forget to add your questions to the question list var**
