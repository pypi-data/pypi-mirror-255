

from langchain.prompts import PromptTemplate
from langchain.chains.base import Chain
from langchain.chains import LLMChain
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain_experimental.sql.base import SQLDatabase
from pydantic import Field
from typing import Dict,Any,Optional, List, Literal
import pathlib
import datetime
from loguru import logger

SYSTEM = """You are a SQLite expert. Given an input question, first create a syntactically correct SQLite query to run, then look at the results of the query and return the answer to the input question.
Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per SQLite. You can order the results to return the most informative data in the database.
Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
Pay attention to use date('now') function to get the current date, if the question involves "today"."""

PROMPT = """
    You are a SQLite expert. Given an input question, first create a syntactically correct SQLite query to run, then look at the results of the query and return the answer to the input question.
Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per SQLite. You can order the results to return the most informative data in the database.
Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
Pay attention to use date('now') function to get the current date, if the question involves "today".today is {today}


已知有如下SQLITE表, 具体的表定义如下:
{table_info}

请根据我的要求帮我生成一个SQL语句，回复以'SQLQuery:'开头不要说多余的话,答案用中文回答（标题、正文、关键词中出现均算涉及）。
要求: {query}"""
SQL_QUERY = "SQLQuery:"
SQL_QUERY_BACK = "SQL:"
SQL_QUOTE = "```sql"
SQL_QUOTE2= "```vbnet"
SQL_RES_KEY = "sql_res"
INTERMEDIATE_STEPS_KEY = "intermediate_steps"
SQL_CMD = "sql_cmd"
class SQLiteChain(Chain):

    database:SQLDatabase = Field(exclude=True)
    prompt:PromptTemplate = PROMPT
    top_k: int = 5
    llm_chain: LLMChain
    llm: Any
    table_info:str = None
    """Number of results to return from the query"""
    input_key: str = "query"  
    output_key: str = "result"  
    return_sql: bool = False
    """Whether or not to return the intermediate steps along with the final answer."""
    return_direct: bool = False
    """Will return sql-command directly without executing it"""
    return_intermediate_steps: bool = False
    try_time: int = 4
    normal_llm:Any

    @classmethod
    def from_llm(cls, llm, db:[SQLDatabase,str], prompt=None, table_info=None):
        database = db
        if isinstance(db, str) and pathlib.Path(db).expanduser().exists():
            database = SQLDatabase.from_uri(f"sqlite:///{str(pathlib.Path(db).expanduser())}")
        prompt = prompt
        if prompt is None:
            prompt = PromptTemplate(template=PROMPT, input_variables=["table_info","query"])
        llm = llm.copy_llm()
        normal_llm = llm.copy_llm()
        normal_llm.history = []
        llm.top_p = 1
        llm.temperature = 0
        table_info = table_info
        database._sample_rows_in_table_info = 3
        if table_info is None:
            table_info = database.get_table_info(database.get_usable_table_names())
    
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        return cls(llm_chain=llm_chain, llm=llm, database=database,
                   table_info=table_info, prompt=prompt, normal_llm=normal_llm,
                   )
    
    def try_get_sql(self, sql_cmd):
        if SQL_QUERY in sql_cmd:
            sql_cmd = sql_cmd.split(SQL_QUERY)[1].strip()
            if ";" in sql_cmd:
                sql_cmd = sql_cmd.split(";")[0].strip()
        if  sql_cmd.startswith(SQL_QUERY_BACK):
            sql_cmd = sql_cmd.split(SQL_QUERY_BACK)[1].strip()
            if ";" in sql_cmd:
                sql_cmd = sql_cmd.split(";")[0].strip()
        
        if SQL_QUOTE in sql_cmd:
            sql_cmd = sql_cmd.split(SQL_QUOTE)[1].split("```")[0].strip()
            if ";" in sql_cmd:
                sql_cmd = sql_cmd.split(";")[0].strip()
        if SQL_QUOTE2 in sql_cmd:
            sql_cmd = sql_cmd.split(SQL_QUOTE2)[1].split("```")[0].strip()
            if ";" in sql_cmd:
                sql_cmd = sql_cmd.split(";")[0].strip()
        if sql_cmd.count("`") == 2:
            return sql_cmd.split("`")[1].strip()
        return sql_cmd
    
    @property
    def input_keys(self) -> List[str]:
        """Return the singular input key.

        :meta private:
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Return the singular output key.

        :meta private:
        """
        if not self.return_intermediate_steps:
            return [self.output_key, SQL_RES_KEY, SQL_CMD]
        else:
            return [self.output_key, SQL_RES_KEY,SQL_CMD, INTERMEDIATE_STEPS_KEY]


    def _call(self,inputs: Dict[str, Any],
            run_manager: Optional[CallbackManagerForChainRun] = None,
                ) -> Dict[str, Any]:
        
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        input_text:str = f"{inputs[self.input_key]}"
        _run_manager.on_text(input_text, verbose=self.verbose)
        # If not present, then defaults to None which is all tables.
        table_names_to_use = inputs.get("table_names_to_use")
        # self.llm.system = SYSTEM.format(top_k=str(self.top_k))
        if self.table_info is None or self.table_info == "":
            self.table_info = self.database.get_table_info()
        table_info = self.table_info
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        llm_inputs = {
            "query": input_text,
            "today":today,
            "table_info": table_info,
            "top_k": self.top_k,
            "stop": ["\nSQLResult:"],
        }
        if self.memory is not None:
            for k in self.memory.memory_variables:
                llm_inputs[k] = inputs[k]
        intermediate_steps: List = []
        finally_result = {}
        try:
            intermediate_steps.append(llm_inputs.copy())  # input: sql generation
            Trying = True
            TryingTimes = 0 
            result = []
            while Trying and TryingTimes < self.try_time:
                sql_cmd = self.llm_chain.predict(
                    callbacks=_run_manager.get_child(),
                    **llm_inputs,
                ).strip()
                if self.return_sql:
                    return {self.output_key: "", SQL_RES_KEY:"",SQL_CMD:sql_cmd}
                
                _run_manager.on_text(sql_cmd, color="green", verbose=self.verbose)
                intermediate_steps.append(
                    sql_cmd
                )  # output: sql generation (no checker)
                intermediate_steps.append({"sql_cmd": sql_cmd})  # input: sql exec
                sql_cmd = self.try_get_sql(sql_cmd)
                
                try:
                    result = self.database.run(sql_cmd)
                    logger.info(f"[result]: {len(result)}")
                    
                    finally_result[SQL_RES_KEY] = result
                    finally_result[SQL_CMD] = sql_cmd
                    break
                except Exception as e:
                    if "sqlite3.OperationalError" in str(e):
                        if TryingTimes > self.try_time:
                            return {self.output_key:sql_cmd, SQL_RES_KEY:"", SQL_CMD:sql_cmd}
                        else:
                            logger.debug(f"[SQL Eerr][try :{TryingTimes}/{self.try_time}]: {e}")
                            TryingTimes += 1
                            llm_inputs["query"] = str(e) +"\n"+llm_inputs["query"] +",一步一步想"
                    


            
            _run_manager.on_text("\nSQLResult: ", verbose=self.verbose)
            _run_manager.on_text(result, color="yellow", verbose=self.verbose)
            # If return direct, we just set the final result equal to
            # the result of the sql query result, otherwise try to get a human readable
            # final answer

            logger.info(f"[finally]")
            if isinstance(result, str):
                result = eval(result)
            if self.return_direct:
                final_result = result
            else:
                # print("\nGo an Sql Say:",result)
                if len(str(result)) > 8096:
                    if len(str(result)) < 50000:
                        batch_result = []
                        st = 0
                        batch_results = []
                        
                        while 1:
                            logger.info(f"{st}/{len(result)}")
                            for no,r in enumerate(result[st:]):
                                batch_result.append(r)
                                if len(str(batch_result)) > 7000:
                                    st += no
                                    break
                            if len(str(batch_result)) < 7000:
                                st = len(result)
                            if len(batch_result) > 0:
                                
                                tmp_input_text = input_text + f"\nSQLQuery:sql```{sql_cmd}```\nSQLResult: {batch_result}\nAnswer:"
                                tmp_llm_inputs = llm_inputs.copy()
                                tmp_llm_inputs["query"] = tmp_input_text
                                llm = self.normal_llm.copy_llm()
                                llm.cache = False
                                llm.history = []
                                llm_chain = LLMChain(llm=llm, prompt=self.prompt)
                                final_result = llm_chain.predict(
                                    callbacks=_run_manager.get_child(),
                                    **tmp_llm_inputs,
                                ).strip()
                                logger.info(f"[Batch:{st}:{len(batch_result)}] summart summary:{final_result}")
                                batch_results.append(final_result)
                                batch_result = []
                            else:
                                break

                        
                        llm_inputs["query"] = input_text + "\n".join(batch_results) + "\n总结以上的Answer后得出最终结论:"
                        intermediate_steps.append(llm_inputs.copy())  # input: final answer
                        final_result = self.llm_chain.predict(
                            callbacks=_run_manager.get_child(),
                            **llm_inputs,
                        ).strip()
                        intermediate_steps.append(final_result)  # output: final answer
                        finally_result[self.output_key] = final_result
                        _run_manager.on_text(final_result, color="green", verbose=self.verbose)
                        
                    else:    
                        return {self.output_key:"more than 8096",SQL_RES_KEY:result, SQL_CMD:sql_cmd }
                else:
                    _run_manager.on_text("\nAnswer:", verbose=self.verbose)
                    input_text += f"SQLQuery:{sql_cmd}\nSQLResult: {result}\nAnswer:"
                    llm_inputs["query"] = input_text
                    intermediate_steps.append(llm_inputs.copy())  # input: final answer
                    final_result = self.llm_chain.predict(
                        callbacks=_run_manager.get_child(),
                        **llm_inputs,
                    ).strip()
                    intermediate_steps.append(final_result)  # output: final answer
                    finally_result[self.output_key] = final_result
                    _run_manager.on_text(final_result, color="green", verbose=self.verbose)
            chain_result: Dict[str, Any] = finally_result
            
            return chain_result
        except Exception as exc:
            # Append intermediate steps to exception, to aid in logging and later
            # improvement of few shot prompt seeds
            # exc.intermediate_steps = intermediate_steps  # type: ignore
            raise exc

    def reset(self):
        self.llm.history = []
        self.llm.cache = False
    
    def __ldiv__(self, i):
        if i == 0:
            self.reset()
