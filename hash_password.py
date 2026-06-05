from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()

def genera_hash(password_in_chiaro: str) -> str:
    return password_hasher.hash(password_in_chiaro)

def verifica_password(password_in_chiaro: str, hash_dal_db: str) -> bool:
    return password_hasher.verify(password_in_chiaro, hash_dal_db)