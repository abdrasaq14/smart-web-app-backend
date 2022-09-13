

class OrganizationMockData:
    def get_data(self):
        return {
            "cardsData": self._get_cards_data(),
            "chartsData": self._get_charts_data()
        }

    def _get_cards_data(self):
        return {
            "totalConsumption": 32727658,
            "currentLoad": 2727121,
            "avgAvailability": 20,
            "powerCuts": 5,
            "overloadedDTs": 10,
            "sitesUnderMaintenance": 2
        }

    def _get_charts_data(self):
        return {
            "powerConsumption": {
                "data": [
                    ['district', 'consumption'],
                    ['District E', 850],
                    ['District D', 200],
                    ['District C', 300],
                    ['District B', 500],
                    ['District A', 800],
                ],
            }
        }
