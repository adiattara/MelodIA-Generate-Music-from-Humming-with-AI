import streamlit as st
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import librosa
import pretty_midi
import os
import subprocess
import requests

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

METRONOME_FILE = os.path.join(DATA_DIR, 'metronome_track.wav')
VOICE_RECORDING_FILE = os.path.join(DATA_DIR, 'voice_recording.wav')
OUTPUT_MIDI_FILE = os.path.join(DATA_DIR, 'output.mid')
ENHANCED_MIDI_FILE = os.path.join(DATA_DIR, 'enhanced_output.mid')
OUTPUT_MP3_FILE = os.path.join(DATA_DIR, 'enhanced_output.mp3')

def generate_metronome_sound(frequency=1000, duration=100, fs=44100):
    t = np.linspace(0, duration / 1000, int(fs * duration / 1000), endpoint=False)
    sound = 0.5 * np.sin(2 * np.pi * frequency * t)
    return sound

def generate_metronome_track(bpm, measures=4, beats_per_measure=4, fs=44100):
    beat_duration = 60 / bpm
    total_beats = measures * beats_per_measure
    metronome_click = generate_metronome_sound(frequency=1000, duration=100, fs=fs)
    silence_duration = beat_duration - (len(metronome_click) / fs)
    silence = np.zeros(int(fs * silence_duration))
    metronome_track = np.array([])
    for _ in range(int(total_beats)):
        beat = np.concatenate((metronome_click, silence))
        metronome_track = np.concatenate((metronome_track, beat))
    metronome_track = (metronome_track * 32767).astype(np.int16)
    write(METRONOME_FILE, fs, metronome_track)
    return metronome_track, fs

def audio_to_midi(audio_file):
    y, sr = librosa.load(audio_file)
    # Supposons que wave_to_midi est défini dans un module à part
    from monophonic import wave_to_midi
    notes, estimated_bpm = wave_to_midi(y, sr)
    midi = pretty_midi.PrettyMIDI()
    piano_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
    piano = pretty_midi.Instrument(program=piano_program)
    for note in notes:
        note_start = note[0]
        note_end = note[1]
        note_pitch = int(note[2])
        midi_note = pretty_midi.Note(velocity=100, pitch=note_pitch, start=note_start, end=note_end)
        piano.notes.append(midi_note)
    midi.instruments.append(piano)
    midi.write(OUTPUT_MIDI_FILE)
    st.success("Conversion audio en MIDI terminée.")
    return OUTPUT_MIDI_FILE

def improve_midi_with_ai(midi_file_path, ai_service_url=os.environ.get("API_URL", "http://backend:8000/enrich_midi/")):
    st.info("Amélioration du MIDI avec l'IA via FastAPI en cours...")
    with open(midi_file_path, "rb") as f:
        files = {"file": (os.path.basename(midi_file_path), f, "audio/midi")}
        try:
            response = requests.post(ai_service_url, files=files)
            response.raise_for_status()
        except requests.RequestException as e:
            st.error(f"Erreur lors de l'appel au service IA : {e}")
            return None
    enriched_midi_path = ENHANCED_MIDI_FILE
    with open(enriched_midi_path, "wb") as out_f:
        out_f.write(response.content)
    st.success(f"MIDI amélioré reçu et sauvegardé dans {enriched_midi_path}")
    return enriched_midi_path

def midi_to_mp3(midi_file, output_audio_file=OUTPUT_MP3_FILE):
    wav_file = os.path.join(DATA_DIR, 'temp_output.wav')
    try:
        subprocess.run(['timidity', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        st.error("TiMidity++ n'est pas installé ou accessible.")
        return None
    try:
        subprocess.run(['timidity', midi_file, '-Ow', '-o', wav_file], check=True)
    except subprocess.CalledProcessError as e:
        st.error(f"Erreur lors de la conversion MIDI -> WAV : {e}")
        return None
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        st.error("ffmpeg n'est pas installé ou accessible.")
        return None
    try:
        subprocess.run(['ffmpeg', '-y', '-i', wav_file, output_audio_file], check=True)
    except subprocess.CalledProcessError as e:
        st.error(f"Erreur lors de la conversion WAV -> MP3 : {e}")
        return None
    finally:
        if os.path.exists(wav_file):
            os.remove(wav_file)
    st.success(f"Conversion MIDI en MP3 terminée : {output_audio_file}")
    return output_audio_file

def main():
    st.title("🎵 MelodIA - Générateur de Musique Assisté par IA 🎵")

    if 'step' not in st.session_state:
        st.session_state.step = 1

    if st.session_state.step == 1:
        st.header("1️⃣ Paramètres du Métronome")
        bpm = st.number_input('Entrez le BPM :', min_value=1, max_value=300, value=120)
        measures = st.number_input('Nombre de mesures :', min_value=1, max_value=16, value=4)
        beats_per_measure = 4
        if st.button("Jouer le Métronome"):
            generate_metronome_track(bpm, measures, beats_per_measure)
            st.audio(METRONOME_FILE, format='audio/wav')
            st.success("Métronome joué. Enregistrez votre voix.")
            st.session_state.step = 2

    if st.session_state.step == 2:
        st.header("2️⃣ Téléchargez un fichier audio WAV")
        uploaded_file = st.file_uploader("Choisissez un fichier audio", type=["wav"])
        if uploaded_file is not None:
            with open(VOICE_RECORDING_FILE, "wb") as f:
                f.write(uploaded_file.read())
            st.audio(VOICE_RECORDING_FILE, format='audio/wav')
            st.session_state.step = 3

    if st.session_state.step == 3:
        st.header("3️⃣ Conversion en MIDI")
        if st.button("Convertir en MIDI"):
            if os.path.exists(VOICE_RECORDING_FILE):
                audio_to_midi(VOICE_RECORDING_FILE)
                with open(OUTPUT_MIDI_FILE, "rb") as f:
                    st.download_button("Télécharger le MIDI généré", f, file_name="output.mid")
                st.session_state.step = 4
            else:
                st.warning("Aucun fichier audio trouvé.")

    if st.session_state.step == 4:
        st.header("4️⃣ Amélioration du MIDI avec l'IA")
        if st.button("Améliorer avec IA"):
            if os.path.exists(OUTPUT_MIDI_FILE):
                improved = improve_midi_with_ai(OUTPUT_MIDI_FILE)
                if improved and os.path.exists(improved):
                    with open(improved, "rb") as f:
                        st.download_button("Télécharger le MIDI amélioré", f, file_name="enhanced_output.mid")
                    st.session_state.step = 5
                else:
                    st.error("Échec de l'amélioration.")
            else:
                st.warning("Aucun fichier MIDI trouvé.")

    if st.session_state.step == 5:
        st.header("5️⃣ Conversion en MP3")
        if st.button("Convertir en MP3"):
            if os.path.exists(ENHANCED_MIDI_FILE):
                mp3_file = midi_to_mp3(ENHANCED_MIDI_FILE)
                if mp3_file and os.path.exists(mp3_file):
                    st.audio(mp3_file, format="audio/mp3")
                    with open(mp3_file, "rb") as f:
                        st.download_button("Télécharger le MP3", f, file_name="enhanced_output.mp3")
                else:
                    st.error("Échec de la conversion en MP3.")
            else:
                st.warning("Aucun fichier MIDI amélioré trouvé.")

if __name__ == "__main__":
    main()
