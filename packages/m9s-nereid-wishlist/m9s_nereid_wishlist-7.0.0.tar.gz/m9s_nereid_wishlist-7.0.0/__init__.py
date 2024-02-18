# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool

from . import wishlist

__all__ = ['register']


def register():
    Pool.register(
        wishlist.NereidUser,
        wishlist.Wishlist,
        wishlist.Product,
        wishlist.ProductWishlistRelationship,
        module='nereid_wishlist', type_='model')
