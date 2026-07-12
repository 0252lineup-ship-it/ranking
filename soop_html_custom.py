import json
import html
import webbrowser
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

API_URL = "https://live.sooplive.com/api/challenge_funding_api.php"
RESULT_FILE = Path(__file__).resolve().parent / "result.txt"
HTML_FILE = Path(__file__).resolve().parent / "result.html"

GUILDS = {
    "태산": [
        ("킴성태", "rrvv17"), ("라로시", "larothy"), ("태민98", "damin0714"),
        ("클로이", "vf3366"), ("나나문", "nanamoon777"), ("채윤아", "yuna812"),
        ("깐숙", "nangnan"), ("견자희", "gyeonjahee"), ("백청미", "wtcheongmi"),
        ("하루아이", "loveya4860"), ("김뱅글", "happyness192"), ("김진아", "ase7129"),
    ],
    "만월": [
        ("강만식", "rkdakstlr911"), ("마왕루야", "maoruyakr"), ("떵규", "sunglim001"),
        ("깡담비", "cjstkdbsl3"), ("베베리", "hye11u"), ("김세노", "os3n0o"),
        ("뽀린걸", "bboringirl"), ("소유나", "kyoonah1217"), ("리브레", "libre1900"),
        ("프하", "peuhaha"), ("물초코", "moolchoco"), ("민서먕", "325959"),
    ],
    "아랑": [
        ("오아", "legendhyuk"), ("모요", "duvl123"), ("진호", "jangjh5409"),
        ("쨈도은", "odoeun"), ("피치", "nslah830"), ("루디딕", "mnomno55"),
        ("설빈달", "nsnowthemoon"), ("너보링", "hibby1004"), ("유키", "amaiyk0105"),
        ("호미밍", "donggeul2"), ("키이세", "0e0e4e"), ("나비", "navixx"),
    ],
    "천박": [
        ("박사장", "wnstn0905"), ("쥐돌이", "aa6232"), ("진성준", "m2stic"),
        ("해이", "kjkj4424"), ("백도아", "heeeejyu"), ("땡지", "yyk3390"),
        ("나옹이빵", "naong2bbang"), ("꼼모리", "et0726"), ("니니밍", "niniming"),
        ("마리별", "maribyeol"), ("묭씨", "secymyong"), ("이릴", "irrilll"),
    ],
    "도황": [
        ("도현", "dobby1031"), ("최은뽀", "eunpp0"), ("김규태", "gyutae1638"),
        ("요요에요", "wooldi"), ("김마렌", "kimmaren77"), ("졔리", "0jjerry0"),
        ("투냥츠", "toocats"), ("잼율이", "jamyul2"), ("킴아연", "gptn1109"),
        ("비비", "gamer5g5"), ("차투리", "hololoolu"), ("체비", "chebi2"),
    ],
    "하북펭가": [
        ("수피", "lovely5959"), ("김동하", "gkdlqk13"), ("눈길", "qksdy147"),
        ("한아밍", "kim91709"), ("먼지뭉탱이", "monmoong"), ("묵아", "nororo"),
        ("히뚜", "rud21458"), ("르미루", "rmrss2"), ("또니", "tjsgml899"),
        ("찌미♥", "zzimio3o"), ("두부랑", "dubulang0901"), ("슨미", "jjgod9312"),
    ],
}

REQUEST_STATUSES = ["REQUEST", "PROGRESS", "SUCCESS", "FAIL", "CANCEL"]


