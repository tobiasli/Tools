﻿#-------------------------------------------------------------------------------
# Name:        GroceryShopping_Test_Suite
# Purpose:      Test the components of the GroceryShopping class.
#
# Author:      Tobias
#
# Created:     01.05.2015
# Copyright:   (c) Tobias 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import unittest
import groceryshopping
import random


class TestGroceryClass(unittest.TestCase):

    def test_unit_class(self):
        for a in ['102.5','1/2','0.5','0.000001']:
            for u in groceryshopping.UNIT_PROPERTIES:
                if u[2]:
                    prefixes = u[2].keys()
                else:
                    prefixes = ['']
                for p in prefixes:
                    unit = groceryshopping.Unit(u)

                    self.assertEqual(unit.base_unit,u[0])
                    self.assertEqual(unit.variants,u[1])
                    self.assertEqual(unit.unit_prefixes,u[2])
                    self.assertEqual(unit.plural_of_base_unit,u[3])
                    self.assertTrue(unit._pattern())

                    amount_test = a
                    test_string = amount_test+' '
                    if p:
                        prefix = p
                        prefix_adjust = groceryshopping.UNIT_PREFIXES[prefix]
                        test_string += prefix
                    else:
                        prefix_adjust = 1
                    test_string += u[0]

                    unit_dictionary = unit.match_unit(test_string)

                    self.assertTrue(unit_dictionary)

                    self.assertTrue(unit.normalize_amount(unit_dictionary))

                    print unit.amount_formated(unit.normalize_amount(unit_dictionary))




    def test_units_class(self):
        pass


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGroceryClass)
    unittest.TextTestRunner(verbosity=2).run(suite)
