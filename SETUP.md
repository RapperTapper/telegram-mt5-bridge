# Telegram MT5 Bridge: Einrichtung für Einsteiger

Diese Anleitung ist für die erstmalige Einrichtung auf einem Mac gedacht. Arbeitet sie gemeinsam
von oben nach unten durch. Überspringt keinen Prüfschritt.

Der aktuelle Stand des Projekts sammelt Telegram-Nachrichten als Rohdaten in einer lokalen
SQLite-Datenbank. Er analysiert noch keine Trading-Signale und löst keine Trades aus.

## Vor dem Start

Der neue Benutzer benötigt:

- einen Mac mit Internetverbindung;
- ein aktives persönliches Telegram-Konto;
- Zugriff auf das GitHub-Repository;
- die Berechtigung, im gewünschten Telegram-Chat Nachrichten zu lesen;
- ungefähr 15 bis 30 Minuten Zeit.

Wichtig: Jeder Benutzer sollte sein eigenes Telegram-Konto und seine eigenen Telegram-API-Daten
verwenden. API-Hash, Login-Code, Zwei-Faktor-Passwort, `.env` und `telegram.session` dürfen niemals
weitergegeben oder in Git committed werden.

## 1. Terminal öffnen

1. Drücke `Command + Leertaste`.
2. Suche nach `Terminal`.
3. Öffne die App.

Alle folgenden Befehle werden im Terminal eingegeben. Kopiere jeweils nur den Inhalt eines
Codeblocks und drücke danach `Enter`.

## 2. Git prüfen

```console
git --version
```

Wenn eine Versionsnummer erscheint, ist Git bereit. Falls macOS die Installation der Command Line
Tools anbietet, bestätige sie und führe den Befehl nach der Installation erneut aus.

## 3. uv installieren

`uv` verwaltet für dieses Projekt Python, die virtuelle Umgebung und alle Python-Pakete. Python
muss normalerweise nicht separat installiert werden; `uv` lädt eine passende Python-3.13-Version
bei Bedarf automatisch herunter.

### Empfohlener Weg auf diesem Projekt-Mac: Homebrew

Die bestehende Entwicklungsumgebung verwendet die Homebrew-Installation von `uv`. Prüfe zuerst:

```console
brew --version
```

Wenn eine Homebrew-Version erscheint, installiere `uv` so:

```console
brew install uv
```

### Alternative ohne Homebrew

Wenn `brew: command not found` erscheint, verwende den offiziellen uv-Installer:

