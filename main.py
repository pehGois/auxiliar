from Bedrock import BedrockWrapper
from dotenv import load_dotenv
import pandas as pd
import json
import time
import os

load_dotenv()

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def to_csv(filepath):
    with open(filepath, "r", encoding="UTF-8") as file:
            data = json.load(file)

    rows = [{"questions": obj.get("question"), "answers": obj.get("answer")} for obj in data]
    pd.DataFrame(rows).to_csv(f"{filepath.split('.')[0]}.csv", index=False)

def format_response(response_data:dict, response_time, question) -> dict:
    try:        
        completion_text = response_data.get('response')
        trace = response_data.get('trace')

        # if raw_response.get('trace'):
        #     trace = {
        #         'trace_id': raw_response.get('trace', {}).get('traceId', ''),
        #         'agent_name': raw_response.get('trace', {}).get('agentName', ''),
        #         'knowledge_base_responses': raw_response.get('trace', {}).get('knowledgeBaseResponses', []),
        #         'lambda_functions': raw_response.get('trace', {}).get('lambdaFunctions', [])
        #     }

        return {
            'question': question,
            'answer': completion_text,
            'time': response_time,
            'trace': trace
        }
    
    except Exception as e:
        print(f"Error formatting response: {str(e)}")
        return {
            'question': '',
            'answer': 'Error formatting response',
            'time': response_time,
            'trace': None
        }

def save_response(response, file_path):
    data = []

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='UTF-8') as json_file_read:
            data = json.load(json_file_read)
        data.append(response)
    
    elif not isinstance(response, list):
        data.append(response)
    else:
        data = response

    with open(file_path, "w", encoding='UTF-8') as json_file_write:
        json.dump(data, json_file_write, indent=4, default=str, ensure_ascii=False)

def process_questions(questions, filepath, store_history = True):
    global session_id

    if isinstance(questions, str):
        questions = [questions]
    try: 
        for question in questions:
            if question.lower() == 'novo':
                # bedrock.delete_agent_memory(session_id=session_id)
                print('---\nNova Sessão\n')
                session_id = None

            elif question.lower() in ['finalizar', 'sair']:
                # bedrock.delete_agent_memory(session_id=session_id)
                print('Sessão Encerrada')
                return True
            
            else:
                if not store_history and session_id is not None:
                    # bedrock.delete_agent_memory(session_id=session_id)
                    session_id = None

                start_time = time.time()
                response, session_id = bedrock.invoke_model(
                    question=question,
                    end_session=False,
                    session_id=session_id
                )
                end_time = time.time() - start_time
            
                formatted_response = format_response(response, end_time, question)

                print('Resposta:', formatted_response['answer'])
                print('')
                save_response(formatted_response, filepath)
    except Exception as e:
        print(f"Um erro ocorreu na hora de responder a pergunta {question}\nErro: {e}\n Pulando para a Próxima Pergunta")
            
    return False

if __name__ == '__main__':
    mode = input(""" Digite o modo de interação: 
        \n[0] Rodar as perguntas descritas no código
        \n[1] Chat Interativo\n\n""").strip()
    
    filepath = 'data.json'
    region = os.environ.get('REGION')
    bedrock = BedrockWrapper(region)

    bedrock.set_agent_id(agent_id=os.environ.get('AGENT_ID'))
    bedrock.set_agent_alias_id(agent_alias_id=os.environ.get('AGENT_ALIAS_ID'))
    session_id = None
    if mode == '1':
        clear_terminal()

        print("Digite 'Novo' para Reiniciar a Sessão")
        print("Digite 'Sair' para Finalizar a Sessão")
        stop = False
        while not stop:
            question = input('Digite a sua pergunta: ').strip()
            stop = process_questions(question, filepath)
    else:
        clear_terminal()
        questions = [
            "Operacional - Qual é o ticket médio por cliente no mês atual?",
            "Operacional - Quais são os produtos mais vendidos em volume no último mês?",
            "Operacional - Quantas notas fiscais foram emitidas por dia na última semana?",
            "Operacional - Quais são as condições de pagamento mais utilizadas pelos clientes?",
            "Operacional - Qual é a distribuição de pedidos por tipo de pedido no mês atual?",
            "Gerencal - Qual é a evolução mensal das vendas por regional nos últimos 6 meses?",
            "Gerencal - Qual é a participação percentual de cada bandeira do cliente no faturamento total?",
            "Gerencal - Como está a distribuição de vendas por estado e sua comparação com o mesmo período do ano anterior?",
            "Gerencal - Qual é a margem de contribuição por grupo de cliente?",
            "Gerencal - Qual é o tempo médio entre pedido e faturamento por regional?",
            "Gerencal - Como está a performance de vendas por key brand comparada com as metas?",
            "Gerencal - Qual é a análise de concentração de vendas por cliente (curva ABC)?",
            "Gerencal - Como está a distribuição de vendas por condição de pagamento e seu impacto no fluxo de caixa?",
            "Gerencal - Qual é a taxa de conversão de pedidos por origem de transação?",
            "Gerencal - Como está a evolução do ticket médio por sub-canal de vendas?",
            "Estratégico - Qual é o potencial de crescimento por região baseado na análise histórica de vendas e market share?",
            "Estratégico - Como a alteração no mix de produtos tem impactado a rentabilidade por segmento de cliente?",
            "Estratégico - Qual é o impacto das políticas comerciais na performance de vendas por grupo de cliente?",
            "Estratégico - Como está a penetração de mercado por região e quais são as oportunidades de expansão?",
            "Estratégico - Qual é a correlação entre condições comerciais oferecidas e o crescimento das vendas por cliente?",
            "Estratégico - Como as mudanças tributárias (ICMS, IPI, ST) têm afetado a competitividade por região?",
            "Estratégico - Qual é o lifetime value dos clientes por segmento e sua evolução nos últimos anos?",
            "Estratégico - Como está a elasticidade-preço por categoria de produto e região?",
            "Estratégico - Qual é o impacto das estratégias de pricing na participação de mercado por região?",
            "Estratégico - Como está a eficiência operacional de vendas considerando custos tributários e logísticos por região?"
        ] # ADD your questions here
        process_questions(questions, filepath, store_history=False)
    
    to_csv(filepath)