
import pandas as pd
import math

def load_data():
    """TSV 파일을 읽어서 DataFrame으로 반환합니다."""

    # 주차,라운드,레드,블루,옐로
    # on_bad_lines='skip'을 사용하여 오류가 있는 라인을 건너뛰거나, quoting을 조절합니다.
    df_match = pd.read_csv('match_result_sample.tsv', sep='\t', on_bad_lines='warn')
    
    # 팀이름,선수이름,1주차,2주차,3주차
    df_att = pd.read_csv('attendance_sample.tsv', sep='\t', on_bad_lines='warn')
    
    return df_match, df_att

def count_goals(scorer_str):
    """
    쉼표로 구분된 득점자 문자열에서 골 수를 계산합니다.
    - '0'은 0골
    - 빈 값(NaN)은 None (경기 불참)
    - '자살골'은 팀 득점에는 포함되지만 개인 득점 집계시 별도 처리가 필요할 수 있음
       (여기서는 단순 골 수 카운트용)
    """
    if pd.isna(scorer_str) or scorer_str == '' or str(scorer_str).strip() == '':
        return None  # Participating check is important
    
    scorer_str = str(scorer_str).strip()
    if scorer_str == '0':
        return 0
    
    # 쉼표로 분리하여 카운트
    scorers = [s.strip() for s in scorer_str.split(',')]
    # 빈 문자열 제거
    scorers = [s for s in scorers if s]
    return len(scorers)

def get_scorers_list(scorer_str):
    """득점자 리스트를 반환합니다. (자살골 제외)"""
    if pd.isna(scorer_str) or scorer_str == '0':
        return []
    
    scorers = [s.strip() for s in str(scorer_str).split(',')]
    # 자살골 제외
    return [s for s in scorers if s and '자살골' not in s]

def process_match_results(df_match):
    """경기 결과를 분석하여 팀 및 선수 통계를 생성합니다."""
    
    # 팀 통계 초기화
    teams = ['레드', '블루', '옐로']
    team_stats = {t: {'Points': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'Played': 0, 'Be_Played':0} for t in teams}
    # 주차별 팀 승점 기록 (트렌드 분석용) -> {Team: {Week: CumulativePoints}}
    # 좀 더 쉽게 -> List of dicts: [{'Week': 1, 'Team': 'Red', 'Points': 3}, ...]
    history_records = []
    
    # 선수 통계 초기화: {PlayerName: {'Goals': 0, 'Team': ''}} (플레이어 팀은 나중에 매핑)
    player_stats = {}

    # 라운드별 처리
    for idx, row in df_match.iterrows():
        week = row['주차']
        scores = {}
        participating_teams = []
        
        # 1. 각 팀의 득점 파싱
        for team in teams:
            val = row[team]
            goals = count_goals(val)
            if goals is not None:
                scores[team] = goals
                participating_teams.append(team)
                
                # 팀 득점 누적
                team_stats[team]['GF'] += goals
                
                # 선수 득점 누적
                p_list = get_scorers_list(val)
                for p in p_list:
                    if p not in player_stats:
                        player_stats[p] = 0
                    player_stats[p] += 1
        
        if len(participating_teams) < 2:
            continue # 경기가 아님
            
        # 2. 승무패 판별 및 승점 부여
        # 참여한 팀들끼리 비교
        for my_team in participating_teams:
            my_score = scores[my_team]
            # 상대팀들의 점수
            opponent_scores = [scores[t] for t in participating_teams if t != my_team]
            my_max_opponent_score = max(opponent_scores) if opponent_scores else 0
            
            # 실점 누적 (상대팀들의 총 득점? 아니면 실점? 축구 규칙상 상대가 넣은게 실점)
            # 여기선 A vs B일땐 B의 골이 실점. A vs B vs C 일땐? B+C 골이 실점? 
            # 일반적인 리그 테이블에서는 상대팀 득점 합을 실점으로 함.
            gained_against = sum(opponent_scores)
            team_stats[my_team]['GA'] += gained_against
            team_stats[my_team]['Played'] += 1
            
            # 주차별 데이터에 '주차'가 있으므로, 출전 횟수 카운트 (나중에 가성비 계산용)
            # 주차별 승점 기록을 위해 임시 변수
            points_gained = 0
            
            if my_score > my_max_opponent_score:
                # 승리 (단독 1등)
                team_stats[my_team]['W'] += 1
                team_stats[my_team]['Points'] += 3
                points_gained = 3
            elif my_score == my_max_opponent_score:
                # 무승부 (공동 1등 포함)
                team_stats[my_team]['D'] += 1
                team_stats[my_team]['Points'] += 1
                points_gained = 1
            else:
                # 패배
                team_stats[my_team]['L'] += 1
                team_stats[my_team]['Points'] += 0
                points_gained = 0
            
            # 경기 이력 저장
            history_records.append({
                'Week': week,
                'Team': my_team,
                'PointsGained': points_gained
            })

    # 팀 통계 DataFrame 변환
    df_teams = pd.DataFrame(team_stats).T
    df_teams.index.name = 'Team'
    df_teams['GD'] = df_teams['GF'] - df_teams['GA']
    df_teams = df_teams.reset_index()
    # 순위 산정: 승점 -> 득실차 -> 득점 순
    df_teams = df_teams.sort_values(by=['Points', 'GD', 'GF'], ascending=[False, False, False])
    df_teams = df_teams.reset_index(drop=True)
    df_teams.index += 1 # 1위부터 시작
    
    # 히스토리 DataFrame
    df_history = pd.DataFrame(history_records)
    
    # 선수 득점 DataFrame
    df_scorers = pd.DataFrame(list(player_stats.items()), columns=['Player', 'Goals'])
    
    return df_teams, df_history, df_scorers

def process_attendance(df_att):
    """출석 데이터를 분석합니다."""
    # Melt 처리하여 주차별 데이터를 행으로 변환
    # 컬럼: 팀이름, 선수이름, 1주차, 2주차, 3주차 ...
    
    # '주차'가 들어간 컬럼만 찾기
    week_cols = [c for c in df_att.columns if '주차' in c]
    
    # Long format으로 변환
    df_melt = df_att.melt(id_vars=['팀이름', '선수이름'], value_vars=week_cols, var_name='WeekName', value_name='Attended')
    
    # 출석 체크된 것만 필터링 (값이 1이거나 비어있지 않은 것)
    # TSV에서 빈값은 NaN.
    # 안전하게 str 변환 후 처리
    df_melt['Attended'] = df_melt['Attended'].fillna(0)
    
    # 출석 여부를 1로 통일
    def check_att(val):
        try:
            if float(val) > 0: return 1
        except:
            if str(val).strip() != '': return 1
        return 0
        
    df_melt['IsAttended'] = df_melt['Attended'].apply(check_att)
    
    # 주차 숫자 추출 (1주차 -> 1)
    df_melt['WeekNum'] = df_melt['WeekName'].str.extract(r'(\d+)').astype(int)
    
    return df_melt