```console
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Schließe danach das Terminal vollständig und öffne es erneut.

### Installation prüfen

```console
uv --version
```

Erwartet wird eine Ausgabe wie `uv 0.x.y`. Falls weiterhin `uv: command not found` erscheint,
starte den Mac nicht sofort neu, sondern schließe zuerst alle Terminalfenster und öffne Terminal
erneut.

Offizielle uv-Anleitung: <https://docs.astral.sh/uv/getting-started/installation/>

## 4. Repository herunterladen

Lege zuerst einen Ordner für Entwicklungsprojekte an und wechsle hinein:

```console
mkdir -p ~/Developer
cd ~/Developer
```

Klone anschließend das Repository:

```console
git clone https://github.com/RapperTapper/telegram-mt5-bridge.git
cd telegram-mt5-bridge
```

Falls GitHub `Repository not found` meldet, fehlt sehr wahrscheinlich der Zugriff auf das
Repository oder die GitHub-Anmeldung. In diesem Fall muss der Repository-Eigentümer den Kollegen
zuerst als Collaborator freischalten.

Prüfe, ob du im richtigen Ordner bist:

```console
pwd
ls
```

In der Ausgabe von `ls` müssen mindestens `README.md`, `pyproject.toml`, `uv.lock`, `src` und
`tests` erscheinen.

Alle weiteren Projektbefehle müssen aus diesem Ordner ausgeführt werden. Das ist wichtig, weil dort
später auch die lokale `.env` liegt.

## 5. Projekt und Python installieren

```console
uv sync --locked
```

Dieser Befehl:

- verwendet exakt die in `uv.lock` festgelegten Abhängigkeiten;
- installiert bei Bedarf eine kompatible Python-3.13-Version;
- erstellt die lokale virtuelle Umgebung `.venv`;
- installiert die Befehle des Projekts.

Die virtuelle Umgebung muss nicht manuell aktiviert werden. Verwendet für dieses Projekt immer
`uv run ...`.

Prüfe die verwendete Python-Version:

```console
uv run python --version
```

Erwartet wird `Python 3.13.x`.

## 6. Eigene Telegram-API-Daten erstellen

Die Werte sind keine BotFather-Daten und kein Bot-Token. Das Projekt meldet ein persönliches
Telegram-Benutzerkonto über Telethon an.

1. Öffne <https://my.telegram.org>.
2. Melde dich mit der Telefonnummer des Telegram-Kontos an, das später sammeln soll.
3. Telegram sendet einen Bestätigungscode. Gib diesen nur auf der Telegram-Webseite ein.
4. Öffne `API development tools`.
5. Erstelle eine Anwendung. Ein einfacher App-Titel und Kurzname reichen aus.
6. Kopiere `api_id` und `api_hash` an einen sicheren Ort für den nächsten Schritt.

Offizielle Telegram-Anleitung: <https://core.telegram.org/api/obtaining_api_id>

## 7. Lokale Konfiguration anlegen

Erstelle `.env` aus der mitgelieferten Vorlage:

```console
cp .env.example .env
```

Öffne die Datei im einfachen Terminal-Editor `nano`:

```console
nano .env
```

Trage zunächst nur `TELEGRAM_API_ID` und `TELEGRAM_API_HASH` ein. Beispiel:

```dotenv
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
TELEGRAM_ALLOWED_CHAT_IDS=

