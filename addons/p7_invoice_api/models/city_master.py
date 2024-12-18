from odoo import models, fields

class WakaCityMaster(models.Model):
    _name = 'waka.city.master'
    _description = 'City Master of wakatech'

    wakatech_city_id = fields.Char(string='Wakatech City ID', required=True)
    name = fields.Char(string='City Name', required=True)
    state_id = fields.Char(string='State ID', required=True)
    state_code = fields.Char(string='State Code', required=True)
    country_id = fields.Char(string='Country ID', required=True)
    country_code = fields.Char(string='Country Code', required=True)

