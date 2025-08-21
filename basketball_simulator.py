import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt

class BasketballSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Exhibition Basketball Game Simulator')
        self.setFixedSize(480, 400)
        self.setStyleSheet('background-color: #232946; color: #fffffe;')

        font_title = QFont('Arial', 20, QFont.Bold)
        font_label = QFont('Arial', 12)
        font_button = QFont('Arial', 12, QFont.Bold)

        layout = QVBoxLayout()
        title = QLabel('🏀 Basketball Game Simulator')
        title.setFont(font_title)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Team input fields
        team_layout = QHBoxLayout()
        self.team1_input = QLineEdit()
        self.team1_input.setPlaceholderText('Team 1 Name')
        self.team1_input.setFont(font_label)
        self.team1_input.setStyleSheet('padding: 8px; border-radius: 8px; background: #eebbc3; color: #232946;')
        self.team2_input = QLineEdit()
        self.team2_input.setPlaceholderText('Team 2 Name')
        self.team2_input.setFont(font_label)
        self.team2_input.setStyleSheet('padding: 8px; border-radius: 8px; background: #eebbc3; color: #232946;')
        team_layout.addWidget(self.team1_input)
        team_layout.addWidget(self.team2_input)
        layout.addLayout(team_layout)

        # Simulate button
        self.simulate_btn = QPushButton('Simulate Game')
        self.simulate_btn.setFont(font_button)
        self.simulate_btn.setStyleSheet('background: #393d63; color: #fffffe; padding: 10px; border-radius: 8px;')
        self.simulate_btn.clicked.connect(self.simulate_game)
        layout.addWidget(self.simulate_btn)

        # Result display
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setFont(font_label)
        self.result_box.setStyleSheet('background: #121629; color: #fffffe; border-radius: 8px; padding: 10px;')
        layout.addWidget(self.result_box)

        self.setLayout(layout)

    def simulate_game(self):
        team1 = self.team1_input.text().strip() or 'Team 1'
        team2 = self.team2_input.text().strip() or 'Team 2'
        score1 = random.randint(60, 120)
        score2 = random.randint(60, 120)
        winner = team1 if score1 > score2 else team2 if score2 > score1 else 'It\'s a tie!'
        summary = self.generate_summary(team1, team2, score1, score2, winner)
        self.result_box.setHtml(summary)

    def generate_summary(self, team1, team2, score1, score2, winner):
        if winner == "It's a tie!":
            result = f"<b>{team1}</b> {score1} - {score2} <b>{team2}</b><br><span style='color:#eebbc3;'>It was a thrilling tie game!</span>"
        else:
            result = f"<b>{team1}</b> {score1} - {score2} <b>{team2}</b><br><span style='color:#eebbc3;'>Winner: <b>{winner}</b></span>"
        # Add a short random summary
        highlights = [
            f"{winner} dominated the paint and controlled the boards.",
            f"A last-second three-pointer sealed the win for {winner}.",
            f"Both teams showed great defense, but {winner} had the edge.",
            f"The crowd was on their feet as {winner} pulled ahead in the final minutes.",
            f"{winner} made a stunning comeback after trailing at halftime."
        ]
        if winner != "It's a tie!":
            result += f"<br><i>{random.choice(highlights)}</i>"
        return result

def main():
    app = QApplication(sys.argv)
    window = BasketballSimulator()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
