from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from Match import Match
import os


class TipBot:
    def __init__(self):
        self._initialize_headless_browser()

    def _initialize_headless_browser(self):
        opts = Options()
        # opts.headless = True
        try:
            self.browser = Chrome(options=opts)
        except WebDriverException:
            self.browser = Chrome(executable_path=os.environ['CHROMEDRIVER'], options=opts)


    def _authenticate_to_kicktipp(self):
        self.browser.get('https://www.kicktipp.de/djk-labbeck/profil/login')

        self.browser.find_element_by_id("kennung").send_keys(os.environ['EMAIL'])
        self.browser.find_element_by_id("passwort").send_keys(os.environ['PASSWORD'])
        self.browser.find_element_by_name("submitbutton").click()

    def _go_to_tip_submission(self):
        self.browser.get("https://www.kicktipp.de/djk-labbeck/tippabgabe")

    def _get_match_list_of_current_gameday(self):
        most_recent_game_day_matches = []

        # Scrape the html to gather the required information
        table = self.browser.find_element_by_xpath("//table[@id='tippabgabeSpiele']")

        for row in table.find_elements_by_xpath(".//tr"):
            data_of_table_row = row.find_elements_by_xpath(".//td")
            if len(data_of_table_row) >= 6:
                match = Match(home_team=data_of_table_row[1].text,
                              away_team=data_of_table_row[2].text,
                              odd_home_team_wins=float(data_of_table_row[4].text.replace(",", ".")),
                              odd_draw=float(data_of_table_row[5].text.replace(",", ".")),
                              odd_away_team_wins=float(data_of_table_row[6].text.replace(",", ".")),
                              table_data_html=data_of_table_row[3]
                              )
                most_recent_game_day_matches.append(match)

        return most_recent_game_day_matches

    def _tip_each_match(self, match_list):
        for match in match_list:
            self._fill_tip_input_for_match(match)

    def _fill_tip_input_for_match(self, match):
        tip_tuple = self._get_expected_goals_for_match_as_tuple(match)
        inputs_fields = match.table_data_html.find_elements_by_xpath(".//input")
        if len(inputs_fields) >= 2:
            inputs_fields[1].clear()
            inputs_fields[1].send_keys(tip_tuple[0])
            inputs_fields[2].clear()
            inputs_fields[2].send_keys(tip_tuple[1])

    def _get_expected_goals_for_match_as_tuple(self, match):
        probabilities = [match.odd_home_team_wins, match.odd_draw, match.odd_away_team_wins]
        index_of_most_probable_event = probabilities.index(min(probabilities))

        if index_of_most_probable_event == 0:
            return 2, 1
        elif index_of_most_probable_event == 1:
            return 1, 1
        elif index_of_most_probable_event == 2:
            return 1, 2

    def _submit_all_tips(self):
        self.browser.find_element_by_name("submitbutton").click()

    def tip_all_matches_and_submit(self):
        self._authenticate_to_kicktipp()
        self._go_to_tip_submission()
        most_recent_game_day_matches = self._get_match_list_of_current_gameday()
        self._tip_each_match(most_recent_game_day_matches)
        self._submit_all_tips()
        self.browser.close()


if __name__ == "__main__":
    bot = TipBot()
    bot.tip_all_matches_and_submit()
