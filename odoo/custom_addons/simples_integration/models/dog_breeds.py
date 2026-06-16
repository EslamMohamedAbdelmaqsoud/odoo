import requests
from odoo import models, fields, api
from odoo.exceptions import UserError


class DogBreeds(models.Model):
    _name = 'dog.breeds'
    _description = 'Dog Breeds from External API'

    name = fields.Char(string='Breed Name')
    sub_breeds = fields.Text(string='Sub Breeds')

    def action_sync_breeds(self):
        #  Postman (Dog Breeds API)
        url = "https://dog.ceo/api/breeds/list/all"

        try:
            # Make the API request to fetch dog breeds
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                breeds_dict = data.get('message', {})

                for breed, subs in breeds_dict.items():
                    # Check if the breed already exists in the databasel
                    existing = self.search([('name', '=', breed)], limit=1)

                    vals = {
                        'name': breed.capitalize(),
                        'sub_breeds': ", ".join(subs) if subs else "None"
                    }

                    if existing:
                        existing.write(vals)
                    else:
                        self.create(vals)

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Synchronization Successful',
                        'message': 'The dog breeds have been successfully brought in and updated!',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(f"API connection failed: {response.status_code}")

        except Exception as e:
            raise UserError(f"An error occurred during synchronization:{str(e)}")

    def sync_breeds(self):
        return self.action_sync_breeds()
