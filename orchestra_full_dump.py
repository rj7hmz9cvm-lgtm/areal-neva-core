import json,sqlite3,os,glob
from datetime import datetime
BASE="/root/.areal-neva-core"
def build():
    d={"chat_id":"UNKNOWN","exported_at":datetime.utcnow().isoformat()+"Z","source_platform":"areal-neva-core","source_model":"orchestra_full_dump","system":"AREAL-NEVA ORCHESTRA server 89.22.225.136 owner Ilya bot @ai_orkestra_all_bot","architecture":"telegram_daemon->core.db->task_worker->ai_router OpenRouter perplexity/sonar+deepseek->reply_sender->Telegram","pipeline":"voice/text->daemon->create_task->worker->STT->ai_router->perplexity search->deepseek format->reply","memory":"core.db tasks+task_history+pin. memory.db key/value. memory_files CHATS/GLOBAL/SYSTEM jsonl","integrations":"OpenRouter perplexity/sonar deepseek/deepseek-chat Groq STT OpenAI STT Google Drive Telegram","services":["telegram-ingress.service","areal-task-worker.service","areal-memory-api.service"],"env":[],"db":"tasks(id,chat_id,input_type,raw_input,state,result,error_message,reply_to_message_id,created_at,updated_at) task_history(task_id,action,created_at) pin(task_id,chat_id,state,updated_at) memory(chat_id,key,value,timestamp)","logic":"NEW->IN_PROGRESS->AWAITING_CONFIRMATION->DONE. search: perplexity/sonar->inject search_context->deepseek formats. STT in daemon. BAD_RESULT_RE filters junk","decisions":"ONLINE_MODEL=perplexity/sonar DEFAULT_MODEL=deepseek/deepseek-chat STT in daemon override=True links check removed gemini removed","errors":["gemini 403 blocked->replaced with perplexity/sonar","links check killed valid results->removed","DeepSeek placeholder->BAD_RESULT_RE","voice file not found stale tasks->recover_stale","ai_router old version persisted->full rewrite"],"state":"voice ok STT ok search ok perplexity/sonar ok results reach Telegram","limits":"memory.db write after DONE not implemented web_engine.py duckduckgo dead code dump command not yet in daemon","pending":"verify memory.db writes remove duckduckgo clean web_engine.py","files":{},"tasks":[],"memory_data":[],"logs":{}}
    env_path=BASE+"/.env"
    if os.path.exists(env_path):
        for line in open(env_path):
            line=line.strip()
            if line and not line.startswith("#") and "=" in line:
                d["env"].append(line.split("=")[0])
    for f in ["telegram_daemon.py","task_worker.py","core/ai_router.py","core/stt_engine.py","core/reply_sender.py","core/pin_manager.py","memory_api_server.py","google_io.py"]:
        p=BASE+"/"+f
        d["files"][f]=open(p).read() if os.path.exists(p) else "NOT_FOUND"
    db_path=BASE+"/data/core.db"
    if os.path.exists(db_path):
        conn=sqlite3.connect(db_path)
        conn.row_factory=sqlite3.Row
        try:
            rows=conn.execute("SELECT t.id,t.chat_id,t.input_type,t.raw_input,t.state,t.result,t.error_message,t.created_at,t.updated_at,GROUP_CONCAT(h.action,\" | \") as history FROM tasks t LEFT JOIN task_history h ON h.task_id=t.id GROUP BY t.id ORDER BY t.created_at DESC LIMIT 200").fetchall()
            for r in rows: d["tasks"].append(dict(r))
        except: pass
        finally: conn.close()
    mem_path=BASE+"/data/memory.db"
    if os.path.exists(mem_path):
        conn=sqlite3.connect(mem_path)
        conn.row_factory=sqlite3.Row
        try:
            rows=conn.execute("SELECT * FROM memory ORDER BY timestamp DESC LIMIT 500").fetchall()
            for r in rows: d["memory_data"].append(dict(r))
        except: pass
        finally: conn.close()
    for log in ["task_worker.log","ai_router.log","telegram_daemon.log"]:
        p=BASE+"/logs/"+log
        d["logs"][log]="".join(open(p).readlines()[-300:]) if os.path.exists(p) else "NOT_FOUND"
    return d
if __name__=="__main__":
    import sys
    out=json.dumps(build(),ensure_ascii=False,default=str)
    from datetime import datetime
    ts=datetime.now().strftime("%Y%m%d_%H%M%S")
    fp="/root/.areal-neva-core/data/memory/UNSORTED/orchestra_dump_"+ts+".json"
    open(fp,"w").write(out)
    print(out)
