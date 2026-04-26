#!/usr/bin/env python3
"""Sync Division 3 teams/players from stats.innebandy.se and local template assets.

This script:
1. Pulls standings + full team rosters for season 43 / competition 41160.
2. Copies/renames team assets from template-mod-ssl into this mod package.
3. Copies/renames player portraits from template-mod-ssl (keeps Tobias custom portrait).
4. Writes full team/player CSV datasets used by build_mod_scaffold.py.
"""

from __future__ import annotations

import csv
import re
import shutil
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import requests

SEASON_ID = 43
COMPETITION_ID = 41160

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
TEMPLATE_ROOT = REPO_ROOT / "template-mod-ssl"
TEMPLATE_PLAYERS_DIR = TEMPLATE_ROOT / "players"
TEMPLATE_TEAMS_DIR = TEMPLATE_ROOT / "teams"

DATA_DIR = ROOT / "data"
PLAYERS_DIR = ROOT / "players"
TEAMS_DIR = ROOT / "teams"

TEAMS_CSV = DATA_DIR / "div3_orebro_vastmanland_teams.csv"
PLAYERS_CSV = DATA_DIR / "div3_orebro_vastmanland_players.csv"

# Stable short team codes used in portrait file names.
TEAM_CODE_OVERRIDES: dict[int, str] = {
    117042: "ASK",
    9128: "GRO",
    8321: "IBF",
    2958: "KUN",
    118252: "RBV",
    21617: "OSK",
    117018: "KOP",
    117040: "EKE",
    124610: "RAM",
    17749: "SAL",
    22200: "RAB",
    122855: "RAN",
}

TEAM_BUNDLES = [
    "AIK",
    "Jonkoping",
    "Kalmarsund",
    "Linkoping",
    "Strangnas",
    "Vaxjo",
    "Visby",
]

TEAM_ASSET_FIELDS = [
    "team_logo",
    "field_asset",
    "rink_ads_asset",
    "side_ads_asset",
    "jersey_home",
    "jersey_away",
    "shorts_home",
    "shorts_away",
    "socks_home",
    "socks_away",
]

PRESERVE_TEAM_ASSETS = {
    "TeamLogoAskersundIBK.png",
    "FieldAskersund.png",
    "RinkAdsAskersund.png",
    "SideAdsAskersund.png",
    "PlayerJerseyAskersundHome.png",
    "PlayerJerseyAskersundAway.png",
    "PlayerShortsAskersundHome.png",
    "PlayerShortsAskersundAway.png",
    "PlayerSocksAskersundHome.png",
    "PlayerSocksAskersundAway.png",
}


@dataclass
class ApiContext:
    api_root: str
    token: str


