# Data collection notes (Division 3 Örebro/Västmanland)

## Source links
- Primary standings URL: `https://stats.innebandy.se/sasong/43/serie/41160/serietabell`
- Legacy mirror listing for this series id: `https://statistik.innebandy.se/ft.aspx?ftid=41160&scr=table`

## Current state in this iteration
- Added full **team scaffold** for the division in `data/div3_orebro_vastmanland_teams.csv`.
- Started **player database** with priority player Tobias Bäckström in `data/askersund_h3_players.csv`.
- Tobias Bäckström is set to maxed attributes (`overall=99`, `potential=99`) as requested.

## Next-step import process
1. Open each team page from iBIS and export/collect full roster.
2. Save one CSV per team under `data/teams/`.
3. Add portrait filenames under `players/` for each player.
4. Run `python mod-div3-askersund/scripts/build_mod_scaffold.py`.
5. Convert `build/mod_manifest.json` into game-native `.teams` and `.players` binary assets.
