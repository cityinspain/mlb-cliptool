import datetime
import requests

API_URL = "https://fastball-gateway.mlb.com/graphql?operationName=Search"

BASE_QUERY_VARS = {
    "limit": 100,
    "page": 0,
    "languagePreference": "EN",
    "contentPreference": "CMS_FIRST",
}

QUERY_BODY = """
query Search(
  $query: String!
  $page: Int
  $limit: Int
  $feedPreference: FeedPreference
  $languagePreference: LanguagePreference
  $contentPreference: ContentPreference
  $queryType: QueryType = STRUCTURED
) {
  search(
    query: $query
    limit: $limit
    page: $page
    feedPreference: $feedPreference
    languagePreference: $languagePreference
    contentPreference: $contentPreference
    queryType: $queryType
  ) {
    plays {
      gameDate
      gamePk
      mediaPlayback {
        slug
        feeds {
          duration
          playbacks {
            url
            __typename
          }
          __typename
        }
        __typename
      }
      __typename
    }
    total
    __typename
  }
}
"""


def create_film_query(
    batter_id=None,
    pitcher_id=None,
    player_id=None,
    hit_result=None,
    season=None,
    start_date=None,
    end_date=None,
    limit=100,
    page=0
):
    query_vars = BASE_QUERY_VARS.copy()

    if limit:
        query_vars["limit"] = limit
    if page:
        query_vars["page"] = page

    criteria = []
    if batter_id:
        criteria.append(f"BatterId = [{batter_id}]")
    if pitcher_id:
        criteria.append(f"PitcherId = [{pitcher_id}]")
    if player_id:
        criteria.append(f"PlayerId = [{player_id}]")
    if hit_result:
        criteria.append(f"HitResult = [\"{hit_result}\"]")
    if start_date:
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        criteria.append(f'Date = {{{{\"{start_date}\", \"{end_date}\"}}}}')
    if end_date:
        if not start_date:
            start_date = "1900-01-01"
            # only do the append again if we didn't already do it above
            criteria.append(f'Date = {{{{\"{start_date}\", \"{end_date}\"}}}}')
    if season:
        criteria.append(f"Season = [{season}]")

    query_vars["query"] = " AND ".join(criteria)

    return query_vars


def get_clips(
    batter_id=None,
    pitcher_id=None,
    player_id=None,
    hit_result=None,
    season=None,
    start_date=None,
    end_date=None,
    limit=100,
    page=0
):
    query_vars = create_film_query(
        batter_id, pitcher_id, player_id, hit_result, season, start_date, end_date, limit, page)

    r = requests.post(
        API_URL, json={"query": QUERY_BODY, "variables": query_vars})
    res = r.json()
    return res['data']['search']['plays']
