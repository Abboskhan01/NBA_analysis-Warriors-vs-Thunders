from collections import defaultdict
import csv
import re


def load_data(file_name):
    data = []
    with open(file_name) as file:
        play_moves = csv.reader(file, delimiter='|')
        for play in play_moves:
            data.append(play)
    return data


''' extracts 2P 2PM 3P 3PM FT FTM ORB DRB TOV PF'''


def get_action1(action):
    if re.search(r'(.*) makes 2-pt', action):
        player_name = re.search(r'(.*) makes 2-pt', action)[1]
        return [player_name, "2P"]

    if re.search(r'(.*) misses 2-pt', action):
        player_name = re.search(r'(.*) misses 2-pt', action)[1]
        return [player_name, "2PM"]

    if re.search(r'(.*) makes 3-pt', action):
        player_name = re.search(r'(.*) makes 3-pt', action)[1]
        return [player_name, "3P"]
    if re.search(r'(.*) misses 3-pt', action):
        player_name = re.search(r'(.*) misses 3-pt', action)[1]
        return [player_name, "3PM"]

    if re.search(r'(.*) makes free throw', action):
        player_name = re.search(r'(.*) makes free throw', action)[1]
        return [player_name, "FT"]

    if re.search(r'(.*) misses free throw', action):
        player_name = re.search(r'(.*) misses free throw', action)[1]
        return [player_name, "FTM"]

    if re.search(r'Offensive rebound by (\w\.\s\w+)', action):
        player_name = re.search(r'Offensive rebound by (\w\.\s\w+)', action)[1]
        return [player_name, "ORB"]

    if re.search(r'Defensive rebound by (\w\.\s\w+)', action):
        player_name = re.search(r'Defensive rebound by (\w\.\s\w+)', action)[1]
        return [player_name, "DRB"]

    if re.search(r'Turnover by (\w\.\s\w+)', action):
        player_name = re.search(r'Turnover by (\w\.\s\w+)', action)[1]
        return [player_name, "TOV"]

    if re.search(r'.*foul by (\w\.\s\w+)', action):
        player_name = re.search(r'.*foul by (\w\.\s\w+)', action)[1]
        return [player_name, "PF"]


''' extracts AST STL BLK '''


def get_action2(action):
    if re.search(r'\(assist by (\w\.\s\w+)', action):
        player_name = re.search(r'\(assist by (\w\.\s\w+)', action)[1]
        return [player_name, "AST"]

    if re.search(r'; steal by (\w\.\s\w+)', action):
        player_name = re.search(r'; steal by (\w\.\s\w+)', action)[1]
        return [player_name, "STL"]

    if re.search(r'\(block by (\w\.\s\w+)', action):
        player_name = re.search(r'\(block by (\w\.\s\w+)', action)[1]
        return [player_name, "BLK"]


def collect_data(player_action, data_of_players, current_team, away_team, home_team):
    player = player_action[0]
    action = player_action[1]

    if data_of_players[player].get(action) is None:
        data_of_players[player][action] = 1
        if action in ["STL", "BLK", "PF"]:
            data_of_players[player]["team"] = not_current(current_team, away_team, home_team)
        else:
            data_of_players[player]["team"] = current_team
    else:
        if action in ["STL", "BLK", "PF"]:
            data_of_players[player]["team"] = not_current(current_team, away_team, home_team)
        else:
            data_of_players[player]["team"] = current_team
        data_of_players[player][action] += 1

    return data_of_players


def not_current(current_team, away_team, home_team):
    if current_team == home_team:
        return away_team
    if current_team == away_team:
        return home_team


def fill_with_zeros(player, data_of_players):
    fields = ["2P", "2PM", "3P", "3PM", "FT", "FTM", "ORB", "DRB", "TOV", "PF", "AST", "STL", "BLK"]

    for field in fields:
        if data_of_players[player].get(field) is None:
            data_of_players[player][field] = 0

    return data_of_players


def extract(play_by_play_moves):
    data_of_players = defaultdict(dict)

    for play in play_by_play_moves:
        current_team = play[2]
        away_team = play[3]
        home_team = play[4]
        action = play[7]
        player_action1 = get_action1(action)
        player_action2 = get_action2(action)

        if player_action1 is not None:
            data_of_players = collect_data(player_action1, data_of_players, current_team, away_team, home_team)
        if player_action2 is not None:
            data_of_players = collect_data(player_action2, data_of_players, current_team, away_team, home_team)

    return data_of_players


def fill(data_of_players):
    for player in data_of_players:
        data_of_players = fill_with_zeros(player, data_of_players)
        data_of_players[player]["FG"] = data_of_players[player]["2P"] + data_of_players[player]["3P"]
        data_of_players[player]["FGA"] = data_of_players[player]["FG"] + data_of_players[player]["3PM"] + \
                                         data_of_players[player]["2PM"]
        data_of_players[player]["FG%"] = round(data_of_players[player]["FG"] / data_of_players[player]["FGA"], 3) if \
        data_of_players[player]["FGA"] != 0 else " "
        data_of_players[player]["3PA"] = data_of_players[player]["3P"] + data_of_players[player]["3PM"]
        data_of_players[player]["3P%"] = round(data_of_players[player]["3P"] / data_of_players[player]["3PA"], 3) if \
        data_of_players[player]["3PA"] != 0 else " "
        data_of_players[player]["FTA"] = data_of_players[player]["FT"] + data_of_players[player]["FTM"]
        data_of_players[player]["FT%"] = round(data_of_players[player]["FT"] / data_of_players[player]["FTA"], 3) if \
        data_of_players[player]["FTA"] != 0 else " "
        data_of_players[player]["TRB"] = data_of_players[player]["ORB"] + data_of_players[player]["DRB"]
        data_of_players[player]["PTS"] = 2 * data_of_players[player]["2P"] + 3 * data_of_players[player]["3P"] + \
                                         data_of_players[player]["FT"]

    return data_of_players


