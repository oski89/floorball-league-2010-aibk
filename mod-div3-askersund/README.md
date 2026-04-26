# Division 3 mod scaffold (full series batch)

This folder contains a complete series batch for season 43 / competition 41160,
built in the same style as `template-mod-ssl`.

## Included now
- Full team dataset for all teams in the series (`data/div3_orebro_vastmanland_teams.csv`).
- Full player roster dataset for all teams (`data/div3_orebro_vastmanland_players.csv`).
- Renamed team assets for each team (`teams/*.png`), sourced from `template-mod-ssl`.
- Renamed player portraits for each rostered player (`players/*.png`), sourced from `template-mod-ssl`.
- Tobias Bäckström preserved with custom correct portrait and maxed attributes (`overall=99`, `potential=99`).
- Scripts for syncing and manifest generation:
  - `scripts/sync_series_from_stats.py`
  - `scripts/build_mod_scaffold.py`

## Sync from stats API
```bash
python mod-div3-askersund/scripts/sync_series_from_stats.py
```

This refreshes teams, players, and renamed assets from:
- `https://stats.innebandy.se/sasong/43/serie/41160/serietabell`

## Build
```bash
python mod-div3-askersund/scripts/build_mod_scaffold.py
```

Output:
- `mod-div3-askersund/build/mod_manifest.json`

## Notes
- This iteration is intentionally compatible with your `template-mod-ssl` style and naming.
- The final game-native binary files (`.teams`, `.players`, `.league`) still need conversion tooling or in-game editor export.
