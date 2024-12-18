# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
import requests
import base64
import odoo
import odoo.modules.registry
from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.service import security
from odoo.tools import ustr
from odoo.tools.translate import _
from .utils import ensure_db, _get_login_redirect_url, is_user_internal
import jwt
from werkzeug.utils import redirect


_logger = logging.getLogger(__name__)


# Shared parameters for all login/signup flows
SIGN_UP_REQUEST_PARAMS = {'db', 'login', 'debug', 'token', 'message', 'error', 'scope', 'mode',
                          'redirect', 'redirect_hostname', 'email', 'name', 'partner_id',
                          'password', 'confirm_password', 'city', 'country_id', 'lang', 'signup_email'}
LOGIN_SUCCESSFUL_PARAMS = set()

def go_to_waka():

    # Fetch the redirection URL for this base URL
    redirect_url = request.env['ir.config_parameter'].sudo().get_param('waka_redirect_url', "https://www.wakatech.com/login")

    # HTML template with dynamic href
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto-click Button</title>
    <script>
        window.onload = function() {{
            document.getElementById('autoClickButton').click();
        }};
    </script>
    </head>
    <body>
    <!-- Button with dynamically assigned href -->
    <a id="autoClickButton" href="{redirect_url}">Auto-click Button</a>
    </body>
    </html>
    """
    # Return the HTML response
    return request.make_response(html_content, [('Content-Type', 'text/html')])

class Home(http.Controller):

    @http.route('/', type='http', auth="none")
    def index(self, s_action=None, db=None, **kw):
        logging.info("=========Params=========%s",request.params)
        data = request.params
        auth = data.get('auth_token')

        if auth:
            try:
                auth_dict = json.loads(auth)
            except json.JSONDecodeError as e:
                logging.info("Invalid JSON:%s", e)
                return request.redirect_query('/web', query=None)

            if not auth_dict['token']:
                logging.info("====== Invalid Token============")
                return request.redirect_query('/web', query=None)
            token = auth_dict['token']
            base64_token = base64.b64decode(token)
            _token = base64_token.decode('utf-8')

            token_data = json.loads(_token)
            auth_token = token_data['token']
            # auth_token = "eyJ0b2tlbiI6IjM0ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SjFjMlZ5U1dRaU9qSXhPRGdzSW1sd0lqb2lPanBtWm1abU9qRTNOQzR3TGpJNExqRTVNQ0lzSW1selFXUnRhVzRpT21aaGJITmxMQ0psYldGcGJDSTZJbkpoYldGdVlYUm9ZVzR1WjI5MmFXNTBhR0Z5WVdveEsyWmxaR1Y0UUdkdFlXbHNMbU52YlNJc0ltbGhkQ0k2TVRjek1qZzFOamMzTXl3aVpYaHdJam94TnpNeU9EazVPVGN6ZlEuVlEwU1VDNkVKdUtXN01majhjNndzdUZVTVl5Y3pvR3QzS1AxdmFtY2xuMCZHUnh2XkFUOE0wMWxlMFNZMUFqTi0ySER0OE1QI2o3IzN5I1BKI0tCYnlKZjktaDdFMGIiLCJ1c2VyIjp7InVzZXJfaWQiOjIxODgsImVtYWlsIjoicmFtYW5hdGhhbi5nb3ZpbnRoYXJhajErZmVkZXhAZ21haWwuY29tIiwiZnVsbF9uYW1lIjoiRmVkZXggbG9naXN0Y3MiLCJtb2JpbGUiOm51bGwsImlzX2FkbWluIjpmYWxzZSwid2VjaGF0X2lkIjpudWxsLCJhY3RpdmVfZmxhZyI6dHJ1ZSwidXNlcl9jb21wYW55X3R5cGUiOiJGcmVpZ2h0IEZvcndhcmRlciIsImVtYWlsX25vdGlmaWNhdGlvbiI6dHJ1ZSwic2hhcmVkX2xpY2Vuc2VfY291bnQiOjAsImNvbXBhbnlfYWRtaW5fY250IjozLCJwcm9maWxlX2ltYWdlX3R5cGUiOm51bGx9fQ=="

            jtkey = request.env['ir.config_parameter'].sudo().search([('key','=','jwt')],limit=1).value
            print(">........auth jt key........",jtkey)
            if not jtkey:
                logging.info("======There is no JWT key============")
                return request.redirect_query('/web', query=None)

            decoded_data = self.process_auth(auth_token,jtkey)
            logging.info("====== decoded_data ============%s",decoded_data)
            if 'data' in decoded_data.keys():
                user_obj = request.env['res.users'].sudo().search([('login','=',decoded_data['data']['email'])])

                login_pass = request.env['ir.config_parameter'].sudo().search([('key','=','login_pass')],limit=1).value
                if user_obj and login_pass:
                    if request.session.uid and request.session.uid == user_obj.id:
                        logging.info("====== User already logged in============")
                        return request.redirect_query('/web', query=None)
            
                    # accounting_company_id = decoded_data['data']['accounting_company_id'] or None
                    # if accounting_company_id:
                    #     accounting_role = request.env['waka.roles'].sudo().search([('company_id','=',decoded_data['data']['accounting_company_id']),('user_ids','in',user_obj.id)],limit=1)
                    #     logging.info("====== accounting_role00000000============%s",accounting_role)
                    #     if accounting_role:
                    #         acc_groups = request.env['res.groups'].sudo().search([('category_id.name','=','Accounting')])
                    #         user_obj.sudo().write({"groups_id": [(3, user_id, 0) for user_id in acc_groups.ids]+ [(4, accounting_role.accounting_group.id, 0)],})

                    return request.redirect_query('/web/login', query={'login': user_obj.login, 'password': login_pass, 'redirect': '','wakatech_post':"POST"})
                else:
                    logging.info("====== User not found============%s",decoded_data['data']['email'])
                    return request.redirect_query('/web', query=None)



        if request.db and request.session.uid and not is_user_internal(request.session.uid):
            return request.redirect_query('/web/login_successful', query=request.params)
        return request.redirect_query('/web', query=request.params)

    def process_auth(self,auth,jtkey):
        length_str = auth[:2]
        key_length = int(length_str,16)
        token = auth[2:-key_length]
        try:
            decoded = jwt.decode(token, jtkey, algorithms=["HS256"])
            return {'success': True, 'invalidToken': False, 'data': decoded}
        except jwt.ExpiredSignatureError:
            return {'success': False, 'invalidToken': True, 'message': 'Session Expired'}
        except jwt.InvalidTokenError:
            return {'success': False, 'invalidToken': True, 'message': 'Invalid Token'}

    # ideally, this route should be `auth="user"` but that don't work in non-monodb mode.
    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):

        # Ensure we have both a database and a user
        ensure_db()
        if not request.session.uid:
            return request.redirect_query('/web/login', query=request.params, code=303)
        if kw.get('redirect'):
            return request.redirect(kw.get('redirect'), 303)
        if not security.check_session(request.session, request.env):
            raise http.SessionExpiredException("Session expired")
        if not is_user_internal(request.session.uid):
            return request.redirect('/web/login_successful', 303)

        # Side-effect, refresh the session lifetime
        request.session.touch()

        # Restore the user on the environment, it was lost due to auth="none"
        request.update_env(user=request.session.uid)
        try:
            context = request.env['ir.http'].webclient_rendering_context()
            response = request.render('web.webclient_bootstrap', qcontext=context)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        except AccessError:
            return request.redirect('/web/login?error=access')

    @http.route('/web/webclient/load_menus/<string:unique>', type='http', auth='user', methods=['GET'])
    def web_load_menus(self, unique, lang=None):
        """
        Loads the menus for the webclient
        :param unique: this parameters is not used, but mandatory: it is used by the HTTP stack to make a unique request
        :param lang: language in which the menus should be loaded (only works if language is installed)
        :return: the menus (including the images in Base64)
        """
        if lang:
            request.update_context(lang=lang)

        menus = request.env["ir.ui.menu"].load_web_menus(request.session.debug)
        body = json.dumps(menus, default=ustr)
        response = request.make_response(body, [
            # this method must specify a content-type application/json instead of using the default text/html set because
            # the type of the route is set to HTTP, but the rpc is made with a get and expects JSON
            ('Content-Type', 'application/json'),
            ('Cache-Control', 'public, max-age=' + str(http.STATIC_CACHE_LONG)),
        ])
        return response

    def _login_redirect(self, uid, redirect=None):
        return _get_login_redirect_url(uid, redirect)

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        logging.info("---------request.params----------%s",request.params)
        if "wakatech_post" in request.params:
            request.httprequest.method = "POST"
        else:
            # return GO_TO_WAKA
            logging.info("---------go_to_waka----------")
            return go_to_waka()

        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        # simulate hybrid auth=user/auth=public, despite using auth=none to be able
        # to redirect users when no db is selected - cfr ensure_db()
        if request.env.uid is None:
            if request.session.uid is None:
                # no user -> auth=public with specific website public user
                request.env["ir.http"]._auth_method_public()
            else:
                # auth=user
                request.update_env(user=request.session.uid)

        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            try:
                uid = request.session.authenticate(request.db, request.params['login'], request.params['password'])
                request.params['login_success'] = True
                return request.redirect(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    @http.route('/web/login_successful', type='http', auth='user', website=True, sitemap=False)
    def login_successful_external_user(self, **kwargs):
        """Landing page after successful login for external users (unused when portal is installed)."""
        valid_values = {k: v for k, v in kwargs.items() if k in LOGIN_SUCCESSFUL_PARAMS}
        return request.render('web.login_successful', valid_values)

    @http.route('/web/become', type='http', auth='user', sitemap=False)
    def switch_to_admin(self):
        uid = request.env.user.id
        if request.env.user._is_system():
            uid = request.session.uid = odoo.SUPERUSER_ID
            # invalidate session token cache as we've changed the uid
            request.env.registry.clear_cache()
            request.session.session_token = security.compute_session_token(request.session, request.env)

        return request.redirect(self._login_redirect(uid))

    @http.route('/web/health', type='http', auth='none', save_session=False)
    def health(self):
        data = json.dumps({
            'status': 'pass',
        })
        headers = [('Content-Type', 'application/json'),
                   ('Cache-Control', 'no-store')]
        return request.make_response(data, headers)

    @http.route(['/robots.txt'], type='http', auth="none")
    def robots(self, **kwargs):
        return "User-agent: *\nDisallow: /\n"

GO_TO_WAKA = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Auto-click Button</title>
<script>
    window.onload = function() {
        document.getElementById('autoClickButton').click();
    };
</script>
</head>
<body>
<!-- Button with href attribute -->
<a id="autoClickButton" href="https://qa.wakatech.com/login">Auto-click Button</a>
</body>
</html>
        """