def slug_ascii(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    chunks = re.findall(r"[A-Za-z0-9]+", ascii_text)
    return "".join(chunks)


def split_name(full_name: str) -> tuple[str, str]:
    chunks = full_name.strip().split()
    if not chunks:
        return "Unknown", "Player"
    if len(chunks) == 1:
        return chunks[0], ""
    return chunks[0], " ".join(chunks[1:])


def derive_city(team_name: str) -> str:
    patterns = [
        "Askersund",
        "Gropen",
        "Örebro",
        "Kungsör",
        "Västerås",
        "Köping",
        "Ekeby",
        "Ramnäs",
        "Sala",
        "Ransta",
    ]
    for token in patterns:
        if token in team_name:
            return token
    return ""


def map_position(position_text: str) -> str:
    text = (position_text or "").strip().lower()
    if "m" in text and ("lvakt" in text or "goal" in text):
        return "G"
    if "goal" in text:
        return "G"
    if "back" in text or "def" in text:
        return "D"
    if "center" in text or text == "c":
        return "C"
    return "F"


def player_rating(player: dict[str, object]) -> tuple[int, int]:
    matches = int(player.get("Matches") or 0)
    points = int(player.get("Points") or 0)
    goals = int(player.get("Goals") or 0)
    assists = int(player.get("Assists") or 0)
    baseline = 58 + matches * 0.12 + points * 0.30 + goals * 0.08 + assists * 0.04
    overall = int(round(max(55, min(90, baseline))))
    potential = int(min(95, overall + 6))
    return overall, potential


def fetch_api_context() -> ApiContext:
    startkit = requests.get(
        "https://api.innebandy.se/StatsAppApi/api/startkit", timeout=30
    ).json()
    return ApiContext(
        api_root=startkit["apiRoot"].rstrip("/") + "/",
        token=startkit["accessToken"],
    )


def api_get(ctx: ApiContext, path: str) -> dict:
    headers = {"Authorization": f"Bearer {ctx.token}"}
    url = f"{ctx.api_root}{path.lstrip('/')}"
    return requests.get(url, headers=headers, timeout=30).json()


def pick_logo(bundle: str) -> Path:
    modern = TEMPLATE_TEAMS_DIR / f"TeamLogo{bundle}_new.png"
    legacy = TEMPLATE_TEAMS_DIR / f"TeamLogo{bundle}.png"
    if modern.exists():
        return modern
    if legacy.exists():
        return legacy
    raise FileNotFoundError(f"No logo file for team bundle: {bundle}")


def copy_team_assets(bundle: str, asset_slug: str) -> dict[str, str]:
    sources = {
        "team_logo": pick_logo(bundle),
        "field_asset": TEMPLATE_TEAMS_DIR / f"Field{bundle}.png",
        "rink_ads_asset": TEMPLATE_TEAMS_DIR / f"RinkAds{bundle}.png",
        "side_ads_asset": TEMPLATE_TEAMS_DIR / f"SideAds{bundle}.png",
        "jersey_home": TEMPLATE_TEAMS_DIR / f"PlayerJersey{bundle}Home.png",
        "jersey_away": TEMPLATE_TEAMS_DIR / f"PlayerJersey{bundle}Away.png",
        "shorts_home": TEMPLATE_TEAMS_DIR / f"PlayerShorts{bundle}Home.png",
        "shorts_away": TEMPLATE_TEAMS_DIR / f"PlayerShorts{bundle}Away.png",
        "socks_home": TEMPLATE_TEAMS_DIR / f"PlayerSocks{bundle}Home.png",
        "socks_away": TEMPLATE_TEAMS_DIR / f"PlayerSocks{bundle}Away.png",
    }
    for key, source in sources.items():
        if not source.exists():
            raise FileNotFoundError(f"Missing source for {key}: {source}")

    targets = {
        "team_logo": f"TeamLogo{asset_slug}.png",
        "field_asset": f"Field{asset_slug}.png",
        "rink_ads_asset": f"RinkAds{asset_slug}.png",
        "side_ads_asset": f"SideAds{asset_slug}.png",
        "jersey_home": f"PlayerJersey{asset_slug}Home.png",
        "jersey_away": f"PlayerJersey{asset_slug}Away.png",
        "shorts_home": f"PlayerShorts{asset_slug}Home.png",
        "shorts_away": f"PlayerShorts{asset_slug}Away.png",
        "socks_home": f"PlayerSocks{asset_slug}Home.png",
        "socks_away": f"PlayerSocks{asset_slug}Away.png",
    }
    for key, target_name in targets.items():
        shutil.copy2(sources[key], TEAMS_DIR / target_name)
    return targets


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    PLAYERS_DIR.mkdir(parents=True, exist_ok=True)
    TEAMS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Keep Tobias custom portrait, replace all other generated portraits.
    for file in PLAYERS_DIR.glob("*.png"):
        if file.name != "ASK_TobiasBackstrom.png":
            file.unlink()
    for file in TEAMS_DIR.glob("*.png"):
        if file.name not in PRESERVE_TEAM_ASSETS:
            file.unlink()

    ctx = fetch_api_context()
    standings = api_get(ctx, f"competitions/{COMPETITION_ID}/standings")["StandingsRows"]

    teams_rows: list[dict[str, object]] = []
    players_rows: list[dict[str, object]] = []

    template_portraits = sorted(TEMPLATE_PLAYERS_DIR.glob("*.png"))
    if not template_portraits:
        raise FileNotFoundError("No portraits found in template-mod-ssl/players")
    portrait_idx = 0

    bundle_idx = 0
    used_portrait_names: set[str] = set()

    for standing_row in standings:
        team_id = int(standing_row["TeamID"])
        team_name = str(standing_row["TeamName"])
        team_short_name = str(standing_row.get("TeamShortName") or "")
        team_status_id = int(standing_row.get("TeamStatusID") or 0)
        team_status_name = str(standing_row.get("TeamStatusName") or "")

        team = api_get(ctx, f"seasons/{SEASON_ID}/teams/{team_id}")
        association_name = str(team.get("AssociationName") or "")
        city = derive_city(team_name)

        team_code = TEAM_CODE_OVERRIDES.get(team_id, slug_ascii(team_name).upper()[:3] or "TMX")

        if team_id == 117042:
            asset_slug = "Askersund"
            team_assets = {
                "team_logo": "TeamLogoAskersundIBK.png",
                "field_asset": "FieldAskersund.png",
                "rink_ads_asset": "RinkAdsAskersund.png",
                "side_ads_asset": "SideAdsAskersund.png",
                "jersey_home": "PlayerJerseyAskersundHome.png",
                "jersey_away": "PlayerJerseyAskersundAway.png",
                "shorts_home": "PlayerShortsAskersundHome.png",
                "shorts_away": "PlayerShortsAskersundAway.png",
                "socks_home": "PlayerSocksAskersundHome.png",
                "socks_away": "PlayerSocksAskersundAway.png",
            }
        else:
            cleaned_name = team_name.replace(" H3", "").strip()
            asset_slug = slug_ascii(cleaned_name) or f"Team{team_id}"
            bundle = TEAM_BUNDLES[bundle_idx % len(TEAM_BUNDLES)]
            bundle_idx += 1
            team_assets = copy_team_assets(bundle=bundle, asset_slug=asset_slug)

        source_status = "confirmed"
        if team_status_id == 5:
            source_status = "withdrawn"

        team_row = {
            "team_id": team_id,
            "team_name": team_name,
            "short_code": team_code,
            "short_name": team_short_name,
            "city": city,
            "association_name": association_name,
            "status_id": team_status_id,
            "status_name": team_status_name,
            "asset_slug": asset_slug,
            **team_assets,
            "source_status": source_status,
        }
        teams_rows.append(team_row)

        team_players = sorted(team.get("Players") or [], key=lambda p: str(p.get("Name") or ""))
        for player in team_players:
            player_id = int(player.get("PlayerID") or 0)
            person_id = int(player.get("PersonID") or 0)
            full_name = str(player.get("Name") or "").strip()
            first_name, last_name = split_name(full_name)
            ascii_name = slug_ascii(full_name) or f"Player{player_id}"
            portrait_name = f"{team_code}_{ascii_name}.png"

            if portrait_name in used_portrait_names:
                portrait_name = f"{team_code}_{ascii_name}_{player_id}.png"
            used_portrait_names.add(portrait_name)

            if player_id == 286723 and team_id == 117042:
                portrait_name = "ASK_TobiasBackstrom.png"
                overall, potential = 99, 99
                notes = "priority player maxed per request"
            else:
                portrait_src = template_portraits[portrait_idx % len(template_portraits)]
                portrait_idx += 1
                shutil.copy2(portrait_src, PLAYERS_DIR / portrait_name)
                overall, potential = player_rating(player)
                notes = f"portrait from template-mod-ssl/{portrait_src.name}"

            jersey = player.get("ShirtNo")
            position = map_position(str(player.get("Position") or ""))

            player_row = {
                "team_id": team_id,
                "team_code": team_code,
                "team_name": team_name,
                "player_id": player_id,
                "person_id": person_id,
                "first_name": first_name,
                "last_name": last_name,
                "full_name": full_name,
                "position": position,
                "jersey_no": "" if jersey is None else jersey,
                "overall": overall,
                "potential": potential,
                "portrait_file": portrait_name,
                "stats_position": str(player.get("Position") or ""),
                "matches": int(player.get("Matches") or 0),
                "goals": int(player.get("Goals") or 0),
                "assists": int(player.get("Assists") or 0),
                "points": int(player.get("Points") or 0),
                "penalty_minutes": int(player.get("PenaltyMinutes") or 0),
                "source_image_url": str(player.get("ImageUrl") or ""),
                "notes": notes,
            }
            players_rows.append(player_row)

    write_csv(TEAMS_CSV, teams_rows)
    write_csv(PLAYERS_CSV, players_rows)

    print(f"Wrote {TEAMS_CSV} ({len(teams_rows)} teams)")
    print(f"Wrote {PLAYERS_CSV} ({len(players_rows)} players)")
    print(f"Portrait assets in mod: {len(list(PLAYERS_DIR.glob('*.png')))}")
    print(f"Team assets in mod: {len(list(TEAMS_DIR.glob('*.png')))}")


if __name__ == "__main__":
    main()
