import sys
import math
import random
from itertools import combinations
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QRadioButton,
    QPushButton,
    QLabel,
    QLineEdit,
    QListWidget,
    QTextEdit,
    QMessageBox,
    QListWidgetItem,
)
from PySide6.QtCore import Qt


class TournamentScheduler:
    """
    一個用於產生羽球賽程的類別，支援淘汰賽與循環賽。
    """

    def __init__(self, participants, event_type="單打"):
        if len(participants) < 2:
            raise ValueError("參賽者/隊伍至少需要兩位/兩隊。")
        self.participants = participants
        self.event_type = event_type
        self.num_participants = len(participants)

    def _format_participant(self, p):
        if p is None:
            return "輪空"
        if self.event_type == "雙打" and isinstance(p, (list, tuple)):
            return f"{p[0]}/{p[1]}"
        return str(p)

    def generate_knockout_schedule(self):
        """產生並回傳「淘汰賽」賽程表的字串。"""
        output = []
        output.append("=" * 40)
        output.append("      羽球錦標賽 - 淘汰賽賽程表      ")
        output.append("=" * 40)
        output.append(f"賽事類型: {self.event_type}")
        output.append(f"總參賽隊伍數: {self.num_participants}")

        bracket_size = 2 ** math.ceil(math.log2(self.num_participants))
        num_byes = bracket_size - self.num_participants
        output.append(f"總籤位數: {bracket_size}")
        output.append(f"輪空隊伍數: {num_byes}")
        output.append("=" * 40)

        players_with_byes = self.participants[:num_byes]
        players_for_round1 = self.participants[num_byes:]
        random.shuffle(players_for_round1)

        round1_matches = []
        if players_for_round1:
            output.append("\n--- 第一輪 (預賽) ---")
            num_round1_matches = len(players_for_round1) // 2
            for i in range(num_round1_matches):
                p1, p2 = players_for_round1[i * 2], players_for_round1[i * 2 + 1]
                round1_matches.append((p1, p2))
                output.append(
                    f"比賽 {i+1}: {self._format_participant(p1)} vs {self._format_participant(p2)}"
                )
        else:
            output.append("\n所有參賽隊伍在第一輪輪空。")

        current_round = 2
        round2_entrants = players_with_byes + [
            f"第一輪比賽 {i+1} 勝方" for i in range(len(round1_matches))
        ]

        while len(round2_entrants) > 1:
            output.append(f"\n--- 第 {current_round} 輪 ---")
            if len(round2_entrants) == 4:
                output.append("(半決賽)")
            if len(round2_entrants) == 2:
                output.append("(決賽)")

            next_round_entrants = []
            num_matches_this_round = len(round2_entrants) // 2
            for i in range(num_matches_this_round):
                p1, p2 = (
                    round2_entrants[i],
                    round2_entrants[len(round2_entrants) - 1 - i],
                )
                output.append(
                    f"比賽 {i+1}: {self._format_participant(p1)} vs {self._format_participant(p2)}"
                )
                next_round_entrants.append(f"第 {current_round} 輪比賽 {i+1} 勝方")

            round2_entrants = next_round_entrants
            current_round += 1

        output.append("\n" + "=" * 40)
        output.append("      淘汰賽賽程產生完畢      ")
        output.append("=" * 40 + "\n")
        return "\n".join(output)

    def generate_round_robin_schedule(self):
        """產生並回傳「循環賽」賽程表的字串。"""
        output = []
        output.append("=" * 40)
        output.append("      羽球錦標賽 - 循環賽賽程表      ")
        output.append("=" * 40)
        output.append(f"賽事類型: {self.event_type}")
        output.append(f"總參賽隊伍數: {self.num_participants}")

        all_matches = list(combinations(self.participants, 2))
        output.append(f"總比賽場次: {len(all_matches)}")
        output.append("=" * 40)

        local_participants = list(self.participants)
        random.shuffle(local_participants)
        if self.num_participants % 2 != 0:
            local_participants.append(None)

        num_rounds = len(local_participants) - 1
        half_size = len(local_participants) // 2

        for r in range(num_rounds):
            output.append(f"\n--- 第 {r+1} 輪 ---")
            p1_list, p2_list = (
                local_participants[:half_size],
                local_participants[half_size:],
            )
            p2_list.reverse()

            for i in range(half_size):
                p1, p2 = p1_list[i], p2_list[i]
                if p1 is None:
                    output.append(f"{self._format_participant(p2)} 本輪輪空")
                elif p2 is None:
                    output.append(f"{self._format_participant(p1)} 本輪輪空")
                else:
                    output.append(
                        f"比賽 {i+1}: {self._format_participant(p1)} vs {self._format_participant(p2)}"
                    )

            last_player = local_participants.pop()
            local_participants.insert(1, last_player)

        output.append("\n" + "=" * 40)
        output.append("      循環賽賽程產生完畢      ")
        output.append("=" * 40 + "\n")
        return "\n".join(output)


