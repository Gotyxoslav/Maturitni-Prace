# Toney
Maturitní projekt

Autor: Holakovský Matyáš, IT-4

# Popis
Stránka na přehrávání hudby inspirovaná aplikacemi, jako je Spotify a YouTube Music.

Uživatel se může registrovat, upravit profil, poslouchat hudbu, a tvořit playlisty. Autoři pak také mohou přidávat písničky a alba.

# Aktivace
1. install.bat by měl nainstalovat všechny potřebné knihovny, mimo to se dá vše nainstalovat pomocí "pip install Flask argon2-cffi mysql-connector-python pyqt6"
2. Samotná stránka se zapne pomocí run_website.bat, či pomocí main.py ve views
3. Administrátorská aplikace se zapne pomocí run_adminapp.py či pomocí adminapp.py ve views



# Struktura Databáze
1. MATURITA_HOL_USERS

Tabulka pro uchovávání uživatelských účtů a jejich profilů.

id: Primární klíč, unikátní UUID (generováno přes generate_id()).

username: Uživatelské jméno (Text).

email: E-mailová adresa (Text).

password: Zahashované heslo pomocí Argon2 (Text).

role: Uživatelská role (Číslo/Text, používá se např. role 1 nebo 2 pro administrátory).

pfp: Cesta k profilovému obrázku (Text, např. ../static/data/pfp/UUID.png).

description: Popisek profilu uživatele (Text).

2. MATURITA_HOL_SONGS

Tabulka obsahující jednotlivé nahrané písničky.

song_id: Primární klíč, unikátní UUID (Text).

title: Název písničky (Text).

author: ID uživatele, který písničku nahrál (Vazba na id v tabulce USERS).

album: ID alba, do kterého písnička patří (Vazba na album_id v tabulce ALBUMS).

songfile: Cesta k nahranému .mp3 souboru (Text, např. songs/UUID.mp3).

3. MATURITA_HOL_ALBUMS

Tabulka seskupující písničky do alb.

album_id: Primární klíč, unikátní UUID (Text).

title: Název alba (Text).

author: ID uživatele, který album vytvořil (Vazba na id v tabulce USERS).

release_date: Datum vydání alba (Datum/Text).

albumfile: Cesta k obalu alba (Text, např. ../static/data/albums/UUID.png).

4. MATURITA_HOL_PLAYLISTS

Tabulka uživatelských playlistů.

id: Primární klíč, unikátní UUID (Text).

author: ID uživatele, který playlist vytvořil (Vazba na id v tabulce USERS).

name: Název playlistu (Text, výchozí je "My playlist").

description: Popisek playlistu (Text).

playlistfile: Cesta k obrázku playlistu (Text, např. ../static/data/playlists/UUID.png).

5. MATURITA_HOL_PLAYLIST_SONGS

Vazební tabulka (M:N), která spojuje konkrétní písničky s konkrétními playlisty a určuje jejich pořadí.

playlist_id: ID playlistu (Vazba na id v tabulce PLAYLISTS).

song_id: ID písničky (Vazba na song_id v tabulce SONGS).

placement: Pořadí písničky v daném playlistu (Číslo, začíná od 1 a přepočítává se při smazání písničky).