LOG_LEVEL=INFO
API_HOST=127.0.0.1
API_PORT=8765
```

Dabei gilt:

- Ersetze die Beispielwerte durch die eigenen Werte von `my.telegram.org`.
- Verwende keine zusätzlichen Leerzeichen vor oder nach `=`.
- Verwende keine Anführungszeichen.
- Lass `TELEGRAM_ALLOWED_CHAT_IDS` vorerst leer.
- Verändere die übrigen Werte nicht.

Speichern in `nano`:

1. Drücke `Control + O`.
2. Bestätige den Dateinamen mit `Enter`.
3. Beende `nano` mit `Control + X`.

Die Datei `.env` ist absichtlich von Git ausgeschlossen. Prüfe trotzdem niemals ihren Inhalt mit
Screenshots, Chatnachrichten oder Bildschirmfreigaben, während Secrets sichtbar sind.

## 8. Telegram einmalig authentifizieren

Stelle sicher, dass kein anderer Bridge-Befehl läuft. Starte dann:

```console
uv run telegram-mt5-auth
```

Beim ersten Mal fragt Telethon interaktiv nach:

1. der Telefonnummer inklusive Landesvorwahl, beispielsweise `+41...`;
2. dem Telegram-Login-Code;
3. gegebenenfalls dem Telegram-Zwei-Faktor-Passwort.

Login-Code und Passwort bleiben im Terminal und dürfen nicht weitergegeben werden. Bei Erfolg
erscheint sinngemäß:

```text
Telegram authentication successful.
```

Die Anmeldung wird lokal in der Telethon-Session gespeichert. Auf macOS liegt sie standardmäßig
unter:

```text
~/Library/Application Support/TelegramMT5Bridge/telegram.session
```

Diese Datei ermöglicht den Zugriff auf das Telegram-Konto und ist deshalb genauso sensibel wie ein
Passwort. Nicht kopieren, nicht hochladen und nicht in Git aufnehmen.

## 9. Verfügbare Chats anzeigen

Führe Auth, Dialogliste und Collector nie gleichzeitig aus. Beende zuerst den vorherigen Befehl und
starte dann:

```console
uv run telegram-mt5-dialogs
```

Beispielausgabe:

```text
id=-5269379494 | name='Signal Group A'
id=-5584034450 | name='Signal Group B'
```

Notiere ausschließlich die IDs der Chats, die gesammelt werden sollen. Negative IDs sind bei
Telegram-Gruppen und -Channels normal. Die angezeigten Namen sind private Telegram-Daten; poste
diese Ausgabe nicht öffentlich.

## 10. Chat-Allowlist eintragen

Öffne `.env` erneut:

```console
nano .env
```

Trage die gewünschten IDs kommasepariert und ohne Klammern oder Anführungszeichen ein:

```dotenv
TELEGRAM_ALLOWED_CHAT_IDS=-5269379494,-5584034450
```

Speichere mit `Control + O`, `Enter` und beende mit `Control + X`.

Nur Chats in dieser Allowlist werden gespeichert. Eine falsche ID führt normalerweise nicht zu
einem Absturz; aus diesem Chat werden dann schlicht keine Nachrichten gesammelt.

## 11. Einrichtung mit dem Doctor prüfen

```console
uv run telegram-mt5-doctor
```

Der Doctor verbindet sich nicht mit Telegram und zeigt keine Secrets oder Nachrichtentexte an. Er
prüft die Konfiguration, Session, lokalen Verzeichnisse und SQLite. Beim ersten Lauf kann er die
leere lokale Datenbank anlegen.

Das Ende der Ausgabe muss lauten:

```text
Status: OK
```

Falls `Status: SETUP REQUIRED` erscheint, prüfe die entsprechende Zeile:

- `Telegram API ID: missing`: `TELEGRAM_API_ID` in `.env` prüfen.
- `Telegram API hash: missing`: `TELEGRAM_API_HASH` in `.env` prüfen.
- `Allowed chats: 0` oder `invalid`: Allowlist erneut prüfen.
- `Telegram session: missing`: Schritt 8 wiederholen.
- `Database writable: no`: Zugriffsrechte auf das App-Verzeichnis prüfen.

## 12. Automatische Projekttests ausführen

Vor der ersten echten Sammlung:

```console
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Alle drei Befehle müssen erfolgreich enden. Diese Tests verbinden sich nicht mit Telegram.

## 13. Collector starten

```console
uv run telegram-mt5-collect
```

Erwartete Startmeldungen:

```text
Telegram collector started.
Configured chats: 2
Database: /Users/.../TelegramMT5Bridge/runtime/messages.sqlite3
Press Ctrl+C to stop.
```

Das Terminalfenster muss geöffnet bleiben. Solange der Collector läuft:

- darf kein zweiter Collector gestartet werden;
- sollten `telegram-mt5-auth` und `telegram-mt5-dialogs` nicht parallel laufen;
- muss der Mac wach und mit dem Internet verbunden bleiben;
- werden ausschließlich Chats aus der Allowlist erfasst;
- werden keine Nachrichtentexte in die normalen Logs geschrieben;
- werden keine Trades ausgelöst.

Beende den Collector kontrolliert mit `Control + C`. Dadurch kann er die SQLite-Datenbank sauber
abschließen.

## 14. Ersten vollständigen Funktionstest durchführen

Verwendet nach Möglichkeit eine kontrollierte Testgruppe und keine produktive Signalgruppe.

Während der Collector läuft:

1. Sende eine normale Textnachricht.
2. Antworte auf eine bereits erfasste Nachricht.
3. Bearbeite eine Nachricht.
4. Sende eine Mediennachricht mit oder ohne Text.
5. Lösche eine Nachricht, die der Collector zuvor erfasst hat.
6. Warte nach jedem Schritt kurz auf die entsprechende Collector-Meldung.
7. Stoppe den Collector mit `Control + C`.

Danach:

```console
uv run telegram-mt5-db-stats
```

