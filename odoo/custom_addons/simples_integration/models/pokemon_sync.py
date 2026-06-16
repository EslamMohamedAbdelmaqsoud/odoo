import requests
from odoo import models, fields


class PokemonSync(models.Model):
    _name = 'pokemon.sync'
    _description = 'Pokemon Data from API'

    pokemon_id = fields.Integer('PokeID', help="ID from API")
    name = fields.Char('Name')
    weight = fields.Integer('Weight')
    image_url = fields.Char('Image URL')

    def action_fetch_pokemon(self):
        # سنقوم بجلب أول 20 بوكيمون كمثال
        for i in range(1, 21):
            url = f"https://pokeapi.co/api/v2/pokemon/{i}"
            try:
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    data = res.json()

                    # البحث عن البوكيمون إذا كان موجوداً لتحديثه، وإلا نقوم بإنشائه
                    existing = self.search([('pokemon_id', '=', data.get('id'))], limit=1)
                    vals = {
                        'pokemon_id': data.get('id'),
                        'name': data.get('name').capitalize(),
                        'weight': data.get('weight'),
                        'image_url': data.get('sprites').get('front_default'),  # الوصول لبيانات متداخلة
                    }

                    if existing:
                        existing.write(vals)
                    else:
                        self.create(vals)
            except Exception as e:
                print(f"Error fetching Pokemon {i}: {str(e)}")

    def action_fetch_data(self):
        return self.action_fetch_pokemon()