def format(away_team, home_team, data_of_players):
    home_players = []
    away_players = []

    for player in data_of_players:
        if data_of_players[player].get("team") == home_team:
            home_players.append({
                "player_name": player, "FG": data_of_players[player]["FG"], "FGA": data_of_players[player]["FGA"],
                "FG%": data_of_players[player]["FG%"], "3P": data_of_players[player]["3P"],
                "3PA": data_of_players[player]["3PA"], "3P%": data_of_players[player]["3P%"],
                "FT": data_of_players[player]["FT"], "FTA": data_of_players[player]["FTA"],
                "FT%": data_of_players[player]["FT%"],
                "ORB": data_of_players[player]["ORB"], "DRB": data_of_players[player]["DRB"],
                "TRB": data_of_players[player]["TRB"], "AST": data_of_players[player]["AST"],
                "STL": data_of_players[player]["STL"],
                "BLK": data_of_players[player]["BLK"], "TOV": data_of_players[player]["TOV"],
                "PF": data_of_players[player]["PF"], "PTS": data_of_players[player]["PTS"]
            })
        else:
            away_players.append({
                "player_name": player, "FG": data_of_players[player]["FG"], "FGA": data_of_players[player]["FGA"],
                "FG%": data_of_players[player]["FG%"], "3P": data_of_players[player]["3P"],
                "3PA": data_of_players[player]["3PA"], "3P%": data_of_players[player]["3P%"],
                "FT": data_of_players[player]["FT"], "FTA": data_of_players[player]["FTA"],
                "FT%": data_of_players[player]["FT%"],
                "ORB": data_of_players[player]["ORB"], "DRB": data_of_players[player]["DRB"],
                "TRB": data_of_players[player]["TRB"], "AST": data_of_players[player]["AST"],
                "STL": data_of_players[player]["STL"],
                "BLK": data_of_players[player]["BLK"], "TOV": data_of_players[player]["TOV"],
                "PF": data_of_players[player]["PF"], "PTS": data_of_players[player]["PTS"]
            })
    result = {"home_team": {"name": home_team, "players_data": home_players},
              "away_team": {"name": away_team, "players_data": away_players}}

    return result


def analyse_nba_game(play_by_play_moves):
    away_team = play_by_play_moves[0][3]
    home_team = play_by_play_moves[0][4]

    data_of_players = extract(play_by_play_moves)
    data_of_players = fill(data_of_players)
    result = format(away_team, home_team, data_of_players)
    return result


def get_header(player_data):
    header = "Players\t"
    for field in player_data.keys():
        if field != "player_name":
            header += "\t" + field
    return header


def get_players(players_data):
    lines = ""
    for player in players_data:
        line = ""
        for data in player.values():
            if type(data) is float:
                if data == 1:
                    line += "1.000\t"
                    continue
                else:
                    x = str(data).split(".")
                    if len(x[1]) == 1:
                        line += "." + x[1] + "00" + "\t"
                        continue
                    if len(x[1]) == 2:
                        line += "." + x[1] + "0" + "\t"
                        continue
                    if len(x[1]) >= 3:
                        line += "." + x[1][:3] + "\t"
                        continue
            line += str(data) + "\t"
        lines += line + "\n"
    return lines[:-2]


def get_team_totals(players_data):
    number_of_players = len(players_data)
    calcs = [0, 0, 0]
    points = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for player in players_data:
        points[0] += player["FG"]
        points[1] += player["FGA"]
        points[3] += player["3P"]
        points[4] += player["3PA"]
        points[6] += player["FT"]
        points[7] += player["FTA"]
        points[9] += player["ORB"]
        points[10] += player["DRB"]
        points[11] += player["TRB"]
        points[12] += player["AST"]
        points[13] += player["STL"]
        points[14] += player["BLK"]
        points[15] += player["TOV"]
        points[16] += player["PF"]
        points[17] += player["PTS"]
    points[2] = round(points[0] / points[1], 3)
    points[5] = round(points[3] / points[4], 3)
    points[8] = round(points[6] / points[7], 3)

    line = ""
    for data in points:
        if type(data) is float:
            if data == 1:
                line += "1.000\t"
                continue
            else:
                x = str(data).split(".")
                if len(x[1]) == 1:
                    line += "." + x[1] + "00" + "\t"
                    continue
                if len(x[1]) == 2:
                    line += "." + x[1] + "0" + "\t"
                    continue
                if len(x[1]) == 3:
                    line += "." + x[1] + "\t"
                    continue
        line += str(data) + "\t"
    total = "Total Team\t" + line
    return total


def print_nba_game_stats(team_dict):
    header = get_header(team_dict["players_data"][0])
    players = get_players(team_dict["players_data"])
    team_totals = get_team_totals(team_dict["players_data"])

    print(header)
    print(players)
    print(team_totals)
    print("\n\n\n")


def _main():
    file_name = "Warriors _vs_Thunders.txt"
    play_by_play_moves = load_data(file_name)
    team_dict1 = analyse_nba_game(play_by_play_moves)["home_team"]
    team_dict2 = analyse_nba_game(play_by_play_moves)["away_team"]
    print_nba_game_stats(team_dict1)
    print_nba_game_stats(team_dict2)


_main()