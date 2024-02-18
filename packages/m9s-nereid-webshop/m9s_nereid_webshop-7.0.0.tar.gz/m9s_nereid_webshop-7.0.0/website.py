# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from nereid import current_app, jsonify, render_template, request, route
from trytond.model import ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Not


class Website(metaclass=PoolMeta):
    __name__ = 'nereid.website'

    cms_root_menu = fields.Many2One(
        'nereid.cms.menuitem', "CMS root menu", ondelete='RESTRICT',
        
    )

    show_site_message = fields.Boolean('Show Site Message')
    site_message = fields.Char(
        'Site Message',
        states={
            'readonly': Not(Eval('show_site_message', False)),
            'required': Eval('show_site_message', False)
        },
        depends=['show_site_message']
    )

    copyright_year_range = fields.Char('Copyright Year Range')

    cms_root_footer = fields.Many2One(
        'nereid.cms.menuitem', "CMS root Footer", ondelete='RESTRICT',
        
    )

    homepage_menu = fields.Many2One(
        'nereid.cms.menuitem', "Homepage Menu", ondelete='RESTRICT',
        
    )
    default_product_image = fields.Many2One("nereid.static.file",
        'Default product image',
        help='This image will be shown as a placeholder if no other '
        'product image is found')
    accept_gift_card = fields.Boolean('Accept Gift Card')
    carriers = fields.Many2Many(
        "nereid.website.website-carrier", "website", "carrier", "Carriers")

    @classmethod
    @route('/sitemap', methods=["GET"])
    def render_sitemap(cls):
        """
        Return the sitemap.
        """
        Node = Pool().get('product.tree_node')

        # Search for nodes, sort by sequence.
        nodes = Node.search([
            ('parent', '=', None),
        ], order=[
            ('sequence', 'ASC'),
        ])

        return render_template('sitemap.jinja', nodes=nodes)

    @classmethod
    def auto_complete(cls, phrase):
        """
        Customizable method which returns a list of dictionaries
        according to the search query. The search service used can
        be modified in downstream modules.

        The front-end expects a jsonified list of dictionaries. For example,
        a downstream implementation of this method could return -:
        [
            ...
            {
                "value": "<suggestion string>"
            }, {
                "value": "Nexus 6"
            }
            ...
        ]
        """
        return []

    @classmethod
    @route('/search-auto-complete')
    def search_auto_complete(cls):
        """
        Handler for auto-completing search.
        """
        return jsonify(results=cls.auto_complete(
            request.args.get('q', '')
        ))

    @classmethod
    @route('/search')
    def quick_search(cls):
        """
        Downstream implementation of quick_search().

        TODO:
            * Add article search.
        """
        return super(Website, cls).quick_search()

    @staticmethod
    def default_cms_root_footer():
        """
        Get default record from xml
        """
        ModelData = Pool().get('ir.model.data')

        menu_item_id = ModelData.get_id("nereid_webshop", "cms_root_footer")
        return menu_item_id


class WebsiteCarrier(ModelSQL):
    "Website Carrier"
    __name__ = "nereid.website.website-carrier"

    website = fields.Many2One(
        "nereid.website", "Website", ondelete='CASCADE',
        required=True)
    carrier = fields.Many2One(
        "carrier", "Carrier", ondelete='CASCADE', required=True)
