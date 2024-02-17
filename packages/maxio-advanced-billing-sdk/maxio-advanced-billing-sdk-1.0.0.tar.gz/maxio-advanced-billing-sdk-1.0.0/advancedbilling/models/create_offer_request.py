# -*- coding: utf-8 -*-

"""
advanced_billing

This file was automatically generated for Maxio by APIMATIC v3.0 (
 https://www.apimatic.io ).
"""
from advancedbilling.models.create_offer import CreateOffer


class CreateOfferRequest(object):

    """Implementation of the 'Create Offer Request' model.

    TODO: type model description here.

    Attributes:
        offer (CreateOffer): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "offer": 'offer'
    }

    def __init__(self,
                 offer=None):
        """Constructor for the CreateOfferRequest class"""

        # Initialize members of the class
        self.offer = offer 

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
        offer = CreateOffer.from_dictionary(dictionary.get('offer')) if dictionary.get('offer') else None
        # Return an object of this model
        return cls(offer)
