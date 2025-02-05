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
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="UTF-8") as file:
                data = json.load(file)

        rows = [{
                "questions": obj.get("question"),
                "answers": obj.get("answer"),
                "time": obj.get("time")
            }
            for obj in data
        ]
        
        pd.DataFrame(rows).to_csv(f"{filepath.split('.')[0]}.csv", index=False)

def format_response(response_data:dict, response_time, question) -> dict:
    try:        
        completion_text = response_data.get('response')
        trace = response_data.get('trace')

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

    for question in questions:
        try: 
            if question.lower() == 'novo':
                bedrock.delete_agent_memory(session_id=session_id)
                print('---\nNova Sessão\n')
                session_id = None

            elif question.lower() in ['finalizar', 'sair']:
                bedrock.delete_agent_memory(session_id=session_id)
                print('Sessão Encerrada')
                return True
            
            else:
                if not store_history and session_id is not None:
                    bedrock.delete_agent_memory(session_id=session_id)
                    session_id = None

                start_time = time.time()
                response, session_id = bedrock.invoke_model(
                    question=question,
                    end_session=False,
                    session_id=session_id
                )
                end_time = str(round(time.time() - start_time,2))
            
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

        ] # ADD your questions here
        process_questions(questions, filepath, store_history=False)
    
    to_csv(filepath)