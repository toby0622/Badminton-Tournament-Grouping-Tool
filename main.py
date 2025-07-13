import math
import random
from itertools import combinations

class TournamentScheduler:
    """
    一個用於產生羽球賽程的類別，支援淘汰賽與循環賽。
    """

    def __init__(self, participants, event_type='單打'):
        """
        初始化賽程產生器。

        參數:
        - participants (list): 參賽者/隊伍列表。
        - event_type (str): 賽事類型，'單打' 或 '雙打'。
        """
        if len(participants) < 2:
            raise ValueError("參賽者/隊伍至少需要兩位/兩隊。")
        
        self.participants = participants
        self.event_type = event_type
        self.num_participants = len(participants)

    def _format_participant(self, p):
        """格式化參賽者名稱以供顯示。"""
        if p is None:
            return "輪空"
        if self.event_type == '雙打' and isinstance(p, (list, tuple)):
            return f"{p[0]}/{p[1]}"
        return str(p)

    def generate_knockout_schedule(self):
        """
        產生並印出「淘汰賽」的賽程表。
        """
        print("\n" + "="*40)
        print("      羽球錦標賽 - 淘汰賽賽程表      ")
        print("="*40)
        print(f"賽事類型: {self.event_type}")
        print(f"總參賽隊伍數: {self.num_participants}")

        # --- 淘汰賽專用計算 ---
        bracket_size = 2**math.ceil(math.log2(self.num_participants))
        num_byes = bracket_size - self.num_participants
        print(f"總籤位數: {bracket_size}")
        print(f"輪空隊伍數: {num_byes}")
        print("="*40)

        # 根據種子順序，將輪空資格分配給前面的參賽者
        # 重要：這裡假設 self.participants 是已經排好種子序的
        players_with_byes = self.participants[:num_byes]
        players_for_round1 = self.participants[num_byes:]
        random.shuffle(players_for_round1)

        # --- 產生第一輪 (預賽) ---
        round1_matches = []
        if players_for_round1:
            print("\n--- 第一輪 (預賽) ---")
            num_round1_matches = len(players_for_round1) // 2
            for i in range(num_round1_matches):
                p1 = players_for_round1[i*2]
                p2 = players_for_round1[i*2 + 1]
                round1_matches.append((p1, p2))
                print(f"比賽 {i+1}: {self._format_participant(p1)} vs {self._format_participant(p2)}")
        else:
            print("\n所有參賽隊伍在第一輪輪空。")

        # --- 產生後續輪次 ---
        current_round = 2
        round2_entrants = players_with_byes + [f"第一輪比賽 {i+1} 勝方" for i in range(len(round1_matches))]

        while len(round2_entrants) > 1:
            print(f"\n--- 第 {current_round} 輪 ---")
            if len(round2_entrants) == 4: print("(半決賽)")
            if len(round2_entrants) == 2: print("(決賽)")

            next_round_entrants = []
            num_matches_this_round = len(round2_entrants) // 2
            for i in range(num_matches_this_round):
                p1 = round2_entrants[i]
                p2 = round2_entrants[len(round2_entrants) - 1 - i]
                print(f"比賽 {i+1}: {self._format_participant(p1)} vs {self._format_participant(p2)}")
                next_round_entrants.append(f"第 {current_round} 輪比賽 {i+1} 勝方")
            
            round2_entrants = next_round_entrants
            current_round += 1
        
        print("\n" + "="*40)
        print("      淘汰賽賽程產生完畢      ")
        print("="*40 + "\n")

    def generate_round_robin_schedule(self):
        """
        產生並印出「循環賽」的賽程表。
        """
        print("\n" + "="*40)
        print("      羽球錦標賽 - 循環賽賽程表      ")
        print("="*40)
        print(f"賽事類型: {self.event_type}")
        print(f"總參賽隊伍數: {self.num_participants}")
        
        # 使用 itertools.combinations 產生所有可能的對戰組合
        all_matches = list(combinations(self.participants, 2))
        total_matches = len(all_matches)
        print(f"總比賽場次: {total_matches}")
        print("="*40)
        
        # 為了讓賽程更公平，隨機打亂隊伍順序
        local_participants = list(self.participants)
        random.shuffle(local_participants)

        # 如果人數是奇數，補一個 "輪空" 標記
        if self.num_participants % 2 != 0:
            local_participants.append(None) # None 代表輪空

        num_rounds = len(local_participants) - 1
        half_size = len(local_participants) // 2
        
        for r in range(num_rounds):
            print(f"\n--- 第 {r+1} 輪 ---")
            
            # 固定第一個選手，其餘選手輪轉
            p1_list = local_participants[:half_size]
            p2_list = local_participants[half_size:]
            p2_list.reverse() # 反轉第二部分以配對

            for i in range(half_size):
                p1 = p1_list[i]
                p2 = p2_list[i]
                
                if p1 is None:
                    print(f"{self._format_participant(p2)} 本輪輪空")
                elif p2 is None:
                    print(f"{self._format_participant(p1)} 本輪輪空")
                else:
                    print(f"比賽 {i+1}: {self._format_participant(p1)} vs {self._format_participant(p2)}")

            # 輪轉選手: 固定第一個，其餘順時針移動
            last_player = local_participants.pop()
            local_participants.insert(1, last_player)

        print("\n" + "="*40)
        print("      循環賽賽程產生完畢      ")
        print("="*40 + "\n")


