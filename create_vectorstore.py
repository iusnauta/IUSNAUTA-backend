import os
from openai import OpenAI

client = OpenAI()

print("🔍 Creando Vector Store en OpenAI...")
vs = client.vector_stores.create(name="iusnauta_leyes_honduras")
print(f"✔ Vector Store creado: {vs.id}")

folder = "./legal_corpus"
pdf_files = [
    os.path.join(folder, f)
    for f in os.listdir(folder)
    if f.lower().endswith(".pdf")
]

print(f"📚 PDFs detectados ({len(pdf_files)}):")
for f in pdf_files:
    print(" -", f)

print("\n⬆ Subiendo PDFs...")

for path in pdf_files:
    print(f"   -> Subiendo: {path}")
    with open(path, "rb") as f:
        data = f.read()
        response = client.vector_stores.files.create_and_poll(
            vector_store_id=vs.id,
            input=data  # <-- FIRMA CORRECTA
        )
    print(f"      ✔ Procesado: {os.path.basename(path)}")

print("\n🎉 TODOS LOS ARCHIVOS SUBIDOS EXITOSAMENTE 🔥")
print(f"📌 Vector Store listo: {vs.id}")