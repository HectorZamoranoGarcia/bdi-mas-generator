"""
update_rag.py — Utilidad para reconstruir la base de datos vectorial del RAG.

Ejecutar este script cuando se añadan, modifiquen o eliminen documentos
en la carpeta 'docs/'.  Borra el índice anterior y re-indexa todo.

Uso:
    python -m bdi_mas.update_rag
"""

import shutil
from pathlib import Path

from .rag import build_vectorstore, BASE_DIR, DOCS_PATH


def rebuild_rag_database():
    db_path = BASE_DIR / ".rag_db"

    print("=" * 44)
    print("🔄 REGENERANDO BASE DE DATOS DEL RAG")
    print("=" * 44, "\n")

    if db_path.exists():
        print(f"[*] Borrando índice obsoleto en: {db_path} ...")
        shutil.rmtree(db_path)
    else:
        print("[*] No existía índice previo.")

    print(f"[*] Escaneando nuevos documentos en: {DOCS_PATH[0]} ...")

    try:
        collection = build_vectorstore(DOCS_PATH)
        count = collection.count()
        if count == 0:
            print(
                "\n⚠  No se encontraron documentos válidos "
                "(txt, md, asl, java, html, pdf) en la carpeta docs/."
            )
        else:
            print(
                f"\n✅ Base de datos actualizada correctamente. "
                f"Se indexaron {count} fragmentos de conocimiento."
            )
    except Exception as e:
        print(f"\n❌ ERROR fatal reconstruyendo el índice: {e}")


if __name__ == "__main__":
    rebuild_rag_database()
