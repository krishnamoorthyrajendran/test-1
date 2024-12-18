from odoo import http
from odoo.http import request
import json
import base64
from odoo.addons.web.controllers.main import Binary


class CustomController(http.Controller):

    @http.route('/rpc/custom/endpoint', type='json', auth='user')
    def custom_endpoint(self):
        
        return {'status': 'success', 'message': 'RPC call successful!'}
    
class MenuController(http.Controller):

   
    @http.route('/get/menu/items', type='http', auth='public', website=True)
    def get_menu_items(self, **kw):
        
        user = request.env.user
        menu_items = []
        for record in user.menus:
            submenus = []
            for submenu in record.submenu_ids:
                submenus.append({
                    'submenu_name': submenu.name,
                    'submenu_link': submenu.url,
                    'name_id': submenu.name_id,
                    'image_url': submenu.logo if submenu.logo else 'https://img.icons8.com/?size=100&id=j1UxMbqzPi7n&format=png&color=FFFFFF',
                })
            
            # image_url = '/web/image/menu.line.item/{}/logo'.format(record.id)
            menu_items.append({
                'main_menu': record.main_menu,
                'submenus': submenus,
                'main_menu_id':record.main_menu_id,
                'image_url': record.logo if record.logo else 'https://img.icons8.com/?size=100&id=j1UxMbqzPi7n&format=png&color=FFFFFF',
            })
        return json.dumps(menu_items)
    
   
    
    
    

