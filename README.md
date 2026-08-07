# Fake News Simulator

## Overview

Dieses Projekt wurde im Rahmen des Moduls "Informatik und Gesellschaft" erstellt.
Es simuliert abstrakt ein soziales Netzwerk wie es zum Beispiel bei Instagram zu finden ist. Insbesondere
wird dabei die Verbreitung von Desinformationen ("Fake News") basierend auf unterschiedlichen Annahmen bezogen auf das
Netzwerk untersucht. Diese Annahmen betreffen auch Moderation und wie beziehungsweise wie stark sie eingesetzt wird.

## Model Idea

Das soziale Netzwerk wird als gerichteter Graph simuliert. Dabei stellt ein Knoten in diesem Graph einen Account dar.
Ein Account kann entweder ein Influencer oder ein normaler User sein. Zwischen den Knoten liegen gerichtete Kanten,
welche die Beziehung zwischen diesen Knoten darstellen. Eine gerichtete Kante von Account A zu Account B bedeutet, dass
A B folgt. Wenn B eine Desinformation teilt, kann A sie erhalten.
Influencer kommen seltener in diesem Netzwerk vor, besitzen aber aufgrund von mehr Followern eine höhere Reichweite.

## Model Assumptions

Das Ziel dieses Projektes ist es nicht, ein reales soziales Netzwerk auf Plattformen wie Instagram im Detail
nachzustellen. Gleiches gilt für die Empfehlungsalgorithmen und Moderationsstrategien. Downranking und Labeling als
Moderationsstrategien werden nur über ihre angenommenen Effekte auf Sichtbarkeit beziehungsweise Teilverhalten
modelliert.

## Installation

Das Projekt benötigt Python 3.12 oder neuer. Die benötigten Dependencies sind in `pyproject.toml` definiert.
Installation der Dependencies mit: `uv sync` (Ausführung im Projektordner).
`uv` muss auf dem System installiert sein.

## CLI Usage

Commands:

- `simulator init <experiment_name>`: Initiiert eine neue Experiment-JSON mit Standardwerten.
- `simulator list`: Listet alle generierten Experimente auf.
- `simulator validate <experiment_name>`: Validiert ein existierendes Experiment auf Basis von Regeln, welche in
  `experiment_schema.py` definiert sind.
- `simulator start <experiment_name>`: Validiert ein Experiment, erstellt Szenarien und simuliert diese. Anschließend
  werden Ergebnisse und Grafiken in `results/` ausgegeben.

## Experiment Files

Experiment-Konfigurationen sind unter `experiments/` gespeichert. Eine Datei `experiments/<experiment_name>.json` wird
mit `simulator start <experiment_name>` simuliert. Bei der Angabe von Parameterwerten gibt es folgende
Regeln:

- Es sind maximal 2 variierende Parameter erlaubt. Einen variierenden Parameter erkennt man daran, dass diesem eine
  Liste von Werten zugewiesen wird.
- Jedem variierenden Parameter dürfen 2 bis 3 Werte zugeordnet werden.

## Simulation Process

Beim Start eines Experimentes wird zuerst die angegebene JSON-Datei aus `experiments/` geladen und mit dem
Pydantic-Schema in `experiment_schema` validiert. Danach erzeugt `scenario_generator` aus allen variierenden Parametern
konkrete Szenarien. Pro Experiment sind bis zu 9 Szenarien möglich. Ein Szenario wird für eine bestimmte Anzahl
wiederholt, um danach Durchschnitte bilden zu können. Für jeden Run wird ein neuer zufälliger Graph erzeugt. Derselbe
Graph und derselbe Startknoten werden innerhalb dieses Runs für alle Szenarien verwendet. Dadurch sind die Szenarien
eines Runs besser vergleichbar. Anschließend wird jedes Szenario simuliert, dabei breitet sich die Desinformation
schrittweise über die Follower-Beziehungen aus. Nach allen Runs werden Mittelwerte und Standardabweichungen berechnet.
Zum Schluss werden CSV-Dateien, eine Kopie der Experiment-Konfiguration und PNG-Diagramme im Ordner `results/`
gespeichert.

## Parameters

- `number_of_nodes`: Anzahl von Knoten im Graphen. [500, 7000].
- `influencer_ratio`: Anteil der Influencer-Knoten an allen Knoten. 0.05 entspricht 5% Influencer.
- `share_probability`: Wahrscheinlichkeit dafür, dass ein Account eine Desinformation teilt.
- `recipient_ratio`: Gibt an, an welchen Anteil von Followern ein Account eine Desinformation sendet, wenn dieser sie
  teilt. 0.3 bedeutet, ein Account teilt mit 30% seiner Follower. `share_probability` entscheidet vorher, ob ein Account
  überhaupt teilt.
- `check_probability`: Wahrscheinlichkeit dafür, dass ein Account eine mögliche Desinformation überprüft und daraufhin
  nicht weiter teilt.
- `moderation.type`: Wahl der Moderationsstrategie:
    - `none`: Keine Moderation.
    - `label`: Ein erreichter Account wird darauf hingewiesen, dass es sich bei dem Post um Desinformation handelt. Wenn
      aktiv, wird `share_probability` eines Knotens um `moderation.label_reduction_factor` reduziert.
    - `downrank`: Bestimmte Accounts bekommen eine Desinformation nicht zu sehen. Im Modell wird dies dadurch
      abstrahiert, dass bei aktiver Moderation `recipient_ratio` eines Knotens um `moderation.downrank_reduction_factor`
      reduziert wird. Dies bewirkt, dass weniger andere Accounts diese Desinformation zu sehen bekommen.
    - `delete`: Wenn aktiv, wird eine Desinformation gelöscht. Die Ausbreitung wird gestoppt.
