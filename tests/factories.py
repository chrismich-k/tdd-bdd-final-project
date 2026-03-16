# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
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

# pylint: disable=too-few-public-methods

"""
Test Factory to make fake objects for testing
"""
from itertools import product
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal
from service.models import Product, Category

PRODUCT_CATEGORY_PREFIX = {
    Category.CLOTHS: ["Second Hand", "Fashion", "Designer"],
    Category.FOOD: ["Organic", "Frozen", "Low-Carb"],
    Category.HOUSEWARES: ["Basic", "Premium", "Home Line"],
    Category.AUTOMOTIVE: ["Budget", "Refurbished", "Quality"],
    Category.TOOLS: ["Pro", "Stainless Steel", "Industrial Grade"],
}

PRODUCT_CATEGORY_NAMES = {
    Category.CLOTHS: ["Sweater", "Hoodie", "Jeans"],
    Category.FOOD: ["Bread", "Boiled Egg", "Cheese Burger"],
    Category.HOUSEWARES: ["Bug Repellant", "Clock"],
    Category.AUTOMOTIVE: ["Spark Plug", "Motor Oil", "Jerry Can"],
    Category.TOOLS: ["Electric Drill", "Monkey Wrench", "Pliers"],
}

# product names per category
PRODUCT_CATEGORY_PREFIXED_NAMES = {
    category: [
        f"{p} {n}" for p, n in product(
            PRODUCT_CATEGORY_PREFIX[category],
            PRODUCT_CATEGORY_NAMES[category]
        )
    ]
    for category in set(PRODUCT_CATEGORY_PREFIX) & set(PRODUCT_CATEGORY_NAMES)
}

# all products in one list, to just use a simple FuzzyChoice()
PRODUCT_NAMES = [
    product_name
    for sublist in PRODUCT_CATEGORY_PREFIXED_NAMES.values()
    for product_name in sublist
]


class ProductFactory(factory.Factory):
    """Creates fake products for testing"""

    class Meta:
        """Maps factory to data model"""

        model = Product

    id = factory.Sequence(lambda n: n)
    # FUTURE: match name and category using PRODUCT_CATEGORY_PREFIXED_NAMES
    name = FuzzyChoice(PRODUCT_NAMES)
    description = factory.Faker("text")
    price = FuzzyDecimal(2, 200, 2)
    available = FuzzyChoice([True, False])
    category = FuzzyChoice(Category)
