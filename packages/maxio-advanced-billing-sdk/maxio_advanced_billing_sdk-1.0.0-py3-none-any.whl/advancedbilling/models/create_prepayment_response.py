# -*- coding: utf-8 -*-

"""
advanced_billing

This file was automatically generated for Maxio by APIMATIC v3.0 (
 https://www.apimatic.io ).
"""
from advancedbilling.models.created_prepayment import CreatedPrepayment


class CreatePrepaymentResponse(object):

    """Implementation of the 'Create Prepayment Response' model.

    TODO: type model description here.

    Attributes:
        prepayment (CreatedPrepayment): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "prepayment": 'prepayment'
    }

    def __init__(self,
                 prepayment=None):
        """Constructor for the CreatePrepaymentResponse class"""

        # Initialize members of the class
        self.prepayment = prepayment 

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
        prepayment = CreatedPrepayment.from_dictionary(dictionary.get('prepayment')) if dictionary.get('prepayment') else None
        # Return an object of this model
        return cls(prepayment)