def create_random_teams(players):
    random.shuffle(players)
    teams = []
    left_out_player = None
    num_players = len(players)
    for i in range(0, num_players // 2 * 2, 2):
        teams.append((players[i], players[i + 1]))
    if num_players % 2 != 0:
        left_out_player = players[-1]
    return teams, left_out_player


# =============================================================================
# PySide6 GUI 應用程式
# =============================================================================


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("羽球賽程產生器")
        self.setGeometry(100, 100, 900, 600)

        # 主佈局
        main_layout = QHBoxLayout()

        # 左側控制面板
        left_panel = QVBoxLayout()

        # 賽事類型
        self.event_type_group = QGroupBox("1. 賽事類型")
        self.radio_singles = QRadioButton("單打")
        self.radio_doubles = QRadioButton("雙打")
        self.radio_singles.setChecked(True)
        event_type_layout = QVBoxLayout()
        event_type_layout.addWidget(self.radio_singles)
        event_type_layout.addWidget(self.radio_doubles)
        self.event_type_group.setLayout(event_type_layout)
        left_panel.addWidget(self.event_type_group)

        # 組隊方式 (雙打專用)
        self.teaming_group = QGroupBox("2. 組隊方式 (雙打)")
        self.radio_manual_teams = QRadioButton("手動輸入隊伍")
        self.radio_random_teams = QRadioButton("從選手名單隨機分隊")
        self.radio_manual_teams.setChecked(True)
        teaming_layout = QVBoxLayout()
        teaming_layout.addWidget(self.radio_manual_teams)
        teaming_layout.addWidget(self.radio_random_teams)
        self.teaming_group.setLayout(teaming_layout)
        self.teaming_group.setVisible(False)  # 預設隱藏
        left_panel.addWidget(self.teaming_group)

        # 參賽者名單
        self.participants_group = QGroupBox("3. 參賽者名單")
        participants_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        add_player_layout = QHBoxLayout()
        self.player_name_input = QLineEdit()
        self.player_name_input.setPlaceholderText("輸入姓名後按 Enter 或按鈕")
        self.add_button = QPushButton("新增")
        add_player_layout.addWidget(self.player_name_input)
        add_player_layout.addWidget(self.add_button)
        self.remove_button = QPushButton("移除選取選手")
        participants_layout.addLayout(add_player_layout)
        participants_layout.addWidget(self.list_widget)
        participants_layout.addWidget(self.remove_button)
        self.participants_group.setLayout(participants_layout)
        left_panel.addWidget(self.participants_group)

        # 賽制
        self.format_group = QGroupBox("4. 賽制")
        self.radio_knockout = QRadioButton("淘汰賽 (請依種子順序新增選手)")
        self.radio_round_robin = QRadioButton("循環賽")
        self.radio_knockout.setChecked(True)
        format_layout = QVBoxLayout()
        format_layout.addWidget(self.radio_knockout)
        format_layout.addWidget(self.radio_round_robin)
        self.format_group.setLayout(format_layout)
        left_panel.addWidget(self.format_group)

        # 產生按鈕
        self.generate_button = QPushButton("產生賽程")
        self.generate_button.setStyleSheet("font-size: 16px; padding: 10px;")
        left_panel.addWidget(self.generate_button)

        left_panel.addStretch()

        # 右側結果顯示
        right_panel = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFontFamily("Courier New")
        right_panel.addWidget(QLabel("賽程結果:"))
        right_panel.addWidget(self.result_text)

        # 將左右面板加入主佈局
        main_layout.addLayout(left_panel, 1)  # 比例 1
        main_layout.addLayout(right_panel, 2)  # 比例 2

        # 設定主視窗的中央元件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # --- 連接信號與槽 ---
        self.radio_doubles.toggled.connect(self.teaming_group.setVisible)
        self.add_button.clicked.connect(self.add_participant)
        self.player_name_input.returnPressed.connect(self.add_participant)
        self.remove_button.clicked.connect(self.remove_participant)
        self.generate_button.clicked.connect(self.generate_schedule)

    def add_participant(self):
        name = self.player_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "輸入錯誤", "姓名不能為空！")
            return

        self.list_widget.addItem(name)
        self.player_name_input.clear()
        self.player_name_input.setFocus()

    def remove_participant(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.list_widget.takeItem(self.list_widget.row(item))

    def generate_schedule(self):
        try:
            # 1. 獲取所有選手
            all_players = [
                self.list_widget.item(i).text() for i in range(self.list_widget.count())
            ]

            event_type = "單打"
            participants = []

            # 2. 根據賽事類型和組隊方式處理參賽名單
            if self.radio_singles.isChecked():
                event_type = "單打"
                participants = all_players
                if len(participants) < 2:
                    raise ValueError("單打比賽至少需要 2 位選手。")
            else:  # 雙打
                event_type = "雙打"
                if self.radio_random_teams.isChecked():
                    if len(all_players) < 4:
                        raise ValueError("隨機分隊至少需要 4 位選手。")
                    participants, left_out = create_random_teams(all_players)
                    if left_out:
                        QMessageBox.information(
                            self,
                            "分隊提醒",
                            f"選手 '{left_out}' 因人數為奇數，本次未被分到隊伍。",
                        )
                else:  # 手動輸入隊伍
                    if len(all_players) % 2 != 0:
                        raise ValueError("手動輸入隊伍時，選手總數必須為偶數。")
                    # 將列表兩兩一組
                    for i in range(0, len(all_players), 2):
                        participants.append((all_players[i], all_players[i + 1]))
                    if len(participants) < 2:
                        raise ValueError("雙打比賽至少需要 2 隊。")

            # 3. 建立 Scheduler 並產生賽程
            scheduler = TournamentScheduler(participants, event_type)

            result_str = ""
            if self.radio_knockout.isChecked():
                result_str = scheduler.generate_knockout_schedule()
            else:
                result_str = scheduler.generate_round_robin_schedule()

            # 4. 顯示結果
            self.result_text.setText(result_str)

        except ValueError as e:
            QMessageBox.critical(self, "錯誤", str(e))
        except Exception as e:
            QMessageBox.critical(self, "未知錯誤", f"發生了未預期的錯誤: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
