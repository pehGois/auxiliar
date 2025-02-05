from botocore.exceptions import ClientError
import boto3
import json
import uuid

class BedrockWrapper:
  
    def __init__(self, region):
        """ Initiates the bedrock client and runtime"""
        try:
            self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
            self.bedrock_agent = boto3.client('bedrock-agent', region_name=region)
            self.bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=region)
            self.agent_id = None
            self.agent_alias_id = None
        except ClientError as e:
            print(f"Error initializing Bedrock clients: {str(e)}")
            raise

    def set_agent_id(self, agent_id):
        self.agent_id = agent_id

    def set_agent_alias_id(self, agent_alias_id):
        self.agent_alias_id = agent_alias_id

    # def delete_agent_memory(self,session_id):
    #     try:
    #         self.bedrock_agent_runtime.delete_agent_memory(
    #             agentAliasId=self.agent_alias_id,
    #             agentId=self.agent_id,
    #             sessionId=session_id
    #         )
    #     except Exception as e:
    #         print(f'Um erro ocorreu enquanto a sessão era excluída\n {e}')

    def invoke_model(self, end_session=False, question='Tchau', session_id=None):
        """calls the model and get response string"""
        try:
            if not self.agent_id or not self.agent_alias_id:
                raise ValueError("Agent ID and Agent Alias ID must be set before invoking the model")
            
            if not session_id:
                session_id = str(uuid.uuid4())
                
            response_data = self.bedrock_agent_runtime.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                sessionId=session_id,  
                inputText=question,    
                endSession=end_session,  
                enableTrace=True
            )
            
            response = self._read_bedrock_response(response_data)

            return response, session_id
        
        except ClientError as e:
            print(f"Error invoking agent: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise
    
    def _list_agent_aliases(self):
        response = self.bedrock_agent.list_agent_aliases(
            agentId = self.agent_id
        )
        return response
    
    def _read_bedrock_response(self, response):
        completion = response['completion']
        trace = response.get('trace', {})
        full_response = ""
        
        for event in completion:
            if "chunk" in event:
                try:
                    chunk_data = json.loads(event['chunk']['bytes'].decode())
                    if "content" in chunk_data:
                        full_response += chunk_data["content"]
                except json.JSONDecodeError:
                    chunk_data = event['chunk']['bytes'].decode('utf-8')
                    full_response += chunk_data
        
        return {'response':full_response, 'trace':trace}
    
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    bedrock = BedrockWrapper(region=os.environ.get('REGION'))
    agent_id = os.environ.get('AGENT_ID')
    bedrock.set_agent_id(agent_id=agent_id)
    response = bedrock._list_agent_aliases()
    print(
        'Add it to your .env\nAgent Alias: ',
        response.get('agentAliasSummaries', [])[0].get('agentAliasId')
    )
