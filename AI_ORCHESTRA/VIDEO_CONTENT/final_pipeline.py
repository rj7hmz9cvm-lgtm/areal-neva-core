#!/usr/bin/env python3
 , os, time
from datetime import datetime

# DISABLED: client = DISABLED_PROVIDER(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url='https://openrouter.ai/api/v1'
)

PROMPT = '''
... (весь тот же длинный промпт, который был выше) ...
'''

models = ['deepseek/deepseek-v3', 'deepseek/deepseek-chat', 'deepseek/deepseek-chat']
results = {}
print("\n🔍 Опрашиваю модели...")
for i, m in enumerate(models, 1):
    print(f"  {i}/{len(models)} {m} ...")
    try:
        r = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": PROMPT}],
            temperature=0.3,
            max_tokens=4000
        )
        results[m] = r.choices[0].message.content
    except Exception as e:
        results[m] = f"Ошибка: {str(e)}"
    time.sleep(2)

timestamp = datetime.now().strftime("%Y%m%d_%H%M")
path = os.path.expanduser(f"~/AI_ORCHESTRA/VIDEO_CONTENT/final_platform_pipeline_{timestamp}.md")
with open(path, 'w', encoding='utf-8') as f:
    f.write("# ИТОГОВЫЙ ПАЙПЛАЙН\n\n")
    for m, ans in results.items():
        f.write(f"## {m}\n\n{ans}\n\n---\n")

links_path = os.path.expanduser("~/AI_ORCHESTRA/VIDEO_CONTENT/registration_links.md")
with open(links_path, 'w', encoding='utf-8') as f:
    f.write("# ССЫЛКИ ДЛЯ РЕГИСТРАЦИИ\n\n")
    f.write("- [Kling](https://kling.kuaishou.com)\n")
    f.write("- [Hailuo](https://hailuo.ai)\n")
    f.write("- [Runway](https://runwayml.com)\n")
    f.write("- [Pika](https://pika.art)\n")
    f.write("- [HeyGen](https://heygen.com)\n")
    f.write("- [ElevenLabs](https://elevenlabs.io)\n")
    f.write("- [CapCut](https://capcut.com)\n")
    f.write("- [DaVinci Resolve](https://blackmagicdesign.com/products/davinciresolve)\n")
    f.write("- [Leonardo AI](https://leonardo.ai)\n")
    f.write("- [Clipdrop](https://clipdrop.co)\n")
    f.write("- [Playground AI](https://playgroundai.com)\n")
    f.write("- [Canva](https://canva.com)\n")

print("\n✅ ГОТОВО!")
print(f"📄 {path}")
print(f"🔗 {links_path}")
os.system('afplay /System/Library/Sounds/Glass.aiff &')
