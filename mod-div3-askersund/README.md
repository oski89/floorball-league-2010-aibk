# Division 3 mod scaffold (Askersunds IBK focus)

This folder contains the first complete mod iteration scaffold based on your template mod structure.

## Included now
- Team asset pack for Askersunds IBK naming convention (`teams/*.png`).
- Priority portrait for Tobias Bäckström (`players/ASK_TobiasBackstrom.png`).
- Team list dataset for Division 3 Örebro/Västmanland (`data/div3_orebro_vastmanland_teams.csv`).
- Askersund player dataset starter with Tobias maxed (`data/askersund_h3_players.csv`).
- Build script generating a machine-readable manifest (`scripts/build_mod_scaffold.py`).

## Build
```bash
python mod-div3-askersund/scripts/build_mod_scaffold.py
```

Output:
- `mod-div3-askersund/build/mod_manifest.json`

## Notes
- This iteration is intentionally compatible with your `template-mod-ssl` style and naming.
- The final game-native binary files (`.teams`, `.players`, `.league`) still need conversion tooling or in-game editor export.
