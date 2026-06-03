# hash_password.py
from pwdlib import PasswordHash

# Inizializza lo stesso hasher consigliato usato nel tuo backend
password_hash = PasswordHash.recommended()

def genera_hash(password_in_chiaro: str) -> str:
    """Genera l'hash sicuro per la password passata."""
    return password_hash.hash(password_in_chiaro)

if __name__ == "__main__":
    # Inserisci qui la password che vuoi inserire nel database
    password_da_criptare = input() 
    
    hash_risultante = genera_hash(password_da_criptare)
    
    print("\n--- GENERATORE DI HASH ---")
    print(f"Password originale: {password_da_criptare}")
    print(f"Hash da copiare nel DB: {hash_risultante}")
    print("--------------------------\n")