Prüfe:

- `Messages` ist gestiegen;
- `Events` ist mindestens so groß wie `Messages`;
- `new`, `edit` und möglichst `deleted` wurden gezählt;
- `replies` und `media` passen zum Test;
- der Testchat erscheint im Abschnitt `Chats`.

Telegram liefert Löschereignisse nicht in jeder Situation garantiert. Ein einzelnes fehlendes
Delete-Event bedeutet deshalb nicht automatisch, dass die lokale Datenbank defekt ist.

Zum Abschluss:

```console
uv run telegram-mt5-doctor
```

Der Status sollte weiterhin `OK` sein und die Datenbankstatistiken sollten die Testdaten zeigen.

## 15. Normaler Betrieb nach der Einrichtung

Für jeden späteren Start:

```console
cd ~/Developer/telegram-mt5-bridge
uv run telegram-mt5-doctor
uv run telegram-mt5-collect
```

Zum Stoppen `Control + C` drücken.

Nach einem Projekt-Update:

```console
cd ~/Developer/telegram-mt5-bridge
git pull --ff-only
uv sync --locked
uv run telegram-mt5-doctor
uv run telegram-mt5-collect
```

Die lokale `.env`, Telegram-Session und SQLite-Datenbank liegen nicht im Git-Repository und werden
durch `git pull` nicht ersetzt.

## Häufige Probleme

### `uv: command not found`

Terminal komplett schließen und neu öffnen. Danach `uv --version` erneut ausführen. Falls das nicht
hilft, `uv` über Homebrew oder den offiziellen Installer aus Schritt 3 erneut installieren.

### `Repository not found`

GitHub-Zugriff und Repository-URL prüfen. Bei einem privaten Repository muss der Benutzer vorher als
Collaborator eingeladen sein und die Einladung angenommen haben.

### `TELEGRAM_API_ID is not configured`

Prüfen, ob die Datei wirklich `.env` heißt, im Projektordner liegt und die Zeile keinen Tippfehler
enthält. Der Befehl muss aus dem Ordner `telegram-mt5-bridge` gestartet werden.

### `TELEGRAM_API_HASH is not configured`

API-Hash aus `my.telegram.org` erneut eintragen. Nicht den Telegram-Login-Code oder einen Bot-Token
verwenden.

### `No Telegram chats configured`

`uv run telegram-mt5-dialogs` ausführen und die gewünschten IDs in
`TELEGRAM_ALLOWED_CHAT_IDS` eintragen.

### `database is locked` oder Session-Fehler

Prüfen, ob Collector, Auth oder Dialogliste in einem anderen Terminal noch laufen. Es sollte nur ein
Prozess dieselbe Telegram-Session verwenden.

### Collector läuft, aber sammelt nichts

Prüfen:

1. Ist die exakte Chat-ID in `.env` eingetragen?
2. Ist das Telegram-Konto weiterhin Mitglied im Chat?
3. Entstehen nach dem Start neue Nachrichten?
4. Ist der Mac wach und online?
5. Zeigt `uv run telegram-mt5-doctor` den Status `OK`?

## Übergabe-Checkliste

- [ ] `git --version` funktioniert.
- [ ] `uv --version` funktioniert.
- [ ] Repository wurde geklont.
- [ ] `uv sync --locked` war erfolgreich.
- [ ] Eigene Telegram-API-Daten wurden erstellt.
- [ ] `.env` wurde lokal angelegt und nicht geteilt.
- [ ] `telegram-mt5-auth` war erfolgreich.
- [ ] Richtige Chat-IDs wurden ausgewählt.
- [ ] Doctor zeigt `Status: OK`.
- [ ] Ruff und pytest sind grün.
- [ ] Text, Reply, Edit, Media und Delete wurden getestet.
- [ ] `telegram-mt5-db-stats` zeigt plausible Werte.
- [ ] Der Kollege kann Collector und Doctor ohne Hilfe starten und stoppen.
