# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from wtforms import ValidationError

from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool, PoolMeta

from nereid import (
    abort, current_user, flash, login_required, redirect, render_template,
    request, route, url_for)
from nereid.contrib.locale import make_lazy_gettext

_ = make_lazy_gettext('nereid_wishlist')


class Product(metaclass=PoolMeta):
    """
    Extension of product variant
    """
    __name__ = 'product.product'

    wishlists = fields.Many2Many(
        'product.wishlist-product',
        'product', 'wishlist', 'Wishlists'
    )

    @classmethod
    def copy(cls, products, default=None):
        """Duplicate products
        """
        if default is None:
            default = {}
        default = default.copy()

        default['wishlists'] = []

        return super(Product, cls).copy(products, default)


class NereidUser(metaclass=PoolMeta):
    """
    Extension of Nereid User
    """
    __name__ = 'nereid.user'

    wishlists = fields.One2Many(
        'wishlist.wishlist', 'nereid_user', 'Wishlist'
    )


class Wishlist(ModelSQL, ModelView):
    """
    Wishlist
    """
    __name__ = "wishlist.wishlist"

    is_public = fields.Boolean('Public')

    nereid_user = fields.Many2One(
        'nereid.user', 'Nereid User', required=True
    )
    name = fields.Char('Name', required=True)
    products = fields.Many2Many(
        'product.wishlist-product',
        'wishlist', 'product', 'Products',
    )

    @staticmethod
    def default_is_public():
        return False

    @classmethod
    def _search_or_create_wishlist(cls, name=''):
        """
        Search wishlist according to name.
        if wishlist exist return wishlist, if not create a
        new wishlist named Default and return that wishlist

        return type: wishlist
        """
        if not name:
            name = str(_('Default'))
        try:
            wishlist, = cls.search([
                ('nereid_user', '=', current_user.id),
                ('name', '=', name),
            ])
        except ValueError:
            wishlist, = cls.create([{
                'name': name,
                'nereid_user': current_user.id,
            }])
        return wishlist

    @classmethod
    @route('/wishlists', methods=["GET", "POST"])
    @login_required
    def render_wishlists(cls):
        """
        Render all wishlist of the current user.
        if request is post and name is passed then call method
        _search_or_create_wishlist.
        """
        if request.method == 'POST' and request.form.get("name"):
            wishlist = cls._search_or_create_wishlist(request.form.get("name"))
            if request.is_xhr:
                # TODO: send all wishlist as serialized data
                return 'success', 200
            return redirect(
                url_for(
                    'wishlist.wishlist.render_wishlist', active_id=wishlist.id
                )
            )
        return render_template('wishlists.jinja')

    @route(
        '/wishlists/<int:active_id>',
        methods=["POST", "GET", "DELETE"]
    )
    def render_wishlist(self):
        """
        Render specific wishlist of current user.
        rename wishlist on post  and delete on delete request
        """
        Wishlist = Pool().get('wishlist.wishlist')

        if self.nereid_user != current_user and \
                (request.method != "GET" or not self.is_public):

            abort(404)

        if request.method == "POST" and request.form.get('name'):

            name = request.form.get('name')
            wishlist = Wishlist.search([
                ('nereid_user', '=', current_user.id),
                ('id', '!=', self.id),
                ('name', '=', name),
            ], limit=1)
            if wishlist:
                flash(
                    _(
                        'Wishlist with name: %(name)s already exists.',
                        name=name
                    )
                )
                return redirect(request.referrer)
            else:
                self.name = name
                self.is_public = True if request.form.get('is_public') \
                    else False
                self.save()
                flash(_('Wishlist Updated'))
            if request.is_xhr:
                return 'success', 200

            return redirect(request.referrer)

        elif request.method == "DELETE":
            Wishlist.delete([self])
            if request.is_xhr:
                # TODO: send serialized data of current wishlist
                return 'success', 200

            return url_for('wishlist.wishlist.render_wishlists')

        return render_template('wishlist.jinja', wishlist=self)

    @classmethod
    @route('/wishlists/products', methods=["POST"])
    @login_required
    def wishlist_product(cls):
        """
        Add/Remove product in wishlist.
        If wishlist_id is passed then search for wishlist and add/remove
        product else create a default wishlist and add product.

        :params
            wishlist: Get the id of wishlist
            product: Get product id
            action: add or remove, add will add product to wishlist.
                remove will unlink product from wishlist
        """
        Product = Pool().get('product.product')

        wishlist_id = request.form.get("wishlist", type=int)
        if wishlist_id:
            try:
                wishlist, = cls.search([
                    ('id', '=', wishlist_id),
                    ('nereid_user', '=', current_user.id),
                ])
            except ValueError:
                raise ValidationError("Wishlist not valid!")
        else:
            wishlist = cls._search_or_create_wishlist()
        product = Product.search([
            ('id', '=', request.form.get("product", type=int)),
            ('displayed_on_eshop', '=', True),
            ('template.active', '=', True),
        ], limit=1)
        if not product or request.form.get('action') not in ['add', 'remove']:
            abort(404)
        cls.write([wishlist], {
            'products': [(request.form.get('action'), product)],
        })
        if request.is_xhr:
            # TODO: Send serailized data of wishllist
            return 'success', 200

        return redirect(
            url_for(
                'wishlist.wishlist.render_wishlist',
                active_id=wishlist.id
            )
        )


class ProductWishlistRelationship(ModelSQL):
    """
    This is the relation between wishlist and a product.
    """
    __name__ = 'product.wishlist-product'

    product = fields.Many2One(
        'product.product', 'Product',
        domain=[
            ('active', '=', True),
        ],
        ondelete='CASCADE', required=True,
    )
    wishlist = fields.Many2One(
        'wishlist.wishlist', 'Wishlist',
        ondelete='CASCADE', required=True
    )
