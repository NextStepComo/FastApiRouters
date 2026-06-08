import ollama

def chiedi_a_gemma():
    try:
        response = ollama.chat(
            model='gemma4:e2b',
            messages=[
                {
                    'role': 'system',
                    'content': 'Sei un assistente virtuale locale conciso e preciso. Rispondi in italiano.'
                },
                {
                    'role': 'user',
                    'content': 'Spiegami brevemente cos\'è il calcolo quantistico.'
                }
            ],
            options={
                'temperature': 0.7,  # Controlla la creatività (0.0 = deterministico, 1.0 = creativo)
                'top_p': 0.9
            }
        )
        
        # Stampa la risposta generata dal modello
        print(response['message']['content'])
        
    except Exception as e:
        print(f"Errore durante la chiamata: {e}")

if __name__ == "__main__":
    chiedi_a_gemma()