def fetch_challenges(session: requests.Session, bj_id: str) -> list[dict]:
    response = session.post(
        API_URL,
        data={
            "szWork": "getChallengeFunding",
            "szBjId": bj_id,
            "szStatus": json.dumps(REQUEST_STATUSES, ensure_ascii=False),
        },
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("result") != 1:
        raise RuntimeError(payload.get("msg") or "SOOP API 응답 오류")
    return payload.get("data") or []


def format_result(rows: list[dict], guild_totals: dict[str, int]) -> str:
    lines = []
    lines.append("[길드별 총합 도시락 랭킹]")
    lines.append("")
    sorted_guilds = sorted(guild_totals.items(), key=lambda item: item[1], reverse=True)
    total_all = sum(guild_totals.values())

    lines.append(f"전체 도시락 합계 : {total_all:,}개")
    lines.append("")

    leader_total = sorted_guilds[0][1] if sorted_guilds else 0

    for rank, (guild, total) in enumerate(sorted_guilds, 1):
        if rank == 1:
            lines.append(f"{rank}위. {guild} : {total:,}개")
        else:
            lines.append(f"{rank}위. {guild} : {total:,}개")


    lines.append("")
    lines.append("")
    lines.append("[각 길드별 상세 도시락 랭킹]")

    for guild in GUILDS:
        lines.append("")
        lines.append("")
        lines.append(f"[{guild}]")
        lines.append("")
        guild_rows = sorted(
            [row for row in rows if row["guild"] == guild],
            key=lambda row: row["stars"],
            reverse=True,
        )
        for rank, row in enumerate(guild_rows, 1):
            lines.append(f'{rank}. {row["nick"]} / {row["stars"]:,}개')

    lines.append("")
    lines.append("")
    # =========================
    # 전체 랭킹 TOP 20
    # =========================
    lines.append("[전체 랭킹 TOP 20]")
    lines.append("")

    top20 = sorted(rows, key=lambda x: x["stars"], reverse=True)[:20]
    for i, row in enumerate(top20, 1):
        lines.append(f"{i}. {row['nick']} / {row['stars']:,}개 / {row['guild']}")

    lines.append("")
    lines.append("")
    lines.append("[전체 랭킹 (닉네임 / 개수 / 길드)]")
    lines.append("")
    for row in sorted(rows, key=lambda row: row["stars"], reverse=True):
        lines.append(
            f'{row["nick"]} / {row["stars"]:,}개 / {row["guild"]}'
        )


    return "\n".join(lines).rstrip() + "\n"



def format_html(rows: list[dict], guild_totals: dict[str, int]) -> str:
    kst = timezone(timedelta(hours=9))
    updated_at = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')
    sorted_guilds = sorted(guild_totals.items(), key=lambda x: x[1], reverse=True)
    total_all = sum(guild_totals.values())
    max_total = sorted_guilds[0][1] if sorted_guilds else 1

    colors = {
        "태산": "#ef4444",
        "만월": "#a855f7",
        "아랑": "#facc15",
        "천박": "#38bdf8",
        "도황": "#f472b6",
        "하북펭가": "#3b82f6",
    }

    guild_cards = []
    for rank, (guild, total) in enumerate(sorted_guilds, 1):
        width = total / max_total * 100 if max_total else 0
        guild_cards.append(f"""
        <div class="guild-card" style="--c:{colors[guild]}">
            <div class="rank">{rank}위</div>
            <img src="logos/{guild}.png" alt="{guild}" onerror="this.style.display='none'">
            <div class="guild">{guild}</div>
            <div class="count">{total:,}개</div>
            <div class="bar"><span style="width:{width:.1f}%"></span></div>
        </div>
        """)

    detail_cards = []
    for guild in GUILDS:
        guild_total = guild_totals[guild]
        guild_rows = sorted(
            [r for r in rows if r["guild"] == guild],
            key=lambda r: r["stars"],
            reverse=True,
        )
        member_rows = []
        for rank, row in enumerate(guild_rows, 1):
            member_rows.append(
                f'<div class="member"><span>{rank}</span><b>{html.escape(row["nick"])}</b>'
                f'<em>{row["stars"]:,}개</em></div>'
            )
        detail_cards.append(f"""
        <section class="detail" style="--c:{colors[guild]}">
            <header><img src="logos/{guild}.png" alt="{guild}" onerror="this.style.display='none'"><h2>{guild}</h2></header>
            {''.join(member_rows)}
            <footer>길드 합계 {guild_total:,}개</footer>
        </section>
        """)

    top20 = sorted(rows, key=lambda r: r["stars"], reverse=True)[:20]

    def ranking_block(items):
        parts = []
        for i, row in enumerate(items, 1):
            parts.append(
                f'<div class="ranking-row"><span>{i}</span><b>{html.escape(row["nick"])}</b>'
                f'<small>{row["guild"]}</small><em>{row["stars"]:,}개</em></div>'
            )
        return "".join(parts)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="300">
<title>총겜동 내수서버 도시락 현황</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#080b12;color:#f8fafc;font-family:"Malgun Gothic",sans-serif}}
.wrap{{width:min(1500px,96%);margin:auto;padding:32px 0 70px}}
.title-row{{display:flex;align-items:center;justify-content:center;gap:14px;margin-bottom:24px}}
.title-row img{{width:86px;height:auto;object-fit:contain}}
h1{{text-align:center;font-size:42px;margin:0}}
.update-time{{text-align:center;color:#94a3b8;font-size:14px;margin:-12px 0 24px}}
.total{{text-align:center;padding:24px;border:1px solid #7c3aed;border-radius:18px;background:#111827;margin-bottom:24px}}
.total span{{display:block;color:#c4b5fd}}
.total strong{{font-size:48px;color:#c084fc}}
.guild-grid{{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;margin-bottom:24px}}
.guild-card{{padding:18px;border:1px solid #273041;border-radius:16px;background:#111827;text-align:center}}
.guild-card .rank,.guild-card .count{{color:var(--c);font-weight:800}}
.guild-card img{{width:76px;height:76px;object-fit:contain;margin:10px 0}}
.guild-card .guild{{font-size:22px;font-weight:800}}
.guild-card .count{{font-size:21px;margin-top:6px}}
.bar{{height:8px;background:#293241;border-radius:99px;overflow:hidden;margin-top:14px}}
.bar span{{display:block;height:100%;background:var(--c)}}
.diff{{font-size:12px;color:#94a3b8;margin-top:8px}}
.main{{display:grid;grid-template-columns:2fr 1fr;gap:18px}}
.details{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.detail,.rank-card{{background:#111827;border:1px solid #273041;border-radius:16px;overflow:hidden}}
.detail header{{display:flex;align-items:center;justify-content:center;gap:10px;padding:12px;border-bottom:1px solid #273041}}
.detail header img{{width:44px;height:44px;object-fit:contain}}
.detail h2{{color:var(--c);margin:0}}
.member{{display:grid;grid-template-columns:24px 1fr auto;gap:8px;padding:9px 12px;border-bottom:1px solid #1f2937}}
.member span{{color:var(--c);font-weight:700}}
.member em,.ranking-row em{{font-style:normal;font-weight:800}}
.detail footer{{padding:12px;text-align:center;color:var(--c);font-weight:800}}
.rank-card h2 h2{{margin:0;padding:15px;border-bottom:1px solid #273041}}
.ranking-row{{display:grid;grid-template-columns:28px 1fr 70px auto;gap:8px;padding:10px 12px;border-bottom:1px solid #1f2937}}
.ranking-row span{{color:#fbbf24;font-weight:800}}
.ranking-row small{{color:#94a3b8}}
.ranking-row em{{color:#fde68a}}
.side{{display:grid;gap:16px}}
summary strong{{color:#fbbf24}}
@media(max-width:1200px){{.guild-grid{{grid-template-columns:repeat(3,1fr)}}.main{{grid-template-columns:1fr}}}}
@media(max-width:800px){{.details{{grid-template-columns:1fr}}.mission-grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="wrap">
<div class="title-row"><img src="총겜동.png" alt="총겜동 로고" onerror="this.style.display='none'"><h1>총겜동 내수서버 도시락 현황</h1></div>
<div class="update-time">마지막 업데이트: {updated_at} (KST) · 5분마다 자동 새로고침</div>
<section class="total"><span>전체 도시락 합계</span><strong>{total_all:,}개</strong></section>
<section class="guild-grid">{''.join(guild_cards)}</section>
<section class="main">
<div class="details">{''.join(detail_cards)}</div>
<div class="side">
<section class="rank-card"><h2>전체 랭킹 TOP 20</h2>{ranking_block(top20)}</section>
</div>
</section>
</div>
</body>
</html>"""

def main() -> None:
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/149.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://play.sooplive.com/",
        "Origin": "https://play.sooplive.com",
    })

    rows = []
    guild_totals = {guild: 0 for guild in GUILDS}
    total_members = sum(len(members) for members in GUILDS.values())
    checked = 0

    for guild, members in GUILDS.items():
        for nick, bj_id in members:
            checked += 1
            print(f"[{checked:02d}/{total_members}] {guild} / {nick} 조회 중...")
            try:
                challenges = fetch_challenges(session, bj_id)
            except Exception as error:
                print(f"  오류: {error}")
                challenges = []

            progress_missions = []
            total_stars = 0
            for item in challenges:
                if item.get("status") != "PROGRESS":
                    continue
                balloon_cnt = int(item.get("balloon_cnt") or 0)
                total_stars += balloon_cnt
                progress_missions.append({
                    "idx": str(item.get("idx", "")),
                    "title": str(item.get("title", "")),
                    "balloon_cnt": balloon_cnt,
                    "expire_date": str(item.get("expire_date", "")),
                    "remain_time": int(item.get("remain_time") or 0),
                })

            guild_totals[guild] += total_stars
            rows.append({
                "guild": guild,
                "nick": nick,
                "bj_id": bj_id,
                "stars": total_stars,
                "missions": progress_missions,
            })
            print(f"  PROGRESS {len(progress_missions)}개 / {total_stars:,}개")

    result_text = format_result(rows, guild_totals)
    RESULT_FILE.write_text(result_text, encoding="utf-8")

    html_text = format_html(rows, guild_totals)
    HTML_FILE.write_text(html_text, encoding="utf-8")

    print()
    print("=" * 60)
    print("집계 완료")
    print(f"TXT 결과 파일: {RESULT_FILE}")
    print(f"HTML 결과 파일: {HTML_FILE}")
    webbrowser.open(HTML_FILE.as_uri())
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n사용자가 중단했습니다.")
    except requests.RequestException as error:
        print(f"\n네트워크 오류: {error}")
    except Exception as error:
        print(f"\n실행 오류: {error}")