def create_random_teams(players):
    """從選手列表中隨機建立雙打隊伍。"""
    random.shuffle(players)
    teams = []
    left_out_player = None
    num_players = len(players)
    for i in range(0, num_players // 2 * 2, 2):
        teams.append((players[i], players[i+1]))
    if num_players % 2 != 0:
        left_out_player = players[-1]
    return teams, left_out_player

def run_interactive_mode():
    """提供一個互動式介面，讓使用者輸入資料來產生賽程。"""
    print("歡迎使用羽球賽程產生器！")
    
    # --- 選擇賽事類型 ---
    event_type = ''
    while event_type not in ['1', '2']:
        event_type = input("請選擇賽事類型 (1: 單打, 2: 雙打): ")
    event_type = '單打' if event_type == '1' else '雙打'

    participants = []

    if event_type == '單打':
        while True:
            try:
                num_participants = int(input("請輸入單打的總參賽人數: "))
                if num_participants >= 2: break
                else: print("錯誤：參賽人數至少需要 2。")
            except ValueError: print("錯誤：請輸入一個有效的數字。")
        
        print("\n請輸入參賽者名單（若為淘汰賽，請依種子順序輸入）：")
        for i in range(num_participants):
            while True:
                name = input(f"請輸入第 {i+1} 位選手的姓名: ")
                if name.strip():
                    participants.append(name.strip())
                    break
                else: print("姓名不能為空。")
    else: # 雙打
        team_mode = ''
        while team_mode not in ['1', '2']:
            team_mode = input("請選擇雙打組隊方式 (1: 手動輸入隊伍, 2: 從選手名單隨機分隊): ")

        if team_mode == '1': # 手動輸入
            while True:
                try:
                    num_teams = int(input("請輸入總參賽隊伍數: "))
                    if num_teams >= 2: break
                    else: print("錯誤：參賽隊伍數至少需要 2。")
                except ValueError: print("錯誤：請輸入一個有效的數字。")

            print("\n請輸入隊伍名單（若為淘汰賽，請依種子順序輸入）：")
            for i in range(num_teams):
                while True:
                    p1 = input(f"請輸入第 {i+1} 隊的第 1 位選手姓名: ").strip()
                    p2 = input(f"請輸入第 {i+1} 隊的第 2 位選手姓名: ").strip()
                    if p1 and p2:
                        participants.append((p1, p2))
                        break
                    else: print("兩位選手的姓名都不能為空。")
        else: # 隨機分隊
            while True:
                try:
                    num_players = int(input("請輸入所有要參加分隊的選手總人數: "))
                    if num_players >= 4: break
                    else: print("錯誤：隨機分隊至少需要 4 位選手。")
                except ValueError: print("錯誤：請輸入一個有效的數字。")
            
            players_to_group = []
            print("\n請輸入所有選手的姓名：")
            for i in range(num_players):
                 while True:
                    name = input(f"請輸入第 {i+1} 位選手的姓名: ")
                    if name.strip():
                        players_to_group.append(name.strip())
                        break
                    else: print("姓名不能為空。")
            
            participants, left_out = create_random_teams(players_to_group)
            print("\n--- 隨機分隊結果 ---")
            for i, team in enumerate(participants):
                print(f"第 {i+1} 隊: {team[0]} / {team[1]}")
            if left_out:
                print(f"\n注意：選手 '{left_out}' 因人數為奇數，本次未被分到隊伍。")
            print("------------------------")
            input("按 Enter 鍵繼續...")

    # --- 選擇賽制 ---
    tournament_format = ''
    while tournament_format not in ['1', '2']:
        tournament_format = input("\n請選擇賽制 (1: 淘汰賽, 2: 循環賽): ")

    # --- 產生賽程 ---
    try:
        scheduler = TournamentScheduler(participants, event_type)
        if tournament_format == '1':
            scheduler.generate_knockout_schedule()
        else:
            scheduler.generate_round_robin_schedule()
    except ValueError as e:
        print(f"\n產生賽程時發生錯誤: {e}")

if __name__ == '__main__':
    run_interactive_mode()