- `moderation.threshold_activation_ratio`: Moderation wird aktiv, sobald
  `reached_accounts >= number_of_nodes * moderation.threshold_activation_ratio` gilt.
- `runs_per_scenario`: Gibt an, wie oft ein Szenario wiederholt werden soll. [30, 50].
- `max_steps_per_run`: Gibt an, wie viele Schritte in einer Simulation ausgeführt werden, bevor diese beendet wird.
  Vermeidet zu langwierige Simulationen. [30, 100].

Folgende Parameter sind als variierende Parameter erlaubt:

- `share_probability`
- `recipient_ratio`
- `check_probability`
- `moderation.type`
- `moderation.threshold_activation_ratio`
- `moderation.label_reduction_factor`
- `moderation.downrank_reduction_factor`

Alle anderen Parameter sind nicht als variierende Parameter erlaubt, da sie maßgeblich die Struktur des Graphen
beeinflussen und den beschriebenen Ablauf einer Simulation erschweren würden.

## Storage of Results

Results are stored in `results/`. Für jedes simulierte Experiment wird ein Unterordner erstellt, welcher wie folgt
benannt ist: `<experiment_name>__<YYYY-MM-DD>_<HH-MM-SS>`.

In jedem Ordner werden die Ergebnisse gespeichert:

- `00_experiment_config.json`: Kopie der validierten Experiment-Konfiguration.
- `01_scenario_table.csv`: Alle aus dem Experiment generierten Szenarien mit konkreten Parameterwerten.
- `02_simulation_results.csv`: Ergebnisse aller Szenarien und Runs.
- `03_scenario_summaries.csv`: Zusammenfassungen aller Szenarien: Angabe von Durchschnittswerten und
  Standardabweichungen.
- `04_spread_summaries.csv`: Für jedes Szenario und jeden Step wird gespeichert, wie viele Accounts im Durchschnitt bis
  zu diesem Zeitpunkt erreicht wurden.
- `05_reached_accounts.png`: Grafik, welche die durchschnittlich erreichten Accounts pro Szenario darstellt. Zeigt auch
  Fehlerbereiche auf Basis der Standardabweichung von erreichten Accounts an.
- `06_total_shares.png`: Grafik, welche die durchschnittlichen Shares einer Desinformation pro Szenario darstellt. Zeigt
  auch Fehlerbereiche auf Basis der Standardabweichung von Shares an.
- `07_spread_over_steps.png`: Grafik, welche den zeitlichen Verlauf von durchschnittlich erreichten Accounts pro
  Szenario darstellt.

## Example Experiments

Das Projekt enthält sechs vorbereitete Experiment-Konfigurationen:

- `downrank_strength`: Variiert `moderation.threshold_activation_ratio` und `moderation.downrank_reduction_factor`.
  Untersucht, wie stark Downranking die Reichweite reduzieren muss, um die Ausbreitung zu beeinflussen.
- `label_strength`: Variiert `moderation.threshold_activation_ratio` und `moderation.label_reduction_factor`.
  Untersucht, wie stark ein Warnhinweis das Teilverhalten reduzieren muss, um die Ausbreitung zu beeinflussen.
- `moderation_type_and_threshold`: Variiert `moderation.type` und `moderation.threshold_activation_ratio`. Untersucht,
  ob die Art der Moderation oder der Zeitpunkt der Aktivierung stärker beeinflusst, wie weit sich Desinformationen
  verbreiten.
- `moderation_under_high_spread`: Variiert `moderation.type` und `moderation.threshold_activation_ratio` in einem Setup
  mit hoher `share_probability`, hohem `recipient_ratio` und niedriger `check_probability`. Testet Moderationsstrategien
  unter stärkerer Ausbreitungsdynamik.
- `share_and_check`: Variiert `share_probability` und `check_probability`. Untersucht, wie Teilverhalten und
  Prüfverhalten die Ausbreitung von Desinformationen ohne aktive Moderation beeinflussen.
- `share_and_recipient_ratio`: Variiert `share_probability` und `recipient_ratio`. Untersucht, ob die Ausbreitung
  stärker durch die Wahrscheinlichkeit des Teilens oder durch den Anteil erreichter Follower beim Teilen beeinflusst
  wird.

## Example Experiments - Main Findings/Results

- Eine hohe `check_probability` kann die Ausbreitung bremsen. Besonders bei niedriger und mittlerer
  Teilwahrscheinlichkeit ist dieser Effekt sichtbar. Bei sehr hoher Teilwahrscheinlichkeit reicht Prüfverhalten allein
  jedoch nicht immer aus, um große Reichweite zu verhindern.
- `label` reduziert vor allem das Weiterteilen. Da die Desinformation weiterhin sichtbar bleibt, sinkt die Anzahl der
  Shares stärker als die erreichte Reichweite. Weniger Shares bedeuten nicht automatisch, dass weniger Accounts mit der
  Desinformation in Kontakt kommen.
- Frühe Moderation wirkt stärker als spätere, insbesondere wenn die Maßnahmen stark genug sind. Bei schwachen Labels
  oder schwachem Downranking ist der Unterschied zwischen früher/später Aktivierung teilweise klein. Wenn eine
  Moderationsstrategie erst nach hoher Verbreitung aktiviert wird, hat die Desinformation bereits viele Accounts
  erreicht.
- Ob eine Moderationsmaßnahme als wirksam bewertet wird, hängt von der gewählten Messgröße ab. Eine Maßnahme kann die
  Anzahl der Shares deutlich reduzieren, ohne die erreichte Reichweite gleichermaßen zu senken.
- Hohe Standardabweichungen zeigen, dass zufällige Netzwerkstruktur und Startknoten (Influencer oder normaler User)
  einen großen Einfluss auf einzelne Runs haben.

