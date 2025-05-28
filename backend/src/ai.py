from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import io
import os
import uuid
import datetime
import databases

from midi_generator import load_model_from_huggingface, generate_continuation_midi

app = FastAPI(title="MelodIA AI Service")

DATABASE_URL="postgresql://postgres:password@db:5432/melodia_db"

database = databases.Database(DATABASE_URL)

ENHANCED_MIDI_FILE = "enhanced_output.mid"


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/enrich_midi/")
async def enrich_midi(file: UploadFile = File(...)):
    if not (file.filename.endswith(".mid") or file.filename.endswith(".midi")):
        raise HTTPException(status_code=400, detail="Seuls les fichiers MIDI sont acceptés.")

    content = await file.read()
    input_path = "input.mid"
    output_path = ENHANCED_MIDI_FILE

    with open(input_path, "wb") as f:
        f.write(content)

    model_name = "skytnt/midi-model-tv2o-medium"
    device = "cuda" if False else "cpu"

    model, tokenizer = load_model_from_huggingface(model_name, device=device)

    try:
        generate_continuation_midi(
            model=model,
            tokenizer=tokenizer,
            output_path=output_path,
            input_midi_path=input_path,
            max_len=512,
            temp=0.90,
            top_p=0.98,
            top_k=20
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération IA : {e}")

    if not os.path.exists(output_path):
        raise HTTPException(status_code=500, detail="Le fichier MIDI enrichi est introuvable.")

    # Génération d'un nom unique et timestamp uniquement pour l'enregistrement en base
    unique_id = str(uuid.uuid4())
    timestamp = datetime.datetime.utcnow()
    filename_for_db = f"{unique_id}_{file.filename}"

    query = """
    INSERT INTO enrich_logs(filename, unique_id, processed_at)
    VALUES (:filename, :unique_id, :processed_at)
    """
    await database.execute(
        query=query,
        values={
            "filename": filename_for_db,
            "unique_id": unique_id,
            "processed_at": timestamp
        }
    )

    def cleanup():
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.remove(path)

    with open(output_path, "rb") as f:
        midi_bytes = f.read()

    cleanup()

    return StreamingResponse(
        io.BytesIO(midi_bytes),
        media_type="audio/midi",
        headers={"Content-Disposition": f"attachment; filename=enriched_{file.filename}"}
    )
