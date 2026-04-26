# Data collection notes (Division 3 Örebro/Västmanland)

## Source links
- Primary standings URL: `https://stats.innebandy.se/sasong/43/serie/41160/serietabell`
- Legacy mirror listing for this series id: `https://statistik.innebandy.se/ft.aspx?ftid=41160&scr=table`

## Current state in this iteration
- Added full **team dataset** in `data/div3_orebro_vastmanland_teams.csv`.
- Added full **player roster dataset** in `data/div3_orebro_vastmanland_players.csv`.
- Added renamed team and player assets in `teams/` and `players/`.
- Tobias Bäckström is set to maxed attributes (`overall=99`, `potential=99`) as requested.

## Sync/build workflow
1. Run `python mod-div3-askersund/scripts/sync_series_from_stats.py` to refresh teams/players from the Stats API and regenerate renamed assets from `template-mod-ssl`.
2. Run `python mod-div3-askersund/scripts/build_mod_scaffold.py`.
3. Convert `build/mod_manifest.json` into game-native `.teams` and `.players` binary assets.
