# CivitAI Browser+ – lokale Weiterentwicklung

## Installation mit bestehenden Einstellungen

1. Stable Diffusion WebUI/Forge vollständig beenden.
2. Den bisherigen Erweiterungsordner und die WebUI-Dateien `config.json`,
   `ui-config.json` sowie `config_states/civitai_subfolders.json` sichern. Diese Konfigurationsdateien
   können je nach Installation an einem anderen WebUI-Arbeitsverzeichnis liegen.
3. Den bisherigen Erweiterungsordner durch diese Version ersetzen und dabei
   denselben Ordnernamen beibehalten: `sd-civitai-browser-plus`.
4. WebUI/Forge starten. Die bisherigen `civitai_*`-Optionen bleiben unverändert;
   es ist keine Einstellungsumwandlung nötig. Modellordner und Sidecar-Dateien
   werden nicht bei der Installation verändert.

## Änderungen

- Der Update-Scan betrachtet standardmäßig nur neuere Versionen derselben
  `baseModel`-Variante wie die installierte Version. Die neue Checkbox im Reiter
  **Update Models** kann andere Varianten ausdrücklich als Updates mitzählen.
  Beim Sammeldownload wird die gefundene Zielversion dieser Variante gewählt.
- **Select all loaded updates** markiert alle bereits in den Browser geladenen
  Update-Ergebnisse. Bestehende Auswahl wird nicht aufgehoben. **Queue all found
  updates** fügt alle Ergebnisse des Scans über sämtliche Ergebnisseiten zur
  Download-Warteschlange hinzu.
- Modellordner werden für kurze Zeit zwischengespeichert, damit Seitenwechsel
  und Auswahl in großen Sammlungen schneller reagieren. Nach einem Download
  wird der Zwischenspeicher geleert.
- Modell- und Info-JSONs werden atomar ersetzt. Leere oder beschädigte
  `.cm-info.json`-Dateien anderer Erweiterungen werden nicht mehr als CivitAI-
  Modellmetadaten eingelesen. Sie werden nicht gelöscht oder repariert.
- Downloads laufen in `.civitai-part`-Dateien und werden erst nach Erfolg unter
  dem endgültigen Modellnamen abgelegt. Bei einem erneuten Versuch kann der
  bereits geladene Teil genutzt werden. Ein Platzcheck prüft das Ziellaufwerk
  mit 512 MiB Reserve. Falls CivitAI keine Dateigröße liefert, kann nur diese
  Reserve vorab geprüft werden.

## Bekannte Grenzen

Die Änderungen wurden mit automatischen Regressionstests und Syntaxprüfung
geprüft. Ein vollständiger Test in einer laufenden Forge-Installation und mit
echten CivitAI-Downloads war in dieser Arbeitsumgebung nicht möglich.
"Model not found" im Log bedeutet, dass der Hash bei CivitAI nicht gefunden
wurde; dies kann bei privaten, entfernten oder anderswo bezogenen Modellen
weiterhin vorkommen.
