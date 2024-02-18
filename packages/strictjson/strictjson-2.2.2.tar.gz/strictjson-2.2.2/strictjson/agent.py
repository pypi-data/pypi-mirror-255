import heapq
import openai
from openai import OpenAI
import numpy as np
from .base import *

### Helper Functions
def top_k_index(lst, k):
    ''' Given a list lst, find the top k indices corresponding to the top k values '''
    indexed_lst = list(enumerate(lst))
    top_k_values_with_indices = heapq.nlargest(k, indexed_lst, key=lambda x: x[1])
    top_k_indices = [index for index, _ in top_k_values_with_indices]
    return top_k_indices

### Main Classes
class Ranker:
    ''' This defines the ranker which outputs a similarity score given a query and a key'''
    def __init__(self, host = "openai", model = "text-embedding-3-small", database = None):
        '''
        host: Str. The host name for the similarity score service
        model: Str. The name of the model for the host
        database: None / Dict (Key is str for query/key, Value is embedding in List[float])
        Takes in database (dict) of currently generated queries / keys and checks them
        so that you do not need to redo already obtained embeddings
        If you provide a database, the calculated embeddings will be added to this database'''
        self.host = host
        self.model = model
        self.database = database
            
    def __call__(self, query, key) -> float:
        ''' Takes in a query and a key and outputs a similarity score 
        Compulsory:
        query: Str. The query you want to evaluate
        key: Str. The key you want to evaluate'''
     
        database_provided = isinstance(self.database, dict)
        if self.host == "openai":
            client = OpenAI()
            if database_provided and query in self.database:
                query_embedding = self.database[query]
            else:
                query = query.replace("\n", " ")
                query_embedding = client.embeddings.create(input = [query], model=self.model).data[0].embedding
                if database_provided:
                    self.database[query] = query_embedding
                
            if database_provided and key in self.database:
                key_embedding = self.database[query]
            else:
                key = key.replace("\n", " ")
                key_embedding = client.embeddings.create(input = [query], model=self.model).data[0].embedding
                if database_provided:
                    self.database[key] = key_embedding
                
        return np.dot(query_embedding, key_embedding)
        
class Memory:
    ''' Retrieves top k information based on task 
    retriever takes in a query and a key and outputs a similarity score'''
    def __init__(self, memory: list, ranker = Ranker()):
        self.memory = memory
        self.ranker = ranker
    def extract(self, task, top_k = 3):
        ''' Performs retrieval of top_k similar memories '''
        memory_score = [self.ranker(memory_chunk, task) for memory_chunk in self.memory]
        top_k_indices = top_k_index(memory_score, top_k)
        return [self.memory[index] for index in top_k_indices]
    def extract_llm(self, task, top_k = 3):
        ''' Performs retrieval via LLMs '''
        res = strict_json(f'You are to output the top {top_k} most similar list items in Memory that meet this description: {task}\nMemory: {self.memory}', '', 
              output_format = {f"top_{top_k}_list": f"Array of top {top_k} most similar list items in Memory, type: list[str]"})
        return res[f'top_{top_k}_list']
    def clear_memory(self):
        ''' Clears all memory '''
        self.memory = []
    
class Agent:
    def __init__(self, agent_name: str = 'Helpful Assistant',
                 agent_description: str = 'You are a generalist agent meant to help solve problems', 
                 output_format: dict = {'output': 'sentence'}, 
                 llm = LLM(),
                 **kwargs):
        ''' 
        Creates an LLM-based agent using description and outputs JSON based on output_format. 
        
        Inputs:
        - agent_name: String. Name of agent, hinting at what the agent does
        - agent_description: String. Short description of what the agent does
        - output_format: String. Dictionary containing output variables names and description for each variable. There must be at least one output variable
           
        Inputs (optional):
        - kwargs: Dict. Additional arguments you would like to pass on to the strict_json function
        '''
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.output_format = output_format
        
    def __call__(self, history):
        ''' Describes the function, and inputs the relevant parameters as either unnamed variables (args) or named variables (kwargs)
        If there is any variable that needs to be strictly converted to a datatype, put mapping function in input_type or output_type
        
        Inputs:
        - *args: Tuple. Unnamed input variables of the function. Will be processed to var1, var2 and so on based on order in the tuple
        - **kwargs: Dict. Named input variables of the function. Can also be variables to pass into strict_json
        
        Output:
        - res: Dict. JSON containing the output variables'''
        
        # extract out only variables listed in variable_list
        function_kwargs = {my_key: kwargs[my_key] for my_key in kwargs if my_key in self.variable_names}
        # extract out only variables not listed in variable list
        strict_json_kwargs = {my_key: kwargs[my_key] for my_key in kwargs if my_key not in self.variable_names}
        
        # Do the auto-naming of variables as var1, var2, or as variable names defined in variable_names
        for num, arg in enumerate(args):
            if len(self.variable_names) > num:
                function_kwargs[self.variable_names[num]] = arg
            else:
                function_kwargs['var'+str(num+1)] = arg

        # do the function. 
        res = strict_json(system_prompt = self.fn_description,
                        user_prompt = function_kwargs,
                        output_format = self.output_format, 
                        **self.kwargs, **strict_json_kwargs)
                
        return res        
    
class TaskGroup:
    ''' This defines a task group that can be used to solve a task'''
    def __init__(self, task = 'Summarise the news', 
                 agent_pool = [Agent('Summariser', 'Summarises information'), 
                               Agent('Writer', 'Writes news articles'), 
                               Agent('General', 'A generalist agent')]):
        '''
        task: Str. The current task to solve
        agent_pool: List[Agents]: The available agents that we have'''

            
    def __call__(self):
        ''' Does the task '''
        pass