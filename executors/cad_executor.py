import os
import ezdxf

def run_cad(query):
    q = query.replace("[CAD]", "").strip()
    lines = []
    lines.append("CAD-МОДУЛЬ")
    lines.append("")
    lines.append("Задача:")
    lines.append(q)
    lines.append("")
    lines.append("Статус:")
    lines.append("DXF-библиотека установлена и готова")
    lines.append("DWG поддерживается через конвертацию в DXF")
    lines.append("")

    dxf_files = []
    for root, _, files in os.walk("."):
        for f in files:
            if f.lower().endswith(".dxf"):
                dxf_files.append(os.path.join(root, f))

    if dxf_files:
        target = dxf_files[0]
        lines.append("Найден DXF:")
        lines.append(target)
        try:
            doc = ezdxf.readfile(target)
            msp = doc.modelspace()
            count = 0
            for _ in msp:
                count += 1
            lines.append("Количество объектов:")
            lines.append(str(count))
        except Exception as e:
            lines.append("Ошибка чтения DXF:")
            lines.append(str(e))
    else:
        lines.append("DXF-файлы в проекте не найдены")

    return "\n".join(lines)
