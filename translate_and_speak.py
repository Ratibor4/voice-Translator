import tkinter as tk
from tkinter import ttk, messagebox
import threading
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import pygame
import tempfile
import os
import re

# Очистка текста от мусорных символов
def clean_text(text):
    return re.sub(r'[\x00-\x1F\x7F]', '', text).strip()

# Озвучивание переведённого текста
def speak_text(text, lang='en'):
    try:
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_file = fp.name
            tts.save(temp_file)

        pygame.mixer.init()
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue

        pygame.mixer.music.unload()
        pygame.mixer.quit()
        os.remove(temp_file)

    except Exception as e:
        print("Ошибка озвучки:", e)

# Распознавание и перевод речи
def translate_and_speak(input_lang, output_lang, input_field, output_field):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        input_field.set("Говорите...")
        try:
            audio = recognizer.listen(source, timeout=5)
            recognized_text = recognizer.recognize_google(audio, language=input_lang)
            recognized_text = clean_text(recognized_text)
            input_field.set(recognized_text)

            translated_text = GoogleTranslator(source='auto', target=output_lang).translate(recognized_text)
            translated_text = clean_text(translated_text)
            output_field.set(translated_text)

            speak_text(translated_text, lang=output_lang)

        except Exception as e:
            input_field.set("Ошибка: " + str(e))

# Интерфейс GUI
def main_gui():
    pygame.init()

    root = tk.Tk()
    root.title("🎙 Голосовой переводчик")
    root.geometry("400x300")
    root.resizable(False, False)

    input_lang = tk.StringVar(value='ru-RU')
    output_lang = tk.StringVar(value='en')
    input_text = tk.StringVar()
    output_text = tk.StringVar()

    def on_translate():
        threading.Thread(
            target=translate_and_speak,
            args=(input_lang.get(), output_lang.get(), input_text, output_text),
            daemon=True
        ).start()

    def on_exit():
        root.destroy()

    langs = {
        'Русский → Английский': ('ru-RU', 'en'),
        'Английский → Русский': ('en-US', 'ru')
    }

    def change_direction(event):
        selection = lang_menu.get()
        in_lang, out_lang = langs[selection]
        input_lang.set(in_lang)
        output_lang.set(out_lang)

    # Элементы
    lang_menu = ttk.Combobox(root, values=list(langs.keys()), state="readonly")
    lang_menu.set('Русский → Английский')
    lang_menu.bind("<<ComboboxSelected>>", change_direction)
    lang_menu.pack(pady=10)

    ttk.Label(root, text="Вы сказали:").pack()
    ttk.Entry(root, textvariable=input_text, state='readonly', width=50).pack(pady=5)

    ttk.Label(root, text="Перевод:").pack()
    ttk.Entry(root, textvariable=output_text, state='readonly', width=50).pack(pady=5)

    ttk.Button(root, text="🎤 Говорить", command=on_translate).pack(pady=10)
    ttk.Button(root, text="🚪 Выход", command=on_exit).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main_gui()
