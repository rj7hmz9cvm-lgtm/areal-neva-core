import sqlite3, json

DB="/root/.areal-neva-core/orchestra.db"

def init_db():
    c=sqlite3.connect(DB)
    cur=c.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY,status TEXT,payload TEXT,result TEXT)")
    c.commit();c.close()

def create_task(task_type,payload,**kw):
    c=sqlite3.connect(DB);cur=c.cursor()
    cur.execute("INSERT INTO tasks(status,payload) VALUES(?,?)",("pending",json.dumps(payload)))
    c.commit();tid=cur.lastrowid;c.close();return tid

def get_pending_tasks():
    c=sqlite3.connect(DB);cur=c.cursor()
    cur.execute("SELECT id,payload FROM tasks WHERE status='pending'")
    rows=cur.fetchall();c.close()
    return [{"id":r[0],"payload":json.loads(r[1])} for r in rows]

def update_task(i,s,r):
    c=sqlite3.connect(DB);cur=c.cursor()
    cur.execute("UPDATE tasks SET status=?, result=? WHERE id=?",(str(s),str(r),i))
    c.commit();c.close()
