# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(
            name="Fedora",
            description="A red hat",
            price=12.50, available=True,
            category=Category.CLOTHS
        )
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_product(self):
        """It should read a newly created object back from the DB and check whether it matches"""
        new_product = ProductFactory()
        app.logger.debug("created a new product object: {new_product}")

        # persist in DB
        new_product.id = None
        new_product.create()
        self.assertIsNotNone(new_product.id)

        # query product from DB
        read_product = Product.find(new_product.id)

        # check if attributes match the created object
        self.assertEqual(read_product.id, new_product.id)
        self.assertEqual(read_product.name, new_product.name)
        self.assertEqual(read_product.description, new_product.description)
        self.assertEqual(read_product.available, new_product.available)
        self.assertEqual(read_product.price, new_product.price)
        self.assertEqual(read_product.category, new_product.category)

    def test_update_product(self):
        """It should update an object and assert the changes are persisted"""
        new_product = ProductFactory()
        app.logger.debug("created a new product object: {new_product}")

        # persist in DB
        new_product.id = None
        new_product.create()
        app.logger.debug("persisted the new product in DB: {new_product}")

        # update attributes and update in DB
        original_description = new_product.description
        new_description = "This is a test description."
        new_product.description = new_description
        new_product.update()

        # assert the description is set and there is an id
        self.assertIsNotNone(new_product.id)
        self.assertEqual(new_description, new_product.description)

        # fetch all products from DB and assert it's one entry
        all_products = Product.all()
        self.assertEqual(len(all_products), 1)

        # assert the description has changed and id is the same
        self.assertNotEqual(original_description, all_products[0].description)
        self.assertEqual(new_product.id, all_products[0].id)

    def test_delete_product(self):
        """It should delete a newly created test object and validate it's deleted"""
        new_product = ProductFactory()
        app.logger.debug("created a new product object: {new_product}")

        # persist in DB
        new_product.id = None
        new_product.create()
        app.logger.debug("persisted the new product in DB: {new_product}")

        # fetch all products from DB and assert it's one entry
        all_products = Product.all()
        self.assertEqual(len(all_products), 1)

        # delete the test product and assert it's deleted (no objects in DB)
        all_products[0].delete()
        remaining_products = Product.all()
        self.assertEqual(len(remaining_products), 0)

    def test_all_five_products(self):
        """It should create 5 products in an empty DB and assert there are 5 products in DB"""
        # fetch all products from DB and assert it's empty
        products = Product.all()
        self.assertEqual(len(products), 0)

        # create five test products
        for _ in range(5):
            new_product = ProductFactory()
            new_product.create()

        # get all products and assert it's five of them
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_products_by_name(self):
        """It should test whether find_by_name() correctly filters products"""
        # create five test products
        for _ in range(5):
            new_product = ProductFactory()
            new_product.create()

        # get first product from list of all products
        all_products = Product.all()
        first_name = all_products[0].name

        # count all products with the same name as first product
        count = sum(1 for product in all_products if product.name == first_name)

        # assert Product.find_by_name() finds the same number of matches
        filtered_products = Product.find_by_name(first_name).all()
        self.assertEqual(len(filtered_products), count)

        # assert all found products have the name we're loooking for
        count = sum(1 for product in filtered_products if product.name == first_name)
        self.assertEqual(len(filtered_products), count)

    def test_find_products_by_availability(self):
        """It should test whether find_by_availability() correctly filters products"""
        # create ten test products
        for _ in range(10):
            new_product = ProductFactory()
            new_product.create()

        # get first product from list of all products
        all_products = Product.all()
        first_available = all_products[0].available

        # count all products with the same availability as the first product
        count = sum(1 for product in all_products if product.available == first_available)

        # assert Product.find_by_availability() finds the same number of matches
        filtered_products = Product.find_by_availability(first_available).all()
        self.assertEqual(len(filtered_products), count)

        # assert all found products have the availability we're loooking for
        count = sum(1 for product in filtered_products if product.availabley == first_available)
        self.assertEqual(len(filtered_products), count)

    def test_find_products_by_category(self):
        """It should test whether find_by_category() correctly filters products"""
        # create ten test products
        for _ in range(10):
            new_product = ProductFactory()
            new_product.create()

        # get first product's category from list of all products
        all_products = Product.all()
        first_category = all_products[0].category

        # count all products with that category
        count = sum(1 for product in all_products if product.category == first_category)

        # assert Product.find_by_availability() finds the same number of matches
        filtered_products = Product.find_by_category(first_category).all()
        self.assertEqual(len(filtered_products), count)

        # assert all found products have the category we're loooking for
        count = sum(1 for product in filtered_products if product.category == first_category)
        self.assertEqual(len(filtered_products), count)
