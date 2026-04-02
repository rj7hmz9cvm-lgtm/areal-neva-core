import sys, time, traceback
sys.path.insert(0,"/root/.areal-neva-core")

import storage_layer
from lib.orchestra_runtime import execute
from telegram_bot import send_telegram_reply

def main():
    storage_layer.init_db()
    print("WORKER_READY")

    while True:
        try:
            tasks = storage_layer.get_pending_tasks()

            for t in tasks:
                try:
                    status, result = execute(t)
                    storage_layer.update_task(t["id"], status, result)

                    # ОТВЕТ В TELEGRAM
                    if t.get("chat_id") and t.get("message_id"):
                        send_telegram_reply(
                            t["chat_id"],
                            t["message_id"],
                            str(result)[:3500]
                        )

                except Exception as e:
                    storage_layer.update_task(t["id"], "failed", str(e))
                    print(traceback.format_exc())

        except Exception as e:
            print("LOOP_ERROR:", e)

        time.sleep(2)

if __name__ == "__main__":
    main()
