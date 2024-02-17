# -*- coding: utf-8 -*-

"""
advanced_billing

This file was automatically generated for Maxio by APIMATIC v3.0 (
 https://www.apimatic.io ).
"""
from advancedbilling.api_helper import APIHelper
from advancedbilling.models.product_price_point import ProductPricePoint


class BulkCreateProductPricePointsResponse(object):

    """Implementation of the 'Bulk Create Product Price Points Response' model.

    TODO: type model description here.

    Attributes:
        price_points (List[ProductPricePoint]): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "price_points": 'price_points'
    }

    _optionals = [
        'price_points',
    ]

    def __init__(self,
                 price_points=APIHelper.SKIP):
        """Constructor for the BulkCreateProductPricePointsResponse class"""

        # Initialize members of the class
        if price_points is not APIHelper.SKIP:
            self.price_points = price_points 

    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object
            as obtained from the deserialization of the server's response. The
            keys MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """

        if dictionary is None:
            return None

        # Extract variables from the dictionary
        price_points = None
        if dictionary.get('price_points') is not None:
            price_points = [ProductPricePoint.from_dictionary(x) for x in dictionary.get('price_points')]
        else:
            price_points = APIHelper.SKIP
        # Return an object of this model
        return cls(price_points)
